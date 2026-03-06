# Poshmark Customer Support Research Tool

Professional-grade Python tool to analyze Poshmark customer support failures using Trustpilot reviews and Reddit (r/poshmark) discussions.

## Features

- **Trustpilot**: Fetches reviews from [poshmark.com on Trustpilot](https://www.trustpilot.com/review/poshmark.com) using `requests` and `BeautifulSoup`. Parses review data from the page’s `__NEXT_DATA__` JSON (Next.js).
- **Reddit**: Uses `praw` to search r/poshmark for support-related keywords.
- **Keyword filter**: Keeps only items that mention at least one of: `bot`, `canned response`, `unresponsive`, `no phone number`, `funds withheld`, `3% cancellation`.
- **Output**: One row per item with **Date**, **Source** (Trustpilot/Reddit), **Content** (cleaned text), and **Sentiment** (based on matched keywords). Exported to `poshmark_support_analysis_2026.csv`.
- **Leadership analysis**: Post-processing reports the percentage of collected items that mention *automation* (e.g. bot, automated, AI) vs *human support* (e.g. human, live agent, phone support).

## Setup

```bash
cd poshmark_support_analysis
pip install -r requirements.txt
```

### Reddit API (optional)

To include Reddit data:

1. Go to [Reddit Apps](https://www.reddit.com/prefs/apps) and create a “script” app.
2. In `poshmark_research_tool.py`, set:
   - `REDDIT_CLIENT_ID` = your app’s client ID (under the app name).
   - `REDDIT_CLIENT_SECRET` = your app’s secret.
   - Leave `REDDIT_USER_AGENT` as-is or customize.

If these are not set, the script still runs and only collects Trustpilot data.

## Usage

```bash
python poshmark_research_tool.py
```

- Trustpilot: fetches the first 5 review pages (configurable via `TRUSTPILOT_PAGES`).
- Reddit: searches r/poshmark for each keyword (up to 25 posts per keyword).
- Writes `poshmark_support_analysis_2026.csv` in the current directory and prints the leadership analysis summary.

## Output CSV

| Date       | Source     | Content        | Sentiment            |
|-----------|------------|----------------|----------------------|
| 2026-02-08| Trustpilot | Cleaned text...| negative: unresponsive|
| 2026-02-01| Reddit     | Cleaned text...| negative: bot, canned response |

## Leadership Analysis

The script prints a short report, for example:

- Total reviews/posts analyzed
- % mentioning automation-related terms (automation, automated, bot, robot, AI, algorithm)
- % mentioning human-support terms (human, real person, live agent, phone support, speak to someone)

You can also call `leadership_analysis(rows)` on your list of row dicts to get the same percentages programmatically.
# poshmark-support-prototype
