"""People groups Scripture ties to a place -- the Samaritans of Samaria, the
Moabites of Moab, and similar -- written up as a short section on that
place's own page rather than as a separate section of the site.

Shape:
    PEOPLE_GROUPS = { place_id: {"name": ..., "desc": ..., "ff": ...} }

`name` is the group's plural name as the section heading ("The Samaritans").
`desc` is the adult-register text and `ff` the family_friendly_summary
retelling, under the same rules as a place's own desc/ff in places_data.py
(chapter:verse references only, no verse text in any translation; ff for an
8-and-up reader, honest in general terms, no adult content). Both render
inside the place's Full Description / Family Version tabs, under a heading,
so the one toggle governs both. Disputed origins or identifications are
stated as disputed in the prose itself (see CLAUDE.md's Factual Accuracy
rules), and extra-biblical background (e.g. Josephus) is labeled as such.

Only full-tier places that have a family_friendly_summary should carry an
entry -- a stub place page renders no curated text.

Consumed by generate_places.py (-> each place's `people_group` object in
data/places/<id>.json), rendered by place_story_tabs_section() in
generate_static_site.py. Force-committed like place_unnamed_people.py.
"""

PEOPLE_GROUPS = {
    "samaria": {
        "name": "The Samaritans",
        "desc": (
            "The Samaritans were the people of the region of Samaria, the hill country between Judea and "
            "Galilee that took its name from this city. Their origin is disputed. 2 Kings 17:24-41 describes "
            "how, after the northern kingdom fell, the king of Assyria resettled the region with peoples from "
            "other conquered lands, who learned to fear the LORD while still serving their "
            "own gods. The Samaritans themselves trace their descent to the tribes of Ephraim and Manasseh "
            "left in the land, and many scholars think both groups contributed. After the exile, "
            "local opponents worked to stop the rebuilding of Jerusalem (Ezra 4:1-5), and Sanballat rallied "
            "the soldiers of Samaria against Nehemiah's wall (Nehemiah 4:1-2).\n\n"
            "By Jesus' day the Samaritans worshiped on Mount Gerizim rather than in Jerusalem (John 4:20) and "
            "accepted only the five books of Moses as Scripture. Jews and Samaritans kept "
            "apart (John 4:9), and calling someone a Samaritan could be an insult (John 8:48). Jesus crossed "
            "that divide again and again. He spoke with a Samaritan woman at Jacob's well "
            "(John 4). He rebuked James and John for wanting to call down fire on a Samaritan "
            "village (Luke 9:52-56), made a Samaritan the hero of a parable (Luke 10:30-37), and noted that "
            "the one healed leper who came back to thank Him was a Samaritan (Luke 17:11-19). After His "
            "resurrection He named Samaria in the gospel's path (Acts 1:8), and through Philip's preaching "
            "many Samaritans believed (Acts 8:4-25). A small Samaritan community still worships on Mount "
            "Gerizim today."
        ),
        "ff": (
            "The Samaritans lived in the land around the city of Samaria, between Judea and Galilee. They "
            "worshiped God on their own mountain instead of at the temple in Jerusalem, and they used only "
            "the five books of Moses as their Scriptures. Jews and Samaritans did not get along, and most "
            "Jews avoided them. Jesus did not. He talked with a Samaritan woman at a well, told a story about "
            "a Samaritan who stopped to help a hurt man when others passed by, and healed a Samaritan who "
            "came back to thank Him. After Jesus rose again, many Samaritans heard the good news about Him "
            "and believed."
        ),
    },
    "moab": {
        "name": "The Moabites",
        "desc": (
            "The Moabites traced their descent to Moab, the son born to Lot by his older daughter after the "
            "destruction of Sodom (Genesis 19:30-37). They lived on the plateau east of the Dead Sea and "
            "worshiped Chemosh, whom Scripture calls their god (Numbers 21:29). Israel was told not to seize "
            "their land (Deuteronomy 2:9), yet Moab's king Eglon oppressed Israel for eighteen years until "
            "Ehud killed him (Judges 3:12-30).\n\n"
            "Relations were never simple. David, Ruth's great-grandson, left his parents in the care of the "
            "king of Moab while Saul hunted him (1 Samuel 22:3-4), but later conquered Moab and made it pay "
            "tribute (2 Samuel 8:2). Solomon married Moabite women and built a high place for Chemosh near "
            "Jerusalem (1 Kings 11:1, 7). After Ahab died, King Mesha of Moab rebelled, and when the armies of "
            "Israel, Judah, and Edom had him trapped, he sacrificed his own son on the city wall (2 Kings "
            "3:4-27). An inscription Mesha set up, the Moabite Stone found in 1868, tells his side of that "
            "rebellion and names Omri king of Israel. Isaiah and Jeremiah gave long oracles of judgment "
            "against Moab (Isaiah 15-16; Jeremiah 48), though Jeremiah's ends with a promise that God would "
            "one day restore Moab's fortunes (Jeremiah 48:47). After the exile, marriages with Moabites were "
            "among the sins Ezra and Nehemiah confronted (Ezra 9:1; Nehemiah 13:1-3, 23). Through Ruth, a "
            "Moabite woman stands in the genealogy of Jesus (Matthew 1:5)."
        ),
        "ff": (
            "The Moabites came from Lot, Abraham's nephew, and lived on high, flat land east of the Dead Sea. "
            "They worshiped a false god named Chemosh. Sometimes they fought against Israel. A Moabite king "
            "named Eglon ruled over Israel for eighteen years until God sent the judge Ehud to set Israel free. "
            "But when King Saul was hunting David, the king of Moab kept David's parents safe. God also spoke "
            "through His prophets about Moab, warning of judgment but promising a better future too. And Ruth, "
            "a Moabite woman, became part of the family line of Jesus."
        ),
    },
    "edom": {
        "name": "The Edomites",
        "desc": (
            "The Edomites descended from Esau, Jacob's twin brother. Before the two were born, God told "
            "Rebekah that two nations were struggling within her and that the older would serve the younger "
            "(Genesis 25:22-23). Genesis 36 lists Esau's descendants and the kings who ruled in Edom before "
            "Israel had any king (Genesis 36:31). Because of that kinship, the law told Israel not to despise "
            "an Edomite, since he was their brother (Deuteronomy 23:7-8).\n\n"
            "The brotherhood rarely showed. Doeg the Edomite, Saul's chief herdsman, informed on David and "
            "then killed the priests of Nob when no one else would (1 Samuel 21:7; 22:9-19). David conquered "
            "Edom and stationed garrisons there (2 Samuel 8:14), and Hadad, a member of Edom's royal family "
            "who had escaped to Egypt, returned to trouble Solomon (1 Kings 11:14-22). Edom broke free of Judah "
            "under Jehoram (2 Kings 8:20-22), and Amaziah later defeated the Edomites in the Valley of Salt "
            "(2 Kings 14:7). When Babylon destroyed Jerusalem, Edom cheered it on (Psalm 137:7), and the book of "
            "Obadiah answers that betrayal of a brother with judgment. Malachi points to Edom's ruin as proof of "
            "God's love for Israel (Malachi 1:2-5), a passage Paul takes up in Romans 9:10-13.\n\n"
            "In the New Testament, Edom's territory appears under its Greek name, Idumea, among the places "
            "crowds came from to hear Jesus (Mark 3:8). According to the Jewish historian Josephus, Herod the "
            "Great's family was Idumean."
        ),
        "ff": (
            "The Edomites came from Esau, the twin brother of Jacob. Even before the twins were born, God said "
            "they would become two nations. God told Israel to remember that the Edomites were their relatives. "
            "But the two nations were often rivals. King David took control of Edom, and later Edom broke "
            "free. When the city of Jerusalem was destroyed, the Edomites were glad, and the prophet Obadiah "
            "warned that God would judge them for turning on their own brother. In Jesus' day, people from "
            "the same land, then called Idumea, came to hear Him teach."
        ),
    },
    "ammon": {
        "name": "The Ammonites",
        "desc": (
            "The Ammonites traced their descent to Ben-ammi, the son born to Lot by his younger daughter "
            "(Genesis 19:38). Their capital was Rabbah, east of the Jordan, and their god was Milcom, also "
            "called Molech (1 Kings 11:5, 7). Like Moab, Ammon's land was not to be taken by Israel "
            "(Deuteronomy 2:19), and the law barred Ammonites from Israel's assembly (Deuteronomy 23:3-4).\n\n"
            "Ammon was a near-constant threat. Its king Nahash besieged Jabesh-gilead and offered peace only "
            "if every man there would let his right eye be put out. Saul's rescue of the city was his first "
            "act as king (1 Samuel 11:1-11). David's war with Nahash's son Hanun led to the siege of Rabbah, "
            "where David arranged Uriah's death (2 Samuel 10; 11:1, 14-17; 12:26-31). Solomon married an "
            "Ammonite, Naamah, who became the mother of King Rehoboam (1 Kings 14:21). Ammon later joined "
            "Moab against Jehoshaphat, and God gave Judah the victory without a fight (2 Chronicles 20:1-30). "
            "Amos condemned Ammon for brutality in war (Amos 1:13-15). After Jerusalem fell, Baalis king of "
            "Ammon sent Ishmael to murder Gedaliah, the governor Babylon had appointed (Jeremiah 40:14; 41:1-2), "
            "and later Tobiah the Ammonite opposed Nehemiah's work and even moved into a room in the temple "
            "courts until Nehemiah threw his belongings out (Nehemiah 13:4-8)."
        ),
        "ff": (
            "The Ammonites came from Lot, Abraham's nephew, and lived east of the Jordan River. They "
            "worshiped a false god named Molech. The Ammonites were often enemies of Israel. When an Ammonite "
            "king attacked the town of Jabesh-gilead, Saul led Israel to rescue it, his first battle as king. "
            "Later, when Ammon and Moab marched against King Jehoshaphat, God won the battle for Judah before "
            "they even had to fight. Even after the exile, an Ammonite official named Tobiah worked against "
            "Nehemiah as he rebuilt Jerusalem's walls."
        ),
    },
    "midian": {
        "name": "The Midianites",
        "desc": (
            "The Midianites descended from Midian, one of Abraham's sons by Keturah, whom Abraham sent away "
            "east with gifts (Genesis 25:1-6). They first appear as traders: Joseph's brothers sold him to a "
            "caravan, and Midianite merchants brought him to Egypt (Genesis 37:25-36). Scripture names both "
            "Ishmaelites and Midianites in the account, and interpreters differ on how the two groups relate.\n\n"
            "Midian gave Moses a home and a family. Jethro, the priest of Midian, became his father-in-law, "
            "rejoiced at what God had done for Israel, offered sacrifices, and advised Moses to share the "
            "work of judging the people (Exodus 18). Moses urged Hobab, a Midianite relative by marriage, to travel "
            "with Israel as a guide (Numbers 10:29-32). Yet Midian's elders joined Moab in hiring Balaam to curse Israel "
            "(Numbers 22:4-7). At Peor a Midianite woman, Cozbi, was killed with the Israelite who brought her "
            "into the camp (Numbers 25:6-18), and Israel then fought a war against Midian in which Balaam "
            "himself died (Numbers 31:1-8).\n\n"
            "In the time of the judges, Midianite raiders came year after year on camels and stripped the "
            "land until Gideon's three hundred routed them (Judges 6-8). That victory became a byword. "
            "Psalm 83:9-11 asks God to do to Israel's enemies as He did to Midian, and Isaiah 9:4 compares "
            "the coming deliverance through the promised Child to the day of Midian's defeat."
        ),
        "ff": (
            "The Midianites came from Midian, one of Abraham's sons. Midianite traders carried young Joseph "
            "down to Egypt after his brothers sold him. Later, Moses lived in Midian for many years. His "
            "father-in-law Jethro was a Midianite priest who praised God for rescuing Israel and gave Moses "
            "wise advice about sharing his work. But other Midianites became Israel's enemies. In Gideon's day, "
            "they swept through the land on camels every year and took Israel's crops, until God gave Gideon "
            "and his 300 men the victory."
        ),
    },
    "canaan": {
        "name": "The Canaanites",
        "desc": (
            "The Canaanites descended from Canaan, a son of Ham, and Genesis 10:15-19 lists the peoples who "
            "came from him: Sidonians, Hittites, Jebusites, Amorites, Hivites, and others. After Ham saw his "
            "father's nakedness, Noah's curse fell on Canaan by name, not on Ham (Genesis 9:20-27).\n\n"
            "God promised Abraham the land but told him that his descendants would wait four generations, "
            "because the wickedness of the Amorites had not yet reached its full measure (Genesis 15:13-16). "
            "The law later names what Canaan's peoples had done, including burning their children to their "
            "gods (Leviticus 18:24-28; Deuteronomy 12:31), and commanded Israel to destroy them and make no "
            "treaties with them so that Israel would not learn their ways (Deuteronomy 7:1-5; 20:16-18).\n\n"
            "Even so, Canaanites who turned to Israel's God were spared. Rahab hid the spies and lived in "
            "Israel from then on (Joshua 2; 6:25), and the Gibeonites were kept alive by their treaty (Joshua "
            "9). The conquest was never finished. Many Canaanite towns remained (Judges 1:27-33), and Israel "
            "soon served Baal and the Ashtaroth (Judges 2:11-13), the pull toward Canaanite worship that runs "
            "through the rest of the Old Testament. Solomon put the remaining peoples to forced labor (1 Kings "
            "9:20-21). Rahab appears in Jesus' genealogy (Matthew 1:5), and a Canaanite woman from the region "
            "of Tyre and Sidon pleaded with Jesus for her daughter until He praised her great faith and healed "
            "the girl (Matthew 15:21-28)."
        ),
        "ff": (
            "The Canaanites were the peoples living in the land of Canaan before Israel came. They worshiped "
            "false gods like Baal, and some of their worship was so cruel that God judged it. God waited "
            "hundreds of years before sending Israel into the land, and He warned Israel not to copy the "
            "Canaanites' ways, but Israel often did. But some Canaanites turned to the true God. Rahab "
            "hid Israel's spies, was saved when Jericho fell, and became part of Jesus' family line. Much "
            "later, a Canaanite mother begged Jesus to heal her daughter, and He praised her great faith."
        ),
    },
    "aram": {
        "name": "The Arameans",
        "desc": (
            "The Arameans take their name from Aram, a son of Shem (Genesis 10:22), and they were close kin to "
            "Israel's own ancestors. Rebekah's brother Laban is called an Aramean, and Isaac and Jacob both "
            "took wives from his family in Paddan-aram (Genesis 25:20; 28:1-5; 31:20). An Israelite bringing "
            "firstfruits was to confess that his forefather had been a wandering Aramean (Deuteronomy 26:5). "
            "Balaam came from Aram (Numbers 23:7), and Cushan-rishathaim of Aram-naharaim was the first "
            "oppressor of the judges period (Judges 3:8-10).\n\n"
            "From David's reign on, the Arameans of Damascus were Israel's northern rival. Rezon seized "
            "Damascus and opposed Solomon (1 Kings 11:23-25). Elijah was sent to anoint Hazael as Aram's next "
            "king (1 Kings 19:15). Elisha led a blinded Aramean raiding party into Samaria and had it fed and "
            "sent home (2 Kings 6:8-23), and when Ben-hadad besieged Samaria, four lepers found the Aramean "
            "camp deserted (2 Kings 6:24-7:16). Rezin of Aram and Pekah of Israel threatened Ahaz, the crisis "
            "in which Isaiah gave the sign of Immanuel (Isaiah 7:1-14). Assyria then took Damascus (2 Kings "
            "16:9).\n\n"
            "Aramaic, the Arameans' language, became the common tongue of the empires. Parts of Ezra and "
            "Daniel are written in it (Ezra 4:8-6:18; Daniel 2:4-7:28), and the Gospels preserve some of "
            "Jesus' own words in Aramaic (Mark 5:41; 15:34)."
        ),
        "ff": (
            "The Arameans lived north of Israel, and their main city was Damascus. They were relatives of "
            "Israel's own family: Rebekah, Isaac's wife, was from an Aramean family, and so were Jacob's "
            "wives Rachel and Leah. Later the Arameans often fought against Israel. Once, God blinded an "
            "Aramean army, and the prophet Elisha led the soldiers to Samaria, where he gave them a meal and "
            "sent them home. The Arameans' language, Aramaic, spread far and wide. Jesus spoke it, and some "
            "of His Aramaic words are written down in the Bible."
        ),
    },
    "gibeon": {
        "name": "The Gibeonites",
        "desc": (
            "The Gibeonites were Hivites (Joshua 9:7; 11:19), the people of Gibeon and three nearby towns, "
            "Chephirah, Beeroth, and Kiriath-jearim (Joshua 9:17). After their deception was uncovered, Joshua "
            "kept the oath Israel had sworn, but made them cutters of wood and drawers of water for the "
            "congregation and for the altar of the LORD (Joshua 9:16-27). Of all the cities of Canaan, Gibeon "
            "alone made peace with Israel (Joshua 11:19).\n\n"
            "Generations later, King Saul broke that oath and tried to wipe the Gibeonites out. In David's day "
            "God sent three years of famine because of it. At the Gibeonites' request, seven of Saul's "
            "descendants were handed over and put to death, and Saul's concubine Rizpah guarded their bodies "
            "until David gave them burial; only then did God answer prayer for the land (2 Samuel 21:1-14). The "
            "account shows how seriously Scripture treats an oath made in the LORD's name, even one obtained "
            "by a trick.\n\n"
            "Gibeonites later served Israel loyally. A Gibeonite was among the warriors who joined David at Ziklag "
            "and was counted with his thirty mighty men (1 Chronicles 12:1-4), and men of Gibeon helped repair Jerusalem's wall under Nehemiah (Nehemiah "
            "3:7). Many interpreters connect the Gibeonites with the temple servants listed after the exile "
            "(Ezra 2:43-58), but the text does not say so directly."
        ),
        "ff": (
            "The Gibeonites were a Canaanite people who tricked Israel into promising not to harm them. Israel "
            "kept that promise, and the Gibeonites became helpers at God's altar, cutting wood and carrying "
            "water. Many years later, King Saul broke the promise and attacked them. God took that broken "
            "promise very seriously, and in David's day He sent a famine until it was made right. Later, "
            "Gibeonites served Israel faithfully. One was among David's mighty men, and others helped rebuild "
            "Jerusalem's walls with Nehemiah."
        ),
    },
    "galilee": {
        "name": "The Galileans",
        "desc": (
            "Galilee's northern tribes were among the first carried off when Assyria invaded (2 Kings 15:29), "
            "and Isaiah spoke of the region as Galilee of the nations, a land in darkness that would see a "
            "great light (Isaiah 9:1-2). Matthew sees that promise fulfilled when Jesus began preaching there "
            "(Matthew 4:12-17).\n\n"
            "By Jesus' day the Galileans were Jews, but people in Judea often looked down on them. Their accent "
            "was recognizable; it gave Peter away in the high priest's courtyard (Matthew 26:73; Mark 14:70). "
            "The Pharisees told Nicodemus that no prophet comes from Galilee (John 7:52), and at Pentecost the "
            "crowd was astonished that men from Galilee were speaking their languages (Acts 2:7). Galilee was "
            "ruled by one of Herod the Great's sons, so when Pilate learned that Jesus was a Galilean, he sent "
            "Him to that ruler (Luke 23:6-7). Galilee also had a name for unrest: Acts 5:37 recalls a revolt "
            "led by a Galilean rebel, and Pilate had some Galileans killed while they offered sacrifices. Jesus used that "
            "event to warn that they were no worse sinners than anyone else, and that all must repent (Luke "
            "13:1-5).\n\n"
            "Yet most of Jesus' disciples were Galileans. Galileans welcomed Him (John 4:45), women from "
            "Galilee followed Him to the cross and the tomb (Luke 23:49, 55), and at His ascension the angels "
            "addressed the apostles as men of Galilee (Acts 1:11)."
        ),
        "ff": (
            "The Galileans were the Jewish people who lived in Galilee, in the north of Israel. People in "
            "Jerusalem often looked down on them, and they could tell a Galilean by the way he talked. That "
            "is how people recognized Peter as one of Jesus' followers on the night Jesus was arrested. But "
            "Jesus grew up among the Galileans, and most of His disciples came from there. Women from Galilee "
            "followed Him all the way to the cross and were the first to find His tomb empty."
        ),
    },
}
