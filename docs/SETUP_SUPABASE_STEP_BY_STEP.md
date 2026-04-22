# Supabase setup — step by step (this repo)

Use this to connect **Variant E** to a real Supabase project. The table name must be **`prototype_cases`** (see `flow_prototype/js/prototype-supabase.js`).

---

## Step 1 — Create a Supabase account and project

1. Open [https://supabase.com](https://supabase.com) and sign up or log in (GitHub sign-in is fine).
2. Click **New project**.
3. Choose your **organization** (default is ok).
4. Set a **name** (e.g. `poshmark-prototype`), a **strong database password** (save it in a password manager; you need it for direct DB access, not for the HTML prototype), and a **region** close to you.
5. Click **Create new project** and wait until the dashboard shows the project as **ready** (can take 1–2 minutes).

---

## Step 2 — Create the `prototype_cases` table

1. In the left sidebar, click **SQL Editor**.
2. Click **New query** (or use the empty editor).
3. Open this file in your repo: `supabase/migrations/001_prototype_cases.sql`.
4. **Copy the entire file** and paste it into the Supabase SQL editor.
5. Click **Run** (or press the shortcut shown in the UI).

You should see **Success. No rows returned** (or similar). That creates:

- Table `public.prototype_cases` with columns `id` (text, primary key), `payload` (jsonb), `created_at`.
- RLS enabled with open policies for **prototyping** (anyone with your anon key can read/write this table—fine for a demo, not for production secrets).

6. Optional check: **Table Editor** in the left sidebar → you should see **`prototype_cases`**.

---

## Step 3 — Get the Project URL and anon key

1. Click the **gear icon** (⚙️) for **Project Settings** (or **Settings** in the sidebar).
2. Open **API** (under *Project Settings*).
3. Find:
   - **Project URL** — looks like `https://xxxxxxxxxxxx.supabase.co`
   - **Project API keys** — copy the **`anon` `public`** key (long string starting with `eyJ...`).

**Do not** copy the `service_role` key into the website. The prototype only uses the **anon** key in `supabase-config.js`.

---

## Step 4 — Configure the prototype on your machine

1. In your repo, open: `flow_prototype/supabase-config.js`.
2. Set:
   - `url` to your **Project URL** (string, in quotes).
   - `anonKey` to the **anon public** key (string, in quotes).
   - `enabled` to **`true`**.
3. Save the file.

Example (use **your** real values, not this sample):

```javascript
window.PROTOTYPE_SUPABASE = {
  url: 'https://abcdefghijklmnop.supabase.co',
  anonKey: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...',
  enabled: true
};
```

---

## Step 5 — Test locally

1. From the **repo root** folder, start a small static server so paths resolve (exact command may vary):

   ```bash
   npx --yes serve .
   ```

2. In the browser, open:

   - `http://localhost:3000/flow_prototype/support_article_led_variant_e.html`  
   (or whatever port `serve` prints; adjust the path if your tool uses another port)

3. At the top of the phone frame you should see a **status banner**:
   - If Supabase is connected and the table is **empty**: gray-ish message that you’re on demo data / empty.
   - If the **GET** request works and there are **rows** in `prototype_cases`: a **green-style** message that cases loaded from Supabase.
4. Open the browser **Developer tools** → **Network** tab, reload: you should see a request to `.../rest/v1/prototype_cases` with status **200** when config is correct.

5. In the app, go through **Support** and create a case if the flow allows it. Then in Supabase **Table Editor** → `prototype_cases` → you should see a **new row** (if that flow calls `upsert`—Variant E does when `enabled` is true).

---

## Step 6 — Publish to GitHub Pages (optional)

1. **Commit and push** `flow_prototype/supabase-config.js` (with `enabled: true` and your keys) **or** use a branch / environment where you’re comfortable having the anon key in the repo (it’s a public key by design; RLS is what must protect data in production).
2. After the site deploys, open:

   `https://<your-username>.github.io/<repo-name>/flow_prototype/support_article_led_variant_e.html`

3. If the page doesn’t load JS from the right path, confirm `support_article_led_variant_e.html` still loads `supabase-config.js` and `js/prototype-supabase.js` with **relative** URLs (same folder layout as in the repo on Pages).

---

## Step 7 — (Optional) Insert a test row in SQL

In **SQL Editor**, you can run:

```sql
insert into public.prototype_cases (id, payload) values (
  'PM-TEST-1',
  '{
    "id": "PM-TEST-1",
    "subject": "Hello from Supabase",
    "category": "Test",
    "status": "open",
    "lastActivityMs": 0,
    "openDate": "Mar 1, 2026",
    "lastUpdated": "Just now",
    "messages": [
      { "kind": "event", "body": "Case created", "time": "10:00 AM" }
    ]
  }'::jsonb
);
```

Reload Variant E. If the GET succeeds, the case list can show this case (the UI may expect more fields for full styling; for a minimal test, extend the JSON to match a real case from the embedded demo in the HTML if needed).

---

## Troubleshooting

| Issue | What to check |
|--------|----------------|
| Banner still says “demo” only | `enabled` is not `true`, or `url` / `anonKey` empty, or a typo. |
| Network shows **401** / **403** | Wrong anon key; or RLS blocking—re-run the migration SQL, or check **Authentication → Policies** for `prototype_cases`. |
| Network shows **404** on `rest/v1/...` | Wrong Project URL. |
| **CORS** error | Rare with Supabase + `anon`; confirm you're using the `https://xxx.supabase.co` URL. |
| Table missing | Re-run `001_prototype_cases.sql` in SQL Editor. |

---

## After you’re done

For production, replace open RLS policies with rules tied to `auth.users` (or move database access to a Vercel API with a server-side secret). This setup is for **prototyping** on GitHub Pages.
