# Stained-glass portrait queue

## Scope

This document tracks ordered batches of devotional portraits to generate and
the completion requirements for each batch.

Canonical fame-first queue for people who have `devotionals` but have no
stained-glass portrait yet. Eligibility was checked against the individual
person JSON, `data/people.json`, and existing files in `images/portraits2`.

**Full-tier only (confirmed 2026-08-10).** `devotionals` is already a
full-tier-only field per the site's `CLAUDE.md` (Coverage and Two-Tier
Depth section), so `tier: "stub"` people should never qualify for this
queue in the first place — a full sweep on 2026-08-10 confirmed zero stub
entries were present in either the numbered queue or the Paused section
below. Still, verify `tier: "full"` on each person's own JSON before
generating a portrait for them (see the orchestration prompt at the bottom
of this file) rather than trusting queue membership alone, in case a
person's tier ever changes after they're queued. A stub is never a
candidate for a *new* generated portrait, even one with unusually strong
narrative-adjacent heuristics (reference count, book spread, verse span) —
those heuristics rank fame, not eligibility.

Use the `person_id` in backticks for filenames and data updates. Check a batch
only after all portraits have been accepted, saved, referenced by `image2` in
both data locations, and validated by rebuilding the site. If a person becomes
ineligible before their turn, strike them out and note why rather than silently
renumbering the queue.

The order is an editorial estimate of broad biblical and cultural recognition;
it is intentionally stable rather than pretending fame has an exact metric.

## Queue

Completed batches are removed from this file to keep it focused on
remaining work; the portraits, `image2` references, and commit history
remain the record of what was done. Remaining people are ordered by a
reproducible heuristic (reference count + distinct-book spread + total
verse span) — an editorial estimate, not a claim of exact fame ordering,
consistent with this document's framing above.

`erastus` (the Ephesus/Acts 19:22 Erastus, distinct from `erastus-2`) and
`mary-5` are queued at the front below as an exception to this queue's
normal `devotionals`-based eligibility rule — both are full-tier but have
no `devotionals` entry. They are queued for a portrait only, because both
are needed for their church's group photo (Ephesus and Rome respectively);
do not add `devotionals` or any other full-tier content for them as part
of completing this batch — they otherwise stay exactly as they are.

Each New Testament Church's group photo (see the person-page "New
Testament Church" section and `data/nt_churches.json`) is a single, newly
generated stained-glass image showing the members standing together side
by side in one continuous scene, the way a real group photograph is
composed, even though the resulting image obviously contains multiple
people. Every member appears as their own recognizable figure with a
small, restrained, Scripture-grounded identifying prop drawn from their
own JSON (same no-invented-detail rule as the individual series), sharing
one unified window rather than being assembled from separately-generated
portrait files. This is separate from the individual-portrait queue above
— those single-person portraits are still needed for each person's own
page regardless. See "Prompt for New Testament Church group photos" below
for the generation instructions; no group photo has been generated yet.

- [x] **110** — `erastus` (Erastus); `mary-5` (Mary)
- [x] **111** — `publius` (Publius); `bar-jesus` (Bar-Jesus); `julius` (Julius); `aeneas` (Aeneas)
- [x] **112** — `jambres` (Jambres); `alexander-3` (Alexander); `archelaus` (Archelaus); `cleopas` (Cleopas)
- [x] **113** — `demetrius-2` (Demetrius); `diotrephes` (Diotrephes); `hermogenes` (Hermogenes); `jezebel-2` (Jezebel)
- [x] **114** — `judas-of-galilee` (Judas of Galilee); `malchus` (Malchus); `sergius-paulus` (Sergius Paulus); `hiram-2` (Hiram)
- [x] **115** — `agag-2` (Agag); `mesha` (Mesha); `sheba-4` (Sheba); `bera` (Bera)
- [x] **116** — `hirah` (Hirah); `chedorlaomer` (Chedorlaomer); `gaal` (Gaal); `delaiah-5` (Delaiah)
- [x] **117** — `obadiah` (Obadiah); `hegai` (Hegai); `pelatiah-4` (Pelatiah); `aner` (Aner)
- [x] **118** — `arioch-2` (Arioch); `eshcol` (Eshcol); `hadad-4` (Hadad); `zimri-2` (Zimri)
- [x] **119** — `nergal-sar-ezer-2` (Nergal-sar-ezer); `orpah` (Orpah); `elishama-6` (Elishama); `jehudi` (Jehudi)
- [x] **120** — `azariah-7` (Azariah); `memucan` (Memucan); `puah` (Puah); `sherebiah` (Sherebiah)
- [x] **121** — `shiphrah` (Shiphrah); `eglon` (Eglon); `hathach` (Hathach); `pashhur-2` (Pashhur)
- [x] **122** — `pharaoh` (Pharaoh); `heldai-2` (Heldai); `jedaiah-6` (Jedaiah); `pekahiah` (Pekahiah)
- [x] **123** — `chimham` (Chimham); `lemuel` (Lemuel); `cushan-rishathaim` (Cushan-rishathaim); `eliel-7` (Eliel)
- [x] **124** — `elimelech` (Elimelech); `lo-ruhamah` (Lo-ruhamah); `amminadab-2` (Amminadab); `eldad` (Eldad)
- [x] **125** — `purah` (Purah); `abijah-2` (Abijah); `abiram-2` (Abiram); `agur` (Agur)
- [x] **126** — `amasa-2` (Amasa); `ammiel` (Ammiel); `armoni` (Armoni); `asaph-4` (Asaph)
- [x] **127** — `ashpenaz` (Ashpenaz); `azariah-10` (Azariah); `azariah-11` (Azariah); `azariah-16` (Azariah)
- [x] **128** — `azaryahu` (Azaryahu); `baalis` (Baalis); `baruch` (Baruch); `berechiah-4` (Berechiah)
- [x] **129** — `elasah-2` (Elasah); `eleazar-2` (Eleazar); `elishaphat` (Elishaphat); `ezer-4` (Ezer)
- [x] **130** — `gaddi` (Gaddi); `gaddiel` (Gaddiel); `gedaliah-4` (Gedaliah); `geuel` (Geuel)
- [x] **131** — `gomer-2` (Gomer); `hashabneiah-2` (Hashabneiah); `hiel` (Hiel); `hobab` (Hobab)
- [x] **132** — `igal` (Igal); `jaazaniah` (Jaazaniah); `jaazaniah-2` (Jaazaniah); `jahaziel-3` (Jahaziel)
- [x] **133** — `jehikhiah` (Jehikhiah); `jemimah` (Jemimah); `jerahmeel-3` (Jerahmeel); `joah-4` (Joah)
- [x] **134** — `jonathan-2` (Jonathan); `keren-happuch` (Keren-happuch); `keziah` (Keziah); `lo-ammi` (Lo-ammi)
- [x] **135** — `maaseiah-4` (Maaseiah); `mephibosheth-2` (Mephibosheth); `nebushazban` (Nebushazban); `nethaniah-3` (Nethaniah)
- [x] **136** — `noadiah` (Noadiah); `noadiah-2` (Noadiah); `obadiah-6` (Obadiah); `on` (On)
- [x] **137** — `regemmelech` (Regemmelech); `shammah-2` (Shammah); `sharezer-2` (Sharezer); `shear-jashub` (Shear-jashub)
- [x] **138** — `shecaniah-5` (Shecaniah); `shemaiah-18` (Shemaiah); `shephatiah-8` (Shephatiah); `shobi` (Shobi)

## Paused — spotlight-ineligible

People who were in the queue above but carry `spotlight_eligible: false` in
`data/people.json` / their person JSON (all "a single brief episode with
minimal narrative weight" per `_build/mark_spotlight_eligibility.py` —
none of this queue's paused people are non-narrated or list-only, the
script's other two exclusion reasons). They still have `devotionals` and are
real full-tier entries, so a stained-glass portrait is still legitimate for
their own person page — they are just excluded from the home spotlight and
FB/IG daily post, which is what drove this queue's priority order. Not
batch-numbered since they are not next in line; move a person back into the
numbered queue above (in roughly the right fame position, not necessarily at
the end) if `spotlight_eligible` is ever revisited for them.

- `adoni-bezek` (Adoni-bezek); `adrammelech` (Adrammelech); `ahab-2` (Ahab); `ahiman` (Ahiman); `amasiah` (Amasiah); `azariah-8` (Azariah)
- `baanah` (Baanah); `bidkar` (Bidkar); `bigthan` (Bigthan); `chenaniah` (Chenaniah); `chilion` (Chilion); `deborah` (Deborah)
- `drusilla` (Drusilla); `elah-2` (Elah); `eleazar-3` (Eleazar); `eliezer-6` (Eliezer); `elon` (Elon); `elon-3` (Elon)
- `geshem` (Geshem); `hanamel` (Hanamel); `ibzan` (Ibzan); `iddo-6` (Iddo); `irijah` (Irijah); `ishbi-benob` (Ishbi-benob)
- `jaazaniah-3` (Jaazaniah); `jair-2` (Jair); `jannes` (Jannes); `jarib` (Jarib); `jehiel-3` (Jehiel); `jehosheba` (Jehosheba)
- `jehucal` (Jehucal); `jether` (Jether); `jezrahiah` (Jezrahiah); `jezreel-2` (Jezreel); `joah-2` (Joah); `joram` (Joram)
- `jozacar` (Jozacar); `jucal` (Jucal); `lamech` (Lamech); `mamre` (Mamre); `mattan` (Mattan); `medad` (Medad)
- `micaiah-6` (Micaiah); `michael-7` (Michael); `mishael` (Mishael); `mithredath` (Mithredath); `mnason` (Mnason); `nethanel-6` (Nethanel)
- `nobah` (Nobah); `palti-2` (Palti); `peninnah` (Peninnah); `phygelus` (Phygelus); `rechab` (Rechab); `rehum-2` (Rehum)
- `rezon` (Rezon); `saph` (Saph); `sargon` (Sargon); `segub` (Segub); `sephatiah` (Sephatiah); `seraiah-10` (Seraiah)
- `seraiah-9` (Seraiah); `shabbethai` (Shabbethai); `shallum` (Shallum); `shemeber` (Shemeber); `shethar-bozenai` (Shethar-bozenai); `shimshai` (Shimshai)

## Prompt for each batch

Start a fresh Codex thread for each batch and paste this short orchestration
prompt. The image prompt itself remains the same every time because it lives in
`STAINED_GLASS_PROMPT.md`; Codex replaces only the three documented values for
each person.

```text
Create the next unchecked batch in
images/portraits2/STAINED_GLASS_QUEUE.md.

Before generating, check each person's own JSON file in data/people/. If
anyone in the batch has "tier": "stub" (not "full"), stop and flag it rather
than generating a portrait for them — stub entries never get a generated
stained-glass portrait, regardless of queue membership or heuristic ranking.

Follow images/portraits2/STAINED_GLASS_PROMPT.md exactly. Generate one distinct
image call per person. Derive restrained, Scripture-grounded symbols and scene
details from that person's JSON; do not invent extra-biblical details. Use the
JSON name as DISPLAY NAME and the person_id as the filename.

For each portrait: inspect the result, save the accepted image to
images/portraits2/<person_id>.png, normalize it to exactly 1024 x 1024, and do
not regenerate it for merely cosmetic differences. Reject and retry only for a
material failure such as wrong or misspelled name text, an extra prominent
person, incorrect biblical symbols, modern objects, or visibly non-stained-glass
rendering.

After all images are accepted, add image2 to the individual person JSON and
data/people.json, rebuild and run the relevant validation, then check off only
that batch in the queue. Preserve unrelated working-tree changes. Report saved
paths, prompts used, validation results, and any retries.
```

## Prompt for New Testament Church group photos

Separate from the individual-portrait batches above. One group photo per
New Testament Church with **2 or more** full-tier members (a single-member
church has nothing to group — its one member's individual portrait already
serves that purpose). Not queue-numbered like the individual batches since
there are only a handful of churches (see `data/nt_churches.json`); work
through them in file order and note completions directly in this section
once any are generated.

This produces one **merged, single-generation** stained-glass image per
church — every named member appears together in one continuous scene, side
by side, the way a group photograph is composed. It is **not** a tiled
composite of separately-generated individual portrait files, and does not
depend on any member's individual `images/portraits2/<person_id>.png`
already existing.

**Do not start generating any group photo until the individual-portrait
queue above is fully cleared** — including `erastus` and `mary-5` at
batch 110. Church group photos come after every full-tier NT church
member has their own individual portrait, not before.

Output, per church:
- **Hi-res master**: 1920 × 1080 (16:9 landscape), PNG, saved to
  `images/nt_churches/<church_id>.png`.
- **Web-optimized copy**: 1200 × 675 (same 16:9 ratio, scaled down), saved
  to `images/nt_churches/<church_id>-web.jpg`, compressed for fast page
  load. This is the size suitable for direct Facebook photo posting
  (landscape display ratio Facebook renders natively in-feed, well under
  its upload size limits) — follow the existing overlay/branding
  conventions already used for the daily social-post images where
  applicable (white background if the source has transparency, logo mark
  placement) per the FB/IG poster pipeline's established format.

Prompt template — adapt per church, following the same fielded structure as
`STAINED_GLASS_PROMPT.md`'s single-portrait prompt for visual family
resemblance, but landscape and multi-figure:

```text
Use case: historical-scene, multi-figure group
Asset type: 1920 × 1080 (16:9) landscape "group photo" website image
Primary request: Create a convincingly authentic late-19th-century or early-20th-century Victorian Gothic Revival church stained-glass window depicting the members of the church at [CHURCH NAME] standing together in one group, the way a group photograph is composed.
Subject and figures: [MEMBER LIST — each person's DISPLAY NAME], standing shoulder to shoulder in a single row (or, for larger rosters, two gently staggered rows so every face stays visible), all facing outward toward the viewer as in a group photograph, each individually recognizable with historically appropriate ancient Near Eastern clothing, appearance, hair, and accessories. [PER-PERSON SYMBOLS — one small, restrained, Scripture-grounded identifying prop or detail per person, derived only from that person's own JSON; do not invent extra-biblical detail.] No figure cropped, turned away, or rendered smaller/less prominent than the others — every named member shares equal visual weight. No unnamed extra figures.
Style/medium: A real handcrafted stained-glass window photographed installed in an old church, not a digital painting or a stained-glass filter. Construct the entire scene from individually shaped pieces of colored glass separated by prominent dark lead came lines. Include irregular glass shapes, subtle variations in glass thickness and translucency, tiny imperfections, fine painted details on each serious, dignified, expressive face and hands, and realistic light glowing through the glass.
Framing: One continuous wide arch or rectangular window frame spanning the full 16:9 canvas — not a grid of separate tiled panes, not individual arches per person, no internal borders or seams splitting the group into separate windows. A single shared architectural frame with decorative floral and geometric border pieces around all four edges, matching the individual-portrait series' framing language.
Palette: Rich traditional ecclesiastical colors—deep cobalt and sapphire blue, ruby and burgundy red, amber, antique gold, cream, muted green, brown, and occasional turquoise—luminous but slightly aged, never neon.
Text (verbatim): "THE CHURCH AT [CHURCH NAME]" as a title banner, with [PRIMARY REFERENCE, e.g. "ACTS 19"] in smaller lettering beneath it.
Text placement: Bottom-center, an elegant antique cream-colored stained-glass name panel framed in gold and dark lead, sized to fit the wider canvas. Write only the church title and reference in large, clear, traditional black serif capitals.
Constraints: exact 16:9 landscape composition; every named member present, distinguishable, and individually recognizable; strong black leading; intricate handcrafted glasswork; realistic transmitted light; elaborate Victorian and Gothic Revival craftsmanship; dignified biblical realism; historically evocative.
Avoid: tiling or grid seams, any figure rendered as a separate framed inset "portrait chip," any other text, misspelling, missing or extra names in the banner, modern illustration, cartoon style, anime, glossy 3D rendering, photorealistic human photography, smooth digital gradients, plastic-looking glass, modern clothing, modern objects, excessive halos unless traditionally appropriate, illegible lettering, or watermark.
```

Generation mode: same tool used for the individual series (Codex built-in
image generation, or the OpenAI Images API directly via the environment's
`OPENAI_API_KEY` — see [[task_nt_church_group_photo]] for the direct-API
path already tested), one call per church.

Notes:
- **Large rosters are a real generation risk**, not just a layout
  preference — Ephesus has 11 full-tier members and Rome's roster runs far
  larger. Treat the first attempt at any church with more than ~6-8
  members as a trial: if members toward the back/edges lose individual
  distinctiveness or the model drops a name, that's a material failure
  worth a retry with a more explicit per-person layout instruction (e.g.
  naming row/position), not a cosmetic one — don't accept a group photo
  where a named member is missing or unrecognizable.
- **Rome is an open question, not yet decided — do not generate Rome's
  group photo until this is resolved.** Rome has 31 members but only 9 are
  full-tier; the other 22 are `tier: "stub"` (bare names from Paul's
  Romans 16 greetings, several with no distinguishing detail at all —
  e.g. "Asyncritus, Phlegon, Hermes, Patrobas, Hermas"), and stubs never
  get a generated portrait under this queue's own eligibility rule, so a
  literal all-31-members photo isn't achievable as things stand. Ask
  Andrew how he wants Rome handled (full-tier-only subset, exclude Rome
  entirely, or some other approach) before touching it — every other
  church's roster is small enough that this doesn't apply.
- No requirement that a member's likeness in the group photo match their
  existing individual `images/portraits2/<person_id>.png`, if one exists —
  this is a separate generation, and the project's images have never
  claimed likeness accuracy in the first place (see CLAUDE.md's Images
  section). Same overall stained-glass style family is sufficient.
- Once a church's group photo is accepted, this is still a prototype
  feature (per [[task_nt_church_group_photo]]) — do not wire `image2`-style
  fields into `data/nt_churches.json` or the site generator until Andrew
  reviews the actual output and confirms the feature should go live.
