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
generated stained-glass image showing a representative congregation together
in one continuous scene, the way a real group photograph is composed. At least
the five best-known full-tier people, when that many are available (and more
when the composition comfortably supports them), should be recognizable from
their existing stained-glass portraits and discreetly identified by name. Additional unnamed
figures fill out a believable congregation without claiming that Scripture
names them individually. Identifying props are optional rather than required.
The group shares one unified window rather than being assembled from
separately generated portrait files. This is separate from the
individual-portrait queue above — those single-person portraits are still
needed for each person's own page regardless. See "Prompt for New Testament
Church group photos" below for the generation instructions; no group photo has
been generated yet.

**Individual-portrait queue complete as of 2026-08-20.** Batches 110-138
(110 people) were the last remaining fame-ranked entries and all have been
generated, saved to `images/portraits2/`, referenced via `image2` in both
the person's own JSON and `data/people.json`, and validated by rebuilding
the site. Completed batches are removed from this file per the convention
above; the portraits, `image2` references, and commit history are the
record of what was done. Nothing remains in the numbered queue — the next
new full-tier person with `devotionals` and no portrait would start a new
batch 139.

The Paused section below is **not** part of this completion — those people
were deliberately held back (spotlight-ineligible) rather than generated,
and still need portraits if reactivated.

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

Separate from the individual-portrait batches above. One representative group
photo per New Testament Church, including churches with few or no named
full-tier members: unnamed congregants may establish a reasonable group size.
Not queue-numbered like the individual batches since there are only a handful
of churches (see `data/nt_churches.json`); work through them in file order and
note completions directly in this section once any are generated.

This produces one **merged, single-generation** stained-glass image per church:
a representative selection of named people and additional unnamed congregants
appear together in one continuous scene, the way a group photograph is
composed. It is **not** a tiled composite of separately-generated individual
portrait files. Existing `images/portraits2/<person_id>.png` portraits should
be supplied as visual references for the selected named people so their face,
hair, clothing colors, and overall visual identity remain recognizably
consistent with the individual portrait series.

**Gating condition met as of 2026-08-20:** the individual-portrait queue
above (including `erastus` and `mary-5`, formerly batch 110) is fully
cleared, so church group photos are no longer blocked on that front. Rome
is still an open question (see below) and pending further direction from
Andrew before any group photo generation begins.

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
Primary request: Create a convincingly authentic late-19th-century or early-20th-century Victorian Gothic Revival church stained-glass window depicting a representative congregation from the church in [CHURCH NAME] standing together in one group, the way a group photograph is composed.
Named figures: Feature [SELECTED FULL-TIER MEMBER LIST — normally the five best-known full-tier people, or every available full-tier person when fewer than five are associated with the church]. Use each selected person's existing stained-glass portrait as a visual reference. Preserve the recognizable face, hair, clothing colors, and overall visual identity of that portrait while adapting the person naturally into the shared scene. Give these named figures clear but natural placement in the front or middle of the group; they need not all have equal prominence.
Name labels: Discreetly identify each selected named figure with their display name in small, restrained, legible antique serif lettering placed immediately beneath or beside that person. Treat these as subtle identifiers integrated into the stained glass, not large banners, modern captions, floating UI labels, or separate portrait frames. Do not label the additional congregants.
Additional congregation: Add enough unnamed men and women in historically appropriate first-century clothing to make the gathering feel like a reasonable local church rather than a lineup of only the named figures. Vary ages and appearances naturally. These background congregants are representative, not claims that Scripture names additional individuals. Arrange the whole gathering in one or two gently staggered rows with faces visible and the selected named figures still easy to find.
Props and story details: It is not essential for anyone to carry an object connected with their story. Include a restrained Scripture-grounded identifying prop only when it improves recognition or composition; do not force one per person and do not invent extra-biblical details.
Style/medium: A real handcrafted stained-glass window photographed installed in an old church, not a digital painting or a stained-glass filter. Construct the entire scene from individually shaped pieces of colored glass separated by prominent dark lead came lines. Include irregular glass shapes, subtle variations in glass thickness and translucency, tiny imperfections, fine painted details on each serious, dignified, expressive face and hands, and realistic light glowing through the glass.
Framing: One continuous wide arch or rectangular window frame spanning the full 16:9 canvas — not a grid of separate tiled panes, not individual arches per person, no internal borders or seams splitting the group into separate windows. A single shared architectural frame with decorative floral and geometric border pieces around all four edges, matching the individual-portrait series' framing language.
Palette: Rich traditional ecclesiastical colors—deep cobalt and sapphire blue, ruby and burgundy red, amber, antique gold, cream, muted green, brown, and occasional turquoise—luminous but slightly aged, never neon.
Text (verbatim): "THE CHURCH IN [CHURCH NAME]" as a title banner, with [PRIMARY REFERENCE, e.g. "ACTS 19"] in smaller lettering beneath it.
Text placement: Bottom-center, an elegant antique cream-colored stained-glass nameplate framed in gold and dark lead, sized to fit the wider canvas. Write the church title in large, clear, traditional black serif capitals and the reference in smaller lettering. The discreet individual name labels belong near their figures, not in this main nameplate.
Constraints: exact 16:9 landscape composition; every selected named figure present, distinguishable, recognizably consistent with their supplied portrait, and correctly labeled; a believable larger congregation; strong black leading; intricate handcrafted glasswork; realistic transmitted light; elaborate Victorian and Gothic Revival craftsmanship; dignified biblical realism; historically evocative.
Avoid: tiling or grid seams, any figure rendered as a separate framed inset "portrait chip," labels on unnamed congregants, misspelling, missing selected named figures, incorrect labels, missing or extra names in the main banner, modern illustration, cartoon style, anime, glossy 3D rendering, photorealistic human photography, smooth digital gradients, plastic-looking glass, modern clothing, modern objects, excessive halos unless traditionally appropriate, illegible lettering, or watermark.
```

Generation mode: same tool used for the individual series (Codex built-in
image generation, or the OpenAI Images API directly via the environment's
`OPENAI_API_KEY` — see [[task_nt_church_group_photo]] for the direct-API
path already tested), one call per church.

Notes:
- Select the normally five featured full-tier people by broad biblical and
  cultural recognition, using the same editorial fame judgment as the portrait
  queue. When fewer than five full-tier people are associated with a church,
  feature all available full-tier people and use unnamed congregants for the
  rest of the group. Name-only (`tier: "stub"`) people are not individually
  portrayed or labeled.
- **Large rosters no longer require literal coverage.** For churches such as
  Ephesus and Rome, feature the best-known five full-tier people by default and
  represent the wider congregation with unnamed faces. If the model loses the
  likeness or label of a selected named person, that is a material failure worth
  a retry with explicit row and position assignments.
- For churches with no named full-tier people, create a representative unnamed
  congregation and omit individual name labels. The church nameplate provides
  the identity of the scene.
- Once a church's group photo is accepted, this is still a prototype
  feature (per [[task_nt_church_group_photo]]) — do not wire `image2`-style
  fields into `data/nt_churches.json` or the site generator until Andrew
  reviews the actual output and confirms the feature should go live.
