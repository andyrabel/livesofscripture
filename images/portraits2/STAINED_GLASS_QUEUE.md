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

Batches 01-56 are complete and have been removed from this file to keep it
focused on remaining work; the portraits, `image2` references, and commit
history for those batches remain the record of what was done.

**Resorted 2026-08-10, then cleaned up the same day once batches 44-56
finished.** The queue below (batches 57 onward, before the second resort
described next) came from a full re-rank done that day: the 78
spotlight-ineligible people then in the queue (`spotlight_eligible: false`
— of the ~113 people site-wide with that flag, only these 78 were still
in this queue; the rest already have a portrait from batches 01-43 — a
single brief episode with minimal narrative weight, see
`_build/mark_spotlight_eligibility.py`) were moved out to the Paused
section below, and the remaining people were re-ordered by broad
recognizability, New Testament preferred over Old Testament wherever the
two were close enough to call either way. The curated front of that
resort (clearly widely-known figures — Judas Iscariot, Pontius Pilate,
Judah, Herod, Lazarus of Bethany, Ruth and Boaz, and similar) has since
been completed and removed above as batches 44-56; the remainder falls
back to a reproducible heuristic (reference count + distinct-book spread
+ total verse span) — an editorial estimate, not a claim of exact fame
ordering, consistent with this document's framing above.

**Bumped again 2026-08-10 for the "New Testament Church group photo" prototype**
(see the person-page "New Testament Church" section and
`data/nt_churches.json`). Andrew wants a composite image tiling every
member's stained-glass portrait on each church's detail page, so any
full-tier church member still missing a portrait was moved to the very
front of the queue regardless of where the broad-recognizability resort
above had placed them — batches 57-67 below. Order within the bump is by
first appearance walking `data/nt_churches.json` in file order (church by
church, member by member), not a fame re-estimate. This pulled 12 people
out of the Paused — spotlight-ineligible section too (Prochorus, Parmenas,
Judas [`judas-5`], Eunice, Lois, Dionysius, Forunatus, Achaicus, Archippus,
Epanetus, Persis, Antipas) — their `spotlight_eligible: false` status is
unchanged and still governs the home spotlight/FB-IG selection, it just no
longer blocks them from getting a portrait, since a group photo needs
every member regardless of spotlight eligibility. Two more full-tier
church members (`erastus` — the Ephesus/Acts 19:22 Erastus, distinct from
`erastus-2` — and `mary-5`) are still not queued at all and were *not*
added here: neither has a `devotionals` entry, which is this queue's own
base eligibility rule, so adding them would require a separate decision
about `devotionals` eligibility, not just a reordering. Batches 68 onward
are the untouched remainder of the prior resort, renumbered contiguously
after the bump (no other reordering).

- [x] **57** — `prochorus` (Prochorus); `nicanor` (Nicanor); `parmenas` (Parmenas); `nicolas` (Nicolas)
- [x] **58** — `mary-4` (Mary); `rhoda` (Rhoda); `judas-5` (Judas); `manaen` (Manaen)
- [x] **59** — `eunice` (Eunice); `lois` (Lois); `lydia` (Lydia); `epaphroditus` (Epaphroditus)
- [x] **60** — `euodia` (Euodia); `demas` (Demas); `jason` (Jason); `aristarchus` (Aristarchus)
- [x] **61** — `dionysius` (Dionysius); `damaris` (Damaris); `crispus` (Crispus); `sosthenes` (Sosthenes)
- [x] **62** — `gaius` (Gaius); `erastus-2` (Erastus); `forunatus` (Forunatus); `achaicus` (Achaicus)
- [x] **63** — `chloe` (Chloe); `tertius` (Tertius); `phoebe` (Phoebe); `tychicus` (Tychicus)
- [x] **64** — `trophimus` (Trophimus); `onesiphorus` (Onesiphorus); `hymenaeus` (Hymenaeus); `philetus` (Philetus)
- [x] **65** — `archippus` (Archippus); `nympha` (Nympha); `epanetus` (Epanetus); `andronicus` (Andronicus)
- [x] **66** — `junias` (Junia); `persis` (Persis); `rufus` (Rufus); `antipas` (Antipas)
- [x] **67** — `tabitha` (Tabitha); `simon-6` (Simon)
- [x] **68** — `jotham-2` (Jotham); `jehoram` (Jehoram); `ithamar` (Ithamar); `machir` (Machir)
- [x] **69** — `nahshon` (Nahshon); `jeduthun` (Jeduthun); `philip` (Philip); `pharaoh-2` (Pharaoh)
- [x] **70** — `pharaoh-7` (Pharaoh); `kish` (Kish); `rebekah` (Rebekah); `asaph-2` (Asaph)
- [x] **71** — `hazael` (Hazael); `joash-3` (Joash); `ben-hadad` (Ben-hadad); `shem` (Shem)
- [x] **72** — `hur` (Hur); `shimeah` (Shimeah); `heman-2` (Heman); `judas` (Judas)
- [x] **73** — `joram-2` (Joram); `ham` (Ham); `joash-4` (Joash); `amasa` (Amasa)
- [x] **74** — `jeroboam-2` (Jeroboam); `abihu` (Abihu); `shishak` (Shishak); `shalmaneser` (Shalmaneser)
- [x] **75** — `canaan` (Canaan); `japheth` (Japheth); `hadadezer` (Hadadezer); `jabin` (Jabin)
- [x] **76** — `shelah-2` (Shelah); `asahel` (Asahel); `pharaoh-neco` (Pharaoh Neco); `jehoahaz-2` (Jehoahaz)
- [x] **77** — `nahash` (Nahash); `elzaphan` (Elzaphan); `jair` (Jair); `pharaoh-3` (Pharaoh)
- [x] **78** — `dathan` (Dathan); `johanan` (Johanan); `eliab-3` (Eliab); `rezin` (Rezin)
- [x] **79** — `onan` (Onan); `er` (Er); `abinadab-2` (Abinadab); `sibbecai` (Sibbecai)
- [x] **80** — `judas-3` (Judas); `obed-edom-2` (Obed-edom); `jehoahaz` (Jehoahaz); `rabshakeh` (Rabshakeh)
- [x] **81** — `hoglah` (Hoglah); `joshua-4` (Joshua); `mahlah` (Mahlah); `milcah-2` (Milcah)
- [x] **82** — `noah-2` (Noah); `tirzah` (Tirzah); `meremoth` (Meremoth); `hoshea` (Hoshea)
- [x] **83** — `maacah-3` (Maacah); `hanani` (Hanani); `eliphaz-2` (Eliphaz); `bildad` (Bildad)
- [x] **84** — `ethan` (Ethan); `abinadab` (Abinadab); `elhanan` (Elhanan); `tola` (Tola)
- [x] **85** — `obadiah-5` (Obadiah); `seraiah-2` (Seraiah); `bethuel` (Bethuel); `elkanah-2` (Elkanah)
- [x] **86** — `tobiah` (Tobiah); `ishmael-2` (Ishmael); `anah` (Anah); `phinehas-2` (Phinehas)
- [x] **87** — `elnathan` (Elnathan); `jonathan-3` (Jonathan); `ephron` (Ephron); `jehu` (Jehu)
- [x] **88** — `amasai` (Amasai); `shemaiah` (Shemaiah); `elihu-5` (Elihu); `joel` (Joel)
- [x] **89** — `obed-edom` (Obed-edom); `oholiab` (Oholiab); `zophar` (Zophar); `abinadab-3` (Abinadab)
- [x] **90** — `jashobeam` (Jashobeam); `jezaniah` (Jezaniah); `jonathan-4` (Jonathan); `oreb` (Oreb)
- [x] **91** — `alexander-4` (Alexander the Coppersmith); `claudius` (Claudius); `micaiah` (Micaiah); `joash` (Joash)
- [x] **92** — `joah` (Joah); `adoni-zedek` (Adoni-zedek); `naaman-2` (Naaman); `zedekiah` (Zedekiah)
- [x] **93** — `shaphan` (Shaphan); `naboth` (Naboth); `ben-hadad-2` (Ben-hadad); `jonadab-2` (Jonadab)
- [x] **94** — `jeshua-7` (Jeshua); `hophni` (Hophni); `berodach-baladan` (Berodach-baladan); `elihu` (Elihu)
- [x] **95** — `hanun` (Hanun); `achsah` (Achsah); `joel-6` (Joel); `abijah` (Abijah)
- [x] **96** — `amaziah-3` (Amaziah); `obed` (Obed); `shobach` (Shobach); `evil-merodach` (Evil-merodach)
- [x] **97** — `asaiah` (Asaiah); `ahio` (Ahio); `hanani-4` (Hanani); `iddo-4` (Iddo)
- [ ] **98** — `jeriah` (Jeriah); `amariah-2` (Amariah); `azariah-14` (Azariah); `joash-2` (Joash)
- [ ] **99** — `sharezer` (Sharezer); `sheba` (Sheba); `sheshai` (Sheshai); `zacharias` (Zacharias)
- [ ] **100** — `lysias` (Lysias); `bernice` (Bernice); `agabus` (Agabus); `ananias-3` (Ananias)
- [ ] **101** — `joanna` (Joanna); `salome` (Salome); `eliezer` (Eliezer of Damascus); `deborah-2` (Deborah)
- [ ] **102** — `eliashib-7` (Eliashib); `micah` (Micah); `hoham` (Hoham); `manoah` (Manoah)
- [ ] **103** — `debir` (Debir); `japhia` (Japhia); `piram` (Piram); `potiphar` (Potiphar)
- [ ] **104** — `abishag` (Abishag); `hananiah-10` (Hananiah); `gemariah` (Gemariah); `phicol` (Phicol)
- [ ] **105** — `ittai` (Ittai the Gittite); `shemaiah-21` (Shemaiah); `oded` (Oded); `nadab-2` (Nadab)
- [ ] **106** — `ebed-melech` (Ebed-melech); `sheshbazzar` (Sheshbazzar); `mahlon` (Mahlon); `rizpah` (Rizpah)
- [ ] **107** — `ethan-3` (Ethan); `conaniah` (Conaniah); `machir-2` (Machir); `harbona` (Harbona)
- [ ] **108** — `ichabod` (Ichabod); `shamgar` (Shamgar); `shelemiah-6` (Shelemiah); `demetrius` (Demetrius)
- [ ] **109** — `simeon-2` (Simeon); `gaius-3` (Gaius); `gallio` (Gallio); `joseph-10` (Joseph called Barsabbas)
- [ ] **110** — `publius` (Publius); `bar-jesus` (Bar-Jesus); `julius` (Julius); `aeneas` (Aeneas)
- [ ] **111** — `jambres` (Jambres); `alexander-3` (Alexander); `archelaus` (Archelaus); `cleopas` (Cleopas)
- [ ] **112** — `demetrius-2` (Demetrius); `diotrephes` (Diotrephes); `hermogenes` (Hermogenes); `jezebel-2` (Jezebel)
- [ ] **113** — `judas-of-galilee` (Judas of Galilee); `malchus` (Malchus); `sergius-paulus` (Sergius Paulus); `hiram-2` (Hiram)
- [ ] **114** — `agag-2` (Agag); `mesha` (Mesha); `sheba-4` (Sheba); `bera` (Bera)
- [ ] **115** — `hirah` (Hirah); `chedorlaomer` (Chedorlaomer); `gaal` (Gaal); `delaiah-5` (Delaiah)
- [ ] **116** — `obadiah` (Obadiah); `hegai` (Hegai); `pelatiah-4` (Pelatiah); `aner` (Aner)
- [ ] **117** — `arioch-2` (Arioch); `eshcol` (Eshcol); `hadad-4` (Hadad); `zimri-2` (Zimri)
- [ ] **118** — `nergal-sar-ezer-2` (Nergal-sar-ezer); `orpah` (Orpah); `elishama-6` (Elishama); `jehudi` (Jehudi)
- [ ] **119** — `azariah-7` (Azariah); `memucan` (Memucan); `puah` (Puah); `sherebiah` (Sherebiah)
- [ ] **120** — `shiphrah` (Shiphrah); `eglon` (Eglon); `hathach` (Hathach); `pashhur-2` (Pashhur)
- [ ] **121** — `pharaoh` (Pharaoh); `heldai-2` (Heldai); `jedaiah-6` (Jedaiah); `pekahiah` (Pekahiah)
- [ ] **122** — `chimham` (Chimham); `lemuel` (Lemuel); `cushan-rishathaim` (Cushan-rishathaim); `eliel-7` (Eliel)
- [ ] **123** — `elimelech` (Elimelech); `lo-ruhamah` (Lo-ruhamah); `amminadab-2` (Amminadab); `eldad` (Eldad)
- [ ] **124** — `purah` (Purah); `abijah-2` (Abijah); `abiram-2` (Abiram); `agur` (Agur)
- [ ] **125** — `amasa-2` (Amasa); `ammiel` (Ammiel); `armoni` (Armoni); `asaph-4` (Asaph)
- [ ] **126** — `ashpenaz` (Ashpenaz); `azariah-10` (Azariah); `azariah-11` (Azariah); `azariah-16` (Azariah)
- [ ] **127** — `azaryahu` (Azaryahu); `baalis` (Baalis); `baruch` (Baruch); `berechiah-4` (Berechiah)
- [ ] **128** — `elasah-2` (Elasah); `eleazar-2` (Eleazar); `elishaphat` (Elishaphat); `ezer-4` (Ezer)
- [ ] **129** — `gaddi` (Gaddi); `gaddiel` (Gaddiel); `gedaliah-4` (Gedaliah); `geuel` (Geuel)
- [ ] **130** — `gomer-2` (Gomer); `hashabneiah-2` (Hashabneiah); `hiel` (Hiel); `hobab` (Hobab)
- [ ] **131** — `igal` (Igal); `jaazaniah` (Jaazaniah); `jaazaniah-2` (Jaazaniah); `jahaziel-3` (Jahaziel)
- [ ] **132** — `jehikhiah` (Jehikhiah); `jemimah` (Jemimah); `jerahmeel-3` (Jerahmeel); `joah-4` (Joah)
- [ ] **133** — `jonathan-2` (Jonathan); `keren-happuch` (Keren-happuch); `keziah` (Keziah); `lo-ammi` (Lo-ammi)
- [ ] **134** — `maaseiah-4` (Maaseiah); `mephibosheth-2` (Mephibosheth); `nebushazban` (Nebushazban); `nethaniah-3` (Nethaniah)
- [ ] **135** — `noadiah` (Noadiah); `noadiah-2` (Noadiah); `obadiah-6` (Obadiah); `on` (On)
- [ ] **136** — `regemmelech` (Regemmelech); `shammah-2` (Shammah); `sharezer-2` (Sharezer); `shear-jashub` (Shear-jashub)
- [ ] **137** — `shecaniah-5` (Shecaniah); `shemaiah-18` (Shemaiah); `shephatiah-8` (Shephatiah); `shobi` (Shobi)

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

People who share `spotlight_eligible: false` and were also full-tier
members of an NT/New Testament church had that status leave them stuck
here until the 2026-08-10 bump above pulled them into the numbered queue
(Prochorus, Parmenas, `judas-5`, Eunice, Lois, Dionysius, Forunatus,
Achaicus, Archippus, Epanetus, Persis, Antipas — see that note). The list
below is what's left after that pull.

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
