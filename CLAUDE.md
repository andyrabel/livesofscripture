# LivesOfScripture.org — Project Instructions

## Project Overview

Build a static GitHub Pages website profiling every person named in the Bible —
patriarchs, judges, kings, prophets, apostles, and everyone else Scripture
names, from Adam to the closing chapters of Revelation. This is a **sibling
site to Lives of Faith** (livesoffaith.org, historical Christians from church
history onward) — same spirit and design language, different scope: this site
covers the biblical text itself, not post-biblical Christian history.

The site serves worship leaders, Bible teachers, and families who want a
reliable reference for who's who in Scripture, how everyone connects by
genealogy and relationship, and what each person's story reveals about God's
redemptive plan.

Domain: **LivesOfScripture.org** (name chosen 2026-07-30; domain purchased by
Andrew 2026-07-30).

---

## Absolute Content Rules

These carry over from Lives of Faith with adaptations for the fact that every
subject here is a biblical figure, not a post-biblical Christian.

### Theological Requirements
- Every full-entry story must point to **Christ** — but the framing differs by
  testament. Old Testament figures are not evangelistically "converted"; per
  Romans 4 and Hebrews 11, they are justified by faith in God's promise,
  looking forward to the Messiah not yet come. New Testament figures relate to
  Christ's accomplished work directly. Both are salvation by grace through
  faith, not by works — but say so in the terms Scripture itself uses for that
  person, not by anachronistically describing an Abraham or a Ruth as
  "converting" the way a Reformation figure does.
- No hero-worship or hagiography — and unlike the historical-figures site,
  this cuts a specific direction here: **Scripture itself does not sanitize
  its own heroes.** David's adultery and murder, Solomon's idolatry, Noah's
  drunkenness, Abraham's deception of Pharaoh, Peter's denial, Jonah's
  rebellion — these are not scandals to flag or footnote, they are the text.
  Tell the story the way Scripture tells it. Omitting a person's documented
  sin to make them look better is a worse error here than including it.
- Tone is reverent, instructive, and worshipful — never sensational, even when
  the material (Judges, for instance) is dark.

### Factual Accuracy
- Primary source is **the biblical text itself** (see Bible Version Handling
  below), not Wikipedia. Wikipedia and standard public-domain Bible
  dictionaries (Easton's Bible Dictionary, Smith's Bible Dictionary, ISBE)
  may supplement for historical/cultural background, never to add narrative
  content Scripture doesn't state.
- Do not import extra-biblical legend as fact. Post-biblical Jewish or church
  tradition about a person (e.g. traditions about apostles' later ministry
  and deaths, rabbinic elaborations on patriarchs) may be *mentioned as
  tradition, explicitly labeled as such* — never stated as confirmed fact.
  Same policy as Lives of Faith's hymn-legend handling (see "A Mighty
  Fortress" pattern in that project).
- If a fact is uncertain or disputed (authorship, dating, identification —
  e.g. "the beloved disciple," Junia's status as an apostle, the identity of
  the "sons of God" in Genesis 6), state that it's disputed rather than
  picking a side silently.

### Inclusion
- Cover the whole canon — Old and New Testament, all named individuals,
  not weighted toward Gospels/famous-name figures.
- No exclusion-by-denomination checklist is needed here (nobody in Scripture
  belongs to a post-biblical movement), but flag **interpretive** disputes
  the same way the historical-figures site flags theological ones — e.g.
  identification questions, chronology disputes, or a figure whose portrayal
  differs sharply across Christian traditions.

---

## Coverage and Two-Tier Depth

Unlike Lives of Faith (every entry gets full treatment), most of the ~3,000
named individuals in Scripture are single-verse genealogy mentions with no
narrative to tell. Two tiers:

### Full entries
For narratively-documented figures — enough text in Scripture to support the
three-paragraph story structure (see Two Story Versions below). Gets: adult
story, family story, a family-friendly summary (see below), image, memorials
(if any — see note below), significant events, connections/genealogy edges,
quiz questions.

**Family-friendly summary** (decided 2026-07-30): a single sentence, 150
characters or fewer, written for an 8-and-up reading level. It sits alongside
`adult_story`/`family_story`, not in place of them — the full-length stories
keep Scripture's own honesty about a person's documented sin per the
Theological Requirements above. The short summary is an age-calibrated
retelling, not a sanitized replacement: it can be honest in general terms
("David made big mistakes but always turned back to God") without spelling
out adult content (adultery, murder, sexual sin, graphic violence) that
isn't appropriate to hand an 8-year-old in a one-line summary. Full entries
only — stub entries have no story to summarize.

### Minimal (stub) entries
For everyone else — a name appearing in a genealogy or list with no narrative
content. Gets: `person_id`, `alt_names`, book/chapter/verse references,
genealogy relationship edges (parent/child, tribe, etc.), and nothing else.
No image, no story, no human-review badge (nothing was generated that needs
reviewing). These exist primarily so the connections/genealogy graph can be
complete.

`tier: "full" | "stub"` on every entry marks which one applies.

Note: "Memorials" (physical gravesites, museums) mostly doesn't apply to
biblical figures — drop that field for this project except in rare cases with
a real, documented, traditional site (e.g. the traditional Tomb of the
Patriarchs) that's worth noting as *tradition*, not confirmed fact.

---

## Bible Version Handling

- **NASB is the default/base translation** for canonical name spelling and
  the id/lookup system.
- The site lets visitors select between **NASB and KJV** for name-display
  purposes (decided 2026-07-30) — this changes displayed **name spelling
  only**, defaulting to NASB. NIV/ESV may be added later without a schema
  change (`alt_names` already generalizes to any number of translations) but
  are not in scope for the initial build.
- **No verse text is stored or quoted anywhere on the site**, in any
  translation, for copyright reasons. NASB/ESV/NIV are all copyrighted with
  quotation-limit policies that don't scale to thousands of entries. Use
  chapter:verse **references** only (e.g. "Genesis 12:1–3"), which are
  version-stable and need no licensing. KJV and the NET Bible are both
  permissively licensed for quotation and may be revisited later as an
  exception if a compelling feature needs it — not in scope now.
- Every person gets one unique `person_id` plus an `alt_names` array holding
  alternate spellings across translations. This matters most for KJV, which
  splits OT/NT spelling for the same person transliterated differently in
  each testament (Elijah/Elias, Isaiah/Esaias, Hosea/Osee, Noah/Noe,
  Boaz/Booz) — without `alt_names`, search and the connections graph would
  treat these as two different people.

---

## JSON Schema — Person Entry (draft)

```json
{
  "person_id": "elijah",
  "name": "Elijah",
  "alt_names": ["Elias"],
  "tier": "full",
  "testament": "OT",
  "era": "Divided Monarchy",
  "geographic_setting": ["Gilead", "Kingdom of Israel"],
  "references": ["1 Kings 17-19", "1 Kings 21", "2 Kings 1-2", "Malachi 4:5-6"],
  "topics": ["prophecy", "faith under persecution", "God's provision"],
  "interpretive_dispute": false,
  "interpretive_note": "",
  "source_summary": "Brief factual summary grounded in the biblical text",
  "family_friendly_summary": "One sentence, <=150 characters, 8-and-up reading level.",
  "adult_story": "...",
  "family_story": "...",
  "image": {
    "file": "elijah.jpg",
    "prompt_used": "Simple outline/line-art illustration, ancient Near Eastern prophet, minimal detail, low file size...",
    "prompt_image_source": null,
    "caption": "AI-generated image — no copyright claimed"
  },
  "genealogy": {
    "father": null,
    "mother": null,
    "spouses": [],
    "children": []
  },
  "review": {
    "human_reviewed": false,
    "reviewed_by": "",
    "reviewed_date": ""
  }
}
```

Stub entry (minimal tier):

```json
{
  "person_id": "jahdai",
  "name": "Jahdai",
  "alt_names": [],
  "tier": "stub",
  "testament": "OT",
  "references": ["1 Chronicles 2:47"],
  "genealogy": {
    "father": "caleb-son-of-hezron",
    "mother": null,
    "spouses": [],
    "children": []
  }
}
```

`era` taxonomy is finalized (see Open Questions history below). Still open:
whether `geographic_setting` is worth a controlled vocabulary for filtering
the way Lives of Faith uses `region` — revisit once enough full entries exist
to see the actual spread of locations.

Note on `interpretive_dispute`/`interpretive_note` (decided 2026-07-30): this
is a deliberately distinct field from Lives of Faith's `flagged`/`footnote`,
not a renamed reuse. Lives of Faith's field flags *moral/historical concerns*
about a person. That concept has no equivalent here — per the Theological
Requirements above, Scripture's own honesty about a hero's sin (David,
Solomon, Noah, Abraham, Peter, Jonah) is the text itself, never a
footnote-worthy concern, and must never be marked via this field.
`interpretive_dispute`/`interpretive_note` exists only for *interpretive*
questions: disputed authorship, disputed identification (e.g. "the beloved
disciple"), disputed chronology, or a figure whose portrayal differs sharply
across Christian traditions.

---

## Images

- **No claim of historical accuracy is possible** — there is no photographic
  or contemporary-portrait record for any biblical figure, unlike Lives of
  Faith's post-Renaissance subjects. Because of this:
  - Style is **simple outline/line-art, low detail, low file size** — not
    photorealistic. This is honest about what these images are (illustrative,
    not evidentiary) and solves the payload-size problem at 3,000 entries.
  - A "public domain reference image" requirement (mandatory on Lives of
    Faith) doesn't apply the same way. A reference may optionally be drawn
    from public-domain classical/traditional religious art for loose
    compositional guidance, but must be labeled in `prompt_image_source` as
    "artistic tradition, not historical record" rather than implying
    likeness accuracy.
- Same caption-burning requirement as Lives of Faith: every published image
  gets "AI-generated image — no copyright claimed" burned into the file
  itself, not just an HTML caption.
- Only full-tier entries with a story get an image. Stub entries never do.

---

## Genealogy / Connections Graph

- Every person (full or stub) participates in the connections/genealogy
  graph — this is the site's core differentiator from existing "Bible
  people" reference sites.
- At ~3,000 people, genealogy edges (parent/child, tribal descent, marriage)
  cannot be hand-curated one-by-one from prose the way Lives of Faith's
  `connections.json` is today. **Source dataset (decided 2026-07-30):
  [BradyStephenson/bible-data](https://github.com/bradystephenson/bible-data)**
  — CC BY 4.0 (attribution required, commercial use permitted). Use its
  `BibleData-Person`, `BibleData-PersonLabel` (Hebrew/Greek originals +
  Strong's numbers), and `BibleData-PersonRelationship` tables to
  bulk-generate parent/child edges and seed `person_id`/`alt_names`, then
  hand-add the smaller set of *narrative* relationship types (mentorship,
  conversion, rivalry, collaboration — same typed-edge model as Lives of
  Faith) only for full-tier entries where the story text documents them.
  Attribution to Brady Stephenson is required somewhere on the site (About
  page / footer) per CC BY 4.0 terms.
- Before bulk-importing, verify the current shape of the CSV/table exports
  (column names, ID scheme) directly from the repo, since this decision was
  made from repo documentation, not a hands-on data review.

---

## Site Architecture

Same pattern as Lives of Faith — flat static site, GitHub Pages, no backend,
all data in JSON, client-side filtering — with one change made up front
based on Lives of Faith's own scaling analysis (2026-07-30): **do not fetch
one monolithic people.json on every page load.** At 3,000 entries that file
would run 14–16MB even with light stub entries. Instead:

- A small **index file** (id, name, alt_names, tier, testament, topics —
  enough for search/filter/list views) loaded on every page.
- Full entry data (`adult_story`, `family_story`, `image`, `genealogy`)
  fetched per-person only when a person's page is opened.

```
/
├── index.html          ← home page + search/filter UI
├── person.html         ← full-entry template page
├── about.html
├── css/style.css
├── js/app.js
├── data/
│   ├── people-index.json     ← lightweight, loaded everywhere
│   ├── people/[person_id].json  ← full entry, fetched on demand
│   └── connections.json      ← genealogy + narrative edges
└── images/portraits/
```

(Chunking strategy decided 2026-07-30: one file per person, as shown above —
not sharded batches. Simpler cache/invalidation behavior and smaller diffs
per content update outweigh the extra file count at this scale.)

---

## Human Review System

Same badge system as Lives of Faith, full-tier entries only:
- ✅ Reviewed for accuracy — `human_reviewed: true`
- ⚠️ AI-generated content — not yet human reviewed — `human_reviewed: false`

Stub entries display no badge (nothing generative was produced beyond a name
and a reference).

---

## Social Media (Facebook / Instagram) — Planned, Not Yet Live

Andrew does not have Facebook or Instagram pages set up for this project
yet, but intends to add them. **Do not attempt to build or configure a
social scheduler until both pages exist.** When they do, the architecture
should mirror Lives of Faith's private `_build/fb/` pipeline (gitignored,
never pushed to GitHub, daily on-this-day/city-fallback posting pattern) —
extended to cover Instagram as a new platform this project's pipeline needs
to support that the original never did. Revisit this section once page IDs
exist.

---

## Reliable Sources

- **The biblical text itself** (NASB primary) — the source for all
  narrative content and factual claims about a person.
- **Easton's Bible Dictionary**, **Smith's Bible Dictionary**, **ISBE**
  (International Standard Bible Encyclopedia) — all public domain — for
  historical/cultural background supplementing the text.
- **Wikipedia** — background/context only, never as the source of narrative
  claims the text itself should be supplying.
- **[BradyStephenson/bible-data](https://github.com/bradystephenson/bible-data)**
  (CC BY 4.0) for bulk parent/child relationship data — see Genealogy /
  Connections Graph above.

---

## Open Questions — Resolved 2026-07-30

All five items flagged during scoping are now resolved; the seed-set build
may proceed.

1. **Era taxonomy**: finalized as drafted — Patriarchal, Exodus/Wilderness,
   Judges, United Monarchy, Divided Monarchy, Exile, Post-Exile/
   Intertestamental, Gospels, Apostolic.
2. **Translations**: NASB (default) + KJV for the initial build. NIV/ESV
   deferred, addable later without a schema change.
3. **Genealogy dataset**: [BradyStephenson/bible-data](https://github.com/bradystephenson/bible-data),
   CC BY 4.0. See Genealogy / Connections Graph section for details and the
   pre-import verification step.
4. **Chunking strategy**: one JSON file per person (`data/people/[person_id].json`),
   not sharded batches.
5. **Interpretive-dispute field**: split into `interpretive_dispute` (bool) +
   `interpretive_note` (string), kept fully distinct from Lives of Faith's
   `flagged`/`footnote` moral-concern mechanism, which has no equivalent on
   this site. See the JSON Schema section for the rationale.

---

## What Claude Code Should Do First

1. Read this entire document before doing anything.
2. Confirm understanding of the theological framing differences from Lives
   of Faith (redemptive-historical Christ-thread for OT figures; Scripture's
   own honesty about its heroes' flaws is not something to flag/footnote).
3. The Open Questions above are resolved (2026-07-30) — content generation
   may proceed.
4. Create the directory structure and begin with a small seed set of
   well-documented figures (e.g. Abraham, Moses, David, Ruth, Peter, Paul)
   to prove out the two-tier schema and chunked data architecture before
   scaling toward full coverage.
