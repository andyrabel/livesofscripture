# Lives of Scripture

## Scope

This README introduces the repository, its local workflow, layout, build
scripts, deployment model, and data sources.

A static, GitHub Pages-hosted reference profiling every person named in the
Bible — patriarchs, judges, kings, prophets, apostles, and everyone else
Scripture names, from Adam to the closing chapters of Revelation. Sibling
site to [Lives of Faith](https://livesoffaith.org) (post-biblical Christian
history) — same design language, different scope: this site covers the
biblical text itself.

Live at **[LivesOfScripture.org](https://livesofscripture.org)**.

## Viewing locally

This is a flat static site with no build step required to view it — serve
the repo root and open it in a browser:

```
python3 -m http.server 8080      # http://localhost:8080
```

## What's here

- **~2,950 people** imported from Scripture, split into two tiers:
  - **Full entries** (~700) — people with an actual narrative: story text,
    an age-appropriate summary, a devotional ("Thought for Today"), a
    hand-drawn or generic role icon, and genealogy links.
  - **Stub entries** (~2,250) — genealogy-only mentions (Genesis 5/10/11,
    1 Chronicles 1–9, and similar) with just a name, references, and
    parent/child edges, so the connections graph stays complete.
- A **genealogy/connections graph**, a **timeline** (era-bucketed for
  disputed Old Testament chronology, dated where scholarly consensus
  allows), a **quiz**, and **NASB/KJV name-spelling toggle**.
- Person pages are **statically pre-rendered** (not just client-rendered)
  so search engines and LLM crawlers that don't execute JavaScript can still
  index full story content.

See [CLAUDE.md](CLAUDE.md) for the full content rules, schema, and design
decisions this project runs on — theological framing, sourcing rules,
image style, disambiguation logic, timeline chronology handling, etc. That
file is the source of truth; read it before making content or schema
changes.

## Site structure

```
/
├── index.html          # home page + search/filter UI
├── people.html          # browse/list page (client + static-fallback grid)
├── person.html           # legacy redirect shim → people/[id].html
├── people/[id].html      # statically pre-rendered per-person pages
├── connections.html      # genealogy/connections graph
├── timeline.html         # chronological view
├── quiz.html
├── about.html
├── css/style.css
├── js/app.js              # client-side rendering, search, filters
├── data/
│   ├── people.json         # lightweight index, loaded everywhere
│   ├── people/[id].json     # full per-person entry, fetched on demand
│   ├── connections.json     # genealogy + narrative relationship edges
│   ├── quiz.json
│   ├── timeline-events.json
│   └── whats-new.json       # site changelog feed
├── images/portraits/         # hand-drawn + generic role icon SVG/PNG
└── _build/                   # data import and static-site generation scripts
```

## Build scripts (`_build/`)

- `import_bible_data.py` — bulk-imports genealogy data from
  [BradyStephenson/bible-data](https://github.com/bradystephenson/bible-data)
  (CC BY 4.0) into `data/people.json` + `data/people/*.json`.
- `generate_static_site.py` — the main build: reads `data/people.json` +
  `data/people/*.json` + `data/connections.json` and generates static
  `people/[id].html` pages, `sitemap.xml`, and the static-fallback person
  grid embedded in `people.html`. **Run this locally any time person or
  connections data changes, and commit the generated output with the data.**
- `generate_disambiguation.py` — computes the `disambiguation` field
  (e.g. "son of Zebedee", "1 Chr 3:21") for people who share a name.
- `infer_stub_eras.py` — propagates `era`/`region`/genealogy onto stub
  entries by walking the graph out from full-tier people, for timeline
  placement.
- `backfill_gender.py`, `backfill_first_reference.py`,
  `backfill_genealogy.py`, `sync_promoted_tiers.py` — one-time/repeatable
  backfill and maintenance passes; safe to re-run.
- `fb/` — private, gitignored Facebook/Instagram daily-posting pipeline
  (not part of the static site build).

Regeneration order when data changes: `infer_stub_eras.py` and
`generate_disambiguation.py` before `generate_static_site.py`.

## Deployment

GitHub Pages serves `main` directly. Generated `people/`, `sitemap.xml`, and
`people.html` files are built and committed locally. On every push to `main`,
`.github/workflows/build.yml` regenerates them only to verify that the committed
copies are current; it fails on any diff and never commits or pushes.

## Data sources

- **Biblical text** (NASB primary translation) — all narrative content.
- **Easton's Bible Dictionary, Smith's Bible Dictionary, ISBE** (public
  domain) — historical/cultural background only.
- **[BradyStephenson/bible-data](https://github.com/bradystephenson/bible-data)**
  (CC BY 4.0) — genealogy/relationship data. Attribution required (see
  About page).

No verse text is stored or quoted anywhere on the site, for copyright
reasons — references (e.g. "Genesis 12:1–3") only.

## License

Site code: no license file yet. Genealogy data derived from
BradyStephenson/bible-data is CC BY 4.0 with attribution on the About page.
