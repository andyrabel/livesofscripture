"""Curated data for the Places feature — top-tier places (10+ associated
people). Merged with data/people/*.json's geographic_setting extraction by
generate_places.py. Not committed via .gitignore's _build/ rule but force-
added, same pattern as the other backfill_*.py scripts (see CLAUDE.md).

Each entry: name, alt (alt_names), type, region, first_reference,
id_status (secure|traditional|disputed|unknown), id_note (only when not
secure), modern (modern place name, or None), major (bool — gets
family_friendly_summary), desc (adult-register description, <=250 words,
chapter:verse refs only, no verse text), ff (family_friendly_summary,
major only, <=150 words), references (extra refs beyond first_reference).
"""

PLACES_MAJOR = {
    "jerusalem": dict(
        name="Jerusalem", alt=["Zion", "Salem", "City of David", "Jebus"],
        type="city", region="canaan-israel", first_reference="Genesis 14:18",
        id_status="secure", modern="Jerusalem, Israel",
        major=True,
        references=["Joshua 10:1", "2 Samuel 5:6-9", "1 Kings 6", "2 Kings 25", "Matthew 21:1-11", "Acts 2"],
        desc=(
            "Called Salem in Abraham's day and Jebus while still held by the Jebusites, Jerusalem became "
            "Israel's capital only when David captured its fortress and made it his own city (2 Samuel 5:6-9). "
            "Solomon built the temple there, giving the city a religious as well as political centrality it "
            "never lost (1 Kings 6; 8). It was the site of a divided kingdom's southern capital, of Isaiah's, "
            "Jeremiah's, and Ezekiel's ministries, and of its own destruction by Babylon in 586 BC — then of a "
            "rebuilt temple under Ezra and Nehemiah after the exile. In the Gospels it is where Jesus was "
            "presented as an infant, taught in the temple courts, was crucified outside its walls, and rose "
            "again; in Acts it is where the church was born at Pentecost. No other place in Scripture carries "
            "this much continuous narrative weight across both Testaments."
        ),
        ff=(
            "Jerusalem is the most important city in the whole Bible. King David made it his capital, and his "
            "son Solomon built God's temple there. Many kings, prophets, and important Bible events happened "
            "in Jerusalem — and it's the city where Jesus was put on the cross and where He rose from the dead. "
            "Jerusalem is still an important city today."
        ),
    ),
    "samaria": dict(
        name="Samaria", alt=[], type="city", region="canaan-israel",
        first_reference="1 Kings 16:24", id_status="secure", modern="Sebastia, West Bank",
        major=True,
        references=["1 Kings 16:24", "2 Kings 17:5-6", "John 4:4-42", "Acts 8:5-8"],
        desc=(
            "Built by King Omri as the new capital of the northern kingdom of Israel and named for Shemer, "
            "the hill's previous owner (1 Kings 16:24), Samaria became the seat of Ahab and Jezebel's Baal "
            "worship and the target of Elijah's and Elisha's confrontations with the royal house. Assyria "
            "besieged and finally destroyed it in 722 BC, deporting its population and resettling the region "
            "with foreigners — the origin of the later Jewish-Samaritan divide (2 Kings 17:5-6, 24). By the "
            "New Testament, Samaria (now naming the whole region, not just the city) was the setting for "
            "Jesus's conversation with a Samaritan woman at Jacob's well (John 4) and for Philip's preaching "
            "and the Spirit's coming there in Acts 8 — an early, deliberate crossing of Jewish-Samaritan "
            "hostility that Acts 1:8 had already marked out as part of the gospel's spread."
        ),
        ff=(
            "Samaria was the capital city of the northern kingdom of Israel, built by King Omri. Wicked King "
            "Ahab and Queen Jezebel ruled from there, and the prophets Elijah and Elisha spoke out against "
            "them. Later, an enemy nation called Assyria conquered Samaria. Long after that, Jesus talked with "
            "a Samaritan woman at a well, and after Jesus rose from the dead, people in Samaria heard the good "
            "news about Him too."
        ),
    ),
    "kingdom-of-judah": dict(
        name="Kingdom of Judah", alt=["Judah"], type="nation", region="canaan-israel",
        first_reference="1 Kings 12:17", id_status="secure",
        major=True,
        references=["1 Kings 12:17", "2 Kings 25"],
        desc=(
            "The southern of the two kingdoms Israel split into after Solomon's death, made up of the tribes "
            "of Judah and Benjamin and ruled continuously by David's descendants from Jerusalem (1 Kings 12; "
            "2 Chronicles 11:1). Judah outlasted the northern kingdom by over a century, surviving Assyria's "
            "722 BC conquest of Israel but eventually falling to Babylon, whose armies destroyed Jerusalem and "
            "its temple in 586 BC and deported much of the population (2 Kings 25). Most of the writing "
            "prophets — Isaiah, Jeremiah, Micah, Zephaniah, Habakkuk — ministered to Judah's kings and people "
            "in this period, warning of coming judgment and, beyond it, of restoration. The kingdom's name "
            "outlived its independence, giving later Scripture the term \"Jew.\""
        ),
        ff=(
            "After wise King Solomon died, God's people split into two kingdoms. Judah was the kingdom in the "
            "south, ruled by kings from David's own family, with Jerusalem as its capital. Some of Judah's "
            "kings loved God and some did not. Many prophets, like Isaiah and Jeremiah, warned Judah's kings "
            "to turn back to God. Eventually, Judah was conquered by Babylon."
        ),
    ),
    "egypt": dict(
        name="Egypt", alt=[], type="nation", region="egypt",
        first_reference="Genesis 12:10", id_status="secure", modern="Egypt",
        major=True,
        references=["Genesis 12:10", "Genesis 37-50", "Exodus 1-14", "Matthew 2:13-15"],
        desc=(
            "The great river-valley civilization to Canaan's southwest, Egypt appears across the whole span "
            "of Scripture: Abraham took refuge there in a famine (Genesis 12:10), Joseph rose from slave to "
            "vizier there and later settled his family in Goshen (Genesis 37-50), and their descendants were "
            "later enslaved there for centuries until the exodus under Moses (Exodus 1-14) — the founding "
            "redemption narrative the rest of the Old Testament keeps returning to. Solomon married a "
            "pharaoh's daughter; later kings sought (and were warned against) Egyptian military alliances; "
            "and in the New Testament, Joseph and Mary fled there with the infant Jesus to escape Herod, so "
            "that Matthew could say \"Out of Egypt I called My Son\" (Matthew 2:13-15, quoting Hosea 11:1)."
        ),
        ff=(
            "Egypt was a powerful country south of Israel, next to the Nile River. Joseph was sold as a slave "
            "there but later became a great leader, second only to Pharaoh. Later, Joseph's family grew into "
            "a huge nation of slaves in Egypt, until God sent Moses to lead them out in the exodus. Much later, "
            "baby Jesus and His parents hid safely in Egypt for a while too."
        ),
    ),
    "canaan": dict(
        name="Canaan", alt=["The Promised Land"], type="region", region="canaan-israel",
        first_reference="Genesis 9:18", id_status="secure",
        major=True,
        references=["Genesis 12:5", "Genesis 15:18-21", "Joshua 1-12"],
        desc=(
            "The land between the Mediterranean and the Jordan promised to Abraham's descendants (Genesis "
            "12:5-7; 15:18-21), named for Noah's grandson whose descendants settled it (Genesis 9:18; 10:15-19). "
            "Abraham, Isaac, and Jacob lived there as resident foreigners without owning it outright, apart "
            "from the burial cave at Machpelah. After the exodus, Joshua led Israel's conquest and settlement "
            "of Canaan, dividing it among the twelve tribes (Joshua 1-12; 13-21) — a land whose Canaanite "
            "population's idolatry and practices Israel was repeatedly warned not to adopt. \"Canaan\" as a "
            "name for the land largely gives way to \"Israel\" once the tribes are settled, though it remains "
            "the standard term for the pre-conquest and patriarchal-era territory throughout Genesis."
        ),
        ff=(
            "Canaan was the land God promised to give to Abraham and his family, long before they lived there. "
            "Abraham, Isaac, and Jacob traveled through Canaan but didn't fully own it yet. Many years later, "
            "after the exodus from Egypt, Joshua led the people of Israel into Canaan and they finally settled "
            "there, dividing the land among the twelve tribes."
        ),
    ),
    "kingdom-of-israel": dict(
        name="Kingdom of Israel", alt=["Northern Kingdom"], type="nation", region="canaan-israel",
        first_reference="1 Kings 12:20", id_status="secure",
        major=True,
        references=["1 Kings 12:20", "2 Kings 17:6"],
        desc=(
            "The northern of the two kingdoms formed when ten tribes broke away from Rehoboam, Solomon's son, "
            "and made Jeroboam king instead (1 Kings 12:16-20). Jeroboam set up rival golden-calf shrines at "
            "Bethel and Dan so his people would not go worship at Jerusalem's temple — a founding act of "
            "idolatry every one of the kingdom's nineteen kings, across several dynasties, is measured against "
            "and none escaped. Elijah and Elisha ministered almost entirely within its borders, confronting "
            "Ahab's and Jezebel's Baal worship. Assyria finally conquered the kingdom in 722 BC and deported "
            "its population, ending it after roughly two centuries — the disaster the prophet Hosea and Amos "
            "had specifically warned of (2 Kings 17:6-23)."
        ),
        ff=(
            "After Solomon's son became king, ten of the twelve tribes rebelled and formed their own kingdom "
            "in the north, called Israel. Their first king, Jeroboam, led the people into idol worship right "
            "from the start. None of Israel's kings that followed turned the nation back to God, even though "
            "prophets like Elijah, Elisha, and Amos warned them. Eventually, Assyria conquered the kingdom."
        ),
    ),
    "babylon": dict(
        name="Babylon", alt=["Shinar", "Chaldea"], type="city", region="mesopotamia",
        first_reference="Genesis 10:10", id_status="secure", modern="Hillah, Iraq",
        major=True,
        references=["Genesis 11:1-9", "2 Kings 25:1-21", "Daniel 1-5", "Revelation 18"],
        desc=(
            "Founded, Genesis says, by Nimrod (Genesis 10:10), Babylon is also the setting of the tower of "
            "Babel, where God confused humanity's language (Genesis 11:1-9) — the city's first appearance "
            "already marking it as a symbol of human pride set against God. Centuries later it became the "
            "capital of the empire that destroyed Jerusalem and its temple in 586 BC and deported Judah's "
            "population there (2 Kings 25). Daniel and his three friends served in Nebuchadnezzar's court "
            "during that exile, and the book of Daniel records God's repeated humbling of Babylon's rulers "
            "(Daniel 1-5). Cyrus of Persia conquered Babylon in 539 BC and let the exiles return. Revelation "
            "later uses \"Babylon\" as a symbolic name for a final, doomed world power opposed to God "
            "(Revelation 17-18) — a use of the name, not a claim about the literal city's end-times future."
        ),
        ff=(
            "Babylon was a great and powerful city, and later the capital of a mighty empire. Long before "
            "that, it's also where people built a huge tower to make a name for themselves, so God gave them "
            "different languages so they couldn't understand each other anymore. Later, the Babylonian army "
            "conquered Jerusalem, and God's people had to live in Babylon for many years. Daniel and his "
            "friends stayed faithful to God even while living there."
        ),
    ),
    "rome": dict(
        name="Rome", alt=[], type="city", region="italy",
        first_reference="Acts 2:10", id_status="secure", modern="Rome, Italy",
        major=True,
        references=["Acts 18:2", "Acts 28:14-16", "Romans 1:7"],
        desc=(
            "Capital of the empire that ruled the whole New Testament world, Rome itself is mentioned less "
            "often in Scripture than the emperors and officials who governed in its name, but it is the city "
            "Paul had long wanted to visit (Romans 1:10-13; 15:22-24) and the destination of his letter to "
            "the Romans, written to a church already established there before he ever arrived. Aquila and "
            "Priscilla had been expelled from Rome under Claudius's edict against Jews (Acts 18:2) before "
            "later returning. Paul finally reached the city as a prisoner appealing his case to Caesar, and "
            "spent two years there under guard, still preaching (Acts 28:14-31) — the point at which Acts's "
            "narrative ends, with the gospel having reached the empire's center."
        ),
        ff=(
            "Rome was the capital city of the huge Roman Empire that ruled over Israel in New Testament "
            "times. Paul wrote his letter to the Romans to Christians already living there, and he always "
            "wanted to visit them. Eventually Paul did travel to Rome — but as a prisoner, appealing to have "
            "his case heard by Caesar. Even under guard, Paul kept telling people about Jesus there."
        ),
    ),
    "bethlehem": dict(
        name="Bethlehem", alt=["Ephrath", "Bethlehem-judah", "City of David"],
        type="town", region="canaan-israel",
        first_reference="Genesis 35:19", id_status="secure", modern="Bethlehem, West Bank",
        major=True,
        id_note=(
            "A separate town also called Bethlehem existed in the territory of Zebulun (Joshua 19:15). Judges "
            "12:8-10 places the judge Ibzan at \"Bethlehem\" without naming which one, and which town is meant "
            "is genuinely disputed among interpreters; this entry treats the far better-attested Bethlehem of "
            "Judah, where Ruth, David, and Jesus's stories are set."
        ),
        references=["Genesis 35:19", "Ruth 1:19-22", "1 Samuel 16:1-13", "Micah 5:2", "Luke 2:1-7"],
        desc=(
            "A small town a few miles south of Jerusalem, Bethlehem is where Rachel died and was buried "
            "(Genesis 35:19), where Naomi's family lived before famine sent them to Moab and where Ruth later "
            "gleaned in Boaz's fields (Ruth 1-4), and where Samuel anointed the shepherd boy David as king "
            "over his older brothers (1 Samuel 16:1-13) — giving the town its lasting title \"the city of "
            "David\" even after David made Jerusalem his capital. Micah named Bethlehem centuries in advance "
            "as the birthplace of Israel's promised ruler, \"from the days of eternity\" (Micah 5:2), which "
            "Matthew explicitly cites as fulfilled when Jesus was born there during a Roman census (Matthew "
            "2:1-6; Luke 2:1-7) — one of Scripture's clearest advance-and-fulfillment pairs."
        ),
        ff=(
            "Bethlehem was a small town near Jerusalem. Ruth moved there with Naomi and later married Boaz. "
            "Bethlehem was also the hometown of young David, the shepherd boy God chose to become king. Long "
            "before Jesus was born, a prophet named Micah said the promised Savior would come from Bethlehem "
            "— and hundreds of years later, that's exactly where Jesus was born!"
        ),
    ),
    "ephesus": dict(
        name="Ephesus", alt=[], type="city", region="asia-minor-greece",
        first_reference="Acts 18:19", id_status="secure", modern="near Selçuk, Turkey",
        major=True,
        references=["Acts 18:19-21", "Acts 19", "Ephesians 1:1", "Revelation 2:1-7"],
        desc=(
            "A major port city in the Roman province of Asia, home to the temple of Artemis, one of the "
            "ancient world's Seven Wonders. Paul first visited briefly (Acts 18:19-21) then returned and "
            "spent about three years establishing a church there, teaching daily in the hall of Tyrannus "
            "(Acts 19:8-10) — long enough that a riot broke out among silversmiths whose idol-making trade "
            "his preaching threatened (Acts 19:23-41). He later wrote Ephesians, likely a circular letter to "
            "churches in the region, and gave Timothy responsibility for the Ephesian church (1 Timothy 1:3). "
            "It is also the first of the seven churches addressed in Revelation, commended for perseverance "
            "but warned for having \"left your first love\" (Revelation 2:1-7)."
        ),
        ff=(
            "Ephesus was a big city with a huge temple to a false goddess called Artemis. Paul spent about "
            "three years there teaching people about Jesus, and so many people believed that it hurt the "
            "business of men who made idols — they even started a riot! Paul later wrote a letter to the "
            "Christians in Ephesus, and it's also one of the seven churches Jesus speaks to in Revelation."
        ),
    ),
    "galilee": dict(
        name="Galilee", alt=[], type="region", region="canaan-israel",
        first_reference="Joshua 20:7", id_status="secure",
        major=True,
        references=["Matthew 4:12-17", "Luke 1:26", "John 1:46"],
        desc=(
            "The hilly northern region of Israel around the Sea of Galilee, home to Nazareth, Capernaum, "
            "Cana, and Bethsaida. Though set apart by Joshua as a place of refuge (Joshua 20:7) and later "
            "the territory of Zebulun and Naphtali, by New Testament times \"Galilee of the Gentiles\" was "
            "viewed by some in Judea as culturally provincial — Nathanael's \"can any good thing come out of "
            "Nazareth?\" reflects the attitude (John 1:46). It was nonetheless where Jesus grew up, was "
            "baptized in the nearby Jordan, called His first disciples (mostly Galilean fishermen), and "
            "conducted the bulk of His public ministry — teaching, healing, and performing most of His "
            "recorded miracles around its lake before His final journey to Jerusalem (Matthew 4:12-17; "
            "Isaiah 9:1-2)."
        ),
        ff=(
            "Galilee was the region in the north of Israel where Jesus grew up and did most of His teaching "
            "and miracles. Its biggest lake, the Sea of Galilee, is where Jesus called His first disciples, "
            "who were fishermen there. Even though some people looked down on Galilee, Jesus spent most of "
            "His time on earth right there among its towns and villages."
        ),
    ),
    "hebron": dict(
        name="Hebron", alt=["Kiriath-arba", "Mamre"], type="city", region="canaan-israel",
        first_reference="Genesis 13:18", id_status="secure", modern="Hebron, West Bank",
        major=True,
        references=["Genesis 23", "Numbers 13:22", "2 Samuel 2:1-4", "2 Samuel 5:1-5"],
        desc=(
            "One of the oldest continuously inhabited cities in the region, Hebron is where Abraham settled "
            "near the oaks of Mamre and later bought the cave of Machpelah to bury Sarah — the family's "
            "eventual burial place too, for Abraham, Isaac, Rebekah, Jacob, and Leah (Genesis 23; 49:29-31). "
            "Caleb received Hebron as his inheritance after driving out its giant Anakim inhabitants (Joshua "
            "14:6-15). It became David's first capital: he reigned there over Judah alone for seven and a "
            "half years before all Israel's elders came and anointed him king over the whole nation (2 Samuel "
            "2:1-4; 5:1-5), only afterward moving the capital to Jerusalem. Absalom later launched his "
            "rebellion from Hebron under the pretext of a vow (2 Samuel 15:7-10)."
        ),
        ff=(
            "Hebron is a very old city where Abraham once lived and bought a burial cave for his wife Sarah. "
            "Many years later, David became king there first, ruling just over the tribe of Judah for a "
            "while before the rest of Israel's leaders came to make him king over everyone. Only after that "
            "did David move his capital to Jerusalem."
        ),
    ),
    "paddan-aram": dict(
        name="Paddan-aram", alt=["Aram-naharaim (in some contexts)"], type="region", region="mesopotamia",
        first_reference="Genesis 25:20", id_status="secure",
        major=True,
        references=["Genesis 28:2-5", "Genesis 29-31"],
        desc=(
            "The upper-Mesopotamian region around Haran where Abraham's brother Nahor's family settled after "
            "leaving Ur, and where Isaac sent his servant to find Rebekah (Genesis 24) and later sent Jacob "
            "himself to find a wife and escape Esau's anger (Genesis 28:2-5). Jacob spent twenty years there "
            "working for his uncle Laban, marrying Leah and Rachel, and fathering most of his children before "
            "fleeing back to Canaan (Genesis 29-31). The name distinguishes this specific district from the "
            "broader term \"Aram\" used elsewhere for Syrian territory further west and north."
        ),
        ff=(
            "Paddan-aram was the faraway land where Abraham's relatives lived. Isaac's servant traveled there "
            "to find Rebekah to be Isaac's wife, and later Jacob himself went there to escape his angry "
            "brother Esau. Jacob lived there for twenty years, working for his uncle Laban and marrying "
            "Leah and Rachel, before finally returning home to Canaan."
        ),
    ),
    "sinai": dict(
        name="Sinai", alt=["Wilderness of Sinai", "Sinai Peninsula"], type="wilderness", region="sinai-wilderness",
        first_reference="Exodus 16:1", id_status="traditional",
        id_note=(
            "The traditional location in the southern Sinai Peninsula (near modern Jebel Musa) is the most "
            "widely held identification, but several other sites in the peninsula and even in northwest "
            "Arabia have been proposed; Scripture itself gives no coordinates."
        ),
        major=True,
        references=["Exodus 19", "Numbers 10:11-12"],
        desc=(
            "The wilderness region Israel reached about three months after leaving Egypt, where they camped "
            "for roughly a year at the foot of Mount Sinai (Exodus 19:1-2; Numbers 10:11-12). It was here "
            "that God gave Moses the Ten Commandments and the rest of the Law, established the covenant with "
            "Israel as a nation, and gave detailed instructions for the tabernacle, priesthood, and sacrificial "
            "system (Exodus 19-40; Leviticus). Aaron's golden calf, Nadab and Abihu's unauthorized fire, and "
            "the tabernacle's construction and dedication all take place here — making Sinai the setting for "
            "most of Exodus's second half and all of Leviticus."
        ),
        ff=(
            "Sinai was the wild, mountain-filled desert where God's people camped for about a year after "
            "leaving Egypt. There God gave Moses the Ten Commandments and many other laws, and the people "
            "built a special worship tent called the tabernacle. It was an important time when God showed "
            "His people how He wanted them to live and worship Him."
        ),
    ),
    "caesarea": dict(
        name="Caesarea", alt=["Caesarea Maritima"], type="city", region="canaan-israel",
        first_reference="Acts 8:40", id_status="secure", modern="Caesarea, Israel",
        major=True,
        id_note=(
            "Distinct from Caesarea Philippi, a separate inland city near Mount Hermon where Peter confessed "
            "Jesus as the Christ (Matthew 16:13-20) — no person in this dataset is specifically tied to that "
            "second Caesarea."
        ),
        references=["Acts 10", "Acts 23:23-24", "Acts 25-26"],
        desc=(
            "A Roman port city built by Herod the Great and named for Caesar Augustus, Caesarea served as "
            "the Roman governor's residence and administrative capital of Judea. Philip the evangelist settled "
            "there (Acts 8:40; 21:8), and it was in Caesarea that Cornelius, a Roman centurion, received a "
            "vision leading to Peter's visit and the first recorded Gentile conversion apart from circumcision "
            "(Acts 10). Paul was later held under guard in Caesarea for two years, tried before governors "
            "Felix and Festus and King Agrippa, and it was from there that he appealed to Caesar and sailed "
            "for Rome (Acts 23-26)."
        ),
        ff=(
            "Caesarea was a busy port city built by Herod the Great, where the Roman governor lived. It's "
            "where a Roman soldier named Cornelius became one of the first non-Jewish believers, after Peter "
            "visited him. Later, Paul was kept as a prisoner in Caesarea for two years and had to defend "
            "himself in front of several important rulers there."
        ),
    ),
    "susa": dict(
        name="Susa", alt=["Shushan"], type="city", region="mesopotamia",
        first_reference="Nehemiah 1:1", id_status="secure", modern="Shush, Iran",
        major=True,
        references=["Esther 1", "Esther 2-9", "Daniel 8:2"],
        desc=(
            "Winter capital of the Persian Empire, Susa is where nearly the entire book of Esther takes "
            "place: King Ahasuerus's court, Esther's rise to queen, Haman's plot against the Jews, and "
            "Mordecai's and Esther's eventual reversal of it (Esther 1-9). Nehemiah was serving as the king's "
            "cupbearer in Susa's citadel when he heard news of Jerusalem's broken walls, prompting his request "
            "to return and rebuild them (Nehemiah 1:1; 2:1-8). Daniel also received one of his visions while "
            "in Susa, though the text does not say he was living there permanently at the time (Daniel 8:2)."
        ),
        ff=(
            "Susa was the winter capital city of the powerful Persian Empire. It's where the whole story of "
            "Esther takes place — Esther became queen there, and later bravely saved her people from a wicked "
            "plot. Nehemiah was also serving as the king's helper in Susa when he heard sad news about "
            "Jerusalem, which led him to ask permission to go rebuild its walls."
        ),
    ),
    "corinth": dict(
        name="Corinth", alt=[], type="city", region="asia-minor-greece",
        first_reference="Acts 18:1", id_status="secure", modern="Corinth, Greece",
        major=True,
        references=["Acts 18:1-18", "1 Corinthians 1:1-2", "2 Corinthians 1:1"],
        desc=(
            "A major, wealthy Roman commercial city on the isthmus connecting mainland Greece to the "
            "Peloponnese, known for its sea trade and, notoriously, its immorality. Paul arrived there on his "
            "second missionary journey, met Aquila and Priscilla, and spent eighteen months establishing a "
            "church, appearing before the proconsul Gallio when opponents brought charges against him (Acts "
            "18:1-18). The church he planted proved troubled — factions, lawsuits between believers, and "
            "tolerated sexual immorality among them — prompting his two New Testament letters to Corinth, "
            "which address these problems along with foundational teaching on love, spiritual gifts, and the "
            "resurrection (1 Corinthians; 2 Corinthians)."
        ),
        ff=(
            "Corinth was a busy trading city in Greece where Paul lived and worked for about a year and a "
            "half, teaching people about Jesus and starting a church. The Christians there sometimes struggled "
            "to get along or live the way Jesus wanted, so Paul wrote them two long letters to help guide "
            "and encourage them."
        ),
    ),
    "damascus": dict(
        name="Damascus", alt=[], type="city", region="canaan-israel",
        first_reference="Genesis 14:15", id_status="secure", modern="Damascus, Syria",
        major=True,
        references=["Genesis 15:2", "2 Samuel 8:5-6", "1 Kings 19:15", "Acts 9:1-19"],
        desc=(
            "One of the oldest continuously inhabited cities in the world, Damascus was Abraham's servant "
            "Eliezer's hometown (Genesis 15:2) and later the capital of Aram (Syria), a persistent rival and "
            "sometime enemy of Israel through the united and divided monarchies (2 Samuel 8:5-6; 1 Kings 19:15; "
            "2 Kings 8; 16:9). Its greatest New Testament significance is as the destination of Saul of "
            "Tarsus's fateful journey: he was blinded by a vision of the risen Christ on the Damascus road, "
            "healed and baptized there by Ananias, and preached in its synagogues before enemies plotted to "
            "kill him and disciples lowered him over the city wall in a basket to escape (Acts 9:1-25)."
        ),
        ff=(
            "Damascus is one of the oldest cities in the world, and was the capital of ancient Syria, a "
            "country that was often Israel's enemy. Damascus is most famous in the New Testament as the place "
            "Saul (later called Paul) was traveling to when Jesus appeared to him in a bright light. Saul was "
            "blinded, then healed and changed forever in Damascus."
        ),
    ),
    "moab": dict(
        name="Moab", alt=[], type="nation", region="moab-transjordan",
        first_reference="Genesis 19:37", id_status="secure",
        major=True,
        references=["Numbers 22-25", "Ruth 1", "2 Kings 3", "2 Kings 24:2"],
        desc=(
            "A nation east of the Dead Sea descended from Lot's son Moab (Genesis 19:36-38), often hostile "
            "toward Israel. Balak, king of Moab, hired Balaam to curse Israel as they camped nearby (Numbers "
            "22-24), and Moabite women later drew Israelite men into idolatry at Baal-peor (Numbers 25). Ruth "
            "was a Moabite who married into an Israelite family, and after being widowed chose to follow her "
            "mother-in-law Naomi back to Bethlehem and to Naomi's God, later becoming David's great-"
            "grandmother (Ruth 1-4) — striking given that the law of Moses barred Moabites from Israel's "
            "assembly for ten generations (Deuteronomy 23:3-6). Moab remained a recurring military opponent "
            "through the monarchy period and drew judgment oracles from several prophets."
        ),
        ff=(
            "Moab was a nation east of the Dead Sea, and its people were often enemies of Israel. But Moab "
            "is also where Ruth came from — a Moabite woman who chose to leave her home and follow her "
            "mother-in-law Naomi back to Israel, and to trust in Naomi's God. Ruth became the "
            "great-grandmother of King David."
        ),
    ),
    "shechem": dict(
        name="Shechem", alt=["Sychar"], type="city", region="canaan-israel",
        first_reference="Genesis 12:6", id_status="secure", modern="Nablus, West Bank",
        major=True,
        references=["Genesis 34", "Joshua 24:1", "Judges 9", "1 Kings 12:1"],
        desc=(
            "A city in the hill country of Ephraim where Abraham first camped and built an altar upon "
            "entering Canaan (Genesis 12:6-7), and where Jacob later bought land, pitched his tent, and saw "
            "his daughter Dinah violated by the city's prince — provoking Simeon and Levi's brutal revenge "
            "(Genesis 33:18-19; 34). Joshua gathered Israel at Shechem near the end of his life to renew the "
            "covenant (Joshua 24), and it was there that Abimelech, Gideon's son, murdered his brothers and "
            "briefly seized power before the city's own people turned on him (Judges 9). Rehoboam went to "
            "Shechem to be crowned king, only for the northern tribes to reject him there and split the "
            "kingdom under Jeroboam instead (1 Kings 12:1-19)."
        ),
        ff=(
            "Shechem was a city where Abraham built one of his first altars after arriving in Canaan. Jacob "
            "later camped there too. Many years after that, Joshua gathered all of Israel at Shechem to renew "
            "their promise to follow God. It's also the city where the kingdom of Israel split in two, after "
            "the northern tribes refused to accept Solomon's son as their king."
        ),
    ),
    "bethel": dict(
        name="Bethel", alt=["Luz"], type="town", region="canaan-israel",
        first_reference="Genesis 12:8", id_status="secure", modern="Beitin, West Bank",
        major=True,
        references=["Genesis 28:10-22", "Genesis 35:1-15", "1 Kings 12:26-33", "Amos 7:10-13"],
        desc=(
            "Originally called Luz, Bethel (\"house of God\") is where Jacob, fleeing Esau, dreamed of a "
            "stairway to heaven, renamed the site, and vowed to serve God there (Genesis 28:10-22) — a vow "
            "he returned to fulfill years later (Genesis 35:1-15). It later became a center of unauthorized "
            "worship when Jeroboam set up one of his two golden calves there to keep the northern kingdom "
            "from worshiping at Jerusalem (1 Kings 12:26-33), a corruption the prophets Amos and Hosea both "
            "condemned by name; Amos was told outright to leave Bethel's royal sanctuary (Amos 7:10-13). "
            "Deborah judged Israel near there, and Samuel visited Bethel on his judging circuit."
        ),
        ff=(
            "Bethel means \"house of God.\" It's the place where Jacob had a dream about a stairway reaching "
            "up to heaven, and he promised to serve God there. Sadly, years later, King Jeroboam set up a "
            "golden calf for people to worship at Bethel instead of going to God's temple in Jerusalem — "
            "something the prophets spoke out strongly against."
        ),
    ),
}
PLACES_MID = {
    "jericho": dict(
        name="Jericho", alt=["City of Palms"], type="city", region="canaan-israel",
        first_reference="Numbers 22:1", id_status="secure", modern="Tell es-Sultan, West Bank",
        references=["Joshua 2", "Joshua 6", "2 Kings 2:4-8", "Luke 19:1-10"],
        desc=(
            "One of the world's oldest cities, Jericho was the first Canaanite city Israel conquered after "
            "crossing the Jordan — its walls falling after Israel marched around it seven days as God had "
            "instructed, following the spies' earlier reception by Rahab (Joshua 2; 6). Centuries later Elijah "
            "and Elisha passed through it near the Jordan (2 Kings 2:4-8), and it was near Jericho that Jesus "
            "healed blind Bartimaeus and called the tax collector Zacchaeus down from his tree (Mark 10:46-52; "
            "Luke 19:1-10)."
        ),
    ),
    "plains-of-moab": dict(
        name="Plains of Moab", alt=[], type="region", region="moab-transjordan",
        first_reference="Numbers 22:1", id_status="secure",
        references=["Numbers 25", "Numbers 33:48-50", "Deuteronomy 34:1-8"],
        desc=(
            "Israel's final wilderness encampment, on the plains east of the Jordan opposite Jericho, where "
            "Balaam was hired to curse Israel and failed (Numbers 22-24), where Israelite men were drawn into "
            "idolatry and immorality with Moabite women at Baal-peor (Numbers 25), and where Moses delivered "
            "the sermons recorded in Deuteronomy before climbing Mount Nebo to view the promised land and die "
            "there (Deuteronomy 34:1-8)."
        ),
    ),
    "shiloh": dict(
        name="Shiloh", alt=[], type="town", region="canaan-israel",
        first_reference="Joshua 18:1", id_status="secure",
        references=["1 Samuel 1-4", "Jeremiah 7:12-14"],
        desc=(
            "The town where the tabernacle was set up after the conquest and remained Israel's central place "
            "of worship for roughly three centuries, until the Philistines captured the ark of the covenant "
            "(Joshua 18:1; 1 Samuel 4). Eli served as priest and judge there, and it was at Shiloh that Hannah "
            "prayed for a son and later brought young Samuel to serve under Eli (1 Samuel 1-3). Jeremiah later "
            "pointed to Shiloh's ruin as a warning of what unfaithfulness would also bring on Jerusalem's "
            "temple (Jeremiah 7:12-14)."
        ),
    ),
    "gilead": dict(
        name="Gilead", alt=[], type="region", region="moab-transjordan",
        first_reference="Genesis 31:21", id_status="secure",
        references=["Judges 10-12", "1 Kings 17:1", "2 Kings 10:32-33"],
        desc=(
            "A hilly, forested region east of the Jordan settled by the tribes of Gad, Reuben, and half of "
            "Manasseh, whose territory it shared — which is why Scripture attaches individuals to Gilead "
            "without always specifying a single tribe. Jephthah led Gilead's fighting men against Ammon "
            "(Judges 10-12), and Elijah was \"of the settlers of Gilead\" (1 Kings 17:1). It was known for "
            "its balm, a valuable healing resin (Genesis 37:25; Jeremiah 8:22)."
        ),
    ),
    "antioch": dict(
        name="Antioch", alt=["Antioch of Syria"], type="city", region="asia-minor-greece",
        first_reference="Acts 11:19", id_status="secure", modern="Antakya, Turkey",
        id_note=(
            "Distinct from Antioch of Pisidia, a separate inland city in Asia Minor where Paul and Barnabas "
            "preached on their first missionary journey (Acts 13:14-52) — no person in this dataset is tied "
            "specifically to that Antioch rather than this one."
        ),
        references=["Acts 11:19-26", "Acts 13:1-3", "Galatians 2:11-14"],
        desc=(
            "A major Syrian city where believers scattered by persecution first preached the gospel to "
            "Gentiles in large numbers, and where the disciples were first called \"Christians\" (Acts "
            "11:19-26). Barnabas brought Saul there to help teach the growing church, and it was from Antioch "
            "that the Holy Spirit set apart Barnabas and Saul for the first missionary journey (Acts 13:1-3) "
            "— making the city the base of operations for the gospel's spread into the Gentile world. Peter's "
            "hypocrisy over eating with Gentiles was also confronted by Paul there (Galatians 2:11-14)."
        ),
    ),
    "gibeon": dict(
        name="Gibeon", alt=[], type="city", region="canaan-israel",
        first_reference="Joshua 9:3", id_status="secure",
        references=["Joshua 10:1-14", "2 Samuel 2:12-17", "1 Kings 3:4-15"],
        desc=(
            "A Canaanite city whose people tricked Joshua into a treaty by disguising themselves as distant "
            "travelers (Joshua 9), which Israel honored even after discovering the deception — later "
            "defending Gibeon from an Amorite coalition in the battle where the sun stood still (Joshua "
            "10:1-14). A deadly contest between Abner's and Joab's men at Gibeon's pool helped ignite civil "
            "war between the houses of Saul and David (2 Samuel 2:12-17), and it was at Gibeon's high place "
            "that Solomon offered sacrifices and God appeared to him in a dream, granting his request for "
            "wisdom (1 Kings 3:4-15)."
        ),
    ),
    "midian": dict(
        name="Midian", alt=[], type="region", region="midian",
        first_reference="Exodus 2:15", id_status="secure",
        references=["Exodus 2-4", "Numbers 25", "Judges 6-8"],
        desc=(
            "A region and people east of the Gulf of Aqaba, descended from Abraham through Keturah (Genesis "
            "25:1-2). Moses fled to Midian after killing an Egyptian, married Jethro's daughter Zipporah, and "
            "received his call from the burning bush while shepherding there (Exodus 2-4). Midianite women "
            "later helped lead Israel into idolatry at Baal-peor (Numbers 25), and generations later Midianite "
            "raiders oppressed Israel until Gideon, with a vastly outnumbered force, routed them (Judges 6-8)."
        ),
    ),
    "mizpah": dict(
        name="Mizpah", alt=["Mizpeh"], type="town", region="canaan-israel",
        first_reference="Joshua 18:26", id_status="traditional",
        id_note=(
            "Usually located at Tell en-Nasbeh north of Jerusalem, though the exact tell is debated. A "
            "separate Mizpah of Gilead, east of the Jordan (Judges 11:11, 29), is a different place — this "
            "entry covers the Benjaminite Mizpah where every person below is placed."
        ),
        references=["1 Samuel 7:5-13", "1 Samuel 10:17-24", "2 Kings 25:22-25", "Jeremiah 40-41"],
        desc=(
            "A town in Benjamin's territory where Samuel gathered Israel to renew their commitment to God and "
            "won a decisive victory over the Philistines (1 Samuel 7:5-13), and where Saul was later chosen "
            "and presented to the nation as its first king by lot (1 Samuel 10:17-24). After Jerusalem's fall "
            "to Babylon, Mizpah became the seat of Gedaliah, the governor Babylon appointed over the "
            "remaining Judeans — an arrangement that collapsed when Ishmael assassinated Gedaliah there, "
            "prompting the frightened remnant to flee to Egypt against Jeremiah's warning (2 Kings 25:22-25; "
            "Jeremiah 40-41)."
        ),
    ),
    "wilderness-of-paran": dict(
        name="Wilderness of Paran", alt=[], type="wilderness", region="sinai-wilderness",
        first_reference="Genesis 21:21", id_status="traditional",
        id_note="Generally located in the central or northern Sinai Peninsula; its exact boundaries are not fixed by the text.",
        references=["Numbers 10:12", "Numbers 13:1-3", "Numbers 13:26"],
        desc=(
            "A wilderness region where Ishmael settled and where his mother Hagar found him a wife (Genesis "
            "21:21), and later a stage of Israel's wilderness journey between Sinai and Kadesh. It was from "
            "Paran that Moses sent out the twelve spies to scout Canaan, ten of whom returned with a "
            "discouraging report that provoked God's judgment of forty years' wandering (Numbers 13)."
        ),
    ),
    "aram": dict(
        name="Aram", alt=["Syria"], type="nation", region="canaan-israel",
        first_reference="2 Samuel 8:5", id_status="secure",
        references=["1 Kings 20", "2 Kings 5", "2 Kings 8:7-15"],
        desc=(
            "The Aramean kingdom centered on Damascus, a recurring military rival of Israel and Judah "
            "throughout the monarchy period. David subdued Aramean forces allied against him (2 Samuel 8:5-6; "
            "10), and later kings like Ben-hadad and Hazael repeatedly warred with Israel — Naaman, an "
            "Aramean army commander healed of leprosy through Elisha, being a notable exception to the "
            "hostility (2 Kings 5)."
        ),
    ),
    "asia-minor": dict(
        name="Asia Minor", alt=["Anatolia"], type="region", region="asia-minor-greece",
        first_reference="Acts 16:6", id_status="secure", modern="Turkey",
        references=["Acts 16:6-10", "Acts 19", "1 Peter 1:1"],
        desc=(
            "The peninsula (modern Turkey) that hosted much of Paul's missionary work and many of the "
            "churches addressed in the New Testament epistles — Ephesus, Colossae, Laodicea, Iconium, Lystra, "
            "and Derbe among them. Paul's team was at one point supernaturally redirected away from the "
            "province of Asia and toward Macedonia instead (Acts 16:6-10), and Peter's first letter is "
            "addressed to believers scattered across several of the region's provinces (1 Peter 1:1)."
        ),
    ),
    "assyria": dict(
        name="Assyria", alt=[], type="nation", region="mesopotamia",
        first_reference="Genesis 10:11", id_status="secure",
        references=["2 Kings 15:19-20", "2 Kings 17:1-6", "2 Kings 18-19"],
        desc=(
            "A powerful Mesopotamian empire that became the northern kingdom of Israel's chief threat, "
            "exacting tribute under kings like Tiglath-pileser and Shalmaneser before finally conquering and "
            "deporting Israel's population in 722 BC under Sargon (2 Kings 15:19-20; 17:1-6). Assyria under "
            "Sennacherib also besieged Jerusalem in Hezekiah's reign, only to withdraw after God struck down "
            "the Assyrian army (2 Kings 18-19). Jonah was sent to preach repentance to Assyria's capital, "
            "Nineveh (Jonah 1:1-2)."
        ),
    ),
    "beersheba": dict(
        name="Beersheba", alt=["Well of the Oath"], type="town", region="canaan-israel",
        first_reference="Genesis 21:14", id_status="secure", modern="Beersheba, Israel",
        references=["Genesis 21:22-34", "Genesis 26:23-33", "1 Kings 19:3"],
        desc=(
            "A well and settlement in Canaan's southern edge where Abraham made a covenant with Abimelech and "
            "named the site for their oath (Genesis 21:22-34), and where Isaac later dug his own well and "
            "renewed the same covenant (Genesis 26:23-33). \"From Dan to Beersheba\" became a standard phrase "
            "for the whole extent of Israel's territory (Judges 20:1). Elijah fled there, exhausted, after "
            "fleeing Jezebel's threat (1 Kings 19:3)."
        ),
    ),
    "gibeah": dict(
        name="Gibeah", alt=["Gibeah of Saul"], type="town", region="canaan-israel",
        first_reference="Judges 19:12", id_status="secure",
        references=["Judges 19-20", "1 Samuel 10:26", "1 Samuel 11:4"],
        desc=(
            "A Benjaminite town whose men's horrific crime against a Levite's concubine triggered a civil war "
            "that nearly wiped out the tribe of Benjamin (Judges 19-20). It later became the hometown and "
            "capital of Israel's first king, Saul, whose family — including Jonathan and Michal — is "
            "repeatedly identified with the place (1 Samuel 10:26; 11:4)."
        ),
    ),
    "jezreel": dict(
        name="Jezreel", alt=[], type="town", region="canaan-israel",
        first_reference="Joshua 19:18", id_status="secure",
        references=["1 Kings 21", "2 Kings 9:30-37"],
        desc=(
            "A town in the fertile valley of the same name, site of Ahab and Jezebel's royal residence and of "
            "Naboth's vineyard, which Jezebel seized after arranging Naboth's murder — provoking Elijah's "
            "denunciation of the royal house (1 Kings 21). Jezebel later met her violent, prophesied death "
            "there when Jehu came to seize the throne (2 Kings 9:30-37)."
        ),
    ),
    "mahanaim": dict(
        name="Mahanaim", alt=[], type="town", region="moab-transjordan",
        first_reference="Genesis 32:2", id_status="secure",
        references=["2 Samuel 2:8-9", "2 Samuel 17:24-27"],
        desc=(
            "A place east of the Jordan where Jacob, returning to Canaan, was met by angels and named the "
            "site \"two camps\" (Genesis 32:1-2). It later became Ish-bosheth's capital when Abner made him "
            "king over Israel against David (2 Samuel 2:8-9), and still later the refuge David fled to during "
            "Absalom's rebellion, where he received support from Machir and Barzillai (2 Samuel 17:24-27)."
        ),
    ),
    "mount-sinai": dict(
        name="Mount Sinai", alt=["Horeb"], type="mountain", region="sinai-wilderness",
        first_reference="Exodus 19:1", id_status="traditional",
        id_note="Traditionally identified with Jebel Musa in the southern Sinai Peninsula, though the exact peak is disputed and not stated by the text.",
        references=["Exodus 19-20", "Exodus 24", "1 Kings 19:8"],
        desc=(
            "The mountain where God gave Moses the Ten Commandments amid thunder, smoke, and fire, and where "
            "Moses and Israel's elders later confirmed the covenant (Exodus 19-20; 24). Also called Horeb, it "
            "is where Moses first encountered God at the burning bush (Exodus 3:1) and where, generations "
            "later, Elijah fled and heard God speak in a gentle whisper rather than the wind, earthquake, or "
            "fire (1 Kings 19:8-13)."
        ),
    ),
    "tirzah": dict(
        name="Tirzah", alt=[], type="city", region="canaan-israel",
        first_reference="Joshua 12:24", id_status="secure",
        references=["1 Kings 15:33", "1 Kings 16:8-24"],
        desc=(
            "An early capital of the northern kingdom of Israel before Omri built Samaria, serving as the "
            "royal seat under kings including Baasha, Elah, and Zimri. Zimri's seven-day reign ended when he "
            "burned the palace down over himself there rather than face Omri's siege (1 Kings 16:8-18), after "
            "which Omri eventually relocated the capital to Samaria."
        ),
    ),
    "ammon": dict(
        name="Ammon", alt=[], type="nation", region="moab-transjordan",
        first_reference="Genesis 19:38", id_status="secure",
        references=["Judges 10-11", "2 Samuel 10", "Nehemiah 2:19"],
        desc=(
            "A nation east of the Jordan descended from Lot's younger son Ben-ammi (Genesis 19:36-38), "
            "frequently hostile to Israel. Jephthah defeated Ammonite forces oppressing Israel (Judges 10-11), "
            "and Ammon's king Hanun's humiliation of David's envoys sparked a war (2 Samuel 10). Ammonite "
            "officials like Tobiah later opposed Nehemiah's rebuilding of Jerusalem's walls (Nehemiah 2:19; "
            "4:3)."
        ),
    ),
    "cyprus": dict(
        name="Cyprus", alt=[], type="region", region="asia-minor-greece",
        first_reference="Acts 4:36", id_status="secure", modern="Cyprus",
        references=["Acts 11:19-20", "Acts 13:4-12"],
        desc=(
            "A Mediterranean island, Barnabas's homeland (Acts 4:36), where some believers scattered by "
            "persecution first preached to Greeks as well as Jews (Acts 11:19-20). Barnabas and Saul made it "
            "the first stop of their missionary journey, confronting the sorcerer Bar-Jesus and seeing the "
            "Roman proconsul Sergius Paulus believe (Acts 13:4-12); Barnabas and his cousin Mark later "
            "returned there together after parting ways with Paul (Acts 15:39)."
        ),
    ),
    "edom": dict(
        name="Edom", alt=["Seir"], type="nation", region="canaan-israel",
        first_reference="Genesis 36:1", id_status="secure",
        references=["Numbers 20:14-21", "2 Kings 8:20-22", "Obadiah"],
        desc=(
            "The nation descended from Esau (also called Edom), settled in the mountainous region of Seir "
            "south of the Dead Sea. Edom refused Israel passage during the wilderness years (Numbers 20:14-21) "
            "and remained a persistent, often bitter rival through the monarchy — rebelling against Judah's "
            "control under Jehoram (2 Kings 8:20-22) and later gloating over Jerusalem's fall, which the "
            "book of Obadiah condemns at length."
        ),
    ),
    "gerar": dict(
        name="Gerar", alt=[], type="town", region="canaan-israel",
        first_reference="Genesis 20:1", id_status="secure",
        references=["Genesis 26:1-33"],
        desc=(
            "A Philistine town in Canaan's south where both Abraham and, later, Isaac sojourned during "
            "famines and each, in turn, told local king Abimelech his wife was his sister out of fear — "
            "deceptions God intervened to expose both times (Genesis 20; 26:1-11). Isaac also dug and "
            "redug wells there amid disputes with Gerar's herdsmen (Genesis 26:12-33)."
        ),
    ),
    "gilgal": dict(
        name="Gilgal", alt=[], type="town", region="canaan-israel",
        first_reference="Joshua 4:19", id_status="secure",
        id_note=(
            "This is the Gilgal near Jericho where Israel first camped after crossing the Jordan. A second "
            "Gilgal in the hill country near Bethel is where Elijah and Elisha's prophetic circuit passed "
            "(2 Kings 2:1; 4:38) and may be the place meant for Elisha here — the two sites are sometimes "
            "conflated, but this entry follows the better-attested Gilgal of Joshua and Samuel."
        ),
        references=["Joshua 5:2-12", "1 Samuel 11:14-15", "1 Samuel 15:10-33"],
        desc=(
            "Israel's first camp in Canaan after crossing the Jordan, where the twelve memorial stones were "
            "set up and the nation was circumcised and kept its first Passover in the land (Joshua 4:19-5:12). "
            "Saul was confirmed as king there (1 Samuel 11:14-15), and it was at Gilgal that Samuel confronted "
            "Saul for disobeying God's instructions regarding Amalek and announced that his kingdom would be "
            "torn from him (1 Samuel 15:10-33)."
        ),
    ),
    "judea": dict(
        name="Judea", alt=[], type="region", region="canaan-israel",
        first_reference="Ezra 5:8", id_status="secure",
        references=["Matthew 2:1", "Luke 3:1", "John 4:3"],
        desc=(
            "The Roman-era name for the southern portion of the former kingdom of Judah, including Jerusalem, "
            "governed at different times by Herod the Great, his son Archelaus, and Roman prefects including "
            "Pontius Pilate (Matthew 2:1; Luke 3:1). Jesus's public ministry moved between Judea and Galilee, "
            "and it was in Judea's wilderness that John the Baptist preached (Matthew 3:1)."
        ),
    ),
    "lachish": dict(
        name="Lachish", alt=[], type="city", region="canaan-israel",
        first_reference="Joshua 10:3", id_status="secure",
        references=["Joshua 10:31-32", "2 Kings 18:13-17", "2 Kings 19:8"],
        desc=(
            "A fortified Canaanite city Joshua conquered during his southern campaign (Joshua 10:31-32), "
            "later one of Judah's most important fortress cities. Sennacherib of Assyria besieged and captured "
            "Lachish and used it as his base while negotiating (and threatening) with Hezekiah's officials "
            "over Jerusalem (2 Kings 18:13-17; 19:8)."
        ),
    ),
    "nazareth": dict(
        name="Nazareth", alt=[], type="town", region="canaan-israel",
        first_reference="Matthew 2:23", id_status="secure", modern="Nazareth, Israel",
        references=["Luke 1:26-38", "Luke 2:39-40", "Luke 4:16-30"],
        desc=(
            "A small, unremarkable Galilean town — Nathanael's skeptical \"can any good thing come out of "
            "Nazareth?\" (John 1:46) reflects its reputation — where the angel Gabriel announced Jesus's birth "
            "to Mary (Luke 1:26-38) and where Jesus grew up after His family's return from Egypt (Matthew "
            "2:23; Luke 2:39-40). When Jesus later preached there and identified Himself as the fulfillment of "
            "Isaiah's prophecy, His own townspeople tried to throw Him off a cliff (Luke 4:16-30)."
        ),
    ),
    "nineveh": dict(
        name="Nineveh", alt=[], type="city", region="mesopotamia",
        first_reference="Genesis 10:11", id_status="secure", modern="near Mosul, Iraq",
        references=["Jonah 1:2", "Jonah 3", "Nahum 1:1"],
        desc=(
            "Capital of the Assyrian Empire, the city God sent Jonah to warn of coming judgment (Jonah 1:2). "
            "Jonah initially fled the assignment, but when he finally preached there the entire city — from "
            "the king down — repented, and God relented from destroying it (Jonah 3). A century or so later, "
            "the prophet Nahum announced Nineveh's coming, and final, destruction, which came at the hands of "
            "Babylon and its allies in 612 BC (Nahum 1:1; 3:1-19)."
        ),
    ),
    "uz": dict(
        name="Uz", alt=[], type="region", region="canaan-israel",
        first_reference="Job 1:1", id_status="unknown",
        id_note="Scholars propose locations in Edom or the Arabian desert east of Canaan, but the text does not fix a precise location.",
        references=["Lamentations 4:21"],
        desc=(
            "The homeland of Job, described as \"the greatest of all the men of the east\" before his sudden "
            "loss of family, wealth, and health became the subject of the book that bears his name (Job 1:1-3). "
            "Its location is not certain, though Lamentations 4:21 associates the name loosely with Edom."
        ),
    ),
    "valley-of-siddim": dict(
        name="Valley of Siddim", alt=["Vale of Siddim"], type="valley", region="canaan-israel",
        first_reference="Genesis 14:3", id_status="disputed",
        id_note="Traditionally identified with the area now under the Dead Sea's shallow southern basin, though this is not archaeologically provable.",
        references=["Genesis 14:1-12"],
        desc=(
            "\"The Salt Sea\" valley where the kings of Sodom, Gomorrah, and three other cities battled an "
            "invading coalition led by Chedorlaomer of Elam and were defeated, with Lot taken captive among "
            "the spoil — prompting Abraham's rescue mission (Genesis 14:1-16)."
        ),
    ),
    "capernaum": dict(
        name="Capernaum", alt=[], type="town", region="canaan-israel",
        first_reference="Matthew 4:13", id_status="secure", modern="Kfar Nahum, Israel",
        references=["Mark 1:21-29", "Matthew 9:9", "Mark 5:21-24"],
        desc=(
            "A fishing town on the Sea of Galilee's north shore that Jesus made the base of much of His "
            "Galilean ministry after leaving Nazareth (Matthew 4:13). It was Peter's hometown, the site of "
            "Jesus's synagogue teaching and many healings — including Peter's mother-in-law and a paralyzed "
            "man lowered through the roof — and where Matthew was called from his tax booth (Mark 1:21-29; "
            "2:1-14; Matthew 9:9)."
        ),
    ),
    "colossae": dict(
        name="Colossae", alt=[], type="city", region="asia-minor-greece",
        first_reference="Colossians 1:2", id_status="secure",
        references=["Colossians 4:12-17", "Philemon 1:1-2"],
        desc=(
            "A city in the Lycus Valley of Asia Minor, home to a church Paul had not personally founded or "
            "visited but wrote to (via Epaphras's report) to combat false teaching that diminished Christ's "
            "supremacy (Colossians 1:2, 7; 2:8-23). Philemon and the runaway slave Onesimus, addressed in "
            "Paul's shortest letter, were also from Colossae."
        ),
    ),
    "garden-of-eden": dict(
        name="Garden of Eden", alt=["Eden"], type="region", region="mesopotamia",
        first_reference="Genesis 2:8", id_status="disputed",
        id_note=(
            "Genesis 2:10-14 names four rivers, two of which (Tigris and Euphrates) are known today, "
            "suggesting a location in or near Mesopotamia — but the other two rivers cannot be securely "
            "identified, and no modern site is confidently proposed. Treated here as the location Scripture "
            "describes, not a claim about a discoverable spot on today's map."
        ),
        references=["Genesis 2:8-3:24"],
        desc=(
            "The garden God planted and placed the first man in, containing the tree of life and the tree of "
            "the knowledge of good and evil (Genesis 2:8-17). Adam and Eve lived there until their "
            "disobedience led to their expulsion, with cherubim and a flaming sword set to guard the way back "
            "(Genesis 3)."
        ),
    ),
    "gob": dict(
        name="Gob", alt=[], type="town", region="canaan-israel",
        first_reference="2 Samuel 21:18", id_status="unknown",
        id_note="Not identified with any known modern site; some manuscripts and the parallel account in 1 Chronicles 20:4 read \"Gezer\" instead.",
        references=["2 Samuel 21:18-22"],
        desc=(
            "The site of battles between David's men and Philistine giants descended from the Rapha, "
            "including Elhanan's killing of Goliath's brother Lahmi (2 Samuel 21:18-22)."
        ),
    ),
    "hill-country-of-ephraim": dict(
        name="Hill Country of Ephraim", alt=["Mount Ephraim"], type="region", region="canaan-israel",
        first_reference="Joshua 17:15", id_status="secure",
        references=["Judges 3:26-27", "Judges 4:4-5", "Judges 17:1"],
        desc=(
            "The forested highland territory allotted to Ephraim, a base of operations for several judges: "
            "Ehud rallied Israel's army from there after killing Eglon (Judges 3:26-27), and Deborah held "
            "court under a palm tree in the same hill country (Judges 4:4-5)."
        ),
    ),
    "jordan-river": dict(
        name="Jordan River", alt=[], type="body-of-water", region="canaan-israel",
        first_reference="Genesis 13:10", id_status="secure",
        references=["Joshua 3", "2 Kings 5:1-14", "Matthew 3:13-17"],
        desc=(
            "Israel's principal river, flowing from the Sea of Galilee to the Dead Sea and forming much of "
            "the eastern boundary of the promised land. Israel crossed it on dry ground entering Canaan "
            "(Joshua 3), Naaman was healed of leprosy after washing in it seven times at Elisha's instruction "
            "(2 Kings 5:1-14), and John the Baptist baptized Jesus in its waters (Matthew 3:13-17)."
        ),
    ),
    "makkedah": dict(
        name="Makkedah", alt=[], type="town", region="canaan-israel",
        first_reference="Joshua 10:10", id_status="unknown",
        id_note="Site not confidently identified with a modern location.",
        references=["Joshua 10:16-28"],
        desc=(
            "A town near which five Amorite kings, defeated in Joshua's southern campaign, hid in a cave and "
            "were captured, executed, and buried by Joshua (Joshua 10:16-28)."
        ),
    ),
    "mesopotamia": dict(
        name="Mesopotamia", alt=[], type="region", region="mesopotamia",
        first_reference="Genesis 24:10", id_status="secure",
        references=["Acts 2:9", "Acts 7:2"],
        desc=(
            "The land \"between the rivers\" Tigris and Euphrates, home to the earliest post-flood "
            "civilizations of Genesis 10-11 and, in a broader sense, the wider region Abraham's family "
            "originally came from before settling in Haran (Acts 7:2)."
        ),
    ),
    "persia": dict(
        name="Persia", alt=[], type="nation", region="mesopotamia",
        first_reference="2 Chronicles 36:20", id_status="secure", modern="Iran",
        references=["Ezra 1:1-4", "Esther 1:1", "Daniel 6"],
        desc=(
            "The empire that conquered Babylon and, under Cyrus, issued the decree allowing exiled Jews to "
            "return and rebuild Jerusalem's temple (Ezra 1:1-4; 2 Chronicles 36:20-23). Esther became queen "
            "of Persia under Ahasuerus, and Daniel served in its administration under Darius, surviving the "
            "lions' den (Daniel 6)."
        ),
    ),
    "philippi": dict(
        name="Philippi", alt=[], type="city", region="asia-minor-greece",
        first_reference="Acts 16:12", id_status="secure",
        references=["Acts 16:12-40", "Philippians 1:1"],
        desc=(
            "A Roman colony in Macedonia and the first place in Europe where Paul preached, following a "
            "vision calling him there (Acts 16:9-12). Lydia was converted and hosted the missionaries; Paul "
            "and Silas were later imprisoned and miraculously freed after an earthquake, leading to the "
            "jailer's conversion (Acts 16:13-40). Paul's warm letter to the Philippians was written to the "
            "church founded there."
        ),
    ),
    "rabbah": dict(
        name="Rabbah", alt=["Rabbah of the Ammonites"], type="city", region="moab-transjordan",
        first_reference="Deuteronomy 3:11", id_status="secure", modern="Amman, Jordan",
        references=["2 Samuel 11:1", "2 Samuel 12:26-31"],
        desc=(
            "Capital of Ammon, besieged by Joab's army in the campaign during which David arranged Uriah's "
            "death while Uriah's own unit fought at its walls (2 Samuel 11:1, 14-17). Joab later called David "
            "to finish the siege personally, and David took the city and its crown (2 Samuel 12:26-31)."
        ),
    ),
    "ararat": dict(
        name="Ararat", alt=["Mountains of Ararat"], type="mountain", region="mesopotamia",
        first_reference="Genesis 8:4", id_status="disputed",
        id_note="Traditionally associated with the mountains of modern eastern Turkey, but the text names a mountain range, not a single peak, and no exact site is fixed.",
        references=["2 Kings 19:37"],
        desc=(
            "The mountains where Noah's ark came to rest as the floodwaters receded (Genesis 8:4). "
            "Sennacherib's sons later fled there after murdering him (2 Kings 19:37)."
        ),
    ),
    "bahurim": dict(
        name="Bahurim", alt=[], type="town", region="canaan-israel",
        first_reference="2 Samuel 3:16", id_status="unknown",
        references=["2 Samuel 16:5-13", "2 Samuel 17:18-20"],
        desc=(
            "A Benjaminite town where Shimei cursed and threw stones at David as he fled Absalom's rebellion "
            "(2 Samuel 16:5-13), and where a woman hid David's spies Ahimaaz and Jonathan in a well to save "
            "them from Absalom's search party (2 Samuel 17:18-20)."
        ),
    ),
    "bethany": dict(
        name="Bethany", alt=[], type="village", region="canaan-israel",
        first_reference="Matthew 21:17", id_status="secure",
        references=["Luke 10:38-42", "John 11:1-44"],
        desc=(
            "A village near Jerusalem, home to the siblings Martha, Mary, and Lazarus, whom Jesus loved and "
            "regularly visited (Luke 10:38-42; John 11:1-5). It was in Bethany that Jesus raised Lazarus from "
            "the dead after four days in the tomb (John 11:1-44), and where He often stayed during His final "
            "week in Jerusalem."
        ),
    ),
    "gath": dict(
        name="Gath", alt=[], type="city", region="canaan-israel",
        first_reference="Joshua 11:22", id_status="secure",
        references=["1 Samuel 17:4", "1 Samuel 21:10-15", "1 Samuel 27:1-4"],
        desc=(
            "One of the five main Philistine cities and the hometown of Goliath (1 Samuel 17:4). David later "
            "fled to Gath's king Achish twice — once feigning madness to escape (1 Samuel 21:10-15), and later "
            "living there openly with his men as a vassal to escape Saul (1 Samuel 27:1-4)."
        ),
    ),
    "haran": dict(
        name="Haran", alt=[], type="city", region="mesopotamia",
        first_reference="Genesis 11:31", id_status="secure", modern="Harran, Turkey",
        references=["Genesis 12:4-5", "Genesis 27:43", "Genesis 29:4"],
        desc=(
            "A city in upper Mesopotamia where Abraham's family settled on their way from Ur, and where "
            "Abraham's father Terah died before Abraham continued on to Canaan at God's call (Genesis 11:31-"
            "12:5). Both Isaac's servant and, later, Jacob traveled back to Haran's vicinity to find wives "
            "among Abraham's extended family there (Genesis 24; 27:43-29:4)."
        ),
    ),
    "kadesh-barnea": dict(
        name="Kadesh-barnea", alt=["Kadesh"], type="town", region="sinai-wilderness",
        first_reference="Genesis 14:7", id_status="traditional",
        id_note="Usually identified with the oasis of Ain el-Qudeirat in the northern Sinai/Negev border area.",
        references=["Numbers 13:26", "Numbers 20:1-13", "Deuteronomy 1:19-46"],
        desc=(
            "A wilderness oasis that served as Israel's main base during much of the forty years of "
            "wandering. The twelve spies returned there with their report of Canaan (Numbers 13:26), and it "
            "was at Kadesh that Moses, in frustration, struck the rock instead of speaking to it as commanded "
            "— an act of disobedience that cost him entry into the promised land (Numbers 20:1-13)."
        ),
    ),
    "karkor": dict(
        name="Karkor", alt=[], type="town", region="moab-transjordan",
        first_reference="Judges 8:10", id_status="unknown",
        references=["Judges 8:10-12"],
        desc=(
            "A place in Transjordan where the Midianite kings Zebah and Zalmunna made their camp with their "
            "surviving forces after fleeing Gideon, before Gideon overtook and captured them there (Judges "
            "8:10-12)."
        ),
    ),
    "kiriath-jearim": dict(
        name="Kiriath-jearim", alt=["Baale-judah"], type="town", region="canaan-israel",
        first_reference="Joshua 9:17", id_status="secure",
        references=["1 Samuel 6:21-7:2", "2 Samuel 6:2-4"],
        desc=(
            "A town where the ark of the covenant rested for twenty years after the Philistines returned it, "
            "kept in the house of Abinadab and cared for by his son Eleazar (1 Samuel 7:1-2), before David "
            "later moved it from there toward Jerusalem (2 Samuel 6:2-4)."
        ),
    ),
    "lo-debar": dict(
        name="Lo-debar", alt=[], type="town", region="moab-transjordan",
        first_reference="2 Samuel 9:4", id_status="unknown",
        references=["2 Samuel 9:1-13", "2 Samuel 17:27"],
        desc=(
            "A town in Transjordan where Saul's grandson Mephibosheth, lame in both feet, was living in "
            "hiding when David sought him out to show him kindness for Jonathan's sake, restoring Saul's land "
            "to him and inviting him to eat at the king's table (2 Samuel 9)."
        ),
    ),
    "lystra": dict(
        name="Lystra", alt=[], type="city", region="asia-minor-greece",
        first_reference="Acts 14:6", id_status="secure",
        references=["Acts 14:8-20", "2 Timothy 1:5"],
        desc=(
            "A city in Asia Minor where Paul healed a man lame from birth, prompting the crowd to try to "
            "worship him and Barnabas as gods before the same crowd, incited by opponents, stoned Paul and "
            "left him for dead (Acts 14:8-20). Timothy, whose grandmother Lois and mother Eunice had genuine "
            "faith, was from Lystra (2 Timothy 1:5)."
        ),
    ),
    "mount-gilboa": dict(
        name="Mount Gilboa", alt=[], type="mountain", region="canaan-israel",
        first_reference="1 Samuel 28:4", id_status="secure",
        references=["1 Samuel 31:1-6"],
        desc=(
            "The mountain range where Saul's final battle against the Philistines took place, ending with "
            "the deaths of Saul and three of his sons, including Jonathan, and Saul's own suicide rather than "
            "capture (1 Samuel 31:1-6)."
        ),
    ),
    "mount-tabor": dict(
        name="Mount Tabor", alt=[], type="mountain", region="canaan-israel",
        first_reference="Judges 4:6", id_status="secure",
        references=["Judges 4:12-16"],
        desc=(
            "A prominent, isolated hill in the Jezreel Valley where Deborah directed Barak to gather Israel's "
            "forces before their victory over Sisera's chariot army (Judges 4:6, 12-16)."
        ),
    ),
    "nob": dict(
        name="Nob", alt=[], type="town", region="canaan-israel",
        first_reference="1 Samuel 21:1", id_status="unknown",
        references=["1 Samuel 21:1-9", "1 Samuel 22:9-19"],
        desc=(
            "A priestly town where the fugitive David received bread and Goliath's sword from the priest "
            "Ahimelech (1 Samuel 21:1-9), an act of unwitting help that led Saul, informed by Doeg the "
            "Edomite, to order the massacre of Nob's priests and townspeople (1 Samuel 22:9-19)."
        ),
    ),
    "ophrah": dict(
        name="Ophrah", alt=[], type="town", region="canaan-israel",
        first_reference="Judges 6:11", id_status="unknown",
        references=["Judges 6:11-32", "Judges 8:27-32", "Judges 9:5"],
        desc=(
            "Gideon's hometown, where the angel of the Lord commissioned him and where he tore down his "
            "father's altar to Baal (Judges 6:11-32). Gideon later made an idolatrous ephod there that became "
            "a snare to Israel (Judges 8:27), and it was there that Abimelech murdered nearly all of his "
            "seventy half-brothers (Judges 9:5)."
        ),
    ),
    "penuel": dict(
        name="Penuel", alt=["Peniel"], type="town", region="moab-transjordan",
        first_reference="Genesis 32:30", id_status="unknown",
        references=["Judges 8:8-17"],
        desc=(
            "The place where Jacob wrestled all night with a divine visitor, was given the name Israel, and "
            "named the site \"the face of God\" (Genesis 32:24-30). Gideon later destroyed its tower after its "
            "men refused to help his pursuit of the Midianite kings (Judges 8:8-9, 17)."
        ),
    ),
    "philistine-territory": dict(
        name="Philistine Territory", alt=["Philistia"], type="region", region="canaan-israel",
        first_reference="Genesis 21:32", id_status="secure",
        references=["Judges 13-16", "1 Samuel 4-6"],
        desc=(
            "The coastal region of five allied Philistine cities (Gaza, Ashkelon, Ashdod, Gath, and Ekron) "
            "that repeatedly warred with Israel, especially during the judges period through Samson's "
            "conflicts with them (Judges 13-16) and their capture and forced return of the ark of the "
            "covenant (1 Samuel 4-6)."
        ),
    ),
    "ramathaim-zophim": dict(
        name="Ramathaim-zophim", alt=["Ramah"], type="town", region="canaan-israel",
        first_reference="1 Samuel 1:1", id_status="secure",
        references=["1 Samuel 1:19-20", "1 Samuel 2:11"],
        desc=(
            "The home of Elkanah and his wives Hannah and Peninnah in the hill country of Ephraim, where "
            "Hannah's prayers for a child were answered with the birth of Samuel, whom she later brought to "
            "Shiloh to serve the Lord as she had vowed (1 Samuel 1:1-2:11)."
        ),
    ),
    "riblah": dict(
        name="Riblah", alt=[], type="town", region="canaan-israel",
        first_reference="2 Kings 23:33", id_status="secure",
        references=["2 Kings 25:6-7", "2 Kings 25:18-21"],
        desc=(
            "A town in Syria used as a military headquarters by Egyptian and Babylonian kings. It was at "
            "Riblah that Nebuchadnezzar had King Zedekiah's sons killed before his eyes, then blinded him "
            "(2 Kings 25:6-7), and later executed a group of Judah's remaining leaders and priests, including "
            "Seraiah, brought there from captured Jerusalem (2 Kings 25:18-21)."
        ),
    ),
    "timnah": dict(
        name="Timnah", alt=[], type="town", region="canaan-israel",
        first_reference="Genesis 38:12", id_status="secure",
        references=["Judges 14:1-5"],
        desc=(
            "A town where Judah went for sheep-shearing and was met, and deceived, by his widowed "
            "daughter-in-law Tamar disguised as a prostitute (Genesis 38:12-19). Generations later it was "
            "home to the Philistine woman Samson wanted to marry, setting off his riddle contest and conflict "
            "with the Philistines (Judges 14)."
        ),
    ),
    "transjordan": dict(
        name="Transjordan", alt=["East of the Jordan"], type="region", region="moab-transjordan",
        first_reference="Numbers 32:1", id_status="secure",
        references=["Numbers 32", "Joshua 22"],
        desc=(
            "The territory east of the Jordan River that the tribes of Reuben, Gad, and half of Manasseh "
            "requested and received as their inheritance because of its suitability for their large herds, "
            "on condition that their fighting men first help conquer Canaan proper (Numbers 32; Joshua 22)."
        ),
    ),
    "tyre": dict(
        name="Tyre", alt=[], type="city", region="asia-minor-greece",
        first_reference="Joshua 19:29", id_status="secure", modern="Tyre, Lebanon",
        references=["2 Samuel 5:11", "1 Kings 5:1-12", "Acts 21:3-6"],
        desc=(
            "A wealthy Phoenician port city whose king Hiram supplied cedar, craftsmen, and materials to "
            "David and Solomon for their building projects, including the temple, in a long friendly alliance "
            "(2 Samuel 5:11; 1 Kings 5:1-12). Paul's ship stopped there and he spent a week with Tyre's "
            "disciples on his final journey to Jerusalem (Acts 21:3-6)."
        ),
    ),
    "ur-of-the-chaldeans": dict(
        name="Ur of the Chaldeans", alt=["Ur"], type="city", region="mesopotamia",
        first_reference="Genesis 11:28", id_status="traditional",
        id_note="Widely identified with Tell el-Muqayyar in southern Iraq, though some scholars propose a northern Mesopotamian location instead.",
        references=["Genesis 11:31", "Genesis 15:7", "Nehemiah 9:7"],
        desc=(
            "Abraham's family's original home before they migrated toward Canaan and settled partway in "
            "Haran (Genesis 11:28-31). God later reminded Abraham that He was the one who brought him out of "
            "Ur (Genesis 15:7; Nehemiah 9:7)."
        ),
    ),
    "valley-of-elah": dict(
        name="Valley of Elah", alt=[], type="valley", region="canaan-israel",
        first_reference="1 Samuel 17:2", id_status="secure",
        references=["1 Samuel 17:1-54"],
        desc=(
            "The valley where the Israelite and Philistine armies camped on opposite hillsides while Goliath "
            "issued his daily challenge, and where the shepherd boy David killed him with a sling and stone "
            "(1 Samuel 17)."
        ),
    ),
    "zoar": dict(
        name="Zoar", alt=["Bela"], type="town", region="canaan-israel",
        first_reference="Genesis 13:10", id_status="unknown",
        id_note="Traditionally placed near the Dead Sea's southeastern shore, but not confidently located.",
        references=["Genesis 19:20-23"],
        desc=(
            "The small town Lot fled to for refuge when Sodom and Gomorrah were destroyed, spared at his "
            "request because of its smallness (Genesis 19:20-23) — before Lot left it too, fearful, for a "
            "cave in the nearby hills."
        ),
    ),
}
PLACES_MINOR = {
    "anathoth": dict(name="Anathoth", type="town", region="canaan-israel", first_reference="Joshua 21:18",
        desc="A priestly town in Benjamin, the hometown of the prophet Jeremiah (Jeremiah 1:1), who later bought a field there from his cousin Hanamel as a prophetic sign of restoration even amid Jerusalem's fall (Jeremiah 32:6-15)."),
    "asia-roman-province": dict(name="Asia (Roman Province)", type="region", region="asia-minor-greece", first_reference="Romans 16:5",
        desc="The Roman province covering western Asia Minor; Paul's letter to the Romans greets Epaenetus as its first convert there (Romans 16:5)."),
    "athens": dict(name="Athens", type="city", region="asia-minor-greece", first_reference="Acts 17:15", modern="Athens, Greece",
        desc="The center of Greek philosophy and culture, where Paul reasoned in the synagogue and marketplace and addressed the Areopagus council on \"the unknown god,\" with Dionysius and Damaris among those who believed (Acts 17:16-34)."),
    "bashan": dict(name="Bashan", type="region", region="moab-transjordan", first_reference="Genesis 14:5",
        desc="A fertile region east of the Jordan ruled by Og, a king of the remnant of the Rephaim giants, whom Israel defeated on the way to Canaan (Numbers 21:33-35; Deuteronomy 3:1-11)."),
    "bethsaida": dict(name="Bethsaida", type="town", region="canaan-israel", first_reference="Matthew 11:21",
        desc="A fishing town on the Sea of Galilee, home of Philip and Andrew (John 1:44), that Jesus rebuked for failing to repent despite witnessing His miracles (Matthew 11:21)."),
    "carmel-of-judah": dict(name="Carmel (of Judah)", type="town", region="canaan-israel", first_reference="1 Samuel 15:12",
        id_status="secure", id_note="Distinct from Mount Carmel, the mountain in the north associated with Elijah — this Carmel is a town in Judah's hill country.",
        desc="A town in Judah's hill country where the wealthy but foolish Nabal kept his flocks; his wife Abigail's wise intervention there kept David from bloodshed after Nabal insulted him (1 Samuel 25)."),
    "casiphia": dict(name="Casiphia", type="town", region="mesopotamia", first_reference="Ezra 8:17",
        desc="A settlement in Babylonia where Ezra sent for Levites to accompany the returning exiles to Jerusalem, since none had yet joined his group (Ezra 8:15-20)."),
    "crete": dict(name="Crete", type="region", region="asia-minor-greece", first_reference="Acts 27:7", modern="Crete, Greece",
        desc="A large Mediterranean island Paul's ship sailed along on the voyage to Rome (Acts 27:7-13), and where Titus was later left to appoint elders and organize the churches (Titus 1:5)."),
    "dan": dict(name="Dan", type="town", region="canaan-israel", first_reference="Genesis 14:14",
        id_status="secure", id_note="Originally called Laish before the tribe of Dan conquered and renamed it (Judges 18:29).",
        desc="The northernmost town of Israel's territory, giving rise to the phrase \"from Dan to Beersheba\" for the land's full extent; Jeroboam later set up one of his two idolatrous golden calves there (1 Kings 12:29-30)."),
    "debir": dict(name="Debir", type="town", region="canaan-israel", first_reference="Joshua 10:38",
        id_status="secure", id_note="Also called Kiriath-sepher.",
        desc="A town Caleb offered his daughter Achsah in marriage to whoever captured it; his nephew Othniel took it and won her hand (Joshua 15:15-17; Judges 1:11-13)."),
    "gallim": dict(name="Gallim", type="town", region="canaan-israel", first_reference="1 Samuel 25:44",
        desc="The town Saul gave his daughter Michal to in marriage to Palti after taking her from David (1 Samuel 25:44)."),
    "havvoth-jair": dict(name="Havvoth-jair", type="region", region="moab-transjordan", first_reference="Numbers 32:41",
        desc="A group of villages in Gilead named for Jair, a descendant of Manasseh who captured them (Numbers 32:41; Deuteronomy 3:14)."),
    "hill-country-of-judea": dict(name="Hill Country of Judea", type="region", region="canaan-israel", first_reference="Luke 1:39",
        desc="The highland region where Zechariah and Elizabeth lived and where Mary visited her relative Elizabeth while both were pregnant, prompting Elizabeth's Spirit-filled greeting (Luke 1:39-45)."),
    "jezreel-valley": dict(name="Jezreel Valley", type="valley", region="canaan-israel", first_reference="Judges 6:33",
        id_status="secure", id_note="Distinct from the town of Jezreel, though both take their name from the same broad valley.",
        desc="The broad valley where the Midianite camp lay before Gideon's night raid with three hundred men routed them (Judges 7)."),
    "joppa": dict(name="Joppa", type="city", region="canaan-israel", first_reference="Joshua 19:46", modern="Jaffa, Israel",
        desc="A coastal port town where Peter raised the disciple Tabitha (Dorcas) from the dead and later, staying with Simon the tanner, received the rooftop vision opening the gospel to Gentiles (Acts 9:36-43; 10:9-23)."),
    "kedesh": dict(name="Kedesh", type="town", region="canaan-israel", first_reference="Joshua 12:22",
        id_status="secure", id_note="This Kedesh, in Naphtali, is distinct from Kadesh-barnea in the southern wilderness.",
        desc="Barak's hometown, from which he gathered Israel's forces at Deborah's summons before their victory over Sisera; the fleeing Sisera was later killed nearby by Jael (Judges 4:6, 10-21)."),
    "malta": dict(name="Malta", type="region", region="italy", first_reference="Acts 28:1",
        desc="The island where Paul's ship ran aground during the storm-tossed voyage to Rome; Paul was unharmed by a viper's bite there and healed the island's chief official, Publius's, sick father (Acts 28:1-10)."),
    "mamre": dict(name="Mamre", type="town", region="canaan-israel", first_reference="Genesis 13:18",
        desc="The oaks near Hebron where Abraham settled and built an altar, and where three visitors (the Lord and two angels) appeared to him and announced Sarah's coming pregnancy (Genesis 18:1-15)."),
    "maon": dict(name="Maon", type="town", region="canaan-israel", first_reference="Joshua 15:55",
        desc="A town in Judah's wilderness near where the wealthy Nabal grazed his flocks and where David had earlier hidden from Saul's pursuit (1 Samuel 23:24-25; 25:2)."),
    "mediterranean-sea": dict(name="Mediterranean Sea", type="body-of-water", region="asia-minor-greece", first_reference="Numbers 34:6",
        id_status="secure", id_note="Called \"the Great Sea\" or \"the western sea\" in the Old Testament.",
        desc="The sea from which Jonah fled by ship before being cast overboard and swallowed by a great fish (Jonah 1:3-17), and across which Paul's final voyage to Rome as a prisoner passed (Acts 27)."),
    "megiddo": dict(name="Megiddo", type="city", region="canaan-israel", first_reference="Joshua 12:21", modern="Tel Megiddo, Israel",
        desc="A strategic fortress city controlling the Jezreel Valley where King Josiah was fatally wounded confronting Pharaoh Neco's army (2 Kings 23:29-30), and the source of the name \"Armageddon\" (Har Megiddo) in Revelation 16:16."),
    "philistia": dict(name="Philistia", type="nation", region="canaan-israel", first_reference="Exodus 15:14",
        id_status="secure", id_note="See also Philistine Territory, the broader coastal region of the same people.",
        desc="The coastal homeland of the Philistines; a descendant of their giants, Ishbi-benob, nearly killed David in battle before Abishai intervened (2 Samuel 21:15-17)."),
    "ramoth-gilead": dict(name="Ramoth-gilead", type="town", region="moab-transjordan", first_reference="Deuteronomy 4:43",
        desc="A frontier city east of the Jordan where King Ahab was fatally wounded fighting Aram despite disguising himself (1 Kings 22:29-38), and where Jehu was later anointed king in a plot to end Ahab's dynasty (2 Kings 9:1-13)."),
    "shinar": dict(name="Shinar", type="region", region="mesopotamia", first_reference="Genesis 10:10",
        id_status="secure", id_note="The broader Mesopotamian plain containing Babylon; Genesis uses the name for both the region and, in Genesis 11, the specific site of the tower of Babel.",
        desc="The plain where humanity built the tower of Babel before God confused their language and scattered them (Genesis 11:1-9), and, later, where the invading king Amraphel of Shinar came from in Abraham's day (Genesis 14:1)."),
    "sodom": dict(name="Sodom", type="city", region="canaan-israel", first_reference="Genesis 10:19",
        id_status="disputed", id_note="Likely located near the Dead Sea, possibly beneath its southern basin, but no site is confidently confirmed.",
        desc="A city of the plain notorious for wickedness, destroyed by fire and sulfur from heaven after Abraham's intercession failed to find even ten righteous people there; Lot and his daughters escaped, though his wife looked back and was turned to a pillar of salt (Genesis 18:16-19:29)."),
    "succoth": dict(name="Succoth", type="town", region="moab-transjordan", first_reference="Genesis 33:17",
        desc="A town east of the Jordan whose leaders refused to feed Gideon's exhausted men during his pursuit of the Midianite kings Zebah and Zalmunna, for which Gideon punished them on his return (Judges 8:4-16)."),
    "tekoa": dict(name="Tekoa", type="town", region="canaan-israel", first_reference="2 Samuel 14:2",
        desc="A town south of Bethlehem, home of both a wise woman Joab enlisted to persuade David to recall the exiled Absalom (2 Samuel 14:1-20) and, later, the prophet Amos, a shepherd there before his call (Amos 1:1)."),
    "thessalonica": dict(name="Thessalonica", type="city", region="asia-minor-greece", first_reference="Acts 17:1",
        desc="A major Macedonian city where Paul preached for three sabbaths before jealous opponents formed a mob and dragged his host Jason before the city officials, forcing Paul to leave by night (Acts 17:1-10); Paul later wrote two letters to the church there."),
    "thyatira": dict(name="Thyatira", type="city", region="asia-minor-greece", first_reference="Acts 16:14",
        desc="Lydia, the dealer in purple cloth converted at Philippi, was originally from Thyatira (Acts 16:14); the city's own church is later addressed in Revelation and rebuked for tolerating a false prophetess (Revelation 2:18-29)."),
    "ziklag": dict(name="Ziklag", type="town", region="canaan-israel", first_reference="Joshua 15:31",
        desc="A town the Philistine king Achish gave David as a base while he served as his vassal; Amalekites later raided and burned it while David's men were away, taking their families captive before David pursued and recovered everyone (1 Samuel 27:6; 30:1-20)."),
    "zobah": dict(name="Zobah", type="nation", region="canaan-israel", first_reference="1 Samuel 14:47",
        desc="An Aramean kingdom north of Israel that David defeated in battle, taking substantial plunder (2 Samuel 8:3-8); its king Hadadezer's general Rezon later fled to found a rival power base in Damascus (1 Kings 11:23-24)."),
    "zorah": dict(name="Zorah", type="town", region="canaan-israel", first_reference="Joshua 15:33",
        desc="The hometown of Samson's parents Manoah and his wife, where the angel of the Lord announced Samson's coming birth and calling as a Nazirite (Judges 13:2-25)."),

    # --- singleton places (1 associated person) ---
    "abel-beth-maacah": dict(name="Abel Beth-maacah", type="town", region="canaan-israel", first_reference="2 Samuel 20:14",
        desc="A northern city where the rebel Sheba fled from Joab's pursuit and was under siege until a wise local woman had the townspeople throw Sheba's severed head over the wall to save the city (2 Samuel 20:14-22)."),
    "abel-meholah": dict(name="Abel-meholah", type="town", region="canaan-israel", first_reference="Judges 7:22",
        desc="A town toward which the routed Midianites fled from Gideon (Judges 7:22); it was also Elisha's hometown, where Elijah found him plowing and called him as his successor (1 Kings 19:16)."),
    "adullam": dict(name="Adullam", type="town", region="canaan-israel", first_reference="Genesis 38:1",
        desc="A town near which Judah's Canaanite friend Hirah lived (Genesis 38:1, 12); a famous cave near there later became David's hideout, where his family and 400 men in distress gathered to him (1 Samuel 22:1-2)."),
    "ai": dict(name="Ai", type="city", region="canaan-israel", first_reference="Joshua 7:2",
        desc="A city Israel first failed to capture because of Achan's hidden sin, then destroyed by ambush once the sin was dealt with (Joshua 7-8)."),
    "aijalon-of-zebulun": dict(name="Aijalon (of Zebulun)", type="town", region="canaan-israel", first_reference="Judges 12:12",
        id_status="secure", id_note="Distinct from the better-known Valley of Aijalon in Dan (Joshua 10:12).",
        desc="A town in Zebulun's territory where the judge Elon was buried after judging Israel ten years (Judges 12:11-12)."),
    "alexandria": dict(name="Alexandria", type="city", region="egypt", first_reference="Acts 18:24", modern="Alexandria, Egypt",
        desc="A major Egyptian city and center of learning, the hometown of Apollos, an eloquent believer skilled in the Scriptures who was further instructed by Priscilla and Aquila before his effective ministry (Acts 18:24-28)."),
    "amalek": dict(name="Amalek", type="nation", region="sinai-wilderness", first_reference="Genesis 36:12",
        desc="A nomadic nation descended from Esau's grandson that attacked Israel in the wilderness (Exodus 17:8-16); Saul was later commanded to destroy Amalek entirely but spared king Agag and the best plunder, disobedience that cost him his kingdom (1 Samuel 15)."),
    "aphek": dict(name="Aphek", type="town", region="canaan-israel", first_reference="Joshua 12:18",
        id_status="unknown", id_note="Several towns named Aphek appear in Scripture; the exact one in view here, where the ark was captured, is generally placed near Philistine territory.",
        desc="The site of a battle where the Philistines defeated Israel and captured the ark of the covenant, in which Eli's sons Hophni and Phinehas were killed (1 Samuel 4:1-11)."),
    "arabia": dict(name="Arabia", type="region", region="egypt", first_reference="Genesis 25:6",
        desc="The desert region south and east of Canaan; Nehemiah's opponent Geshem the Arab came from this broader region and opposed the rebuilding of Jerusalem's walls (Nehemiah 2:19; 6:1-2)."),
    "aram-naharaim": dict(name="Aram-naharaim", type="region", region="mesopotamia", first_reference="Genesis 24:10",
        id_status="secure", id_note="\"Aram of the two rivers,\" a district of upper Mesopotamia distinct from the Aram (Damascus) of the divided-monarchy period.",
        desc="The region a king named Cushan-rishathaim came from to oppress Israel for eight years before the judge Othniel delivered them (Judges 3:8-10)."),
    "argob": dict(name="Argob", type="region", region="moab-transjordan", first_reference="Deuteronomy 3:4",
        desc="A district of Bashan with sixty fortified cities that Israel captured under Moses, later included in the territory allotted to Jair of Manasseh (Deuteronomy 3:4-14)."),
    "arimathea": dict(name="Arimathea", type="town", region="canaan-israel", first_reference="Matthew 27:57",
        desc="Hometown of Joseph, a wealthy member of the Jewish council and secret disciple of Jesus who asked Pilate for Jesus's body and buried it in his own new tomb (Matthew 27:57-60; John 19:38-42)."),
    "ashdod": dict(name="Ashdod", type="city", region="canaan-israel", first_reference="Joshua 11:22",
        desc="A major Philistine city where the captured ark of the covenant was placed in the temple of Dagon, who fell face down before it (1 Samuel 5:1-5); it was later captured by Assyria's commander under Sargon (Isaiah 20:1)."),
    "baal-peor": dict(name="Baal-peor", type="region", region="moab-transjordan", first_reference="Numbers 25:3",
        desc="The site of a local Baal shrine where Israelite men were drawn into idolatry and sexual immorality with Moabite women, a plague-provoking sin that Phinehas's decisive action helped end (Numbers 25)."),
    "benjamin": dict(name="Benjamin", type="region", region="canaan-israel", first_reference="Joshua 18:11",
        id_status="secure", id_note="The tribal territory of Benjamin, distinct from the patriarch Benjamin himself.",
        desc="The territory of the tribe of Benjamin, between Judah and Ephraim, birthplace and home territory of Israel's first king, Saul's father Kish among them (1 Samuel 9:1-2)."),
    "bezek": dict(name="Bezek", type="town", region="canaan-israel", first_reference="Judges 1:4",
        desc="The site of an early Israelite victory over Canaanite and Perizzite forces, where the defeated king Adoni-bezek was captured and had his thumbs and big toes cut off, as he himself said he had done to seventy other kings (Judges 1:4-7)."),
    "buz": dict(name="Buz", type="region", region="canaan-israel", first_reference="Genesis 22:21",
        id_status="unknown", id_note="Named for a son of Abraham's brother Nahor (Genesis 22:20-21); its exact location is not fixed.",
        desc="The homeland implied by Elihu \"the Buzite,\" the youngest of Job's friends, who speaks in Job 32-37."),
    "cana": dict(name="Cana", type="town", region="canaan-israel", first_reference="John 2:1",
        desc="A Galilean town where Jesus performed His first public miracle, turning water into wine at a wedding (John 2:1-11); Nathanael was from Cana (John 21:2)."),
    "cave-of-machpelah": dict(name="Cave of Machpelah", type="site", region="canaan-israel", first_reference="Genesis 23:9",
        id_status="traditional", id_note="Traditionally identified with a site beneath the Ibrahimi Mosque/Tomb of the Patriarchs in Hebron, though the cave itself has not been excavated.",
        desc="The burial cave Abraham purchased from Ephron the Hittite for Sarah, which became the family tomb for Abraham, Isaac, Rebekah, Jacob, and Leah as well (Genesis 23; 49:29-32)."),
    "cenchrea": dict(name="Cenchrea", type="town", region="asia-minor-greece", first_reference="Acts 18:18",
        desc="Corinth's eastern port, home of Phoebe, a deacon of its church whom Paul commended to the Romans and who likely carried his letter to them (Romans 16:1-2)."),
    "chebar-river": dict(name="Chebar River", type="body-of-water", region="mesopotamia", first_reference="Ezekiel 1:1",
        id_status="unknown", id_note="Likely an irrigation canal off the Euphrates near Babylon, but not confidently identified with a specific modern waterway.",
        desc="The river in Babylonia beside which the exiled priest Ezekiel received his opening vision of God's glory and his call as a prophet (Ezekiel 1:1-3)."),
    "cush": dict(name="Cush", type="nation", region="egypt", first_reference="Genesis 2:13",
        id_status="secure", id_note="Generally identified with the ancient kingdom of Nubia/Meroe, south of Egypt along the Nile.",
        desc="A kingdom south of Egypt; its queen, known by the royal title Candace, sent a court official who was reading Isaiah and was baptized by Philip on the road to Gaza (Acts 8:26-39)."),
    "cyrene": dict(name="Cyrene", type="city", region="egypt", first_reference="Matthew 27:32",
        desc="A North African city; Simon of Cyrene was passing by when Roman soldiers forced him to carry Jesus's cross to Golgotha (Matthew 27:32; Mark 15:21)."),
    "eglon": dict(name="Eglon", type="city", region="canaan-israel", first_reference="Joshua 10:3",
        id_status="secure", id_note="A Canaanite city, distinct from Eglon the king of Moab (Judges 3).",
        desc="One of five Amorite cities whose king joined an alliance against Gibeon and was defeated by Joshua in the battle where the sun stood still (Joshua 10:1-27)."),
    "elam": dict(name="Elam", type="nation", region="mesopotamia", first_reference="Genesis 10:22",
        desc="A kingdom east of Babylon whose king Chedorlaomer led the coalition that raided Sodom and Gomorrah and carried off Lot, prompting Abraham's rescue (Genesis 14:1-16)."),
    "elkosh": dict(name="Elkosh", type="town", region="canaan-israel", first_reference="Nahum 1:1",
        id_status="unknown", id_note="Its exact location is not identified; several sites have been proposed.",
        desc="The otherwise-unspecified hometown of the prophet Nahum, whose short book pronounces judgment on Nineveh (Nahum 1:1)."),
    "ellasar": dict(name="Ellasar", type="city", region="mesopotamia", first_reference="Genesis 14:1",
        id_status="unknown", desc="The kingdom of Arioch, one of four kings who joined Chedorlaomer's coalition against Sodom and Gomorrah (Genesis 14:1-9)."),
    "emmaus": dict(name="Emmaus", type="village", region="canaan-israel", first_reference="Luke 24:13",
        id_status="disputed", id_note="Several ancient sites have been proposed for Emmaus, none confirmed; the distance Luke gives (about seven miles from Jerusalem) does not match any single site with certainty.",
        desc="A village to which two disciples, including Cleopas, were walking on the day of the resurrection when the risen Jesus joined them unrecognized, opening the Scriptures until He was revealed in the breaking of bread (Luke 24:13-35)."),
    "ephraim": dict(name="Ephraim", type="town", region="canaan-israel", first_reference="John 11:54",
        id_status="unknown", id_note="Distinct from the tribal territory of Ephraim; this town's exact site near the wilderness is not confidently identified.",
        desc="A town near the wilderness where Jesus withdrew with His disciples after raising Lazarus, once the religious leaders began plotting to kill Him (John 11:53-54)."),
    "ephraim-forest": dict(name="Ephraim Forest", type="region", region="moab-transjordan", first_reference="2 Samuel 18:6",
        desc="The wooded battleground east of the Jordan where David's forces defeated Absalom's rebellion, and where Absalom, caught by his hair in a tree, was killed by Joab against David's explicit order to spare him (2 Samuel 18:6-15)."),
    "ezion-geber": dict(name="Ezion-geber", type="town", region="egypt", first_reference="Numbers 33:35",
        desc="A port on the Red Sea's Gulf of Aqaba where Solomon built a fleet of trading ships (1 Kings 9:26); a similar fleet, built later by Jehoshaphat with Ahaziah of Israel, was wrecked there (1 Kings 22:48)."),
    "gath-hepher": dict(name="Gath-hepher", type="town", region="canaan-israel", first_reference="Joshua 19:13",
        desc="The hometown of the prophet Jonah, in Zebulun's territory (2 Kings 14:25)."),
    "gaza": dict(name="Gaza", type="city", region="canaan-israel", first_reference="Genesis 10:19", modern="Gaza City",
        desc="A major Philistine city where Samson, blinded and enslaved after Delilah's betrayal, pulled down the temple of Dagon on himself and thousands of Philistines gathered there (Judges 16:21-30)."),
    "gaza-road": dict(name="Gaza Road", type="site", region="canaan-israel", first_reference="Acts 8:26",
        id_status="secure", id_note="A specific desert road rather than a settlement; grouped with, but distinct from, the city of Gaza itself.",
        desc="The desert road on which Philip encountered and baptized the Ethiopian court official reading Isaiah, at an angel's direction (Acts 8:26-39)."),
    "geshur": dict(name="Geshur", type="region", region="moab-transjordan", first_reference="Deuteronomy 3:14",
        desc="A small Aramean kingdom northeast of Israel where David's son Absalom, whose mother Maacah was a Geshurite princess, fled for three years after murdering his half-brother Amnon (2 Samuel 13:37-38)."),
    "gethsemane": dict(name="Gethsemane", type="site", region="canaan-israel", first_reference="Matthew 26:36",
        id_status="traditional", id_note="A garden on the Mount of Olives; several nearby sites are traditionally proposed as the exact location, none confirmed.",
        desc="The garden where Jesus prayed in anguish the night before His crucifixion, was betrayed by Judas with a kiss, and where Peter cut off the ear of the high priest's servant Malchus before Jesus healed it (Matthew 26:36-56; John 18:1-11)."),
    "gezer": dict(name="Gezer", type="city", region="canaan-israel", first_reference="Joshua 10:33",
        desc="A Canaanite royal city whose king Horam came to Lachish's aid and was defeated by Joshua along with his people (Joshua 10:33); later given to Solomon by an Egyptian pharaoh as a wedding gift for his daughter (1 Kings 9:16)."),
    "gibbethon": dict(name="Gibbethon", type="town", region="canaan-israel", first_reference="Joshua 19:44",
        desc="A Philistine border town Israel's army was besieging when King Nadab of Israel was assassinated by Baasha, who then seized the throne (1 Kings 15:27-28)."),
    "giloh": dict(name="Giloh", type="town", region="canaan-israel", first_reference="Joshua 15:51",
        desc="The hometown of Ahithophel, David's trusted counselor who later defected to Absalom's rebellion and, when his advice was rejected, went home and hanged himself (2 Samuel 15:12; 17:23)."),
    "gomorrah": dict(name="Gomorrah", type="city", region="canaan-israel", first_reference="Genesis 10:19",
        id_status="disputed", id_note="Like Sodom, likely near the Dead Sea, but no site is confidently confirmed.",
        desc="A city of the plain, allied with Sodom under its king Birsha, destroyed alongside it by fire and sulfur from heaven for its wickedness (Genesis 14:2; 19:24-28)."),
    "greece": dict(name="Greece", type="nation", region="asia-minor-greece", first_reference="Acts 20:2",
        desc="The broader Greek mainland Paul traveled through and spent three months in near the end of his third missionary journey (Acts 20:1-3)."),
    "hamath": dict(name="Hamath", type="city", region="canaan-israel", first_reference="Numbers 13:21",
        desc="A Syrian city whose king Toi sent his son Joram to congratulate David on defeating their mutual enemy Hadadezer, bringing gifts of silver, gold, and bronze (2 Samuel 8:9-10)."),
    "harosheth-hagoyim": dict(name="Harosheth-hagoyim", type="town", region="canaan-israel", first_reference="Judges 4:2",
        id_status="unknown", desc="The base of Sisera, commander of Canaanite king Jabin's army, before his defeat by Barak and Deborah's forces (Judges 4:2, 13-16)."),
    "hazor": dict(name="Hazor", type="city", region="canaan-israel", first_reference="Joshua 11:1",
        desc="A major Canaanite city whose king Jabin led a northern coalition against Joshua and was defeated, with Hazor itself burned (Joshua 11:1-13); a later King Jabin of Hazor oppressed Israel until Deborah and Barak defeated his general Sisera (Judges 4)."),
    "helam": dict(name="Helam", type="town", region="moab-transjordan", first_reference="2 Samuel 10:16",
        id_status="unknown", desc="The site where David's army defeated a coalition of Arameans under Hadadezer's commander Shobach, who was killed in the battle (2 Samuel 10:15-18)."),
    "heshbon": dict(name="Heshbon", type="city", region="moab-transjordan", first_reference="Numbers 21:25",
        desc="Capital of Sihon, the Amorite king who refused Israel passage and was defeated in battle, giving Israel its first Transjordan territory (Numbers 21:21-30)."),
    "jabesh-gilead": dict(name="Jabesh-gilead", type="town", region="moab-transjordan", first_reference="Judges 21:8",
        desc="A town Ammon's king Nahash threatened to besiege on the humiliating condition of gouging out every resident's right eye, until the newly chosen King Saul rallied Israel to rescue it (1 Samuel 11:1-11)."),
    "jarmuth": dict(name="Jarmuth", type="city", region="canaan-israel", first_reference="Joshua 10:3",
        desc="One of five Amorite cities whose king Piram allied against Gibeon and was defeated by Joshua (Joshua 10:3-27)."),
    "jazer": dict(name="Jazer", type="town", region="moab-transjordan", first_reference="Numbers 21:32",
        desc="A Transjordan town in Gilead's territory whose capture is briefly noted during Israel's approach to Canaan (Numbers 21:32); later assigned within Gad's inheritance (Joshua 21:39)."),
    "kabzeel": dict(name="Kabzeel", type="town", region="canaan-israel", first_reference="Joshua 15:21",
        desc="The hometown of Benaiah, one of David's mighty men known for striking down two of Moab's best men and killing a lion in a pit on a snowy day (2 Samuel 23:20-21)."),
    "kenath": dict(name="Kenath", type="town", region="moab-transjordan", first_reference="Numbers 32:42",
        desc="A town in Bashan captured and renamed by Nobah, a Manassite leader, after himself (Numbers 32:42)."),
    "kir-hareseth": dict(name="Kir-hareseth", type="city", region="moab-transjordan", first_reference="2 Kings 3:25",
        desc="The Moabite capital besieged by Israel, Judah, and Edom's combined armies; Moab's king Mesha, facing defeat, sacrificed his own firstborn son on the city wall (2 Kings 3:25-27)."),
    "kishon-river": dict(name="Kishon River", type="body-of-water", region="canaan-israel", first_reference="Judges 4:7",
        desc="The river near which Barak's forces overwhelmed Sisera's chariot army, which became mired in the flooded ground (Judges 4:7, 13; 5:21)."),
    "land-of-nod": dict(name="Land of Nod", type="region", region="mesopotamia", first_reference="Genesis 4:16",
        id_status="unknown", id_note="\"Nod\" (meaning \"wandering\") is not identified with any known location; it names Cain's condition as much as a place.",
        desc="The place east of Eden where Cain settled after God banished him for murdering his brother Abel (Genesis 4:16)."),
    "laodicea": dict(name="Laodicea", type="city", region="asia-minor-greece", first_reference="Colossians 2:1",
        desc="A wealthy city in the Lycus Valley near Colossae, home to Nympha's house church (Colossians 4:15-16), later addressed in Revelation and rebuked for being lukewarm — \"neither cold nor hot\" (Revelation 3:14-22)."),
    "lydda": dict(name="Lydda", type="town", region="canaan-israel", first_reference="Acts 9:32", modern="Lod, Israel",
        desc="A town where Peter healed a paralyzed man named Aeneas, a miracle that led many in the surrounding area to believe (Acts 9:32-35)."),
    "macedonia": dict(name="Macedonia", type="region", region="asia-minor-greece", first_reference="Acts 16:9",
        desc="The northern Greek region Paul was called to in a vision (\"come over and help us\"), beginning his ministry in Europe (Acts 16:9-10); Erastus is named among those Paul sent ahead there (Acts 19:22)."),
    "madon": dict(name="Madon", type="city", region="canaan-israel", first_reference="Joshua 11:1",
        desc="A Canaanite city whose king Jobab joined Hazor's northern coalition against Joshua and was defeated (Joshua 11:1; 12:19)."),
    "magdala": dict(name="Magdala", type="town", region="canaan-israel", first_reference="Matthew 15:39",
        id_status="secure", id_note="Home town of Mary Magdalene, whose epithet identifies her by this town.",
        desc="A fishing town on the Sea of Galilee, home of Mary Magdalene, from whom Jesus cast out seven demons and who later became a witness to His resurrection (Luke 8:2; John 20:11-18)."),
    "magog": dict(name="Magog", type="nation", region="mesopotamia", first_reference="Genesis 10:2",
        id_status="unknown", id_note="Ezekiel's Gog of Magog is generally read as a symbolic future enemy rather than a specific historical nation; its exact identification is disputed.",
        desc="A nation named among Japheth's descendants (Genesis 10:2), later the homeland of Gog in Ezekiel's prophecy of a great end-time invasion of Israel (Ezekiel 38-39)."),
    "mareshah": dict(name="Mareshah", type="town", region="canaan-israel", first_reference="Joshua 15:44",
        desc="A fortified town of Judah where the prophet Eliezer confronted King Jehoshaphat over an ill-advised alliance (2 Chronicles 20:37); also the site of King Asa's earlier victory over a massive Cushite army (2 Chronicles 14:9-10)."),
    "meshech-and-tubal": dict(name="Meshech and Tubal", type="region", region="mesopotamia", first_reference="Genesis 10:2",
        id_status="unknown", id_note="Generally associated with peoples of Asia Minor; named alongside Magog in Ezekiel's prophecy against Gog.",
        desc="Nations named among Japheth's descendants (Genesis 10:2), later listed as part of Gog's coalition in Ezekiel's prophecy against Magog (Ezekiel 38:2-3; 39:1)."),
    "michmash": dict(name="Michmash", type="town", region="canaan-israel", first_reference="1 Samuel 13:2",
        desc="The site of a Philistine garrison that Jonathan and his armor-bearer boldly attacked alone, triggering a panic that turned into an Israelite rout of the Philistines (1 Samuel 14:1-15)."),
    "miletus": dict(name="Miletus", type="city", region="asia-minor-greece", first_reference="Acts 20:15",
        desc="A port city where Paul, sailing past Ephesus to save time, called for that church's elders to meet him and gave them his farewell address, warning of coming false teachers (Acts 20:15-38); Trophimus was later left there sick (2 Timothy 4:20)."),
    "moresheth": dict(name="Moresheth", type="town", region="canaan-israel", first_reference="Micah 1:1",
        id_status="unknown", desc="The hometown of the prophet Micah, near Gath in Judah's lowlands (Micah 1:1, 14)."),
    "mount-carmel": dict(name="Mount Carmel", type="mountain", region="canaan-israel", first_reference="1 Kings 18:19",
        id_status="secure", id_note="Distinct from the town of Carmel in Judah's hill country, associated instead with Nabal and Abigail.",
        desc="The mountain where Elijah confronted 450 prophets of Baal in a public contest to prove who the true God was, calling down fire from heaven when Baal's prophets' pleas went unanswered (1 Kings 18:16-40)."),
    "mount-gerizim": dict(name="Mount Gerizim", type="mountain", region="canaan-israel", first_reference="Deuteronomy 11:29",
        desc="One of two mountains flanking Shechem from which Israel was to pronounce blessings (Gerizim) and curses (Ebal) upon entering Canaan (Deuteronomy 27:11-13); Jotham later shouted his fable warning against Abimelech's kingship from its slope (Judges 9:7)."),
    "mount-hor": dict(name="Mount Hor", type="mountain", region="sinai-wilderness", first_reference="Numbers 20:22",
        id_status="unknown", id_note="Exact peak not confidently identified.",
        desc="The mountain where Aaron died and was buried after his priestly garments were transferred to his son Eleazar (Numbers 20:22-29)."),
    "mount-zemaraim": dict(name="Mount Zemaraim", type="mountain", region="canaan-israel", first_reference="2 Chronicles 13:4",
        id_status="unknown", desc="A hill in Ephraim's territory from which King Abijah of Judah addressed Jeroboam's army before a decisive battle (2 Chronicles 13:4-20)."),
    "naamah": dict(name="Naamah", type="region", region="canaan-israel", first_reference="Joshua 15:41",
        id_status="unknown", id_note="A town of this name is listed in Judah's lowlands, but whether it is the homeland implied by Zophar \"the Naamathite\" is not certain.",
        desc="The homeland implied by Zophar \"the Naamathite,\" one of Job's three friends who came to comfort — and then argue with — him (Job 2:11; 11:1-20)."),
    "negev": dict(name="Negev", type="region", region="canaan-israel", first_reference="Genesis 12:9",
        id_status="secure", id_note="\"Negev\" (meaning \"south\" or \"dry land\") names the arid southern region of Canaan generally, not one specific site.",
        desc="The dry southern region of Canaan through which Abraham traveled (Genesis 12:9), later part of Judah's inheritance including the town given to Achsah with springs of water (Joshua 15:19)."),
    "paphos": dict(name="Paphos", type="city", region="asia-minor-greece", first_reference="Acts 13:6",
        desc="A city on Cyprus where Paul and Barnabas confronted the sorcerer Bar-Jesus (Elymas), striking him blind, after which the Roman proconsul Sergius Paulus believed (Acts 13:6-12)."),
    "pas-dammim": dict(name="Pas-dammim", type="site", region="canaan-israel", first_reference="1 Chronicles 11:13",
        id_status="secure", id_note="Also called Ephes-dammim (1 Samuel 17:1); near the Valley of Elah where David fought Goliath.",
        desc="The site of a battle where David's mighty man Eleazar stood his ground against the Philistines until his hand froze to his sword, securing a great victory (1 Chronicles 11:12-14)."),
    "patmos": dict(name="Patmos", type="region", region="asia-minor-greece", first_reference="Revelation 1:9",
        desc="A small Aegean island where the apostle John was exiled \"because of the word of God\" and where he received the visions recorded in the book of Revelation (Revelation 1:9-11)."),
    "perea": dict(name="Perea", type="region", region="moab-transjordan", first_reference="Matthew 19:1",
        id_status="secure", id_note="The New Testament-era name for the Transjordan territory Jesus passed through; Herod Antipas, tetrarch of Galilee and Perea, imprisoned and beheaded John the Baptist there (Matthew 14:1-12).",
        desc="The region east of the Jordan Jesus traveled through on His final journey toward Jerusalem (Matthew 19:1; Mark 10:1)."),
    "pergamum": dict(name="Pergamum", type="city", region="asia-minor-greece", first_reference="Revelation 1:11",
        desc="A city addressed in Revelation as the location of \"Satan's throne,\" where a believer named Antipas was martyred; the church there is commended for faithfulness but rebuked for tolerating false teaching (Revelation 2:12-17)."),
    # The three churches of Revelation 2-3 with no other named person in the
    # dataset -- added 2026-09-02 so all seven appear on the maps. The other
    # four (Ephesus, Smyrna [now here], Pergamum, Thyatira, Sardis [here],
    # Philadelphia [here], Laodicea) already existed.
    "smyrna": dict(name="Smyrna", type="city", region="asia-minor-greece", first_reference="Revelation 1:11",
        modern="Izmir, Turkey",
        desc="A port city on the Aegean coast of Asia Minor, one of the seven churches addressed in Revelation. The letter to Smyrna contains no rebuke: the church there is poor in circumstances but rich in faith, warned of coming persecution and imprisonment and urged to be faithful to death for the crown of life (Revelation 2:8-11)."),
    "sardis": dict(name="Sardis", type="city", region="asia-minor-greece", first_reference="Revelation 1:11",
        desc="The former capital of ancient Lydia, one of the seven churches addressed in Revelation. The church at Sardis is told it has \"a name that it is alive, but it is dead,\" called to wake up and strengthen what remains, with a few there who have \"not soiled their garments\" (Revelation 3:1-6)."),
    "philadelphia": dict(name="Philadelphia", type="city", region="asia-minor-greece", first_reference="Revelation 1:11",
        modern="Alaşehir, Turkey",
        desc="A city in Asia Minor, one of the seven churches addressed in Revelation. Like Smyrna, Philadelphia receives no rebuke: though it has \"little power,\" it has kept Christ's word and not denied His name, and is promised an open door no one can shut (Revelation 3:7-13)."),
    "pethor": dict(name="Pethor", type="town", region="mesopotamia", first_reference="Numbers 22:5",
        desc="The Mesopotamian hometown of Balaam, the seer Balak of Moab hired to curse Israel — a curse God repeatedly turned into blessing instead (Numbers 22-24)."),
    "pirathon": dict(name="Pirathon", type="town", region="canaan-israel", first_reference="Judges 12:15",
        desc="The hometown, in Ephraim's hill country, of Abdon, a minor judge who had forty sons and thirty grandsons who rode on donkeys (Judges 12:13-15)."),
    "pontus": dict(name="Pontus", type="region", region="asia-minor-greece", first_reference="Acts 2:9",
        desc="A region on the Black Sea's southern coast; Aquila, later Paul's coworker and host, was a native of Pontus (Acts 18:2), and believers there are among those addressed in 1 Peter 1:1."),
    "ramah": dict(name="Ramah", type="town", region="canaan-israel", first_reference="Joshua 18:25",
        id_status="secure", id_note="A Benjaminite town, distinct from Ramathaim-zophim (Samuel's hometown, also sometimes called Ramah) and from Ramah of Naphtali (Joshua 19:36).",
        desc="A town near which Samuel made his home for part of his judging circuit (1 Samuel 7:17), fortified by King Baasha of Israel against Judah before Asa had it dismantled (1 Kings 15:17-22)."),
    "region-of-the-gerasenes": dict(name="Region of the Gerasenes", type="region", region="canaan-israel", first_reference="Mark 5:1",
        id_status="disputed", id_note="The exact town this region is named for (Gerasa, Gadara, or Gergesa, per differing ancient manuscripts) is debated, though the general area east of the Sea of Galilee is agreed on.",
        desc="The territory east of the Sea of Galilee where Jesus cast a legion of demons out of a tormented man and into a herd of pigs, which then rushed into the lake (Mark 5:1-20)."),
    "rephidim": dict(name="Rephidim", type="site", region="sinai-wilderness", first_reference="Exodus 17:1",
        desc="A wilderness campsite where Moses struck a rock to bring forth water for the thirsty people, with Aaron and Hur holding up his arms during Israel's battle victory over Amalek there (Exodus 17:1-13)."),
    "rock-of-oreb": dict(name="Rock of Oreb", type="site", region="canaan-israel", first_reference="Judges 7:25",
        desc="Where Ephraimite forces, joining Gideon's pursuit of the fleeing Midianites, captured and killed the Midianite prince Oreb (Judges 7:24-25)."),
    "rogelim": dict(name="Rogelim", type="town", region="moab-transjordan", first_reference="2 Samuel 17:27",
        desc="The hometown, in Gilead, of Barzillai, an elderly and wealthy man who generously supplied David's fleeing party during Absalom's rebellion (2 Samuel 17:27-29; 19:31-39)."),
    "salem": dict(name="Salem", type="city", region="canaan-israel", first_reference="Genesis 14:18",
        id_status="traditional", id_note="Widely identified with the later Jerusalem (compare Psalm 76:2), though the text of Genesis does not state this explicitly.",
        desc="The city of Melchizedek, priest-king who blessed Abraham and to whom Abraham gave a tenth of his spoils after rescuing Lot — an episode Hebrews later draws on to explain Christ's priesthood (Genesis 14:18-20; Hebrews 7:1-10)."),
    "seir": dict(name="Seir", type="region", region="canaan-israel", first_reference="Genesis 14:6",
        id_status="secure", id_note="The mountainous territory Esau's descendants (Edom) settled, often used interchangeably with \"Edom.\"",
        desc="The hill country south of the Dead Sea originally inhabited by the Horites, including a chief named Anah, before Esau's descendants displaced them (Genesis 36:20-21)."),
    "shamir": dict(name="Shamir", type="town", region="canaan-israel", first_reference="Judges 10:1",
        id_status="unknown", desc="The hometown, in Ephraim's hill country, of the judge Tola, who judged Israel twenty-three years and was buried there (Judges 10:1-2)."),
    "sheba": dict(name="Sheba", type="nation", region="egypt", first_reference="Genesis 10:7",
        id_status="disputed", id_note="Most often placed in southern Arabia (modern Yemen), though an East African location has also been proposed.",
        desc="A distant kingdom whose queen, hearing of Solomon's wisdom, traveled to test him with hard questions and came away amazed, praising the God of Israel (1 Kings 10:1-13)."),
    "shittim": dict(name="Shittim", type="town", region="moab-transjordan", first_reference="Numbers 25:1",
        desc="Israel's camp in the plains of Moab where men were drawn into idolatry and immorality with Moabite women, including Cozbi, a Midianite woman whom Phinehas killed along with her Israelite partner to stop a plague (Numbers 25)."),
    "shuah": dict(name="Shuah", type="region", region="canaan-israel", first_reference="Genesis 25:2",
        id_status="unknown", id_note="Named for a son of Abraham and Keturah (Genesis 25:1-2); its exact location is not fixed.",
        desc="The homeland implied by Bildad \"the Shuhite,\" one of Job's three friends who came to comfort — and then argue with — him (Job 2:11; 8:1-22)."),
    "shunem": dict(name="Shunem", type="town", region="canaan-israel", first_reference="Joshua 19:18",
        desc="Home of the Shunammite woman who provided a room for Elisha and was later given a son through his prophecy, whom Elisha raised from death (2 Kings 4:8-37); Abishag, brought to comfort the elderly David, was also from Shunem (1 Kings 1:3)."),
    "sidon": dict(name="Sidon", type="city", region="asia-minor-greece", first_reference="Genesis 10:15", modern="Sidon, Lebanon",
        desc="An ancient Phoenician port city; Jezebel, Ahab's notorious queen, was the daughter of Sidon's king Ethbaal, bringing Baal worship with her into Israel (1 Kings 16:31)."),
    "tarsus": dict(name="Tarsus", type="city", region="asia-minor-greece", first_reference="Acts 9:11",
        desc="Paul's hometown in the Roman province of Cilicia, a city he proudly noted was \"no insignificant city\" (Acts 21:39), and where Barnabas went to find him and bring him to Antioch (Acts 11:25-26)."),
    "teman": dict(name="Teman", type="region", region="canaan-israel", first_reference="Genesis 36:11",
        id_status="secure", id_note="A district of Edom named for a grandson of Esau.",
        desc="The homeland of Eliphaz \"the Temanite,\" the first and most prominent of Job's three friends who came to comfort — and then argue with — him (Job 2:11; 4:1-5:27)."),
    "thebez": dict(name="Thebez", type="town", region="canaan-israel", first_reference="Judges 9:50",
        desc="A town where Abimelech, besieging its tower, was fatally struck on the head by a millstone dropped by a woman, then had his armor-bearer kill him so he wouldn't be remembered as slain by a woman (Judges 9:50-54)."),
    "troas": dict(name="Troas", type="city", region="asia-minor-greece", first_reference="Acts 16:8",
        desc="A port city where Paul received his vision of a Macedonian man calling him to Europe (Acts 16:8-10), and where, on a later visit, young Eutychus fell asleep during Paul's long sermon, fell from a third-story window, and was raised back to life (Acts 20:6-12)."),
    "valley-of-achor": dict(name="Valley of Achor", type="valley", region="canaan-israel", first_reference="Joshua 7:24",
        id_status="secure", id_note="\"Achor\" means \"trouble,\" naming the valley for what happened there.",
        desc="Where Achan, who had taken devoted plunder from Jericho against God's command, was executed along with his family and possessions after his sin was exposed (Joshua 7:24-26)."),
    "valley-of-sorek": dict(name="Valley of Sorek", type="valley", region="canaan-israel", first_reference="Judges 16:4",
        desc="Home of Delilah, the woman Samson loved who was bribed by Philistine rulers to discover and betray the secret of his strength (Judges 16:4-20)."),
    "wilderness-of-judea": dict(name="Wilderness of Judea", type="wilderness", region="canaan-israel", first_reference="Matthew 3:1",
        desc="The rugged desert region near the Dead Sea where John the Baptist lived and preached, calling people to repentance and baptizing them in the Jordan (Matthew 3:1-6)."),
    "wilderness-of-shur": dict(name="Wilderness of Shur", type="wilderness", region="sinai-wilderness", first_reference="Genesis 16:7",
        desc="A wilderness region on Egypt's border where the angel of the Lord found Hagar, fleeing from Sarah's harsh treatment, by a spring, and spoke a promise over her son Ishmael (Genesis 16:1-14)."),
    "zaanannim": dict(name="Zaanannim", type="site", region="canaan-israel", first_reference="Judges 4:11",
        id_status="unknown", desc="Near where Heber the Kenite had pitched his tent, apart from his own people, at the time his wife Jael killed the fleeing Canaanite commander Sisera (Judges 4:11, 17-21)."),
    "zeboiim": dict(name="Zeboiim", type="city", region="canaan-israel", first_reference="Genesis 10:19",
        id_status="disputed", id_note="Like Sodom and Gomorrah, likely near the Dead Sea, but no site is confidently confirmed.",
        desc="One of the cities of the plain, allied with Sodom under its king Shemeber, destroyed alongside it (Genesis 14:2; Deuteronomy 29:23)."),
    "waters-of-merom": dict(name="Waters of Merom", type="body-of-water", region="canaan-israel", first_reference="Joshua 11:5",
        id_status="unknown", id_note="Generally located in upper Galilee, though the exact site is not confirmed.",
        desc="Where a northern Canaanite coalition led by Jabin of Hazor, including king Jobab of Madon, gathered against Israel and was decisively defeated by Joshua (Joshua 11:1-9)."),
}
