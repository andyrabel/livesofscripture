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
For narratively-documented figures — enough text in Scripture to support two
description fields (decided 2026-08-01, superseding the earlier three-field
draft below): `adult_story` and `family_friendly_summary` — no separate
`family_story` field. Gets: those two descriptions plus `christ_connections`
(added 2026-08-03, see below), image, memorials (if any — see note below),
significant events, connections/genealogy edges, quiz questions.

**`adult_story`** (target ~200 words, **250 words max**, length revised
2026-08-03): the full-length treatment, keeping Scripture's own honesty
about a person's documented sin per the Theological Requirements above —
this is where family/relationship context belongs too, folded into the
narrative rather than a separate field.

**`family_friendly_summary`** (decided 2026-07-30, length revised
2026-08-01, target revised 2026-08-03 to ~100 words, **150 words max**):
written for an 8-and-up reading level — a short paragraph now, not a single
sentence. It is an age-calibrated retelling, not a sanitized replacement: it
can be honest in general terms ("David made big mistakes but always turned
back to God") without spelling out adult content (adultery, murder, sexual
sin, graphic violence) that isn't appropriate to hand an 8-year-old. Full
entries only — stub entries have no story to summarize.

**`christ_connections`** (added 2026-08-03, voice revised 2026-08-03): an
array of up to 3 short (1-2 sentence) phrases on how this person points to
Christ or reminds us of the gospel — per the Theological Requirements'
testament-aware framing (OT figures point forward per Romans 4 / Hebrews 11,
NT figures relate to Christ's accomplished work directly). Full-tier only.
Fewer than 3 entries is fine when that's all the text genuinely supports —
do not pad to hit the count. This supersedes the earlier "one paragraph per
person" draft of this idea in favor of several short, discrete phrases.

**Voice (decided 2026-08-03, superseding the original draft's
explanatory/analytical tone):** devotional and worshipful, not
teaching-mode. Written in first-person prayer voice, addressed to Christ
("Lord Jesus, You are...") rather than describing the connection in the
third person ("David's throne prefigures..."). Simple, short sentences —
plain words over theological vocabulary (e.g. "found" not "sought," "win"
not "victory," "picked" not "chose"). Still text-grounded: each phrase
should trace to a specific, real detail from the person's `adult_story`
(an event, a line, a choice), never generic praise that could apply to
anyone. Example (David):
- "Lord Jesus, You are David's greater Son, and Your throne will never end. Every earthly king has let me down — You never will."
- "David had blood on his hands, and You still forgave him. If grace can cover a murderer, Lord, it can cover me."
- "You didn't pick David for how he looked. You looked at his heart. You look at mine the same way — and You love what You see enough to save it."

**Promotion rule** (decided 2026-08-03): a person belongs in the full tier
whenever Scripture narrates something about them beyond a bare name/parentage
listing — an action, words, or a distinguishing episode — even a minor one
(e.g. Ahimaaz the runner, Nicolas one of the seven in Acts 6). A name that
occurs only inside genealogy-list passages (Genesis 5/10/11/36, 1 Chronicles
1-9, Ezra 2, Nehemiah 7/12, and similar) with nothing else said about them
stays a stub — there is no narrative content to write, and inventing any
would violate the Factual Accuracy rules above. When in doubt, check what
the actual verse(s) say before deciding, not just whether the reference
falls outside a known genealogy chapter — many single-verse mentions outside
those chapters (e.g. a name in a wall-builders list or an officials roster)
are still just a name with no narrative, and should stay stubs.

### Minimal (stub) entries
For people with no narrative in Scripture — a name appearing in a genealogy
or list with nothing else said about them. Gets: `person_id`, `alt_names`,
book/chapter/verse references, genealogy relationship edges (parent/child,
tribe, etc.), and nothing else. No image, no story, no human-review badge
(nothing was generated that needs reviewing). These exist primarily so the
connections/genealogy graph can be
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
  "gender": "male",
  "era": "Divided Monarchy",
  "geographic_setting": ["Gilead", "Kingdom of Israel"],
  "references": ["1 Kings 17-19", "1 Kings 21", "2 Kings 1-2", "Malachi 4:5-6"],
  "first_reference": "1 Kings 17-19",
  "topics": ["prophecy", "faith under persecution", "God's provision"],
  "interpretive_dispute": false,
  "interpretive_note": "",
  "source_summary": "Brief factual summary grounded in the biblical text",
  "family_friendly_summary": "Up to 150 words, 8-and-up reading level.",
  "adult_story": "Up to 250 words. Family/relationship context is folded in here, not a separate field.",
  "christ_connections": [
    "Up to 3 short (1-2 sentence) phrases on how this person points to Christ or the gospel.",
    "Old Testament figures point forward per Romans 4 / Hebrews 11 framing; New Testament figures relate to Christ's accomplished work directly.",
    "Full-tier entries only. Fewer than 3 is fine if that's all the text supports — do not pad."
  ],
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
  "gender": "male",
  "references": ["1 Chronicles 2:47"],
  "first_reference": "1 Chronicles 2:47",
  "genealogy": {
    "father": "caleb-son-of-hezron",
    "mother": null,
    "spouses": [],
    "children": []
  }
}
```

**`first_reference`** (decided 2026-08-01): every person, full or stub, carries
this field — the single reference where they are first named in Scripture,
always equal to `references[0]`. The `references` arrays throughout the
dataset are already in canonical book order (confirmed by sampling the
BradyStephenson import), so this is a derived convenience field, not
independently curated — regenerate it from `references[0]` if the
references array for a person is ever edited.

**`gender`** (added 2026-08-01): `"male" | "female"`, present on every person
(full or stub). Backfilled from the BradyStephenson dataset's `sex` column
(`_build/backfill_gender.py`, `data/people/*.json` + `data/people.json`) —
not independently curated, and not stored for the 4 dataset rows that are
titles rather than named individuals (e.g. "the angel of the LORD"), which
the site's import intentionally never turned into person entries in the
first place. Used to render a `(M)`/`(F)` marker after a person's name on
person pages' Connections section, the People search page, and the
connections graph's sidebar card, and to color-code names on the
connections graph (dark blue for male, dark red for female).

**`disambiguation`** (added 2026-08-03, index-only): a derived string field
on `data/people.json` entries for anyone who shares their `name` with
another person — see the "Name Disambiguation" section below for the rules
and regeneration script. Not part of the per-person JSON schema shown
above; computed and stored only in the lightweight index.

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
  gets a caption identifying its origin burned into the file itself, not
  just an HTML caption. If an image is AI-generated, that caption reads
  "AI-generated image — no copyright claimed"; see the note below for the
  case where it isn't.
- Only full-tier entries with a story get an image. Stub entries never do.

**Note on the seed-set illustrations (2026-07-30):** the six seed images
(Abraham, Moses, David, Ruth, Peter, Paul) were *not* AI-generated — no
AI image-generation tool was available in the environment they were built
in. They're hand-authored SVG line art instead: a plain robed silhouette
with no attempted face, distinguished only by one symbolic prop per person
(Abraham gesturing at stars, Moses with staff and tablets, David with crown
and sling, Ruth with a wheat sheaf, Peter with a key, Paul with a scroll and
radiating light). This still satisfies the style requirement above (simple,
low-detail, no likeness claim) but is a symbolic-emblem approach rather than
a figurative illustration of the person, and their captions say so
("Original line-art illustration...") rather than claiming AI generation,
which would be false. Caption text is *not* burned into these six PNGs
(unlike the AI-generated-image requirement above) since there's no
provenance ambiguity to guard against for original hand-authored vector
art. Revisit this approach once a real image-generation pipeline is
available for the site — decide then whether to keep the symbolic-emblem
style at scale or switch to AI-generated figurative portraits per the
original spec. (The seed set has since grown past the original six as more
full-tier entries were hand-illustrated with their own unique prop, e.g.
Aaron, Sarah, Solomon, Bathsheba, Jochebed — see `images/portraits/*.svg`
for the current roster of person-specific icons.)

**Generic role icons (decided 2026-07-31, extended 2026-08-01):** every
full-tier ("major") person — anyone with enough narrative to get a story,
not just a name in a list, including figures like Mephibosheth, Onesimus, or
Goliath — must have an icon. Hand-authoring a unique symbolic prop per
person doesn't scale, so seven shared generic icons exist in the same
hand-drawn line-art style (`images/portraits/generic-king.svg/png`,
`generic-queen.svg/png`, `generic-prophet.svg/png`, `generic-priest.svg/png`,
`generic-warrior.svg/png`, `generic-figure.svg/png`, `generic-woman.svg/png`)
and are reused across many people rather than duplicated per person:
- **King** — crown + royal staff.
- **Queen** — veil + royal circlet + royal staff (added 2026-08-01, for
  female monarchs, e.g. Jezebel, Athaliah, Queen of Sheba).
- **Prophet** — both arms raised, mouth open (crying out a message).
- **Priest** — turban + the breastplate of judgment (12 stones, Exodus 28).
- **Warrior** — helmet, sword, and round shield.
- **Figure** — the plain base figure with no prop, for full-tier *male*
  people who don't fit any of the roles above (e.g. Mephibosheth, Onesimus).
- **Woman** — the same plain pose as Figure but wearing a veil (added
  2026-08-01), for full-tier *female* people who aren't a monarch and don't
  have a unique icon (e.g. Rachel, Hannah, Priscilla). The veil mirrors the
  convention already used on hand-drawn female icons like Sarah and Ruth,
  rather than inventing a new visual language.

Rule going forward: **keep a person's existing unique hand-drawn icon if one
already exists** (check `images/portraits/[person_id].svg`); only assign a
generic role icon to full-tier people who don't have one. Pick Figure vs.
Woman (and King vs. Queen for monarchs) by the person's `gender` field. Set
`image.file` to the shared filename (e.g. `"generic-priest.png"`), and
`image.caption` to `"Generic line-art icon for {role}s — symbolic, no claim
of likeness"`. The lightweight index (`data/people.json`) also carries a
flat `image` filename string per full-tier entry (not the full nested
object) so client-side code (`js/app.js`'s `portraitImg()`) can render an
avatar without fetching the per-person JSON file — keep that field in sync
whenever a full-tier person's `image.file` changes.

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

### Connections Graph Page

Same pattern as Lives of Faith's `connections.html` — a radial graph
visualization with a combobox picker to select a starting person, network-size
counts, and greyed-out nodes for anyone unconnected to the current selection.
At biblical scale this page matters *more* than it does on Lives of Faith,
since most of a typical person's connections will be genealogical rather than
narrative (mentorship/conversion/etc.), so the graph is likely to be dominated
by long tribal-descent chains (e.g. the Genesis 5 and Genesis 11 "begat"
chains, the 1 Chronicles 1–9 genealogies). Depth/zoom defaults that work for
Lives of Faith's smaller, mostly-narrative-edge graph may not work unchanged
here — expect this to need its own tuning pass once real genealogy data from
BradyStephenson/bible-data is loaded, rather than assuming the original's
settings transfer directly.

---

## Name Disambiguation (decided 2026-08-03)

Distinct from the "Other people named X" grid already implemented at the
bottom of full-tier Person Detail pages (`disambiguation_section()` in
`_build/generate_static_site.py`, full-tier-to-full-tier only, icon + blurb
+ link). This section covers a second, separate mechanism: a short inline
qualifier shown next to a person's *name* wherever it appears, for **any**
person (full or stub) who shares their `name` with another entry in the
dataset — not just full-tier collisions.

**Rules**, applied to whichever have data (never fabricated — see Factual
Accuracy above):
1. Full name / nickname / title, where the dataset already encodes one
   (currently: an `alt_names` entry that extends the base name, e.g. base
   "Judas" + alt_name "Judas Iscariot" → "Iscariot"). Textual epithets like
   "Sons of Thunder" are **not** hand-curated yet — see gap note below.
2. Relationship to a named person: father, else mother, else first spouse,
   else first child, from the person's own `genealogy` edges — worded
   "son of"/"daughter of"/"husband of"/"wife of"/"father of"/"mother of" by
   the subject's `gender` (falls back to "child of"/"spouse of"/"parent
   of" when gender is unknown). The referent does not need to be a
   full-tier person — Scripture itself commonly disambiguates this way
   (e.g. "son of Zebedee" vs. "son of Alphaeus") even when the parent
   named is only a stub entry.
3. Abbreviated first reference: `first_reference` with its book name
   swapped for a standard abbreviation (e.g. "1 Chronicles 3:21" → "1 Chr
   3:21").

Parts that exist are joined (title/nickname, then relationship, then the
abbreviated reference in parentheses); a bare `"(Gen 4:1)"` is a valid
result when rules 1–2 have no data for that person. **Safety rule:** if two
or more people in the same name collision would get an *identical*
relationship phrase, the phrase doesn't disambiguate them and is suppressed
for those people (falls back to reference-only) rather than shown — this
generally signals a pre-existing data problem in the underlying genealogy
import rather than a real "we just don't know more" case.

**Regeneration:** `_build/generate_disambiguation.py` computes this from
`data/people/*.json` (genealogy, `first_reference`, `alt_names`) and bakes
the result into a `disambiguation` string field on `data/people.json`
index entries (same "index carries derived aid fields" pattern as
`_build/infer_stub_eras.py`) — not stored on the per-person files. Re-run
it (before `generate_static_site.py`) whenever genealogy, name,
`alt_names`, or `first_reference` values change.

**Rendered so far — People List page only** (`js/app.js`'s `personCard()`
and `_build/generate_static_site.py`'s `person_card_html()`, for both the
client-rendered and static-fallback grid): every full-tier ("not name
only") person's name renders in `<strong>`; stub-tier names render in
plain `<span>` — this bolding applies to *every* full-tier card, not only
those with a collision. Any person with a `disambiguation` value gets it
shown as a muted line under the name, whichever tier they are. **Person
Detail pages intentionally do not use this yet** — deferred per Andrew
2026-08-03 pending other fixes; when picked up, reuse the same
`disambiguation` index field rather than recomputing it, and decide
placement (byline under the name vs. inline).

**Known gap:** rule 1 (title/nickname) fires for only 1 of 1692 affected
people today (`alt_names` rarely carries a fuller epithet) — hand-curating
Scripture's own epithets (e.g. "Sons of Thunder" for James/John sons of
Zebedee, "the Baptist", "Magdalene", "the Zealot") for the small set of
*famous* collisions is a worthwhile follow-up, not attempted in this pass
to avoid inventing text for the other ~480 collision groups that have no
comparable textual epithet.

**Data-quality issue discovered while building this (2026-08-03):**
several name collisions resolve to identical relationship phrases *and*
overlapping/identical `first_reference` values, which looks like genuine
duplicate person entries from the BradyStephenson import rather than two
different biblical individuals — most clearly `enoch`/`enoch-2` (both cite
Genesis 5:18-24) and likely `zerubbabel`/`zerubbabel-2`/`zerubbabel-3`
(son of Shealtiel, spanning three person_ids). Separately, `matthat`/
`matthat-2` (Luke 3:24 and 3:29 — Luke's genealogy genuinely does contain
two men named Matthat) both resolved to "son of Levi", suggesting the
import may have collapsed two distinct Levis in that same genealogy list
into one `levi` person_id. None of this was fixed here — the
disambiguation script's safety rule (above) just avoids surfacing the
resulting misleading phrases — but it's worth a dedicated genealogy-data
cleanup pass against the source BradyStephenson tables.

---

## Timeline

Same concept as Lives of Faith's `timeline.html` — a chronological view across
all full-tier people — but biblical chronology is a fundamentally harder
problem than post-Reformation history, and this needs to be designed for from
the start rather than discovered as a bug later:

**Extended 2026-08-01 to include everyone in the genealogical ("x begat y")
chains, not just full-tier entries** — Genesis 5, Genesis 11, 1 Chronicles
1-9, and similar passages are the site's core differentiator and belong on
the timeline even though almost none of those names have a narrative.
Consequences for the data model:
- Stub entries now also carry an inferred `era` (and where derivable,
  `region` and a minimal `genealogy` of father/mother/spouses) in the
  lightweight index (`data/people.json`), computed by
  `_build/infer_stub_eras.py`: walk the genealogy graph out from every
  full-tier person's known `era`, propagating to unresolved
  parents/children/spouses until no more can be resolved, then fall back to
  a default `era` by the book their `first_reference` falls in for anyone
  never connected to a known-era anchor. This is a derived visualization
  aid, not curated content — it does not make a stub eligible for a
  human-review badge or any other full-tier treatment.
- The timeline page (`js/app.js`) now builds its dataset directly from the
  index rather than fetching every person's full JSON file, since the index
  now carries every field the timeline needs (`era`, `region`, `genealogy`,
  `timeline`, `first_reference`, `name`) for both tiers. Re-run
  `_build/infer_stub_eras.py` (before `generate_static_site.py`) whenever
  genealogy data or full-tier `era`/`timeline` values change.

- Most Old Testament dates, especially pre-monarchy, are **disputed among
  evangelical scholars themselves** — not just "uncertain" the way an obscure
  missionary's birth year might be uncertain, but genuinely contested by
  competing scholarly frameworks (e.g. the early-date ~1446 BC vs. late-date
  ~1250 BC Exodus debate; differing patriarchal chronologies depending on how
  the genealogies are read). The site must not silently pick one framework and
  present it as settled fact.
- Recommended approach: **default every OT figure to an `era` bucket**
  (Primeval History, Patriarchal, Exodus/Wilderness, Judges, United Monarchy,
  Divided Monarchy, Exile, Post-Exile/Intertestamental, Gospels, Apostolic —
  see the Era Taxonomy note below for `Primeval History`, added 2026-08-01)
  rather than a specific year. Only
  assign a specific year (with the existing Lives of Faith `"c. "`
  uncertainty-prefix convention) where a reasonably solid evangelical
  scholarly consensus exists (e.g. Solomon's temple construction, calculable
  from 1 Kings 6:1 and widely-used regnal chronologies) — and even then, note
  in the entry that the date rests on a particular chronological framework
  rather than stating it as bare fact.
- New Testament dating is comparatively firmer (Roman-era cross-references
  exist) and can follow the existing Lives of Faith `significant_dates`
  pattern much more directly — full dates or `"c. "` estimates as normal.
- The timeline UI itself should visually distinguish "era-only" placements
  from "specific date" placements, since plotting a Judges-era figure at a
  precise x-axis position implies a false precision the underlying data
  doesn't have.

---

## Places / Map (Archaeological and Traditional Sites)

Lives of Faith has two related concepts: a `memorials` array per person
(gravestones, statues — confirmed physical locations) and a separate
`places.json` (museums/archives not tied to one person), both rendered on
`map.html`. For this project:

- **Per-person memorials mostly don't apply**, as already noted under
  Coverage and Two-Tier Depth — most biblical figures have no confirmed
  burial site. Where a **traditional** site is well-known and visited (Tomb
  of the Patriarchs at Hebron, traditional Tomb of David, Garden Tomb vs.
  Church of the Holy Sepulchre for the resurrection site), it may be
  included, but the entry must state plainly that it is a *traditional* or
  *disputed* identification, not an archaeologically confirmed one — and
  where two traditions compete for the same event (as with the two
  resurrection-site candidates), include both rather than silently picking a
  side, the same principle as the "disputed identification" rule under
  Factual Accuracy above.
- **A `places.json`-equivalent for archaeological/biblical-geography sites**
  is a stronger fit here than it was for Lives of Faith, and worth building
  deliberately rather than as an afterthought: excavated sites tied to
  biblical narrative (Jericho, Capernaum, Megiddo, Masada, Corinth, Ephesus,
  the Areopagus in Athens, Bethlehem's Church of the Nativity), and major
  museum holdings relevant to the text (e.g. the Shrine of the Book at the
  Israel Museum for the Dead Sea Scrolls). Same `type` + `open_to_public`
  pattern as Lives of Faith's places schema, plus a new field distinguishing
  **archaeologically confirmed** identification from **traditional/disputed**
  identification — this distinction needs to be visible on the map itself,
  not just buried in body text, given how many biblical site identifications
  are genuinely contested among scholars.

---

## Site Architecture

Same pattern as Lives of Faith — flat static site, GitHub Pages, no backend,
all data in JSON, client-side filtering — with one change made up front
based on Lives of Faith's own scaling analysis (2026-07-30): **do not fetch
one monolithic people.json on every page load.** At 3,000 entries that file
would run 14–16MB even with light stub entries. Instead:

- A small **index file** (id, name, alt_names, tier, testament, topics —
  enough for search/filter/list views) loaded on every page.
- Full entry data (`adult_story`, `family_friendly_summary`, `image`,
  `genealogy`) fetched per-person only when a person's page is opened.

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

### Static pre-rendering for SEO / LLM-search crawlability (decided 2026-07-31)

Person content (`adult_story`, `family_friendly_summary`, genealogy, etc.) was originally
rendered entirely client-side by `js/app.js` fetching `data/people/[id].json`
into `person.html?id=[id]`. Googlebot executes JavaScript so this worked for
Google, but most LLM-search crawlers (GPTBot, ClaudeBot, PerplexityBot,
CCBot, and similar) fetch raw HTML and do not run JavaScript — they would
see an empty "Loading…" page for every person entry, i.e. the site's core
content would be invisible to them.

Fixed by pre-rendering: `_build/generate_static_site.py` (stdlib-only
Python, no dependencies) reads `data/people.json` + `data/people/*.json` +
`data/connections.json` and generates one fully-baked static HTML file per
person at `people/[person_id].html` — real story text, per-person
`<title>`/meta description/OG/Twitter tags, a canonical URL, and a
schema.org `Person` JSON-LD block (including `parent`/`children`/`spouse`
links resolved to sibling person pages, since genealogy is the site's core
differentiator). It also regenerates `sitemap.xml` and the static fallback
`<a class="person-card">` grid embedded in `people.html` between
`STATIC_PERSON_GRID_START`/`_END` markers, so the browse/list page is
crawlable without JS too — `renderIndexPage()` still re-renders that grid
client-side on load for interactive filtering, with no visible difference
for JS-enabled visitors.

Consequences for the file layout above:
- Canonical person URL is now `people/[person_id].html`, not
  `person.html?id=[person_id]`. `person.html` is now a thin JS + meta-refresh
  redirect shim (`noindex, follow`) kept only so old `?id=` links still land
  somewhere; **do not** treat it as the template to extend for new person-page
  features — extend `_build/generate_static_site.py`'s render functions
  instead, mirroring whatever markup/CSS classes are used.
- `.github/workflows/build.yml` runs the generator on every push to `main`
  and commits the regenerated `people/`, `sitemap.xml`, and `people.html`
  output back to the branch GitHub Pages serves — this keeps deployment as
  plain branch-served Pages (no switch to Actions-artifact deployment).
- `robots.txt` explicitly allows `*` plus a belt-and-suspenders explicit
  `Allow: /` for named AI/LLM crawlers, and points to `sitemap.xml`.
- Whenever `data/people.json`, `data/people/*.json`, or `data/connections.json`
  changes, re-run `python3 _build/generate_static_site.py` before committing
  (or just push — CI does it) so the static output doesn't drift from the
  source JSON.

---

## Human Review System

Same badge system as Lives of Faith, full-tier entries only:
- ✅ Reviewed for accuracy — `human_reviewed: true`
- ⚠️ AI-generated content — not yet human reviewed — `human_reviewed: false`

Stub entries display no badge (nothing generative was produced beyond a name
and a reference).

---

## What's New Feed

Same concept as Lives of Faith's `data/whats-new.json` + home-page sidebar box
— a short, factual, most-recent-4-shown feed of site changes (new features,
not routine content additions). Carries over essentially unchanged:
ISO-dated entries with a short title, a target page, and a one-sentence lowercase
description. Not urgent for initial build — this is a nice-to-have once the
site has shipped its first few real features, not part of the seed-set proof
of concept. If Lives of Faith's git-history-driven auto-drafting script
(`_build/generate_whats_new.py`) turns out to work well there, it's a
reasonable candidate to port later rather than reinvent — revisit once this
project has its own commit history to draft from.

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
   Intertestamental, Gospels, Apostolic. **Extended 2026-08-01** with a
   **`Primeval History`** era preceding Patriarchal, for Genesis 1-11 figures
   (Adam through the Table of Nations/Babel) once the timeline began placing
   every person in a genealogical chain, not just full-tier entries — see
   the Timeline section below. This period has no scholarly consensus
   chronology at all, not merely a disputed date the way the Exodus is —
   young-earth, old-earth, and framework readings of Genesis 1-11 disagree
   far more sharply, including on whether the genealogies represent an
   unbroken sequence of years in the first place. The era band is
   deliberately wide and exists only to give these figures *some* ordinal
   position before Patriarchal, never a chronology claim.
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
