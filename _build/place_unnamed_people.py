"""Unnamed individuals Scripture ties to a specific place -- the widow of
Nain, the Philippian jailer, and similar figures the text distinctly
identifies with one location but never names.

Shape:
    UNNAMED_PEOPLE = { place_id: [ {"title": ..., "role": ..., "references": [...]}, ... ] }

`title` is the descriptive designation Scripture's own narrative supports
(never an invented proper name, per CLAUDE.md's Factual Accuracy rules) --
e.g. "the widow of Nain", not a guessed name for her. `role`/`references`
follow the same rules as place_people_roles.py's ROLES: a short, lowercase-
start paraphrase of what the text says happened here, grounded in the
person's own documented episode, and never a direct quotation of verse
text (see CLAUDE.md's Bible Version Handling -- no verse text is quoted
anywhere on the site, in any translation).

Consumed by generate_places.py, which attaches these onto each place's
`unnamed_people` list (a sibling array to `related_people`, but rendered
without a link to a person page since none exists). Not committed via
.gitignore's _build/ rule but force-added, same pattern as
place_people_roles.py and places_data.py.

Deliberately not exhaustive -- covers well-known, unambiguous cases where
the text plainly ties the individual to one identifiable place, the same
bar as the "widow of Nain" / "Philippian jailer" examples this file is
named for. Skipped: figures without a fixed named location (the rich young
ruler, the Ethiopian eunuch met "on the road"), groups rather than
individuals (the magi, the ten lepers, the shepherds at Bethlehem), and
parable characters who were never claimed as historical (the good
Samaritan, the rich man and Lazarus).
"""

UNNAMED_PEOPLE = {
    "nain": [
        {
            "title": "the widow of Nain",
            "role": "had lost her only son, whom Jesus raised to life as the funeral procession left the town gate",
            "references": ["Luke 7:11-15"],
        },
    ],
    "philippi": [
        {
            "title": "the Philippian jailer",
            "role": "asked Paul and Silas what he must do to be saved after an earthquake broke open the prison, and was baptized that night with his whole household",
            "references": ["Acts 16:27-34"],
        },
        {
            "title": "the slave girl with a spirit of divination",
            "role": "followed Paul crying out until he cast the spirit out of her, costing her owners their profit from her fortune-telling",
            "references": ["Acts 16:16-19"],
        },
    ],
    "region-of-the-gerasenes": [
        {
            "title": "the Gerasene demoniac",
            "role": "lived among the tombs possessed by a legion of demons until Jesus freed him, then begged to go with Him and was sent home to tell his own people instead",
            "references": ["Mark 5:1-20", "Luke 8:26-39"],
        },
    ],
    "shechem": [
        {
            "title": "the Samaritan woman at the well",
            "role": "met Jesus at Jacob's well here, and brought her whole town out to Him after He told her everything she had done",
            "references": ["John 4:5-30"],
        },
    ],
    "golgotha": [
        {
            "title": "the repentant criminal",
            "role": "was crucified beside Jesus, rebuked the other criminal for mocking Him, and was promised Paradise that same day",
            "references": ["Luke 23:39-43"],
        },
    ],
    "siloam": [
        {
            "title": "the man born blind",
            "role": "was sent by Jesus to wash the mud from his eyes in this pool, and came back seeing",
            "references": ["John 9:1-11"],
        },
    ],
    "en-dor": [
        {
            "title": "the medium of Endor",
            "role": "was consulted by a disguised Saul the night before his death, and brought up Samuel to pronounce his doom",
            "references": ["1 Samuel 28:7-19"],
        },
    ],
    "gethsemane": [
        {
            "title": "the young man who fled naked",
            "role": "was following Jesus when He was arrested here, and ran off leaving his linen garment behind",
            "references": ["Mark 14:51-52"],
        },
    ],
    "bethel": [
        {
            "title": "the man of God from Judah",
            "role": "prophesied against Jeroboam's altar here, then was killed by a lion for disobeying God's word on the way home",
            "references": ["1 Kings 13:1-10", "1 Kings 13:20-24"],
        },
        {
            "title": "the old prophet of Bethel",
            "role": "lied to lure the man of God from Judah back to his house, then had to pronounce the judgment that followed",
            "references": ["1 Kings 13:11-22"],
        },
    ],
    "emmaus": [
        {
            "title": "the unnamed companion of Cleopas",
            "role": "walked with Cleopas to this village and recognized the risen Jesus in the breaking of bread",
            "references": ["Luke 24:13-31"],
        },
    ],
    "capernaum": [
        {
            "title": "the centurion of Capernaum",
            "role": "asked Jesus only to speak the word, and his servant was healed from a distance",
            "references": ["Matthew 8:5-13", "Luke 7:1-10"],
        },
        {
            "title": "the paralyzed man let down through the roof",
            "role": "was lowered through a broken-open roof here by four friends, and Jesus forgave and healed him",
            "references": ["Mark 2:1-12"],
        },
    ],
    "tyre": [
        {
            "title": "the Syrophoenician woman",
            "role": "begged Jesus to free her daughter from a demon, and won the healing through her persistent faith",
            "references": ["Mark 7:24-30", "Matthew 15:21-28"],
        },
    ],
    "cana": [
        {
            "title": "the royal official",
            "role": "came from Capernaum begging Jesus to heal his dying son, and believed on the spot that his son would live, without Jesus even going to see him",
            "references": ["John 4:46-54"],
        },
    ],
    "lystra": [
        {
            "title": "the man crippled from birth",
            "role": "had never walked, but sprang up healed the moment Paul commanded him to stand",
            "references": ["Acts 14:8-10"],
        },
    ],
    "bethesda": [
        {
            "title": "the invalid at Bethesda",
            "role": "had been sick for thirty-eight years until Jesus told him to pick up his mat and walk",
            "references": ["John 5:1-9"],
        },
    ],
    "jerusalem": [
        {
            "title": "the woman caught in adultery",
            "role": "was brought to Jesus in the temple to be stoned, and left condemned by no one after her accusers walked away one by one",
            "references": ["John 8:1-11"],
        },
        {
            "title": "the man born lame, healed at the temple gate",
            "role": "begged for money at the Beautiful Gate and instead walked for the first time in his life when Peter and John healed him",
            "references": ["Acts 3:1-10"],
        },
    ],
}
