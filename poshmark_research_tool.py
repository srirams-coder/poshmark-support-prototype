#!/usr/bin/env python3
"""
Professional-grade research tool to analyze Poshmark customer support failures.
Collects and analyzes reviews from Trustpilot and Reddit (r/poshmark).
"""

import csv
import json
import re
import time
from datetime import datetime
from typing import Any, Optional

import requests
from bs4 import BeautifulSoup
from google_play_scraper import reviews as gp_reviews, Sort as GP_Sort
from app_store_scraper import AppStore
# Reddit (praw) - optional; script runs without it if credentials missing
try:
    import praw
    PRAW_AVAILABLE = True
except ImportError:
    PRAW_AVAILABLE = False

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
TRUSTPILOT_URL = "https://www.trustpilot.com/review/poshmark.com"
TRUSTPILOT_PAGES = 200  # Number of review pages to fetch (~20 reviews per page). Scraping, not API.
# Reddit communities to search (names with or without leading "r/")
REDDIT_SUBREDDITS = ["poshmark", "BehindTheClosetDoor", "reselling"]

# Minimum date to include (reviews/posts before this are skipped)
MIN_DATE = datetime(2025, 1, 1).date()

# Support themes and detailed keyword lists
SUPPORT_CATEGORIES = {
    "Support Access & Availability": [
        "no phone number",
        "contact person",
        "live human",
        "actual person",
        "no live chat",
        "unresponsive",
        "email only",
        "ghosted",
        "waiting weeks",
        "no reply",
        "support",
        "poshmark support",
        "customer service",
        "customer support",
        "support team" 
    ],
    "Automation & AI Failures": [
        "canned response",
        "boiler plate",
        "generic reply",
        "automated answer",
        "ai response",
        "template",
        "robotic",
        "loop",
        "computer generated",
    ],
    "Procedural & Logic Failures": [
        "closed case",
        "denied return",
        "ignored proof",
        "no appeal",
        "funds withheld",
        "earnings held",
        "payout delayed",
        "security hold",
        "shadow ban",
        "wrongful suspension",
    ],
    "2026 Policy Conflicts": [
        "3% cancellation",
        "cancellation threshold",
        "stealth update",
        "cancellation policy",
        "account restricted",
        "poshmark jail",
        "account suspension",
        "buyer requested cancellation",
    ],
    "Security Support Issues": [
        "tech support scam",
        "impersonation",
        "verification code",
        "locked out",
        "two factor",
        "account hacked",
    ],
}

# Flattened list of all support keywords for matching/searching
SUPPORT_KEYWORDS = sorted({kw for kws in SUPPORT_CATEGORIES.values() for kw in kws})

# Intent words: used for sentiment when there is no star rating (e.g. Reddit).
# Keyword match = relevant; sentiment = from negative/positive intent in the text.
NEGATIVE_INTENT_KEYWORDS = [
    "poor", "bad", "terrible", "worst", "horrible", "awful", "useless", "scam", "scammed",
    "hate", "never again", "no help", "unhelpful", "disappointed", "frustrated", "frustrating",
    "waste", "wasted", "failed", "failure", "broken", "don't use", "do not use", "avoid",
    "stay away", "ridiculous", "pathetic", "canned", "bot", "no response", "unresponsive",
    "ghosted", "ignored", "no reply", "no phone", "can't reach", "cannot reach", "worst experience",
    "rip off", "ripoff", "stole", "steal", "withheld", "withhold", "denied", "refused",
    "unacceptable", "disgusting", "nightmare", "joke", "mess", "disaster", "fake", "fraud",
]
POSITIVE_INTENT_KEYWORDS = [
    "great", "good", "helpful", "resolved", "fixed", "quick", "responsive", "excellent",
    "happy", "satisfied", "recommend", "smooth", "easy", "fast response", "solved", "fixed my",
    "thank", "thanks", "appreciate", "pleased", "professional", "friendly", "prompt",
]

LEADERSHIP_KEYWORDS = {
    "automation": [
        "automation",
        "automated",
        "ai ",
        "algorithm",
        "ai response",
        "automated answer",
        "robotic",
        "computer generated",
        "loop",
        "template",
        "canned response",
        "generic reply",
        "boiler plate",
    ],
    "human_support": [
        "human",
        "real person",
        "live agent",
        "phone support",
        "speak to someone",
        "live human",
        "actual person",
        "contact person",
        "no phone number",
        "no live chat",
        "email only",
    ],
}
OUTPUT_CSV = "poshmark_support_analysis_2026.csv"

# Reddit API placeholders - replace with your credentials from https://www.reddit.com/prefs/apps
REDDIT_CLIENT_ID = "ZgceGcVzL-er9wUbknnJJA"
REDDIT_CLIENT_SECRET = "xr5BId15kOoWsSFpA0aRDEWbH-3vmQ"
REDDIT_USER_AGENT = "PoshmarkSupportResearch/1.0 (Python)"


# ---------------------------------------------------------------------------
# Helpers: text cleaning and sentiment
# ---------------------------------------------------------------------------
def clean_text(text: str) -> str:
    """Remove extra newlines, leading/trailing whitespace, and problematic special characters for CSV."""
    if not text or not isinstance(text, str):
        return ""
    # Normalize whitespace and newlines to single space
    text = re.sub(r"\s+", " ", text)
    # Remove control characters and other problematic chars for CSV
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text)
    return text.strip()


def find_matched_keywords(text: str, keywords: list) -> list:
    """Return list of keywords found in text (case-insensitive)."""
    if not text:
        return []
    text_lower = text.lower()
    return [kw for kw in keywords if kw.lower() in text_lower]


def sentiment_from_keywords(matched: list[str]) -> str:
    """Produce a Sentiment label based on which support keywords were found (no rating)."""
    if not matched:
        return "neutral"
    return "negative: " + ", ".join(matched)


def sentiment_from_rating_and_keywords(rating: Optional[int], matched: list[str]) -> str:
    """
    Sentiment from star rating (1-5) when available, else from keywords.
    - 4-5 stars -> positive; 3 -> neutral; 1-2 -> negative.
    - No rating -> use sentiment_from_intent_and_keywords (caller must pass text).
    """
    label = ", ".join(matched) if matched else ""
    if rating is not None:
        if rating >= 4:
            return f"positive: {label}" if label else "positive"
        if rating == 3:
            return f"neutral: {label}" if label else "neutral"
        if rating <= 2:
            return f"negative: {label}" if label else "negative"
    return f"neutral: {label}" if matched else "neutral"


def sentiment_from_intent_and_keywords(text: str, matched_support_keywords: list[str]) -> str:
    """
    Sentiment from negative/positive intent words in text (for Reddit etc. where there is no rating).
    Keyword match only means relevant; negative/positive/neutral comes from intent words.
    """
    if not isinstance(text, str):
        text = str(text) if text else ""
    if not text:
        label = ", ".join(matched_support_keywords) if matched_support_keywords else ""
        return f"neutral: {label}" if label else "neutral"
    text_lower = text.lower()
    neg = [w for w in NEGATIVE_INTENT_KEYWORDS if w in text_lower]
    pos = [w for w in POSITIVE_INTENT_KEYWORDS if w in text_lower]
    label = ", ".join(matched_support_keywords) if matched_support_keywords else ""
    if neg and not pos:
        return f"negative: {label}" if label else "negative"
    if pos and not neg:
        return f"positive: {label}" if label else "positive"
    if pos and neg:
        return f"mixed: {label}" if label else "mixed"
    return f"neutral: {label}" if label else "neutral"


# ---------------------------------------------------------------------------
# Trustpilot: scraping (no official API). We fetch HTML and parse __NEXT_DATA__.
# Each page = ~20 reviews, newest first. Failed pages are skipped (no retries).
# ---------------------------------------------------------------------------
def _get_trustpilot_headers() -> dict:
    return {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    }


def fetch_trustpilot_page(page: int = 1) -> Optional[requests.Response]:
    """Fetch a single Trustpilot review page (page 1 = default URL, 2+ = ?page=N)."""
    url = TRUSTPILOT_URL if page <= 1 else f"{TRUSTPILOT_URL}?page={page}"
    try:
        r = requests.get(url, headers=_get_trustpilot_headers(), timeout=30)
        r.raise_for_status()
        return r
    except requests.RequestException as e:
        print(f"Trustpilot request error (page {page}): {e}")
        return None


def parse_next_data(html: str) -> Optional[dict]:
    """Extract __NEXT_DATA__ JSON from Trustpilot HTML using BeautifulSoup."""
    soup = BeautifulSoup(html, "html.parser")
    script = soup.find("script", id="__NEXT_DATA__")
    if not script or not script.string:
        return None
    try:
        return json.loads(script.string)
    except json.JSONDecodeError:
        return None


def get_trustpilot_reviews(max_pages: int = TRUSTPILOT_PAGES) -> list:
    """
    Fetch Trustpilot reviews for poshmark.com by scraping HTML (no API).
    Requests page=1, page=2, ... page=max_pages; each page has ~20 reviews (newest first).
    If a page request fails (e.g. 403), that page is skipped so older reviews can be missing.
    """
    all_reviews = []
    pages_fetched = 0
    for page in range(1, max_pages + 1):
        resp = fetch_trustpilot_page(page)
        if not resp:
            continue
        data = parse_next_data(resp.text)
        if not data:
            if page == 1:
                print("Could not find __NEXT_DATA__ on Trustpilot page.")
            continue
        pages_fetched += 1
        try:
            page_props = data.get("props", {}).get("pageProps", {})
            reviews = page_props.get("reviews") or []
        except (AttributeError, TypeError):
            reviews = []
        for r in reviews:
            text = (r.get("text") or "") + " " + (r.get("title") or "")
            matched = find_matched_keywords(text, SUPPORT_KEYWORDS)
            if not matched:
                continue
            dates = r.get("dates") or {}
            pub = dates.get("publishedDate") or dates.get("experiencedDate") or ""
            pub_str = ""
            if pub:
                try:
                    # ISO format e.g. 2026-02-08T...
                    pub_str = pub.split("T")[0] if "T" in pub else str(pub)[:10]
                except Exception:
                    # If date parsing fails, keep pub_str empty and include the review
                    pub_str = ""
            rating = r.get("rating")
            try:
                rating_int = int(rating) if rating is not None else None
            except (TypeError, ValueError):
                rating_int = None
            all_reviews.append({
                "Date": pub_str,
                "Source": "Trustpilot",
                "Content": clean_text((r.get("title") or "") + " " + (r.get("text") or "")),
                "Sentiment": sentiment_from_rating_and_keywords(rating_int, matched),
            })
        if page < max_pages:
            time.sleep(1)
    if pages_fetched < max_pages:
        print(f"Trustpilot: only {pages_fetched}/{max_pages} pages succeeded; some pages may have failed (e.g. 403).")
    return all_reviews


# ---------------------------------------------------------------------------
# Reddit: PRAW
# ---------------------------------------------------------------------------
def get_reddit_posts(max_per_keyword: int = 50) -> list:
    """
    Search configured subreddits for each support keyword and return matching posts (title + selftext).

    Note:
    - In r/poshmark we include any post that matches at least one SUPPORT_KEYWORD.
    - In broader communities (e.g. r/BehindTheClosetDoor, r/reselling) we require BOTH:
        * the word "poshmark" somewhere in the post, AND
        * at least one SUPPORT_KEYWORD match.
    """
    if not PRAW_AVAILABLE:
        print("praw not installed; skipping Reddit.")
        return []
    if not REDDIT_CLIENT_ID or REDDIT_CLIENT_ID == "YOUR_CLIENT_ID":
        print("Reddit credentials not set (client_id/secret); skipping Reddit.")
        return []
    try:
        reddit = praw.Reddit(
            client_id=REDDIT_CLIENT_ID,
            client_secret=REDDIT_CLIENT_SECRET,
            user_agent=REDDIT_USER_AGENT,
        )
    except Exception as e:
        print(f"Reddit auth error: {e}")
        return []

    seen_ids: set[str] = set()
    seen_comment_ids: set[str] = set()
    results = []
    # Normalize subreddit names (strip leading "r/" if present)
    subreddit_names = [name.lstrip("r/") for name in REDDIT_SUBREDDITS]

    for subreddit_name in subreddit_names:
        sub = reddit.subreddit(subreddit_name)
        for keyword in SUPPORT_KEYWORDS:
            try:
                for submission in sub.search(keyword, limit=max_per_keyword, time_filter="all"):
                    if submission.id in seen_ids:
                        continue
                    seen_ids.add(submission.id)
                    content = f"{submission.title or ''} {submission.selftext or ''}"
                    content_lower = content.lower()

                    # For broader communities, require "poshmark" + a support keyword (AND condition).
                    is_broad_sub = subreddit_name.lower() in ("behindtheclosetdoor", "reselling")
                    if is_broad_sub and "poshmark" not in content_lower:
                        continue

                    matched = find_matched_keywords(content, SUPPORT_KEYWORDS)
                    if not matched:
                        continue
                    created = getattr(submission, "created_utc", None)
                    date_str = ""
                    if created:
                        try:
                            created_dt = datetime.utcfromtimestamp(created)
                            created_date = created_dt.date()
                            # Skip if before our minimum date
                            if created_date < MIN_DATE:
                                continue
                            date_str = created_dt.strftime("%Y-%m-%d")
                        except Exception:
                            date_str = str(created)
                    results.append({
                        "Date": date_str,
                        "Source": f"Reddit:{sub.display_name_prefixed}",
                        "Content": clean_text(content),
                        "Sentiment": sentiment_from_intent_and_keywords(content, matched),
                    })

                    # Also scan comments under this submission; this is often where
                    # detailed support failure stories live. Load full comment tree (limit=None)
                    # so we don't miss replies; fall back to top-level only if API limits hit.
                    try:
                        submission.comments.replace_more(limit=None)
                    except Exception:
                        try:
                            submission.comments.replace_more(limit=0)
                        except Exception:
                            pass
                    time.sleep(0.3)
                    try:
                        for comment in submission.comments.list():
                            if getattr(comment, "id", None) in seen_comment_ids:
                                continue
                            seen_comment_ids.add(comment.id)
                            body = getattr(comment, "body", "") or ""
                            if not body:
                                continue
                            body_lower = body.lower()
                            if is_broad_sub and "poshmark" not in body_lower:
                                continue

                            matched_comment = find_matched_keywords(body, SUPPORT_KEYWORDS)
                            if not matched_comment:
                                continue

                            c_created = getattr(comment, "created_utc", None)
                            c_date_str = ""
                            if c_created:
                                try:
                                    c_dt = datetime.utcfromtimestamp(c_created)
                                    c_date = c_dt.date()
                                    if c_date < MIN_DATE:
                                        continue
                                    c_date_str = c_dt.strftime("%Y-%m-%d")
                                except Exception:
                                    c_date_str = str(c_created)

                            results.append({
                                "Date": c_date_str,
                                "Source": f"RedditComment:{sub.display_name_prefixed}",
                                "Content": clean_text(body),
                                "Sentiment": sentiment_from_intent_and_keywords(body, matched_comment),
                            })
                    except Exception as e:
                        print(f"Reddit comments error in r/{subreddit_name} for submission '{submission.id}': {e}")
            except Exception as e:
                print(f"Reddit search error in r/{subreddit_name} for '{keyword}': {e}")
            time.sleep(1)
    return results


# ---------------------------------------------------------------------------
# App stores: Google Play & Apple App Store
# ---------------------------------------------------------------------------
def get_play_store_reviews(app_id: str = "com.poshmark.app", max_reviews: int = 10000) -> list:
    """
    Fetch Google Play reviews for the Poshmark app, walking back until MIN_DATE.

    Includes all ratings (1-5 stars) that match SUPPORT_KEYWORDS; sentiment is set from
    star rating (positive/neutral/negative). We page using the continuation token to
    get as many matching reviews as the store returns.
    """
    rows: list[dict] = []
    token = None

    while len(rows) < max_reviews:
        try:
            batch, token = gp_reviews(
                app_id,
                lang="en",
                country="us",
                sort=GP_Sort.NEWEST,
                count=200,
                continuation_token=token,
            )
        except Exception as e:
            print(f"Play Store fetch error: {e}")
            break

        if not batch:
            break

        # Reviews are returned newest-first within each batch. Include all ratings (1-5) that match keywords.
        for r in batch:
            content = f"{r.get('title') or ''} {r.get('content') or ''}"
            dt = r.get("at")
            date_str = ""
            if isinstance(dt, datetime):
                # Once we pass below MIN_DATE, we can stop entirely.
                if dt.date() < MIN_DATE:
                    token = None
                    break
                date_str = dt.strftime("%Y-%m-%d")

            matched = find_matched_keywords(content, SUPPORT_KEYWORDS)
            if not matched:
                continue

            rating = r.get("score") or r.get("rating")
            try:
                rating_int = int(rating) if rating is not None else None
            except (TypeError, ValueError):
                rating_int = None

            rows.append({
                "Date": date_str,
                "Source": "PlayStore",
                "Content": clean_text(content),
                "Sentiment": sentiment_from_rating_and_keywords(rating_int, matched),
            })

            if len(rows) >= max_reviews:
                break

        if not token or len(rows) >= max_reviews:
            break
        time.sleep(0.5)

    return rows


def get_app_store_reviews(country: str = "us", app_name: str = "poshmark", app_id: int = 470412147,
                          max_reviews: int = 4000) -> list:
    """Fetch recent Apple App Store reviews for the Poshmark app."""
    def _parse_iso_date(value: str) -> Optional[datetime]:
        if not value:
            return None
        try:
            # Common formats: 2026-02-25T11:49:56-07:00 or ...Z
            v = value.replace("Z", "+00:00")
            return datetime.fromisoformat(v)
        except Exception:
            try:
                return datetime.strptime(value.split("T")[0], "%Y-%m-%d")
            except Exception:
                return None

    def _fetch_rss_json_reviews(max_pages: int = 10) -> list[dict]:
        """
        Fallback: Apple's public customer reviews RSS feed (JSON).
        This is often more reliable than HTML scraping.
        """
        collected: list[dict] = []
        page = 1
        # Apple’s public RSS feed is typically limited to ~10 pages.
        while len(collected) < max_reviews and page <= max_pages:
            url = (
                f"https://itunes.apple.com/{country}/rss/customerreviews/"
                f"page={page}/id={app_id}/sortby=mostrecent/json"
            )
            try:
                resp = requests.get(url, timeout=30)
                resp.raise_for_status()
                data = resp.json()
            except Exception as e:
                print(f"App Store RSS fetch error (page {page}): {e}")
                break

            entries = ((data or {}).get("feed") or {}).get("entry") or []
            if not isinstance(entries, list) or not entries:
                break

            # The first entry is often app metadata; reviews include "content" + "im:rating"
            page_added = 0
            for entry in entries:
                if not isinstance(entry, dict):
                    continue
                if "im:rating" not in entry or "content" not in entry:
                    continue
                # Rating filter: only keep reviews with rating < 3 stars.
                rating_raw = (entry.get("im:rating") or {}).get("label") if isinstance(entry.get("im:rating"), dict) else entry.get("im:rating")
                try:
                    rating_value = int(str(rating_raw).strip())
                except Exception:
                    rating_value = None
                if rating_value is None or rating_value >= 3:
                    continue
                title = ((entry.get("title") or {}).get("label")) if isinstance(entry.get("title"), dict) else entry.get("title")
                body = ((entry.get("content") or {}).get("label")) if isinstance(entry.get("content"), dict) else entry.get("content")
                content = f"{title or ''} {body or ''}"

                updated = (entry.get("updated") or {}).get("label") if isinstance(entry.get("updated"), dict) else entry.get("updated")
                dt = _parse_iso_date(updated or "")
                date_str = ""
                if isinstance(dt, datetime):
                    if dt.date() < MIN_DATE:
                        # Since feed is most-recent first, we can stop early once we're past MIN_DATE
                        return collected
                    date_str = dt.strftime("%Y-%m-%d")

                matched = find_matched_keywords(content, SUPPORT_KEYWORDS)
                if not matched:
                    continue

                collected.append({
                    "Date": date_str,
                    "Source": "AppStore",
                    "Content": clean_text(content),
                    "Sentiment": sentiment_from_rating_and_keywords(rating_value, matched),
                })
                page_added += 1
                if len(collected) >= max_reviews:
                    break

            # No reviews on this page means we're done.
            if page_added == 0:
                break
            page += 1
            time.sleep(0.5)

        return collected

    rows: list[dict] = []

    # First try app_store_scraper (can fail if Apple changes HTML / blocks).
    try:
        app = AppStore(country=country, app_name=app_name, app_id=app_id)
        app.review(how_many=max_reviews)
        raw_reviews = app.reviews or []
        for r in raw_reviews:
            # Rating filter: only keep reviews with rating < 3 stars.
            rating = r.get("rating")
            try:
                rating_value = int(rating)
            except Exception:
                rating_value = None
            if rating_value is None or rating_value >= 3:
                continue

            content = f"{r.get('title') or ''} {r.get('review') or ''}"
            matched = find_matched_keywords(content, SUPPORT_KEYWORDS)
            if not matched:
                continue
            dt = r.get("date")
            date_str = ""
            if isinstance(dt, datetime):
                if dt.date() < MIN_DATE:
                    continue
                date_str = dt.strftime("%Y-%m-%d")
            rows.append({
                "Date": date_str,
                "Source": "AppStore",
                "Content": clean_text(content),
                "Sentiment": sentiment_from_rating_and_keywords(rating_value, matched),
            })
    except Exception as e:
        print(f"App Store scrape error (will try RSS fallback): {e}")

    # Fallback to RSS JSON if scraping failed or returned nothing.
    if not rows:
        rows = _fetch_rss_json_reviews()

    return rows


# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------
# Export and leadership analysis
# ---------------------------------------------------------------------------
def export_to_csv(rows: list, path: str = OUTPUT_CSV) -> None:
    """Write combined data to CSV with headers: Date, Source, Content, Sentiment."""
    if not rows:
        print("No rows to export.")
        return
    fieldnames = ["Date", "Source", "Content", "Sentiment"]
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    print(f"Exported {len(rows)} rows to {path}")


def leadership_analysis(rows: list) -> dict:
    """
    Post-processing: percentage of reviews mentioning 'automation' vs 'human support'.
    Returns dict with keys: pct_automation, pct_human_support, total_analyzed.
    """
    if not rows:
        return {"pct_automation": 0.0, "pct_human_support": 0.0, "total_analyzed": 0}
    automation_count = 0
    human_count = 0
    for row in rows:
        content = (row.get("Content") or "").lower()
        if any(kw in content for kw in LEADERSHIP_KEYWORDS["automation"]):
            automation_count += 1
        if any(kw in content for kw in LEADERSHIP_KEYWORDS["human_support"]):
            human_count += 1
    n = len(rows)
    return {
        "pct_automation": round(100.0 * automation_count / n, 2),
        "pct_human_support": round(100.0 * human_count / n, 2),
        "total_analyzed": n,
        "count_automation": automation_count,
        "count_human_support": human_count,
    }


def print_leadership_report(stats: dict) -> None:
    """Print leadership analysis summary to console."""
    print("\n--- Leadership Analysis (automation vs human support) ---")
    print(f"Total reviews/posts analyzed: {stats['total_analyzed']}")
    print(f"Mentioning automation-related terms: {stats.get('count_automation', 0)} ({stats['pct_automation']}%)")
    print(f"Mentioning human support-related terms: {stats.get('count_human_support', 0)} ({stats['pct_human_support']}%)")
    print("---\n")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> None:
    print("Poshmark Customer Support Research Tool")
    print("Keywords:", SUPPORT_KEYWORDS)
    print()

    # Trustpilot
    print("Fetching Trustpilot reviews...")
    trustpilot_rows = get_trustpilot_reviews(max_pages=TRUSTPILOT_PAGES)
    print(f"Trustpilot: {len(trustpilot_rows)} reviews matching keywords.")

    # Reddit
    print("Fetching Reddit posts...")
    reddit_rows = get_reddit_posts(max_per_keyword=50)
    print(f"Reddit: {len(reddit_rows)} posts matching keywords.")

    # Google Play
    print("Fetching Google Play reviews...")
    play_rows = get_play_store_reviews()
    print(f"Play Store: {len(play_rows)} reviews matching keywords.")

    # Apple App Store
    print("Fetching Apple App Store reviews...")
    appstore_rows = get_app_store_reviews()
    print(f"App Store: {len(appstore_rows)} reviews matching keywords.")

    # Combine and export
    combined = trustpilot_rows + reddit_rows + play_rows + appstore_rows
    export_to_csv(combined, OUTPUT_CSV)

    # Leadership analysis
    stats = leadership_analysis(combined)
    print_leadership_report(stats)


if __name__ == "__main__":
    main()
