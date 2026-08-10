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
history for those batches remain the record of what was done. Numbering for
the batches below is preserved as-is (no renumbering) per this document's
own rule against silently renumbering the queue.

- [ ] **44** — `asaph-2` (Asaph); `ethan` (Ethan); `elihu-5` (Elihu); `eliphaz-2` (Eliphaz)
- [ ] **45** — `bildad` (Bildad); `zophar` (Zophar); `bethuel` (Bethuel); `milcah-2` (Milcah)
- [ ] **46** — `anah` (Anah); `noah-2` (Noah); `mahlah` (Mahlah); `hoglah` (Hoglah)
- [ ] **47** — `tirzah` (Tirzah); `elzaphan` (Elzaphan); `abihu` (Abihu); `hophni` (Hophni)
- [ ] **48** — `elkanah-2` (Elkanah); `jair` (Jair); `tola` (Tola); `nahash` (Nahash)
- [ ] **49** — `abinadab` (Abinadab); `abinadab-2` (Abinadab); `abinadab-3` (Abinadab); `eliab-3` (Eliab)
- [ ] **50** — `elhanan` (Elhanan); `amasai` (Amasai); `adoni-zedek` (Adoni-zedek); `asahel` (Asahel)
- [ ] **51** — `amasa` (Amasa); `elnathan` (Elnathan); `meremoth` (Meremoth); `aristarchus` (Aristarchus)
- [ ] **52** — `gaius` (Gaius); `demas` (Demas); `tychicus` (Tychicus); `trophimus` (Trophimus)
- [ ] **53** — `felix` (Felix); `festus` (Festus); `caesar` (Caesar); `caesar-2` (Caesar)
- [ ] **54** — `canaan` (Canaan); `ephron` (Ephron); `er` (Er); `manasseh` (Manasseh)
- [ ] **55** — `nahshon` (Nahshon); `joel` (Joel)

Batches 56 and later, added 2026-08-10: a full fame-ranking pass over every
full-tier person with `devotionals` and a generic image who wasn't yet in
this queue (394 people at the time, including `tabitha` and `agabus`
themselves, plus the newly-promoted `zedekiah` and `simon-6` — see the
person-promotion notes in this repo's memory for that day). Batches 56-65
are hand-ordered by clear cultural/biblical recognition (Joseph husband of
Mary, Judas Iscariot, Pontius Pilate, Lazarus of Bethany, and similar).
Batch 66 onward is ranked by a reproducible heuristic (reference count +
distinct-book spread + total verse span), the same method already used
elsewhere in this project to estimate narrative weight — not a claim of
exact fame ordering, consistent with this document's existing "editorial
estimate" framing above.

- [ ] **56** — `joseph-6` (Joseph); `judas-2` (Judas); `herod` (Herod); `lazarus-2` (Lazarus)
- [ ] **57** — `pilate` (Pilate); `james` (James); `malchus` (Malchus); `zaccheus` (Zaccheus)
- [ ] **58** — `bartimaeus` (Bartimaeus); `cornelius` (Cornelius); `salome-2` (Salome); `matthias` (Matthias)
- [ ] **59** — `gamaliel-2` (Gamaliel); `lydia` (Lydia); `luke` (Luke); `ananias` (Ananias)
- [ ] **60** — `sapphira` (Sapphira); `philemon` (Philemon); `onesimus` (Onesimus); `ananias-2` (Ananias)
- [ ] **61** — `archelaus` (Archelaus); `drusilla` (Drusilla); `agrippa` (Agrippa); `bernice` (Bernice)
- [ ] **62** — `philip` (Philip); `judas` (Judas); `anna` (Anna); `simeon-2` (Simeon)
- [ ] **63** — `salome` (Salome); `rufus` (Rufus); `joanna` (Joanna); `claudius` (Claudius)
- [ ] **64** — `phoebe` (Phoebe); `sosthenes` (Sosthenes); `crispus` (Crispus); `eutychus` (Eutychus)
- [ ] **65** — `epaphroditus` (Epaphroditus); `onesiphorus` (Onesiphorus); `hymenaeus` (Hymenaeus); `alexander-4` (Alexander the Coppersmith)
- [ ] **66** — `junias` (Junia); `ananias-3` (Ananias); `judah` (Judah); `pharaoh-4` (Pharaoh)
- [ ] **67** — `levi` (Levi); `reuben` (Reuben); `dan` (Dan); `pharaoh-2` (Pharaoh)
- [ ] **68** — `simeon` (Simeon); `rebekah` (Rebekah); `issachar` (Issachar); `darius` (Darius)
- [ ] **69** — `sihon` (Sihon); `joash-3` (Joash); `ben-hadad` (Ben-hadad); `og` (Og)
- [ ] **70** — `pharaoh-7` (Pharaoh); `jotham-2` (Jotham); `jehoiachin` (Jehoiachin); `shem` (Shem)
- [ ] **71** — `jehoram` (Jehoram); `joram-2` (Joram); `hazael` (Hazael); `joash-4` (Joash)
- [ ] **72** — `cyrus` (Cyrus); `perez` (Perez); `hur` (Hur); `ithamar` (Ithamar)
- [ ] **73** — `eliezer` (Eliezer of Damascus); `shimeah` (Shimeah); `obed-edom-2` (Obed-edom); `jehoahaz` (Jehoahaz)
- [ ] **74** — `rabshakeh` (Rabshakeh); `machir` (Machir); `micaiah` (Micaiah); `shishak` (Shishak)
- [ ] **75** — `ham` (Ham); `jeduthun` (Jeduthun); `kish` (Kish); `deborah-2` (Deborah)
- [ ] **76** — `shalmaneser` (Shalmaneser); `japheth` (Japheth); `pharaoh-3` (Pharaoh); `jeroboam-2` (Jeroboam)
- [ ] **77** — `hannah` (Hannah); `dathan` (Dathan); `eliashib-7` (Eliashib); `hadadezer` (Hadadezer)
- [ ] **78** — `jabin` (Jabin); `joah` (Joah); `joash` (Joash); `shelah-2` (Shelah)
- [ ] **79** — `tobiah` (Tobiah); `zacharias` (Zacharias); `heman-2` (Heman); `micah` (Micah)
- [ ] **80** — `johanan` (Johanan); `joshua-4` (Joshua); `ishmael-2` (Ishmael); `naaman-2` (Naaman)
- [ ] **81** — `pharaoh-neco` (Pharaoh Neco); `zedekiah` (Zedekiah); `jehoahaz-2` (Jehoahaz); `shaphan` (Shaphan)
- [ ] **82** — `hiram-2` (Hiram); `naboth` (Naboth); `rezin` (Rezin); `ben-hadad-2` (Ben-hadad)
- [ ] **83** — `hoshea` (Hoshea); `jonadab-2` (Jonadab); `maacah-3` (Maacah); `simon-6` (Simon)
- [ ] **84** — `jael` (Jael); `onan` (Onan); `phinehas-2` (Phinehas); `hoham` (Hoham)
- [ ] **85** — `jonathan-3` (Jonathan); `agag-2` (Agag); `manoah` (Manoah); `debir` (Debir)
- [ ] **86** — `herod-3` (Herod); `japhia` (Japhia); `jehu` (Jehu); `piram` (Piram)
- [ ] **87** — `hanani` (Hanani); `jeshua-7` (Jeshua); `potiphar` (Potiphar); `shemaiah` (Shemaiah)
- [ ] **88** — `mesha` (Mesha); `abishag` (Abishag); `berodach-baladan` (Berodach-baladan); `sheba-4` (Sheba)
- [ ] **89** — `sibbecai` (Sibbecai); `bera` (Bera); `hananiah-10` (Hananiah); `gemariah` (Gemariah)
- [ ] **90** — `hirah` (Hirah); `lysias` (Lysias); `delilah` (Delilah); `judas-3` (Judas)
- [ ] **91** — `obadiah-5` (Obadiah); `seraiah-2` (Seraiah); `chedorlaomer` (Chedorlaomer); `elihu` (Elihu)
- [ ] **92** — `hanun` (Hanun); `obed-edom` (Obed-edom); `achsah` (Achsah); `ehud` (Ehud)
- [ ] **93** — `gaal` (Gaal); `rehum-2` (Rehum); `shimshai` (Shimshai); `simon-5` (Simon)
- [ ] **94** — `demetrius` (Demetrius); `phicol` (Phicol); `shethar-bozenai` (Shethar-bozenai); `abijah` (Abijah)
- [ ] **95** — `amaziah-3` (Amaziah); `delaiah-5` (Delaiah); `jashobeam` (Jashobeam); `jason` (Jason)
- [ ] **96** — `jezaniah` (Jezaniah); `jonathan-4` (Jonathan); `obadiah` (Obadiah); `obed` (Obed)
- [ ] **97** — `oholiab` (Oholiab); `oreb` (Oreb); `shobach` (Shobach); `evil-merodach` (Evil-merodach)
- [ ] **98** — `hegai` (Hegai); `ittai` (Ittai the Gittite); `joel-6` (Joel); `pelatiah-4` (Pelatiah)
- [ ] **99** — `shemaiah-21` (Shemaiah); `aner` (Aner); `arioch-2` (Arioch); `asaiah` (Asaiah)
- [ ] **100** — `eshcol` (Eshcol); `hadad-4` (Hadad); `mamre` (Mamre); `oded` (Oded)
- [ ] **101** — `zimri-2` (Zimri); `ahio` (Ahio); `judas-5` (Judas); `nadab-2` (Nadab)
- [ ] **102** — `nergal-sar-ezer-2` (Nergal-sar-ezer); `orpah` (Orpah); `adrammelech` (Adrammelech); `ahiman` (Ahiman)
- [ ] **103** — `amariah-2` (Amariah); `archippus` (Archippus); `azariah-14` (Azariah); `chenaniah` (Chenaniah)
- [ ] **104** — `ebed-melech` (Ebed-melech); `eleazar-3` (Eleazar); `elishama-6` (Elishama); `erastus-2` (Erastus)
- [ ] **105** — `geshem` (Geshem); `huldah` (Huldah); `jehosheba` (Jehosheba); `jehudi` (Jehudi)
- [ ] **106** — `joah-2` (Joah); `joash-2` (Joash); `joram` (Joram); `jozacar` (Jozacar)
- [ ] **107** — `mattan` (Mattan); `mishael` (Mishael); `mordecai` (Mordecai); `palti-2` (Palti)
- [ ] **108** — `saph` (Saph); `sharezer` (Sharezer); `sheba` (Sheba); `sheshai` (Sheshai)
- [ ] **109** — `sheshbazzar` (Sheshbazzar); `elah-2` (Elah); `hanani-4` (Hanani); `iddo-4` (Iddo)
- [ ] **110** — `jeriah` (Jeriah); `mahlon` (Mahlon); `azariah-7` (Azariah); `baanah` (Baanah)
- [ ] **111** — `chilion` (Chilion); `gaius-3` (Gaius); `memucan` (Memucan); `rechab` (Rechab)
- [ ] **112** — `rizpah` (Rizpah); `agabus` (Agabus); `ethan-3` (Ethan); `lamech` (Lamech)
- [ ] **113** — `puah` (Puah); `shemeber` (Shemeber); `sherebiah` (Sherebiah); `shiphrah` (Shiphrah)
- [ ] **114** — `conaniah` (Conaniah); `eglon` (Eglon); `gallio` (Gallio); `hanamel` (Hanamel)
- [ ] **115** — `hathach` (Hathach); `lazarus` (Lazarus); `machir-2` (Machir); `mary-4` (Mary)
- [ ] **116** — `pashhur-2` (Pashhur); `peninnah` (Peninnah); `pharaoh` (Pharaoh); `sargon` (Sargon)
- [ ] **117** — `shallum` (Shallum); `bigthan` (Bigthan); `elon` (Elon); `harbona` (Harbona)
- [ ] **118** — `heldai-2` (Heldai); `ichabod` (Ichabod); `jarib` (Jarib); `jedaiah-6` (Jedaiah)
- [ ] **119** — `pekahiah` (Pekahiah); `rhoda` (Rhoda); `shamgar` (Shamgar); `shelemiah-6` (Shelemiah)
- [ ] **120** — `simon-4` (Simon); `tabitha` (Tabitha); `boaz` (Boaz); `chimham` (Chimham)
- [ ] **121** — `joseph-10` (Joseph called Barsabbas); `lemuel` (Lemuel); `publius` (Publius); `ruth` (Ruth)
- [ ] **122** — `adoni-bezek` (Adoni-bezek); `bar-jesus` (Bar-Jesus); `cushan-rishathaim` (Cushan-rishathaim); `eliel-7` (Eliel)
- [ ] **123** — `elimelech` (Elimelech); `ibzan` (Ibzan); `jair-2` (Jair); `julius` (Julius)
- [ ] **124** — `lo-ruhamah` (Lo-ruhamah); `micaiah-6` (Micaiah); `philetus` (Philetus); `seraiah-10` (Seraiah)
- [ ] **125** — `aeneas` (Aeneas); `ahab-2` (Ahab); `amminadab-2` (Amminadab); `eldad` (Eldad)
- [ ] **126** — `elon-3` (Elon); `irijah` (Irijah); `jambres` (Jambres); `jannes` (Jannes)
- [ ] **127** — `medad` (Medad); `purah` (Purah); `abijah-2` (Abijah); `abiram-2` (Abiram)
- [ ] **128** — `achaicus` (Achaicus); `agur` (Agur); `alexander-3` (Alexander); `amasa-2` (Amasa)
- [ ] **129** — `amasiah` (Amasiah); `ammiel` (Ammiel); `andronicus` (Andronicus); `antipas` (Antipas)
- [ ] **130** — `armoni` (Armoni); `asaph-4` (Asaph); `ashpenaz` (Ashpenaz); `azariah-10` (Azariah)
- [ ] **131** — `azariah-11` (Azariah); `azariah-16` (Azariah); `azariah-8` (Azariah); `azaryahu` (Azaryahu)
- [ ] **132** — `baalis` (Baalis); `baruch` (Baruch); `berechiah-4` (Berechiah); `bidkar` (Bidkar)
- [ ] **133** — `caesar-augustus` (Caesar Augustus); `chloe` (Chloe); `cleopas` (Cleopas); `damaris` (Damaris)
- [ ] **134** — `deborah` (Deborah); `demetrius-2` (Demetrius); `dionysius` (Dionysius); `diotrephes` (Diotrephes)
- [ ] **135** — `elasah-2` (Elasah); `eleazar-2` (Eleazar); `eliezer-6` (Eliezer); `elishaphat` (Elishaphat)
- [ ] **136** — `epanetus` (Epanetus); `eunice` (Eunice); `euodia` (Euodia); `ezer-4` (Ezer)
- [ ] **137** — `forunatus` (Forunatus); `gaddi` (Gaddi); `gaddiel` (Gaddiel); `gedaliah-4` (Gedaliah)
- [ ] **138** — `geuel` (Geuel); `gomer-2` (Gomer); `hashabneiah-2` (Hashabneiah); `hermogenes` (Hermogenes)
- [ ] **139** — `hiel` (Hiel); `hobab` (Hobab); `iddo-6` (Iddo); `igal` (Igal)
- [ ] **140** — `ishbi-benob` (Ishbi-benob); `jaazaniah` (Jaazaniah); `jaazaniah-2` (Jaazaniah); `jaazaniah-3` (Jaazaniah)
- [ ] **141** — `jahaziel-3` (Jahaziel); `jehiel-3` (Jehiel); `jehikhiah` (Jehikhiah); `jehucal` (Jehucal)
- [ ] **142** — `jemimah` (Jemimah); `jerahmeel-3` (Jerahmeel); `jether` (Jether); `jezebel-2` (Jezebel)
- [ ] **143** — `jezrahiah` (Jezrahiah); `jezreel-2` (Jezreel); `joah-4` (Joah); `jonathan-2` (Jonathan)
- [ ] **144** — `jucal` (Jucal); `judas-of-galilee` (Judas of Galilee); `keren-happuch` (Keren-happuch); `keziah` (Keziah)
- [ ] **145** — `lo-ammi` (Lo-ammi); `lois` (Lois); `maaseiah-4` (Maaseiah); `manaen` (Manaen)
- [ ] **146** — `mephibosheth-2` (Mephibosheth); `michael-7` (Michael); `mithredath` (Mithredath); `mnason` (Mnason)
- [ ] **147** — `nebushazban` (Nebushazban); `nethanel-6` (Nethanel); `nethaniah-3` (Nethaniah); `nicanor` (Nicanor)
- [ ] **148** — `nicolas` (Nicolas); `noadiah` (Noadiah); `noadiah-2` (Noadiah); `nobah` (Nobah)
- [ ] **149** — `nympha` (Nympha); `obadiah-6` (Obadiah); `on` (On); `parmenas` (Parmenas)
- [ ] **150** — `persis` (Persis); `phygelus` (Phygelus); `prochorus` (Prochorus); `regemmelech` (Regemmelech)
- [ ] **151** — `rezon` (Rezon); `segub` (Segub); `sephatiah` (Sephatiah); `seraiah-9` (Seraiah)
- [ ] **152** — `sergius-paulus` (Sergius Paulus); `shabbethai` (Shabbethai); `shammah-2` (Shammah); `sharezer-2` (Sharezer)
- [ ] **153** — `shear-jashub` (Shear-jashub); `shecaniah-5` (Shecaniah); `shemaiah-18` (Shemaiah); `shephatiah-8` (Shephatiah)
- [ ] **154** — `shobi` (Shobi); `tertius` (Tertius)

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
