# Deploy to GitHub Pages

Follow these steps to publish the prototype so your team can open it via a link.

## 1. Create a GitHub repository

1. On [GitHub](https://github.com), click **New repository**.
2. Name it (e.g. `poshmark-support-prototype`).
3. Do **not** add a README, .gitignore, or license (we already have these).
4. Create the repo.

## 2. Initialize git and push (first time)

From the project root (`poshmark_support_analysis`), run:

```bash
git init
git add .gitignore index.html DEPLOY.md flow_prototype/
# Optional: add the rest of the project
git add CASE_CREATION_REDESIGN.md poshmark_research_tool.py requirements.txt
git add poshmark_support_analysis_2026.csv
git status   # confirm only intended files are staged
git commit -m "Add support flow prototypes and GitHub Pages landing"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
git push -u origin main
```

Replace `YOUR_USERNAME` and `YOUR_REPO_NAME` with your GitHub username and repo name.

## 3. Turn on GitHub Pages

1. In the repo on GitHub, go to **Settings** → **Pages** (left sidebar).
2. Under **Build and deployment**:
   - **Source**: Deploy from a branch
   - **Branch**: `main` (or `master`)
   - **Folder**: `/ (root)`
3. Click **Save**.

After a minute or two, the site will be available at:

**https://YOUR_USERNAME.github.io/YOUR_REPO_NAME/**

Example: `https://acme.github.io/poshmark-support-prototype/`

Share that link with your team. The landing page links to:
- **Article-led baseline** (`support_article_led_mobile.html`) and **Variant B** (`support_article_led_variant_b.html` — full copy for experiments; each has optional tour)
- **Form-led flow**
- Other prototypes (My Purchases, support flow, track cases, case detail)

## 4. Updates

After changing the prototypes, commit and push:

```bash
git add flow_prototype/
git commit -m "Update prototype"
git push
```

GitHub Pages will update automatically (may take 1–2 minutes).
