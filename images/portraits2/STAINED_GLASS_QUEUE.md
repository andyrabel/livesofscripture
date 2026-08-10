# Stained-glass portrait queue

## Scope

This document tracks ordered batches of devotional portraits to generate and
the completion requirements for each batch.

Canonical fame-first queue for people who have `devotionals` but have no
stained-glass portrait yet. Eligibility was checked against the individual
person JSON, `data/people.json`, and existing files in `images/portraits2`.

Use the `person_id` in backticks for filenames and data updates. Check a batch
only after all portraits have been accepted, saved, referenced by `image2` in
both data locations, and validated by rebuilding the site. If a person becomes
ineligible before their turn, strike them out and note why rather than silently
renumbering the queue.

The order is an editorial estimate of broad biblical and cultural recognition;
it is intentionally stable rather than pretending fame has an exact metric.

## Queue

Batches 01-43 are complete and have been removed from this file to keep it
focused on remaining work; the portraits, `image2` references, and commit
history for those batches remain the record of what was done.

**Resorted 2026-08-10.** The previously-recorded batches 44-154 have not been
started (no checkbox below was checked, so no portrait or `image2` reference
exists for anyone in them), so the full remaining queue was re-ranked from
scratch rather than partially renumbered: the 78 spotlight-ineligible people
among them (`spotlight_eligible: false` — of the ~113 people site-wide with
that flag, only these 78 were still in this queue; the rest already have a
portrait from batches 01-43 — a single brief episode with minimal narrative
weight, see `_build/mark_spotlight_eligibility.py`) were moved out to the
Paused section below, and the remaining 362 people were
re-ordered by broad recognizability, New Testament preferred over Old
Testament wherever the two were close enough to call either way. The top of
the list is a hand-curated set of clearly widely-known figures (Judas
Iscariot, Pontius Pilate, Judah, Herod, Lazarus of Bethany, Ruth and Boaz,
and similar); the remainder falls back to the same reproducible heuristic
already used for the original batch-66-onward ranking (reference count +
distinct-book spread + total verse span) — an editorial estimate, not a
claim of exact fame ordering, consistent with this document's existing
framing above. Batch numbering restarts at 44 and is contiguous through the
end of the active queue.

- [x] **44** — `judas-2` (Judas); `pilate` (Pilate); `judah` (Judah); `herod` (Herod)
- [x] **45** — `lazarus-2` (Lazarus); `ruth` (Ruth); `boaz` (Boaz); `delilah` (Delilah)
- [x] **46** — `mordecai` (Mordecai); `cyrus` (Cyrus); `zaccheus` (Zaccheus); `joseph-6` (Joseph)
- [x] **47** — `james` (James); `levi` (Levi); `reuben` (Reuben); `simon-5` (Simon)
- [x] **48** — `luke` (Luke); `herod-3` (Herod); `caesar` (Caesar); `caesar-augustus` (Caesar Augustus)
- [x] **49** — `darius` (Darius); `hannah` (Hannah); `jael` (Jael); `ehud` (Ehud)
- [x] **50** — `philemon` (Philemon); `onesimus` (Onesimus); `lazarus` (Lazarus); `gamaliel-2` (Gamaliel)
- [ ] **51** — `ananias-2` (Ananias); `ananias` (Ananias); `sapphira` (Sapphira); `cornelius` (Cornelius)
- [ ] **52** — `bartimaeus` (Bartimaeus); `felix` (Felix); `festus` (Festus); `agrippa` (Agrippa)
- [ ] **53** — `matthias` (Matthias); `eutychus` (Eutychus); `anna` (Anna); `salome-2` (Salome)
- [ ] **54** — `huldah` (Huldah); `simon-4` (Simon); `caesar-2` (Caesar); `manasseh` (Manasseh)
- [ ] **55** — `pharaoh-4` (Pharaoh); `dan` (Dan); `simeon` (Simeon); `issachar` (Issachar)
- [ ] **56** — `sihon` (Sihon); `og` (Og); `jehoiachin` (Jehoiachin); `perez` (Perez)
- [ ] **57** — `jotham-2` (Jotham); `jehoram` (Jehoram); `ithamar` (Ithamar); `machir` (Machir)
- [ ] **58** — `nahshon` (Nahshon); `jeduthun` (Jeduthun); `philip` (Philip); `pharaoh-2` (Pharaoh)
- [ ] **59** — `pharaoh-7` (Pharaoh); `kish` (Kish); `rebekah` (Rebekah); `asaph-2` (Asaph)
- [ ] **60** — `hazael` (Hazael); `joash-3` (Joash); `ben-hadad` (Ben-hadad); `shem` (Shem)
- [ ] **61** — `hur` (Hur); `shimeah` (Shimeah); `heman-2` (Heman); `tychicus` (Tychicus)
- [ ] **62** — `judas` (Judas); `joram-2` (Joram); `ham` (Ham); `joash-4` (Joash)
- [ ] **63** — `amasa` (Amasa); `jeroboam-2` (Jeroboam); `abihu` (Abihu); `aristarchus` (Aristarchus)
- [ ] **64** — `shishak` (Shishak); `shalmaneser` (Shalmaneser); `canaan` (Canaan); `japheth` (Japheth)
- [ ] **65** — `hadadezer` (Hadadezer); `jabin` (Jabin); `shelah-2` (Shelah); `asahel` (Asahel)
- [ ] **66** — `pharaoh-neco` (Pharaoh Neco); `jehoahaz-2` (Jehoahaz); `nahash` (Nahash); `elzaphan` (Elzaphan)
- [ ] **67** — `jair` (Jair); `pharaoh-3` (Pharaoh); `dathan` (Dathan); `johanan` (Johanan)
- [ ] **68** — `eliab-3` (Eliab); `rezin` (Rezin); `onan` (Onan); `er` (Er)
- [ ] **69** — `abinadab-2` (Abinadab); `sibbecai` (Sibbecai); `demas` (Demas); `gaius` (Gaius)
- [ ] **70** — `judas-3` (Judas); `obed-edom-2` (Obed-edom); `jehoahaz` (Jehoahaz); `rabshakeh` (Rabshakeh)
- [ ] **71** — `hoglah` (Hoglah); `joshua-4` (Joshua); `mahlah` (Mahlah); `milcah-2` (Milcah)
- [ ] **72** — `noah-2` (Noah); `tirzah` (Tirzah); `meremoth` (Meremoth); `hoshea` (Hoshea)
- [ ] **73** — `maacah-3` (Maacah); `hanani` (Hanani); `eliphaz-2` (Eliphaz); `bildad` (Bildad)
- [ ] **74** — `ethan` (Ethan); `abinadab` (Abinadab); `elhanan` (Elhanan); `tola` (Tola)
- [ ] **75** — `obadiah-5` (Obadiah); `seraiah-2` (Seraiah); `trophimus` (Trophimus); `bethuel` (Bethuel)
- [ ] **76** — `elkanah-2` (Elkanah); `tobiah` (Tobiah); `ishmael-2` (Ishmael); `anah` (Anah)
- [ ] **77** — `phinehas-2` (Phinehas); `elnathan` (Elnathan); `jonathan-3` (Jonathan); `ephron` (Ephron)
- [ ] **78** — `jehu` (Jehu); `amasai` (Amasai); `shemaiah` (Shemaiah); `elihu-5` (Elihu)
- [ ] **79** — `joel` (Joel); `obed-edom` (Obed-edom); `oholiab` (Oholiab); `zophar` (Zophar)
- [ ] **80** — `abinadab-3` (Abinadab); `jashobeam` (Jashobeam); `jezaniah` (Jezaniah); `jonathan-4` (Jonathan)
- [ ] **81** — `oreb` (Oreb); `hymenaeus` (Hymenaeus); `jason` (Jason); `alexander-4` (Alexander the Coppersmith)
- [ ] **82** — `claudius` (Claudius); `crispus` (Crispus); `erastus-2` (Erastus); `rufus` (Rufus)
- [ ] **83** — `sosthenes` (Sosthenes); `micaiah` (Micaiah); `joash` (Joash); `joah` (Joah)
- [ ] **84** — `adoni-zedek` (Adoni-zedek); `naaman-2` (Naaman); `zedekiah` (Zedekiah); `shaphan` (Shaphan)
- [ ] **85** — `naboth` (Naboth); `ben-hadad-2` (Ben-hadad); `jonadab-2` (Jonadab); `jeshua-7` (Jeshua)
- [ ] **86** — `hophni` (Hophni); `berodach-baladan` (Berodach-baladan); `elihu` (Elihu); `hanun` (Hanun)
- [ ] **87** — `achsah` (Achsah); `joel-6` (Joel); `abijah` (Abijah); `amaziah-3` (Amaziah)
- [ ] **88** — `obed` (Obed); `shobach` (Shobach); `evil-merodach` (Evil-merodach); `asaiah` (Asaiah)
- [ ] **89** — `ahio` (Ahio); `hanani-4` (Hanani); `iddo-4` (Iddo); `jeriah` (Jeriah)
- [ ] **90** — `amariah-2` (Amariah); `azariah-14` (Azariah); `joash-2` (Joash); `sharezer` (Sharezer)
- [ ] **91** — `sheba` (Sheba); `sheshai` (Sheshai); `zacharias` (Zacharias); `simon-6` (Simon)
- [ ] **92** — `lysias` (Lysias); `bernice` (Bernice); `epaphroditus` (Epaphroditus); `agabus` (Agabus)
- [ ] **93** — `onesiphorus` (Onesiphorus); `ananias-3` (Ananias); `joanna` (Joanna); `salome` (Salome)
- [ ] **94** — `eliezer` (Eliezer of Damascus); `deborah-2` (Deborah); `eliashib-7` (Eliashib); `micah` (Micah)
- [ ] **95** — `hoham` (Hoham); `manoah` (Manoah); `debir` (Debir); `japhia` (Japhia)
- [ ] **96** — `piram` (Piram); `potiphar` (Potiphar); `abishag` (Abishag); `hananiah-10` (Hananiah)
- [ ] **97** — `gemariah` (Gemariah); `phicol` (Phicol); `ittai` (Ittai the Gittite); `shemaiah-21` (Shemaiah)
- [ ] **98** — `oded` (Oded); `nadab-2` (Nadab); `ebed-melech` (Ebed-melech); `sheshbazzar` (Sheshbazzar)
- [ ] **99** — `mahlon` (Mahlon); `rizpah` (Rizpah); `ethan-3` (Ethan); `conaniah` (Conaniah)
- [ ] **100** — `machir-2` (Machir); `harbona` (Harbona); `ichabod` (Ichabod); `shamgar` (Shamgar)
- [ ] **101** — `shelemiah-6` (Shelemiah); `lydia` (Lydia); `demetrius` (Demetrius); `simeon-2` (Simeon)
- [ ] **102** — `gaius-3` (Gaius); `gallio` (Gallio); `mary-4` (Mary); `rhoda` (Rhoda)
- [ ] **103** — `tabitha` (Tabitha); `joseph-10` (Joseph called Barsabbas); `publius` (Publius); `bar-jesus` (Bar-Jesus)
- [ ] **104** — `julius` (Julius); `philetus` (Philetus); `aeneas` (Aeneas); `jambres` (Jambres)
- [ ] **105** — `phoebe` (Phoebe); `alexander-3` (Alexander); `andronicus` (Andronicus); `archelaus` (Archelaus)
- [ ] **106** — `chloe` (Chloe); `cleopas` (Cleopas); `damaris` (Damaris); `demetrius-2` (Demetrius)
- [ ] **107** — `diotrephes` (Diotrephes); `euodia` (Euodia); `hermogenes` (Hermogenes); `jezebel-2` (Jezebel)
- [ ] **108** — `judas-of-galilee` (Judas of Galilee); `junias` (Junia); `malchus` (Malchus); `manaen` (Manaen)
- [ ] **109** — `nicanor` (Nicanor); `nicolas` (Nicolas); `nympha` (Nympha); `sergius-paulus` (Sergius Paulus)
- [ ] **110** — `tertius` (Tertius); `hiram-2` (Hiram); `agag-2` (Agag); `mesha` (Mesha)
- [ ] **111** — `sheba-4` (Sheba); `bera` (Bera); `hirah` (Hirah); `chedorlaomer` (Chedorlaomer)
- [ ] **112** — `gaal` (Gaal); `delaiah-5` (Delaiah); `obadiah` (Obadiah); `hegai` (Hegai)
- [ ] **113** — `pelatiah-4` (Pelatiah); `aner` (Aner); `arioch-2` (Arioch); `eshcol` (Eshcol)
- [ ] **114** — `hadad-4` (Hadad); `zimri-2` (Zimri); `nergal-sar-ezer-2` (Nergal-sar-ezer); `orpah` (Orpah)
- [ ] **115** — `elishama-6` (Elishama); `jehudi` (Jehudi); `azariah-7` (Azariah); `memucan` (Memucan)
- [ ] **116** — `puah` (Puah); `sherebiah` (Sherebiah); `shiphrah` (Shiphrah); `eglon` (Eglon)
- [ ] **117** — `hathach` (Hathach); `pashhur-2` (Pashhur); `pharaoh` (Pharaoh); `heldai-2` (Heldai)
- [ ] **118** — `jedaiah-6` (Jedaiah); `pekahiah` (Pekahiah); `chimham` (Chimham); `lemuel` (Lemuel)
- [ ] **119** — `cushan-rishathaim` (Cushan-rishathaim); `eliel-7` (Eliel); `elimelech` (Elimelech); `lo-ruhamah` (Lo-ruhamah)
- [ ] **120** — `amminadab-2` (Amminadab); `eldad` (Eldad); `purah` (Purah); `abijah-2` (Abijah)
- [ ] **121** — `abiram-2` (Abiram); `agur` (Agur); `amasa-2` (Amasa); `ammiel` (Ammiel)
- [ ] **122** — `armoni` (Armoni); `asaph-4` (Asaph); `ashpenaz` (Ashpenaz); `azariah-10` (Azariah)
- [ ] **123** — `azariah-11` (Azariah); `azariah-16` (Azariah); `azaryahu` (Azaryahu); `baalis` (Baalis)
- [ ] **124** — `baruch` (Baruch); `berechiah-4` (Berechiah); `elasah-2` (Elasah); `eleazar-2` (Eleazar)
- [ ] **125** — `elishaphat` (Elishaphat); `ezer-4` (Ezer); `gaddi` (Gaddi); `gaddiel` (Gaddiel)
- [ ] **126** — `gedaliah-4` (Gedaliah); `geuel` (Geuel); `gomer-2` (Gomer); `hashabneiah-2` (Hashabneiah)
- [ ] **127** — `hiel` (Hiel); `hobab` (Hobab); `igal` (Igal); `jaazaniah` (Jaazaniah)
- [ ] **128** — `jaazaniah-2` (Jaazaniah); `jahaziel-3` (Jahaziel); `jehikhiah` (Jehikhiah); `jemimah` (Jemimah)
- [ ] **129** — `jerahmeel-3` (Jerahmeel); `joah-4` (Joah); `jonathan-2` (Jonathan); `keren-happuch` (Keren-happuch)
- [ ] **130** — `keziah` (Keziah); `lo-ammi` (Lo-ammi); `maaseiah-4` (Maaseiah); `mephibosheth-2` (Mephibosheth)
- [ ] **131** — `nebushazban` (Nebushazban); `nethaniah-3` (Nethaniah); `noadiah` (Noadiah); `noadiah-2` (Noadiah)
- [ ] **132** — `obadiah-6` (Obadiah); `on` (On); `regemmelech` (Regemmelech); `shammah-2` (Shammah)
- [ ] **133** — `sharezer-2` (Sharezer); `shear-jashub` (Shear-jashub); `shecaniah-5` (Shecaniah); `shemaiah-18` (Shemaiah)
- [ ] **134** — `shephatiah-8` (Shephatiah); `shobi` (Shobi)

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

- `achaicus` (Achaicus); `adoni-bezek` (Adoni-bezek); `adrammelech` (Adrammelech); `ahab-2` (Ahab); `ahiman` (Ahiman); `amasiah` (Amasiah)
- `antipas` (Antipas); `archippus` (Archippus); `azariah-8` (Azariah); `baanah` (Baanah); `bidkar` (Bidkar); `bigthan` (Bigthan)
- `chenaniah` (Chenaniah); `chilion` (Chilion); `deborah` (Deborah); `dionysius` (Dionysius); `drusilla` (Drusilla); `elah-2` (Elah)
- `eleazar-3` (Eleazar); `eliezer-6` (Eliezer); `elon` (Elon); `elon-3` (Elon); `epanetus` (Epanetus); `eunice` (Eunice)
- `forunatus` (Forunatus); `geshem` (Geshem); `hanamel` (Hanamel); `ibzan` (Ibzan); `iddo-6` (Iddo); `irijah` (Irijah)
- `ishbi-benob` (Ishbi-benob); `jaazaniah-3` (Jaazaniah); `jair-2` (Jair); `jannes` (Jannes); `jarib` (Jarib); `jehiel-3` (Jehiel)
- `jehosheba` (Jehosheba); `jehucal` (Jehucal); `jether` (Jether); `jezrahiah` (Jezrahiah); `jezreel-2` (Jezreel); `joah-2` (Joah)
- `joram` (Joram); `jozacar` (Jozacar); `jucal` (Jucal); `judas-5` (Judas); `lamech` (Lamech); `lois` (Lois)
- `mamre` (Mamre); `mattan` (Mattan); `medad` (Medad); `micaiah-6` (Micaiah); `michael-7` (Michael); `mishael` (Mishael)
- `mithredath` (Mithredath); `mnason` (Mnason); `nethanel-6` (Nethanel); `nobah` (Nobah); `palti-2` (Palti); `parmenas` (Parmenas)
- `peninnah` (Peninnah); `persis` (Persis); `phygelus` (Phygelus); `prochorus` (Prochorus); `rechab` (Rechab); `rehum-2` (Rehum)
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
