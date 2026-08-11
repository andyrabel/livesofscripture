# LivesOfScripture.org — Project Instructions

## Scope

This document is the project-wide source of truth for content, architecture,
data, build, and contribution conventions across the repository.

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

### Doctrinal Position (decided 2026-08-06)

All content — full-entry stories and especially `devotionals` (see the
Coverage and Two-Tier Depth section below; `christ_connections`, formerly
named here too, was retired 2026-08-09) — should be written from the
perspective of **conservative
evangelical theology in the Open Brethren (Plymouth Brethren / Gospel Hall)
tradition**. Key commitments to write consistently with:
- The authority and sufficiency of Scripture.
- Salvation by grace through faith in Christ alone.
- **"Once saved, always saved"** — a believer's security in Christ does not
  depend on their ongoing performance. Concretely: avoid any phrasing that
  implies salvation itself is repeatedly lost and re-given (e.g. never write
  something like "I need You to save me again and again" — that reads as
  losable salvation). Ongoing sin after conversion should be framed as a
  believer's continued need of God's **grace**, not a need to be re-saved —
  e.g. Noah's devotional was corrected 2026-08-06 to "I need Your grace
  again and again, every day," which is the right pattern to reuse.
- A plain-reading/dispensational approach to Bible interpretation.
- Believer's (not infant) baptism by immersion.
- Weekly congregational Breaking of Bread/Communion.
- A plurality of local elders rather than a single ordained clergy.
- Simplicity and lay-led worship — avoid sacramentalism, liturgical
  formality, and denominational/clergy hierarchy language.
- Strong emphasis on personal Bible study, missions, evangelism, and
  discipleship.

Content should stay Christ-centered and accessible to lay readers, including
ESL audiences and families — same plain-language instinct already governing
`devotionals` voice/length (see the JSON Schema section and
`_build/`-adjacent devotional pilot notes for the current house style).

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
`family_story` field. Gets: those two descriptions plus `devotionals`
(added 2026-08-05, formalized here 2026-08-09, see below), image, memorials
(if any — see note below), significant events, connections/genealogy edges,
quiz questions.

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

**`devotionals`** (added 2026-08-05 as a pilot alongside the older
`christ_connections` field; formalized as the sole schema field 2026-08-09
once `christ_connections` was retired — see the retirement note below): an
array of 1-3 short phrases on how this person points to Christ or reminds
us of the gospel — per the Theological Requirements' testament-aware
framing (OT figures point forward per Romans 4 / Hebrews 11, NT figures
relate to Christ's accomplished work directly). Full-tier only. Fewer than
3 entries is fine when that's all the text genuinely supports — do not pad
to hit the count.

**Eligibility:** only for *major* people, meaning at least one of: 3 or
more real Bible references (judged by actual narrative substance/verse
mentions, not literal `references`-array length — that array stores
citation *ranges*, e.g. `"Ruth 1-4"` is one entry covering four chapters,
so a literal array-length check structurally undercounts almost everyone
and should not be used on its own), has a Bible book named after them, or
is a known writer of a Bible book. Skip anyone who doesn't clear this bar,
even if they're otherwise full-tier.

**Voice (decided 2026-08-06, superseding an original direct-prayer-address
draft):** first-person-plural, "we/us/may we" — narrate the person's story
in third person, then turn it toward the reader ("may we trust like that
too," "Jesus leads us out of something even bigger"). Do **not** address
Jesus directly in second person ("Lord Jesus, You are...") — that reads too
much like putting words in the reader's mouth as an actual prayer. "We/us"
puts the speaker on equal footing with the reader rather than singling out
an individual "me." No age-segregating references (nothing that only makes
sense read aloud to a child) — the same phrase must work for an adult and
an 8-year-old in the same sitting. Every phrase must name "Jesus" (or
"God" where the phrase is really about the Father's action) somewhere in
that same phrase, since phrases may be shown independently and can't rely
on an earlier phrase in the array for context. Target ~20 words per
phrase, 28 words max. Still text-grounded: each phrase should trace to a
specific, real detail from the person's `adult_story` (an event, a line, a
choice), never generic praise that could apply to anyone. Renders on
person-detail pages as a "Thought for Today" section; the static
pre-renderer always uses the array's first phrase for determinism, while
client-side code may rotate entries for visitors. Example (Noah):
- "Noah walked with God while the whole world turned away. May we stay faithful too, even when no one else around us is."
- "God judged the world but saved Noah's family through the ark. Jesus is our ark, the one safe place from judgment."
- "Even Noah, saved from the flood, still stumbled into sin afterward. We don't need to be saved again — we simply need God's grace again, every day."

**`christ_connections` retired 2026-08-09.** An earlier field with the same
Christ-pointing purpose but a different voice (first-person direct prayer,
e.g. "Lord Jesus, You are David's greater Son") and up to 3 phrases per
person. It was piloted alongside `devotionals` starting 2026-08-05, never
actually rendered anywhere on the site, and was fully removed from all 420
person entries that had it on 2026-08-09 in favor of `devotionals`
covering this role going forward. May be reintroduced later for a
*different* purpose — if so, treat that as a new field, not a revival of
this one's old voice/rules.

**`christ_connections` reintroduced 2026-08-10, as a genuinely new field
that happens to reuse the old name — not a revival of the retired
first-person-prayer field above.** New shape: an array of
`{"type": ..., "reference": ...}` objects, e.g.
`{"type": "ancestor", "reference": "Matthew 1:6"}`. Unlike `devotionals`
(a homiletical reflection, freely composed), this field is a factual
index: it records only connections the biblical text **itself** explicitly
states, each anchored to the specific reference that states it — never a
connection later Christian tradition draws (e.g. common devotional
typology for Joseph son of Jacob is deliberately excluded — no NT text
explicitly calls him a type of Christ, unlike Adam in Romans 5:14 or
Melchizedek in Hebrews 7). Categories in use so far: `ancestor` (named in
Jesus' genealogy, Matthew 1 or Luke 3), `family` (Jesus' actual mother,
legal father, or named siblings), `apostle`/`disciple` (explicitly called
one of the Twelve, or explicitly described as a follower of Jesus),
`forerunner` (John the Baptist), `type` (an NT text explicitly draws a
figurative/typological comparison to Christ), `prophecy` (an OT prophecy
the NT explicitly quotes or applies to Jesus), and `witness` (someone the
text shows explicitly recognizing or testifying about Christ, e.g. Simeon,
Anna, or a resurrection appearance). A person can have zero, one, or
several entries; most full-tier people will have **none**, and that's
expected, not a gap — this field intentionally does not attempt one
connection per person the way `devotionals` eventually did. The
2026-08-10 pass populated 72 of 699 full-tier entries (the Matthew
1/Luke 3 genealogy line so far as it overlaps full-tier people, the
Twelve plus Matthias/Barnabas/Paul, a handful of explicit OT
types/prophecies, and a few explicit eyewitness-testimony cases) as a
first, deliberately non-exhaustive pass — extending it to more figures
with a genuinely explicit textual connection is a reasonable follow-up,
but do not pad entries to "cover everyone." **Data-collection only: not
yet surfaced in the UI** (no rendering code reads this field) —
storage-only, same holding pattern the old field spent its whole life in
before retirement, so revisit whether/how to render it before assuming
it's inert forever.

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
  "devotionals": [
    "1-3 short we/us-voice phrases (~20 words, 28 max) on how this person points to Christ or the gospel.",
    "Old Testament figures point forward per Romans 4 / Hebrews 11 framing; New Testament figures relate to Christ's accomplished work directly.",
    "Full-tier, eligible ('major') entries only. Fewer than 3 is fine if that's all the text supports — do not pad."
  ],
  "name_meaning": {
    "meaning": "The LORD is my God",
    "language": "Hebrew"
  },
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

**`name_meaning`** (added 2026-08-10, full-tier only): `{"meaning": ..., "language": ...}`,
the etymological meaning of the person's own `name` and the language it
comes from. Rendered on the person-detail page header, under the name (and
under `alt_names` when present) — see `render_full_person_body()` in
`_build/generate_static_site.py`. Sourced primarily from **Hitchcock's Bible
Names Dictionary** (Roswell D. Hitchcock, 1869, public domain — added to the
Reliable Sources list below), fetched programmatically for all 589 unique
full-tier names; the ~80 names Hitchcock's page happened to omit (including
surprisingly common ones like Michael and Matthew) and all ~55 multi-word or
hyphenated compound names (e.g. "Mary Magdalene," "Ben-hadad") were
hand-researched and cross-checked instead, since Hitchcock's entries for
those either didn't exist or only captured one half of the name. `language`
defaults to Hebrew for OT-tier people and Greek for NT-tier people (the
language the *text* is written in), but is overridden per-name for anyone
whose name is actually of different origin — Latin (Paul, Mark, Silas'
household, most Roman officials), Aramaic (Barnabas, Thomas, Martha, Bar-
prefixed names), or a foreign king/court name (Persian: Cyrus, Esther,
Ahasuerus; Akkadian/Babylonian/Assyrian: Nebuchadnezzar, Sennacherib,
Tiglath-pileser; Egyptian: Pharaoh, Potiphar; and smaller one-off cases like
Goliath's Philistine origin or Candace, which is actually a Meroitic/Cushite
royal *title*, not a personal name at all). A meaning of "uncertain" is used
where scholarship itself doesn't agree (e.g. Methuselah, several minor
Persian court officials) rather than picking one silently, per the Factual
Accuracy rules above. Stub entries never get this field, matching every
other curated full-tier-only field (see Coverage and Two-Tier Depth).
`_build/backfill_name_meaning.py` holds the full name→meaning/language
mapping and is safe to re-run (same "exists on disk, documented here, not
committed since `_build/` is gitignored by default" pattern already used by
`_build/backfill_lifespan_years.py` — see the Timeline section) — if new
full-tier people are promoted later, add their name to that script's dict
the same way (Hitchcock's first, hand-research for gaps/compounds) before
re-running it.

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

## Tribal Affiliation (added 2026-08-10)

A `tribe` field records which of the twelve tribes of Israel a full-tier
person belongs to, where the text states or clearly implies it. Shape:

```json
"tribe": {
  "name": "Levi",
  "reference": "Exodus 6:20"
}
```

Stored on the full-tier person file (`data/people/<id>.json`) and mirrored
as a flat `tribe` name string on the `data/people.json` index entry (same
"index carries a flat convenience copy" pattern already used for `image`).
Computed by `_build/backfill_tribe.py` (gitignored like the site's other
one-time backfill scripts — see `name_meaning`'s note above — safe to
re-run; add new person_ids to its `EXPLICIT`/`CHAIN_REFERENCE` dicts and
re-run rather than hand-editing the JSON output). **Data-collection only:
not yet surfaced in the UI**, the same holding pattern `christ_connections`
spent its whole life in before being rendered — revisit whether/how to
render this once there's a concrete use (e.g. a tribe filter, or grouping
on the connections graph).

**Deliberately incomplete — 204 of 699 full-tier people (mostly OT).**
Tribal membership only applies to physical descendants of Jacob/Israel;
most full-tier people are outside that entirely (pre-Jacob patriarchs,
Gentiles, foreign kings/officials, Canaanites/Moabites who married in
without themselves being reckoned to a tribe, and virtually every NT
figure whose tribe Scripture never states). Even among Israelites, the
bar for inclusion is deliberately narrow — do not lower it without
revisiting this section:

1. **Explicit statement** — Scripture directly names the tribe or uses a
   tribal epithet attached to the person themselves ("of the tribe of
   Judah," "Ehud... the Benjamite," "Jeroboam... an Ephraimite," "a
   Levite," "Jair the son of Manasseh"). Highest confidence; the
   `reference` cited is the verse making the statement.
2. **Genealogy-chain inference** — the person's own `genealogy.father`
   chain (walked up through `data/people.json`, which the Timeline section
   above already established carries genealogy for both tiers) reaches one
   of the twelve tribal-head person_ids (`reuben`, `simeon`, `levi`,
   `judah`, `dan`, `naphtali`, `gad`, `asher`, `issachar`, `zebulun`,
   `ephraim`, `manasseh`, `benjamin`). Covers the Davidic/Judah royal line,
   the Aaronic/Levitical priestly and musician lines, and a handful of
   other documented Chronicles genealogies. The `reference` cited is the
   Scripture genealogy passage (1 Chronicles 2–9, Ruth 4, Ezra 7, Numbers
   26–27, etc.), not a literal verse-by-verse citation for every link.
3. **Explicit statement overrides the chain when they conflict.** Jair is
   the one case found so far: 1 Chronicles 2:21-22 traces him through
   Hezron (Judah) via his mother, a daughter of Machir of Manasseh, but
   Numbers 32:41 explicitly calls him "the son of Manasseh" — his own
   territorial reckoning in Gilead. The field uses Manasseh, per the
   explicit text, not the patrilineal chain.

**Deliberately excluded even when a tribe might be guessable:** a
person's *hometown* alone (e.g. Bethlehem, Shiloh, a "hill country of
Ephraim" residence) is not treated as sufficient basis unless the text
itself attaches the location to the person as a direct origin statement
("a man of Bethlehem in Judah," Ruth 1:1-2; "a man of the hill country of
Ephraim," Judges 17:1) rather than merely describing where they later
lived, sat in judgment, or held office (Deborah's judgment-seat location,
Elisha's Abel-meholah, Ahijah "the Shilonite," Ibzan's ambiguous
Bethlehem) — those were left out as not clearly enough stated, per the
Factual Accuracy section's "state disputed rather than picking a side"
rule. Territory shared by more than one tribe (Gilead — Gad, Reuben, and
half-Manasseh all held ground there) was also left out by default unless,
as with Jair, an explicit verse resolves it. Genuinely disputed
identifications (e.g. whether the genealogy in Zephaniah 1:1 names King
Hezekiah) were left out for the same reason.

**Data bugs found and fixed while building this (2026-08-10):**
- `data/people.json`'s index entry for **Dinah** had `genealogy.father:
  "jacob"` (the NT stub for Joseph-the-husband-of-Mary's father, Matthew
  1:16) instead of `"israel"` (the patriarch) — her own per-person file
  already had the correct value, so this was an index/file sync bug, not a
  source-data error. Fixed by copying the correct value into the index.
- **Gideon**'s `genealogy.father` was `"joash-3"` (King Joash of Judah,
  2 Kings 11 — son Ahaziah, reigned centuries after the judges) instead of
  `"joash"` (Joash the Abiezrite of Judges 6:11, whose own `children` field
  already correctly listed Gideon) — a person_id collision on a common
  name, the same category of bug as the `matthat`/`levi` and `sheba`/
  `sheba-4` issues already documented in the Name Disambiguation section.
  Fixed in both the index and `data/people/gideon.json`; this also
  corrected Gideon's page, which had been linking to the wrong Joash.
- **`jair-2`** (Judges 10:3-5, "Jair the Gileadite") was left with no
  `tribe` — it's a separate person_id from `jair` (the Numbers 32:41 /
  1 Chronicles 2:21-22 figure most scholars identify as the same person),
  and Gilead's own multi-tribe territory makes the judge's tribe
  unresolvable from the text alone under this section's rules. Worth
  reconsidering together with a possible `jair`/`jair-2` merge in a future
  genealogy-data cleanup pass, alongside the other open duplicate-id items
  in the Name Disambiguation section.
- **`mordecai`** (Ezra 2:2, a returnee leader listed alongside Zerubbabel)
  carries a `disambiguation` of "father of Esther" that does not match the
  text — Ezra 2:2's Mordecai returned from exile decades before Esther's
  story and Ezra 2:2 never calls him her father. This looks like a
  conflation with `mordecai-2` (Esther's Mordecai, Esther 2:5-22, who
  correctly got the `tribe: Benjamin` assignment here). Not fixed here —
  flagged for the same cleanup pass as the item above; `mordecai` was left
  with no `tribe` rather than assigning one under a muddled identity.

---

## Genealogy / Connections Graph

- Every person (full or stub) participates in the connections/genealogy
  graph — this is the site's core differentiator from existing "Bible
  people" reference sites.
- At ~3,000 people, genealogy edges (parent/child, tribal descent, marriage)
  cannot be curated one-by-one from prose the way Lives of Faith's
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
bottom of every Person Detail page, full or stub (`disambiguation_section()`
in `_build/generate_static_site.py`, icon + blurb + link — **extended
2026-08-11 to cover any tier pairing** (full-full, full-stub, stub-stub),
not just full-tier-to-full-tier as originally built; a stub's card has no
portrait/`source_summary` to draw on, so it shows a "name only" badge and a
reference-based blurb instead, built by `build_people_by_name()` reading
every person's own file rather than only full-tier ones). This section
covers a second, separate mechanism: a short inline qualifier shown next to
a person's *name* wherever it appears, for **any** person (full or stub)
who shares their `name` with another entry in the dataset — not just
full-tier collisions.

**Rules**, applied to whichever have data (never fabricated — see Factual
Accuracy above):
1. Full name / nickname / title, where the dataset already encodes one
   (currently: an `alt_names` entry that extends the base name, e.g. base
   "Judas" + alt_name "Judas Iscariot" → "Iscariot"). Textual epithets like
   "Sons of Thunder" are **not** curated yet — see gap note below.
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

**Another instance found 2026-08-06:** `sheba` and `sheba-4` are both
full-tier entries for the same 2 Samuel 20 rebel against David (the
`adult_story`/`family_friendly_summary` text is essentially the same
episode) — but `sheba`'s `references`/`first_reference` are wrongly set to
`Genesis 10:7`/`1 Chronicles 1:9`, which actually belong to a different,
unrelated Table-of-Nations Sheba (son of Raamah, Genesis 10:7). This wasn't
just a cosmetic disambiguation glitch: it fed a real bug in
`_build/infer_stub_eras.py` (see the Timeline section) that silently
mis-era'd `sheba` as "Primeval History" internally and BFS-propagated that
to his stub son Bichri. The script bug is fixed and no longer trusts a
guessed book default over a full-tier person's own curated `era`, but the
underlying duplicate `sheba`/`sheba-4` entry (and its wrong references) is
still unmerged — another candidate for the cleanup pass above.

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

**Bug found and fixed 2026-08-05:** the index never actually carried
`first_reference` despite the paragraph above saying it does — every
era-precision person's narrative (book/chapter) rank came back `null`, so
left-to-right order within an era band fell back to a broken
`Infinity - Infinity` (`NaN`) sort comparator instead of Scripture's own
order. Visibly, this put Enoch and (Noah's father) Lamech ahead of Cain and
Abel in Primeval History. Separately, 917 index entries were missing
`genealogy` their own person file had (also blocked the parent-anchoring
pass — e.g. Cain's-line Lamech had no `father: methushael` in the index even
though his person file did). Fixed via two new one-time backfill scripts,
`_build/backfill_first_reference.py` and `_build/backfill_genealogy.py`
(both safe to re-run), plus updating `_build/import_bible_data.py` and
`_build/sync_promoted_tiers.py` so newly-created/promoted index entries
keep carrying both fields going forward.

**New rule added the same day:** an era-precision person with no
`first_reference` of their own *and* no ranked parent/spouse to inherit a
position from after the relaxation passes has no textual or genealogical
basis for a left-to-right position — `assignEraOrdinalSpans` in `js/app.js`
now leaves them off the Timeline entirely (explicitly nulling their
start/end) rather than guessing. Only one person in the current dataset
(Raphah — no references, no parent, only a child) is excluded by this rule.

**Bar length and inter-era spacing reworked 2026-08-06.** Two related fixes:

1. Era-precision bar length used to be a fraction of the era band's own
   width (16%). Era bands vary hugely (Primeval History spans ~3800
   notional years vs. Exile's 48), so bars in the widest bands ballooned to
   hundreds of "years" long, implying a duration the ordinal placement never
   claimed. Same problem hit the margin kept clear at each band's edges
   (was 8% of the band's width) — on Primeval History that alone was ~300
   years of empty space per side, which compounded into a large visible gap
   before Patriarchal's bars even started, even though the two bands are
   numerically contiguous. Both are now a fixed number of notional years
   (`TIMELINE_ERA_ORDINAL_LIFESPAN_YEARS` = 50, `TIMELINE_ERA_ORDINAL_MARGIN_YEARS`
   = 20 in `js/app.js`), each capped at a fraction of a narrow band's own
   width so they still fit inside it.
2. Separately, ordinal spacing was spreading *every* era-precision person —
   full-tier and stub alike — evenly across the band, but stub entries are
   hidden by default (the "Show name-only entries" toggle). In eras with
   many stubs (Genesis 10's Table of Nations, Genesis 11's genealogy — ~100
   stub entries in Primeval History alone), the handful of visible full-tier
   people ended up positioned as if all those now-invisible stubs still sat
   between them, producing large visible gaps between visible bars (e.g.
   Nimrod stranded far from Abraham). Fixed by spacing only full-tier
   clusters evenly across the band (the visible "spine"); stub-only clusters
   interpolate between their nearest full-tier neighbors by narrative rank,
   so they slot in sensibly when the toggle is switched on without moving
   the full-tier bars.
3. That alone didn't fully fix Nimrod/Abraham — the existing parent-overlap
   re-anchor pass (see `TIMELINE_PARENT_OVERLAP_START_FRACTION` above) was
   still re-anchoring a full-tier "spine" person onto *any* linked parent
   regardless of tier, and most genealogy links are to a stub (Nimrod's
   father is Cush, a stub). That dragged Nimrod off his correct last-in-era
   spine slot back onto wherever his stub ancestors landed, several thousand
   notional years earlier. Fixed by only re-anchoring a spine cluster onto
   an *also-spine* (full-tier) parent; stub clusters still re-anchor onto
   any parent, full or stub, as before.
4. Investigating this also surfaced a real bug in `_build/infer_stub_eras.py`
   unrelated to `js/app.js`: its BFS seed dict let a low-quality
   book/chapter-guessed era silently overwrite a full-tier person's own
   curated `era` (`dict(known_era); .update(high_conf_era)` had the two
   backwards). The corrupted value was never written back for the full-tier
   person's own index entry (full-tier entries keep their authored `era`
   untouched — see below), so it was invisible on that person's own page,
   but it *was* used to BFS-propagate the wrong era to their stub
   relatives — e.g. Abraham, Sarah, and Lot's internally-computed era
   flipped to "Primeval History" (their first_reference starts in Genesis
   11), corrupting era for any stub whose nearest full-tier anchor was one
   of them. Bichri (2 Samuel 20) was one casualty, reached via a duplicate
   `sheba`/`sheba-4` entry with a wrong `first_reference` — see the Name
   Disambiguation section's data-quality note. Fixed by reversing the
   dict-update order so the curated `known_era` always wins.

**Run order note:** whenever `_build/backfill_lifespan_years.py` and
`_build/infer_stub_eras.py` are both re-run, run `infer_stub_eras.py`
*first* — it rebuilds every stub's `timeline` object from scratch and,
before 2026-08-06, discarded any `lifespan_years` already on it. It now
preserves an existing `lifespan_years` value when rebuilding that object,
but running the lifespan backfill last is still the safer order.

**`timeline.lifespan_years` added 2026-08-06.** Genesis (and a few later
books) states many OT figures' total years lived explicitly — "and all his
days were 969 years, and he died" for Methuselah (Genesis 5:27) is the
best-known, but the same pattern covers all of Genesis 5 and 11, several of
the patriarchs, Moses, Aaron, Joshua, and Eli. Unlike the ordinal
left-right *position* (always an estimate — see above), this is a directly
stated fact, so where present it now sets the *length* of an era-precision
person's bar instead of the generic fixed default — `assignEraOrdinalSpans`
extends their bar forward from their ordinal slot (treated as an
approximate birth point) by their actual `lifespan_years`, uncapped, so
e.g. Methuselah's bar renders roughly 19x longer than someone with no
stated age. Sourced only from an explicit "lived N years" statement in the
text (never inferred or estimated) — currently backfilled for Adam, Seth,
Enosh, Kenan, Mahalalel, Jared, Enoch (age at translation, not death),
Methuselah, Lamech (Noah's father, `lamech-2`), Noah, Shem, Arpachshad,
Shelah, Eber, Peleg, Reu, Serug, Nahor (son of Serug), Terah, Sarah,
Abraham, Ishmael, Isaac, Israel/Jacob, Joseph, Moses, Aaron, Joshua, and
Eli — see `_build/backfill_lifespan_years.py` for the full sourced list and
references. Stored on full-tier people's own `timeline` object in
`data/people/<id>.json`; for stub entries (which carry no curated fields of
their own — see the Coverage section above) it lives only in the index's
synthesized `timeline` object, the same "derived index-only aid" precedent
already established for stub `era`/`genealogy`. Re-run
`_build/backfill_lifespan_years.py` (before `generate_static_site.py`)
whenever this list is extended.

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
- Generated static output is committed locally with its source-data changes.
  `.github/workflows/build.yml` runs the generator on every push to `main` and
  fails if `people/`, `sitemap.xml`, or `people.html` differs afterward. It
  validates only and never commits or pushes. This avoids bot-created remote
  commits while keeping deployment as plain branch-served GitHub Pages.
- Static generation must remain deterministic so a clean checkout regenerates
  byte-for-byte identical output. The pre-renderer uses the first devotional
  entry, while client-side code may rotate entries for visitors. Sitemap output
  omits volatile build-date metadata.
- `robots.txt` explicitly allows `*` plus a belt-and-suspenders explicit
  `Allow: /` for named AI/LLM crawlers, and points to `sitemap.xml`.
- Whenever `data/people.json`, `data/people/*.json`, or `data/connections.json`
  changes, re-run `python3 _build/generate_static_site.py` before committing
  and include all resulting `people/`, `sitemap.xml`, and `people.html` changes
  in the same commit. CI rejects drift from the source JSON.

### Markdown document convention

Every Markdown file must start with a top-level title followed immediately by
a `## Scope` section explaining what the document governs or describes.

---

## Quiz

`data/quiz.json` holds the question bank behind `quiz.html` and the home
page's "Quiz Question" box (`js/app.js`'s `loadQuiz`/`renderQuizPick`/
`buildDefaultQuizSheet`). Each question carries a `difficulty` (1=Easy,
2=Medium, 3=Hard) and a `topic_id` linking back to the person it's about.
The **default** experience — home page box and the quiz builder's initial
max-difficulty filter (`getPreferredQuizDifficulty` defaults to 1) — shows
only difficulty-1 (Easy) questions unless a visitor explicitly raises the
difficulty, so difficulty-1 quality directly shapes most visitors' first
impression of the site.

**Rules for difficulty 1 ("Easy") questions (decided 2026-08-10):**
- **Well-known character only.** An Easy question's `topic_id` must be a
  Bible figure an average visitor — not just a biblically literate one —
  would already recognize by name and story: Abraham, Moses, David, Ruth,
  Peter, Paul, and figures of that same fame tier. Being "major"/full-tier
  or having 3+ real references (the `devotionals`-eligibility bar — see
  [[feedback_devotionals_eligibility]]) is not sufficient on its own —
  that bar still let in many genuinely obscure figures (Barzillai, Ittai
  the Gittite, Tertius, Onesiphorus, Sosthenes, Hymenaeus and Philetus,
  minor kings like Pekahiah/Shallum/Zimri) whose *questions* were easy to
  answer once you already knew the fact, but whose *characters* are not
  well known — that combination doesn't belong in Easy. A person can be
  full-tier and still never have an Easy-difficulty question; that's
  expected, not a gap to fill.
- **8-year-old reading level.** Question and answer text must use short
  sentences and plain, concrete vocabulary — no theological jargon
  (`"discern between good and evil"` → `"know right from wrong"`), no
  Hebrew/Greek terms left unglossed (`Nehushtan`, `seraph`, `El Roi`
  without a plain-English gloss), no clinical/legal words a child
  wouldn't use (`"leprosy"` → `"skin disease"`, `"insurrection"` →
  describe the crowd's choice instead of naming the charge). The same
  phrase should read naturally aloud to an adult and a child, the same
  register already required of `devotionals` phrasing (see
  [[feedback_devotionals_voice]]) — simplifying for age is not an excuse
  to write childishly or lose factual precision, just to avoid words a
  fourth-grader hasn't met yet.
- **Content, not just vocabulary, must fit the audience.** An Easy
  question about a well-known figure can still fail this bar if the
  *fact* itself is adult content the `family_friendly_summary` rules
  (see Coverage and Two-Tier Depth above) would keep out of a child-aimed
  telling — e.g. an original Easy question asked what David did while
  Bathsheba's husband was at war and answered with the affair itself.
  Replace this kind of question with a different Easy-appropriate fact
  about the same well-known person rather than softening the wording of
  the same explicit fact.
- Medium (2) and Hard (3) questions are not held to either rule — that's
  where the site's obscure-figure and harder-fact questions belong, and
  where "well known but hard" questions about famous people (exact verse
  numbers, minor chronology) should live too.
- When adding new quiz questions going forward, apply both rules before
  ever tagging a question `difficulty: 1` — don't add an Easy question
  for a person and rely on a later audit pass to catch it.

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
- **Hitchcock's Bible Names Dictionary** (Roswell D. Hitchcock, 1869, public
  domain) — the primary source for the `name_meaning` field (see the JSON
  Schema section above).
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
