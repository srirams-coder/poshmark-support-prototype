# GitHub Pages + Supabase (dynamic prototype)

**GitHub Pages only serves static files** (HTML, CSS, JS). It does **not** run Node, Python, or a database server in the repo.

To get **live data** on a Pages site, the browser must call an **HTTPS API** hosted elsewhere. This repo uses **[Supabase](https://supabase.com/)** (free tier): PostgreSQL + auto-generated REST API that allows CORS from your GitHub Pages origin.

## What Variant E does

- [`flow_prototype/support_article_led_variant_e.html`](../flow_prototype/support_article_led_variant_e.html) loads the same UI as Variant D.
- On startup it runs [`flow_prototype/js/prototype-supabase.js`](../flow_prototype/js/prototype-supabase.js) to optionally `GET` rows from table `prototype_cases`.
- Each row stores `{ id, payload }` where `payload` is the full case object (JSON).
- New cases created in the prototype are `POST`ed to the same table when Supabase is enabled.

## Setup (once)

1. Create a project at [supabase.com](https://supabase.com/).
2. In **SQL Editor**, run the script in [`supabase/migrations/001_prototype_cases.sql`](../supabase/migrations/001_prototype_cases.sql).
3. In **Project Settings → API**, copy:
   - **Project URL**
   - **anon public** key
4. Copy `flow_prototype/supabase-config.example.js` to `flow_prototype/supabase-config.js` (or edit the committed stub) and set:
   - `url`
   - `anonKey`
   - `enabled: true`
5. Commit and push; GitHub Pages will serve `supabase-config.js` with your keys (the anon key is designed to be public; protect data with **RLS**—the migration uses open policies for prototyping only).

## Optional: seed from demo JSON

You can insert seed rows by converting each case object to JSON. Example (single row):

```sql
insert into public.prototype_cases (id, payload) values (
  'PM-2026-001',
  '{"id":"PM-2026-001","subject":"Demo","status":"open","messages":[]}'::jsonb
);
```

Or leave the table empty: the prototype falls back to embedded `CASES_SEED`.

## Verify

1. Open the site on GitHub Pages.
2. Open Variant E; a **green banner** means cases came from Supabase; **gray** means demo-only config.

## Limits

- **Rate limits** and **RLS** apply per Supabase plan.
- This is a **prototype** pattern, not production security review.
