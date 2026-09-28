# Project Notes — yh-v5.github.io

> **Status (2026-09-28):** Site is live with a custom neo-Swiss / blueprint theme (see "Design" below) layered on al-folio. Four works, each with its own exhibit page: HyperSPACE (ISLPED '26), DiP-MEMHD (IEEE IoT-J, Early Access), MEMHD (DATE '25), and HDC normalization (AISP 2024). Navigation is Index / Works / News / Contact. CV, projects and blog are still hidden behind `nav: false` and still use the stock al-folio layout.

> **For the next agent:** This file is excluded from the published site (see `_config.yml` exclude list). Skim this end-to-end before touching anything. Then re-read [`AGENTS.md`](AGENTS.md) for al-folio-specific build conventions.

---

## Owner & Environment

- **Owner:** Yeong Hwan Oh (오영환), Combined M.S. & Ph.D. student, IRIS Lab, Sungkyunkwan University. Advisor: Prof. Jong Hwan Ko.
- **Email:** `yh991111@g.skku.edu` (academic) / `yh991111@gmail.com` (personal, GitHub)
- **GitHub:** `yh-v5`
- **ORCID:** `0009-0001-6001-5728`
- **Research:** Sparse representations for energy-efficient on-device AI — HDC on SRAM-CIM, dynamic sparse training, machine unlearning at ultra-high sparsity.

The owner plans to **continue editing this site from a remote Linux dev container** (SSH alias + Docker + code-server already set up). The bootstrap was done from Windows 11 + WSL2 Ubuntu-22.04. Either path works; the GitHub repo is the single source of truth.

### To resume on the remote dev container

This section is the _only thing_ you need to read end-to-end before the next agent (or you) starts on a fresh remote machine. Everything else in PROJECT_NOTES.md is reference.

#### 0. Server choice

Either of the user's remote servers works. Jekyll uses **0 GPU**, ~200 MB RAM, and ~15 s of single-thread CPU per build. It does not contend for the same resources as ML workloads from other tenants. The only practical risk on a "noisy" server is interactive lag in code-server — not data loss (git is the safety net) and not build correctness (deterministic, depends only on the source tree). If running `jekyll serve --watch` for an extended session, wrap it in `tmux` or `screen` so an SSH disconnect doesn't kill it.

**Never push from two environments simultaneously to the same branch.** Pick one as the active dev environment and use the other only after a `git pull`.

#### 1. Get the code

```bash
cd ~/projects   # or wherever you prefer inside the container
git clone https://github.com/yh-v5/yh-v5.github.io.git
cd yh-v5.github.io
```

If you bind-mount a host directory into the container, verify the cloned dir is owned by your container user (`ls -la`). UID/GID mismatches give "permission denied" on later edits; fix with `chown -R $(id -u):$(id -g) .` or set the container's `PUID`/`PGID` env vars to match the host UID.

#### 2. Identity + push auth (one-time per environment)

```bash
git config --global user.name "Yeong Hwan Oh"
git config --global user.email "yh991111@gmail.com"
git config --global init.defaultBranch main
git config --global core.autocrlf input    # harmless on Linux, important if container ever sees Windows-line-ending files
git config --global pull.rebase false

# Choose ONE of the two auth methods below.
```

**Auth option A — HTTPS + Personal Access Token (simplest, recommended for code-server containers).**

Generate a `repo`-scope classic PAT at https://github.com/settings/tokens/new (90-day expiry is reasonable). Then in the container:

```bash
git config --global credential.helper store
git push   # or git pull — first network op prompts:
           #   Username: yh-v5
           #   Password: <paste the PAT — NOT your GitHub password>
# Subsequent pushes/pulls reuse the stored credentials.
```

The token lives in plaintext at `~/.git-credentials`. Make sure that path is on a persistent volume (it usually is — code-server typically persists `$HOME`). When the PAT expires, just regenerate and re-prompt: `rm ~/.git-credentials` then push again.

**Auth option B — SSH key.** No token expiry, fewer plaintext secrets, but requires you to keep `~/.ssh/id_ed25519` on a persistent volume.

```bash
ssh-keygen -t ed25519 -C "yh991111@gmail.com" -f ~/.ssh/id_ed25519 -N ''
cat ~/.ssh/id_ed25519.pub      # copy the single line of output
# → paste at https://github.com/settings/ssh/new

cd yh-v5.github.io
git remote set-url origin git@github.com:yh-v5/yh-v5.github.io.git
git pull && git push
```

#### 3. Build environment

Two paths. Path A is what al-folio officially supports and "Just Works"; Path B is what to do if you don't want a nested Docker.

**Path A — al-folio's own Docker (recommended on a host that already runs Docker).**

```bash
docker compose up         # standard, ~400 MB image
# or:
docker compose -f docker-compose-slim.yml up    # < 100 MB, identical functionality

# Site at http://localhost:8080 (with livereload at :35729).
# Initial pull is the only slow part; subsequent ups are instant.
```

This image bundles a known-good Ruby + Node + ImageMagick + Poppler combination, so **none of the Gemfile pins this repo carries (activesupport ~> 7.1, jekyll-sass-converter ~> 3.0, sass-embedded < 1.79) actually constrain anything inside the container**. They only mattered on the WSL Ruby-3.0.2 environment used for the bootstrap. You can ignore them.

**Path B — install into the existing code-server container directly.**

System packages (sudo, one-time):

```bash
sudo apt update && sudo apt install -y \
  ruby-dev bundler nodejs npm \
  poppler-utils imagemagick \
  build-essential
```

Note the `nodejs` package — without a JavaScript runtime, `jekyll-terser` raises `Could not find a JavaScript runtime` exception per JS file during build. Build still completes (assets ship un-minified) but the warning spam is annoying. The package name varies (`nodejs` on Debian/Ubuntu, may need `nodejs-legacy` on older bases).

Per-project gems (no sudo):

```bash
cd yh-v5.github.io
bundle config set --local path vendor/bundle
bundle install
bundle exec jekyll serve --host 0.0.0.0 --port 4000
# → http://localhost:4000 — verify the page renders
```

The `--host 0.0.0.0` is necessary if you want the site reachable from outside the container (i.e., your browser via code-server's port forwarding, or via an SSH tunnel). Inside-container-only access can use the default `127.0.0.1`.

If your container's Ruby is **3.1 or higher**, you can safely loosen the `sass-embedded` cap and revert the `_themes.scss` patch:

```bash
# In Gemfile, change `gem 'sass-embedded', '< 1.79'` to:
gem 'sass-embedded', '>= 1.79'
# Then revert the rgba(...) lines in _sass/_themes.scss back to color.channel(...).
bundle update sass-embedded
```

Not required — the patched version compiles identically. But it brings the repo back into sync with upstream al-folio for future merges.

#### 4. Local preview from outside the container

If the container exposes port 4000 to its host and the host is reachable, just hit `http://<host>:4000`. Otherwise, two options:

```bash
# From your laptop, SSH tunnel:
ssh -L 4000:localhost:4000 <server-alias>
# Then http://localhost:4000 in your browser.

# Or, if code-server itself is exposed: code-server's "Forward a Port" UI does it for you.
```

#### 5. The everyday loop

```bash
# inside the container, in yh-v5.github.io/
git pull                                  # always before starting work
# ...edit files...
bundle exec jekyll build                  # quick check (~15 s); or use serve --watch for live
git add -A && git commit -m "..."         # commit early, commit often
git push                                  # triggers .github/workflows/deploy.yml — site refreshes in ~4 min
```

Watch the **Deploy site** workflow at https://github.com/yh-v5/yh-v5.github.io/actions after each push. The other workflows (Render a CV, Prettier, the built-in pages-build-deployment) can fail without affecting your live site — see the "Known build issues" section.

---

## What was changed during initial setup (2026-05-03)

| File                                     | What changed                                                                                                                                                                                                                                                                                                                                                                                        |
| ---------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `_config.yml`                            | Identity (`first_name: Yeong Hwan`, `last_name: Oh`), `url: https://yh-v5.github.io`, `baseurl: ""`, `serve_og_meta: true`, `serve_schema_org: true`, `og_image: /assets/img/prof_pic.jpg`, `scholar.last_name/first_name`, disabled `books`/`teachings` collections, cleared `external_sources`, expanded `exclude:` list to keep al-folio docs out of `_site/`                                    |
| `Gemfile`                                | Pinned `gem 'activesupport', '~> 7.1'` — without this, bundler resolved to `activesupport 3.1.12` (2011), which raises `circular argument reference - now (SyntaxError)` on Ruby 3.x via `_plugins/google-scholar-citations.rb`                                                                                                                                                                     |
| `_data/socials.yml`                      | Replaced demo with real email, ORCID, GitHub. `scholar_userid` left commented — fill in once Scholar profile exists                                                                                                                                                                                                                                                                                 |
| `_data/coauthors.yml`                    | Replaced Einstein-era co-authors with real ones (Ko, Kang, Hwang, Kim, Jeon)                                                                                                                                                                                                                                                                                                                        |
| `_data/cv.yml`                           | Stub with real name + IRIS Lab; education skeleton. The `/cv/` page is hidden — fill out and flip `nav: true` when ready                                                                                                                                                                                                                                                                            |
| `_pages/about.md`                        | Rewritten bio (two research threads + collaboration invite). `selected_papers: true`, `social: true`, `news/announcements/latest_posts` all disabled until content exists                                                                                                                                                                                                                           |
| `_pages/blog.md`, `cv.md`, `projects.md` | `nav: false` — hidden until content exists                                                                                                                                                                                                                                                                                                                                                          |
| Deleted `_pages/`                        | `about_einstein.md`, `dropdown.md`, `profiles.md`, `books.md`, `teaching.md`, `repositories.md`, `news.md`                                                                                                                                                                                                                                                                                          |
| `_bibliography/papers.bib`               | Three entries (HyperSPACE → DiP-MEMHD → MEMHD ordered by visibility intent within years). All authors marked with `*` (co-first) and `†` (co-corresponding) on the appropriate last names; bib.liquid renders the markers as superscripts. `annotation` field documents what each marker means; the ⓘ popover surfaces it in the rendered list. See "Publications" section below for accuracy notes |
| `_layouts/bib.liquid`                    | Patched so the abbr-badge column is rendered whenever `entry.abbr` is set, independent of `enable_publication_thumbnails`. The preview img inside that column still respects the flag                                                                                                                                                                                                               |
| `_sass/_variables.scss`                  | Added `$slate-color: #334155`, `$slate-color-hover: #1e293b`, `$sky-color: #7dd3fc`, `$sky-color-hover: #bae6fd`. Changed `$code-bg-color-light` to slate tint                                                                                                                                                                                                                                      |
| `_sass/_themes.scss`                     | Light theme `--global-theme-color/--global-hover-color` → slate. Dark theme → sky-blue. al-folio's default purple is preserved as a variable but not used                                                                                                                                                                                                                                           |
| Deleted demo content                     | `_projects/{1..9}_project.md`, `_news/announcement_*`, all `_posts/*`, `_books/`, `_teachings/`, `assets/jupyter/blog.ipynb`, `assets/img/{1..12}.jpg`, `assets/img/rhino.png`, `assets/img/template_error.png`, `assets/img/prof_pic_color.png`, `assets/img/book_covers/`, `assets/img/publication_preview/`, `assets/pdf/example_pdf.pdf`                                                        |
| New `assets/img/prof_pic.jpg`            | Replaced on 2026-09-28 with a new portrait: top 1333×1333 square of the 1333×2000 original, resized to 800×800 (Pillow); `prof_pic.webp` written from the same crop. The site shows it in grayscale via CSS                                                                                                                                                                                         |

---

## Publications

The bib file lives at `_bibliography/papers.bib`. **Four entries**, each marked `selected: true`. Status as of 2026-09-28:

1. **HyperSPACE (ISLPED '26) — published.** Accepted as a poster on 2026-05-19, presented in Evanston, IL (Aug 5–7, 2026). ACM DOI `10.1145/3816440.3818512`. Authors confirmed from the ACM DL notice: _Yeong Hwan Oh, Do Yeong Kang, Juhong Park, Chanwook Hwang, Kang Eun Jeon, Jong Hwan Ko_.
2. **DiP-MEMHD / Multi-Centroid HDC for Compact IMC (IEEE IoT-J) — Early Access since 2026-09-02.** Key `kang2026dipmemhd`. DOI `10.1109/JIOT.2026.3730047`. Volume/issue/pages not assigned yet — add them and drop `note = {Early Access}` once the final issue is out (also update `status` in `_data/works.yml`). **Co-first authorship** (D. Y. Kang and Y. H. Oh) noted via `annotation`.
3. **MEMHD (DATE 2025) — published.** DOI `10.23919/DATE64628.2025.10993253`, pp. 1–7, arXiv `2502.07834`, Lyon, France.
4. **HDC normalization (AISP 2024) — published.** 「효율적 이미지 분류 작업을 위한 Hyperdimensional Computing 정규화 기법」, 인공지능신호처리학술대회 (AISP), October 2024. Authors Yeong Hwan Oh, Jong Hwan Ko. The Korean title is kept as the main title on purpose; the English title is in the custom `title_en` field. No DOI; the PDF is not posted (check the proceedings' author-posting policy before adding `pdf:`).

Still open: attach `pdf:` (file under `assets/pdf/`) and `code:` URLs if desired, and replace the schematic exhibit figures with the papers' real overview figures.

## Design (neo-Swiss / blueprint theme)

International Typographic Style with a technical-drawing accent: a 12-column grid, heavy grotesk headlines, small mono captions, one accent blue. **Dark is the default** (deep navy sheet, pale ink); **Light** is the same palette flipped (pale blue-white sheet, navy ink). Both token sets are at the top of `assets/swiss/swiss.css` (`:root` and `:root[data-theme="light"]`). Works are shown like exhibits: the index stays a plain, scannable list, and each paper gets an exhibit page (wall caption, figure plate, spec sheet, abstract, BibTeX).

| Piece                                                   | File                                                                                            |
| ------------------------------------------------------- | ----------------------------------------------------------------------------------------------- |
| Base layout (head, fonts, header, footer)               | `_layouts/swiss.liquid`, `_includes/swiss/{header,footer}.liquid`                               |
| Home                                                    | `_layouts/home.liquid` + front matter in `_pages/about.md` (caption rows, timeline, kicker)     |
| Works index                                             | `_pages/publications.md` (still at `/publications/`), row template `_layouts/work_row.liquid`   |
| Exhibit pages                                           | `_layouts/exhibit.html` — generated by jekyll-scholar's details pages at `/works/<bibtex key>/` |
| Exhibit data (number, statement, medium, specs, figure) | `_data/works.yml` (list order = catalogue order and prev/next)                                  |
| Figures                                                 | `_includes/works/fig-*.svg`, generated by `bin/gen_work_figures.py`                             |
| Styles / behaviour                                      | `assets/swiss/swiss.css`, `assets/swiss/swiss.js`                                               |
| News rows                                               | `_includes/swiss/news.liquid`                                                                   |

Fonts: Archivo (wide, `wdth` 125) for display, Inter Tight for headlines, Inter for body, Space Mono for labels (all Google Fonts), Pretendard for Hangul (jsDelivr). The Dark / Light buttons in the header switch themes; a "light" choice is kept in `localStorage` (`yh-theme`) and applied before first paint by an inline script in `_layouts/swiss.liquid`. There is no longer a grid overlay toggle.

**To add a work:** add the BibTeX entry (with `abbr`, `abstract`, `selected = {true}`), add a matching `- key:` block to `_data/works.yml`, and optionally a figure SVG in `_includes/works/` (use the `bp-*` classes so it follows the theme; the `.plate` frame is added by the layout). The exhibit page appears automatically.

Gotchas:

- `_data/works.yml` uses `num`, not `no` — YAML reads a bare `no` key as `false`.
- `_layouts/exhibit.html` must stay `.html`: jekyll-scholar only recognises details layouts with that extension. It is listed in `.prettierignore` because Prettier would parse its Liquid as HTML.
- `assets/swiss/` sits outside `assets/css/` on purpose, so the deploy workflow's PurgeCSS step (which only scans `assets/css/*.css`) never strips classes toggled from JS.
- Don't look up other exhibit pages through `site.pages` from the exhibit layout: jekyll-scholar renders details pages during generation, before all of them exist. Prev/next links are built from `_data/works.yml` instead.
- Screenshots in a sandbox without font CDN access will show fallback fonts; that is not a site bug.

## Stories

Short fiction in Korean, written by the owner and polished with an LLM. On the site the credit is only ever "polished with an LLM" (no model or vendor name). It is only linked from the header (after Contact); nothing about it appears on the home page. Titles and descriptions are in **English**; the story text stays Korean. The list shows each story as number, title and one key sentence quoted verbatim from the story in Korean (`line`; plus chapter count, reading time, year). The story page shows the English title and the one-line English `description`.

| Piece                       | File                                                                         |
| --------------------------- | ---------------------------------------------------------------------------- |
| Story files (one per story) | `_stories/<slug>.md`: collection `stories`, served at `/stories/<slug>/`     |
| List page                   | `_pages/stories.md` (`/stories/`, `nav: false`) → `_layouts/stories.liquid`  |
| Reader page                 | `_layouts/story.liquid` (default layout for the collection in `_config.yml`) |
| Importer                    | `bin/import_story.py`                                                        |

**To add a story:** export it as HTML (one `h1` title, `h2` chapters, `p` / `hr` / `blockquote` / `em`), or give it as Markdown / plain text (`.md` / `.txt`: `# 제목`, `## 장`, blank lines between paragraphs, `>` quotes, `---` rules; every line break inside a paragraph is kept), then

```bash
python3 bin/import_story.py EXPORT.html --slug <latin-slug> --year 2026 --num 03 \
  --title "English Title" --description "One line in English." \
  --line "본문에서 그대로 옮긴 핵심 문장 하나."
```

This writes `_stories/<slug>.md` with the front matter (`title`, `title_ko` (the export's h1, not shown), `num`, `year`, `date`, `description`). An all-italic first paragraph (subtitle) is dropped. Chapter titles are rewritten without em dashes or middle dots (`1 · 제목` → `1. 제목`, `제목 — 부제` → `제목: 부제`, `제목 — 〈연재명〉 N 번째` → a `<small>` second line), and any `—` / `·` left in the prose are printed so they can be fixed by hand. The list is sorted newest first by `date` (`YEAR-01-01`; set a real date to order two stories from the same year). Chapter count, reading time and the table of contents are computed from the rendered chapters (`## … {#ch-N}`), so nothing else needs editing. A story written directly in Markdown works too, as long as it follows the same conventions.

Current stories: 01 "Your Resonance" (너의 울림, 2021), 02 "Dawn" (새벽, 2022, no chapters), 03 "NLP" (2024, 8 parts "1편"…"8편", first posted as Instagram captions; the copy-tool intro and "[NLP - n/8]" labels were dropped), 04 "The Last Digit" (끝자리, 2025, no chapters), 05 "Common Chip" (보통 칩, 2025, dated 2025-01-02 to sort after 끝자리), 06 "Be Right Back" (다녀올게, 2026). Numbers follow the year the story was written, so a new story may push later ones up by one (URLs use the slug, so nothing breaks). A story without `##` chapters just has no contents list.

Gotchas:

- No italics in stories: the importer drops emphasis, and `.story-body em` is set upright in case a hand-written file has some.
- kramdown here has `hard_wrap: false`, so line breaks inside a paragraph are written as `<br>`. Scene-break paragraphs are a single `◇` with `{: .sep}`; `<hr>` is drawn as `◇` too.
- `_stories/` is in `.prettierignore`: Prettier would rewrite whole-line `*italics*` to `_italics_`, and the importer's output is the source of truth.
- The TOC is cut out of the rendered HTML (`split: '<h2 id="'` … `split: '">'`), so inline HTML in a chapter title must not carry attributes (plain `<small>` is fine).

## House style: no em dashes or middle dots

The owner does not want `—` or `·` visible anywhere on the site (pages, figures, stories). Use `/` for label separators, commas for lists, colons or parentheses otherwise, `…` for cut-off speech. En dashes in number ranges (`2024–2025`, `01–04`) are fine. After a build, check with

```bash
python3 bin/check_glyphs.py _site
```

Figure labels come from `bin/gen_work_figures.py`; edit there and regenerate, not the SVGs.

## News

News items live in `_news/` (one file per item, `inline: true`, `date:` in front matter). `announcements.enabled: true` in `_pages/about.md` shows the latest 5 on the home page; the full list is at `/news/` (`_pages/news.md`, `nav: false`).

---

## Hidden pages — what to fill in to publish each

| Page         | File                                             | What's needed before flipping `nav: true`                                                                                                                                                                                       |
| ------------ | ------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `/cv/`       | `_pages/cv.md` + `_data/cv.yml`                  | Fill education, experience, awards, publications, skills, service in `_data/cv.yml` (RenderCV schema). Optionally generate a PDF via the GitHub Action in `.github/workflows/render-cv.yml` and add `cv_pdf:` to `_pages/cv.md` |
| `/projects/` | `_pages/projects.md` + new files in `_projects/` | Add at least one `_projects/<slug>.md` with frontmatter (`title`, `description`, `img`, `category`, `importance`). Then `display_categories` in `_pages/projects.md` should match those `category` values                       |
| `/blog/`     | `_pages/blog.md` + new files in `_posts/`        | Add `_posts/YYYY-MM-DD-slug.md` posts with `layout: post`. For short posts, set `related_posts: false` to avoid LSI errors                                                                                                      |

Also disabled but kept available: `enable_navbar_social: false` — flip true to show socials in navbar. `announcements.enabled` and `latest_posts.enabled` in `_pages/about.md` are off; flip on after adding `_news/*` and `_posts/*` content.

---

## Known build issues & non-issues

**Real issues (fixed):**

- `activesupport 3.1.12` SyntaxError → fixed via Gemfile pin (see above)
- al-folio's docs being included in `_site/` → fixed via `_config.yml` exclude list
- **SCSS not compiling at all** — al-folio's `_sass/*.scss` use the `@use` rule (Dart Sass), but the default `jekyll-sass-converter 2.x` uses sassc/libsass which silently emits the SCSS as-is into `_site/assets/css/main.css`. Result: a 452-byte file, no styles applied, the page looked like the screenshot was missing all theming (numbered `<ol>` markers visible, empty white squares where styled abbr badges should be, etc.). Fixed by pinning `jekyll-sass-converter ~> 3.0` in Gemfile (uses sass-embedded). The transitive constraint then required `sass-embedded < 1.79` because 1.79+ needs Ruby ≥ 3.1 and this WSL has 3.0.2, which forced patching `_sass/_themes.scss` to drop the upstream `color.channel(...)` calls (added in Sass 1.79) in favor of plain `rgba()` for the back-to-top button. The al-folio Docker image is on a newer Ruby and would not need these caps; on the remote dev container, you can safely raise the `sass-embedded` cap and revert the `_themes.scss` patch if Ruby ≥ 3.1 is available.
- **Empty placeholder boxes next to publication titles** — `_layouts/bib.liquid` originally rendered the entire left column (containing both the abbr badge AND any preview thumbnail) only when `enable_publication_thumbnails: true`. With thumbnails on but no `preview:` field set, the column was empty space; with thumbnails off, the venue badges (DATE/ISLPED/IoT-J) disappeared too. Patched bib.liquid to gate the abbr badge separately from the preview img — abbr always renders if `entry.abbr` is set; preview only when both flags are true.

**Cosmetic / non-blocking:**

- `Terser Exception: Could not find a JavaScript runtime` during local build. Means JS files aren't minified locally because Node.js isn't installed on this WSL box. The site still works; assets just ship slightly larger. al-folio's Docker build (and the `Deploy site` GitHub Action) use a Ruby image with Node, so the deployed site IS minified. Install Node in the next dev environment if local minification matters.
- al-folio template ships failing **Render a CV**, **Prettier**, and **pages-build-deployment** (built-in) GitHub workflows on a fresh repo. Render a CV will start passing once `_data/cv.yml` is fully populated (or just disable the workflow until then). Prettier failures are formatting-only — running `npx prettier . --write` once fixes them. The built-in `pages-build-deployment` workflow conflicts with al-folio's `Deploy site` and should be ignored entirely — the al-folio workflow pushes to `gh-pages` and that's what serves the site.

---

## Deployment

The `Deploy site` workflow (`.github/workflows/deploy.yml`) runs on every push to `main` and pushes the built site to the `gh-pages` branch. **GitHub Pages source must be set to "Deploy from a branch → gh-pages → /(root)"** in _Settings → Pages_. Setting it to "GitHub Actions" will result in a blank page (al-folio uses jekyll-scholar and other gems not on the GitHub Pages whitelist).

After any push to `main`, expect ~4 minutes until the site refreshes at https://yh-v5.github.io.

---

## Open follow-ups for the owner / next agent

1. Fill `_data/cv.yml` end-to-end and flip `_pages/cv.md` → `nav: true`.
2. Add real `_projects/` entries (link MEMHD code repo if public, ditto HyperSPACE simulator).
3. ~~Update **HyperSPACE** bib entry with the full author list once accepted.~~ Done (2026-09-28).
4. Add IoT-J volume/issue/pages once assigned (and remove the `Early Access` note). Attach `pdf:` (place file under `assets/pdf/`) and `code:` URLs to the bib entries; preview thumbnails go in `assets/img/publication_preview/` and are referenced via the `preview:` field.
5. Create a Google Scholar profile (if desired) and fill `scholar_userid` in `_data/socials.yml`.
6. Decide whether to keep the slate/sky theme (`_sass/_themes.scss`) or pick something else. Other variables are in `_sass/_variables.scss`.
7. Add a custom OG image distinct from the profile photo (1200×630 PNG) for richer social previews. Drop in `assets/img/og_image.png` and update `og_image:` in `_config.yml`.
8. Optional: install Node on the dev environment so `npx prettier . --write` and Terser minification both run cleanly locally.
9. Optional: enable Giscus comments — fill `giscus.repo` and `giscus.category_id` in `_config.yml` per giscus.app instructions.
