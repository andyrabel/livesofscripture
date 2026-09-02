#!/usr/bin/env python3
"""Builds the Places feature's data layer from data/people/*.json's curated
`geographic_setting` field plus the hand-curated content in places_data.py.

Emits:
  data/places/<place_id>.json   -- one file per place (mirrors data/people/)
  data/places-index.json        -- lightweight index, loaded everywhere
  data/place-connections.json   -- person<->place graph edges (separate
                                    from data/connections.json, which stays
                                    person-to-person only)

Re-run whenever geographic_setting values change on any person file, or
whenever places_data.py's curation changes. Safe to re-run (same pattern as
the other backfill_*.py scripts documented in CLAUDE.md's Timeline section).
"""
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
from places_data import PLACES_MAJOR, PLACES_MID, PLACES_MINOR  # noqa: E402
from place_people_roles import ROLES  # noqa: E402

# lon/lat + OpenBible confidence per place, produced by
# _build/backfill_place_coords.py. Absent entries just render without a map.
_coords_path = Path(__file__).resolve().parent / "place_coords.json"
PLACE_COORDS = json.loads(_coords_path.read_text())["coords"] if _coords_path.exists() else {}

ERA_ORDER = ["Primeval History", "Patriarchal", "Exodus/Wilderness", "Judges",
             "United Monarchy", "Divided Monarchy", "Exile",
             "Post-Exile/Intertestamental", "Gospels", "Apostolic"]
ERA_RANK = {e: i for i, e in enumerate(ERA_ORDER)}

# Raw geographic_setting string -> canonical place name (None = drop, not a
# proper named place). Kept in lockstep with the extraction used to derive
# places_data.py's roster -- do not add a canonical name here without also
# adding it to places_data.py's PLACES_MAJOR/MID/MINOR.
NORM = {
    "Wilderness": None, "wilderness": None, "the wilderness": None,
    "wilderness camp of Israel": None, "wilderness (Israelite camp)": None,
    "wilderness camp at Sinai": "Mount Sinai", "wilderness camp near Mount Sinai": "Mount Sinai",
    "the stronghold in the wilderness": None, "the wilderness stronghold": None,
    "Judean wilderness": "Wilderness of Judea",
    "outside Jerusalem": "Jerusalem", "near Israel": None, "east of the Jordan": "Transjordan",
    "house of Obed-edom near Jerusalem": None,
    "the Roman Empire": "Rome",
    "Israel": "Kingdom of Israel", "Israel (Northern Kingdom)": "Kingdom of Israel",
    "Northern Kingdom of Israel": "Kingdom of Israel", "Kingdom of Israel": "Kingdom of Israel",
    "Judah": "Kingdom of Judah", "Kingdom of Judah": "Kingdom of Judah",
    "Sinai": "Sinai", "Sinai wilderness": "Sinai", "Sinai Peninsula": "Sinai",
    "wilderness of Sinai": "Sinai", "Mount Sinai": "Mount Sinai", "Horeb": "Mount Sinai",
    "Moab": "Moab", "plains of Moab": "Plains of Moab", "Plains of Moab": "Plains of Moab",
    "Paddan-aram": "Paddan-aram", "Paddan-Aram": "Paddan-aram", "Paddan-aram/Haran": "Paddan-aram",
    "Haran": "Haran", "Ur/Haran (origin)": "Ur of the Chaldeans", "Ur of the Chaldeans": "Ur of the Chaldeans",
    "Aram-naharaim (Mesopotamia)": "Aram-naharaim", "Pethor (Mesopotamia)": "Pethor",
    "Susa": "Susa", "Susa, Persia": "Susa", "Susa (Persia)": "Susa",
    "Persia": "Persia", "Elam": "Elam",
    "Aram": "Aram", "Aram (Syria)": "Aram", "Aram-Damascus": "Aram", "Zobah": "Zobah",
    "Damascus": "Damascus", "Damascus (origin)": "Damascus", "Hamath": "Hamath",
    "Egypt": "Egypt", "Egypt (Goshen)": "Egypt", "Egypt (On/Heliopolis)": "Egypt",
    "Alexandria": "Alexandria", "Cyrene": "Cyrene", "Cyprus": "Cyprus",
    "Garden of Eden (traditional location disputed)": "Garden of Eden",
    "Mesopotamia (traditional setting of Genesis 1-11)": "Mesopotamia",
    "Shinar": "Shinar", "Shinar (Mesopotamia)": "Shinar",
    "Land of Nod, east of Eden": "Land of Nod",
    "Ararat": "Ararat", "Mountains of Ararat (traditional location, exact site disputed)": "Ararat",
    "Uz": "Uz", "land of Uz": "Uz", "Land of Uz": "Uz", "Buz": "Buz", "Teman": "Teman",
    "Bethlehem": "Bethlehem", "Bethlehem in Judah": "Bethlehem",
    "Bethlehem/Ephrath": "Bethlehem", "road to Ephrath (Bethlehem)": "Bethlehem",
    "Jerusalem": "Jerusalem", "Jerusalem (temple)": "Jerusalem", "Jerusalem (Mount Moriah)": "Jerusalem",
    "Jerusalem (under siege)": "Jerusalem", "Mount Zion": "Jerusalem", "Gihon": "Jerusalem",
    "Kidron Valley": "Jerusalem", "En-rogel": "Jerusalem", "Gethsemane": "Gethsemane",
    "Galilee": "Galilee", "Cana": "Cana", "Nazareth": "Nazareth", "Capernaum": "Capernaum",
    "Capernaum (Galilee)": "Capernaum", "Bethsaida": "Bethsaida", "Magdala": "Magdala",
    "Mount Tabor": "Mount Tabor", "region of the Gerasenes": "Region of the Gerasenes",
    "Peniel": "Penuel", "Penuel": "Penuel",
    "Salem (traditionally identified with later Jerusalem)": "Salem",
    "Seir": "Seir", "Seir/Edom": "Edom", "Edom": "Edom",
    "hill country near Zoar": "Zoar", "the hill country near Zoar": "Zoar",
    "hill country of Ephraim": "Hill Country of Ephraim", "Ephraim hill country": "Hill Country of Ephraim",
    "Ephraim": "Ephraim", "Shamir in the hill country of Ephraim": "Shamir",
    "Pirathon in Ephraim": "Pirathon", "hill country of Judea": "Hill Country of Judea",
    "Valley of Siddim": "Valley of Siddim", "Valley of Siddim (Dead Sea region)": "Valley of Siddim",
    "Wilderness of Paran": "Wilderness of Paran", "wilderness of Paran": "Wilderness of Paran",
    "the Havvoth-jair": "Havvoth-jair", "Jair (Gilead)": "Havvoth-jair", "Jair": "Havvoth-jair",
    "Gilead": "Gilead", "Jazer in Gilead": "Jazer", "Rogelim in Gilead": "Rogelim",
    "Transjordan": "Transjordan", "Transjordan, near Karkor": "Karkor",
    "Transjordan (Reuben, Gad, half-tribe of Manasseh)": "Transjordan",
    "Ammon": "Ammon", "Ammon (Rabbah)": "Rabbah", "Rabbah": "Rabbah",
    "Rabbah of the Ammonites": "Rabbah",
    "Samaria": "Samaria", "Tirzah": "Tirzah",
    "Mount Carmel": "Mount Carmel", "Carmel": "Carmel (of Judah)",
    "Mount Gilboa": "Mount Gilboa", "Mount Hor": "Mount Hor", "Mount Gerizim": "Mount Gerizim",
    "Mount Zemaraim": "Mount Zemaraim",
    "the Midianite camp near the valley of Jezreel": "Jezreel Valley",
    "Jezreel": "Jezreel", "Jezreel Valley": "Jezreel Valley",
    "Jordan River": "Jordan River", "Chebar River": "Chebar River", "Kishon River": "Kishon River",
    "Mediterranean Sea": "Mediterranean Sea",
    "Asia Minor": "Asia Minor", "Asia Minor (likely)": "Asia Minor", "Asia": "Asia (Roman Province)",
    "Asia (Roman province)": "Asia (Roman Province)", "Greece": "Greece", "Macedonia": "Macedonia",
    "Ephesus (likely)": "Ephesus", "Ephesus": "Ephesus",
    "Dan (Laish)": "Dan", "Dan": "Dan",
    "the rock of Oreb": "Rock of Oreb", "the land of Canaan": "Canaan", "Canaan": "Canaan",
    "Kush (Ethiopia/Nubia/Meroe)": "Cush", "Sheba (likely southern Arabia)": "Sheba",
    "Arabia": "Arabia", "Midian": "Midian",
    "Debir/Kiriath-sepher": "Debir", "Kiriath-sepher": "Debir", "Kiriath-jearim": "Kiriath-jearim",
    "Hebron/Canaan": "Hebron", "Hebron": "Hebron",
    "Ramathaim-zophim": "Ramathaim-zophim", "Ramah": "Ramah",
    "Zaanannim near Kedesh": "Zaanannim", "Kedesh-naphtali": "Kedesh", "Kedesh": "Kedesh", "near Kedesh": "Kedesh",
    "Aijalon in Zebulun": "Aijalon (of Zebulun)", "Argob": "Argob", "Kenath": "Kenath",
    "Machpelah": "Cave of Machpelah", "Mamre": "Mamre", "Gerar": "Gerar", "Beersheba": "Beersheba",
    "Baal-peor": "Baal-peor", "Shittim": "Shittim",
    "Bethel": "Bethel", "Bashan": "Bashan", "Bahurim": "Bahurim", "Bethany": "Bethany",
    "Gath": "Gath", "Gilgal": "Gilgal", "Judea": "Judea", "Lachish": "Lachish",
    "Colossae": "Colossae", "Gob": "Gob", "Makkedah": "Makkedah",
    "Philippi": "Philippi", "Karkor": "Karkor", "Lo-debar": "Lo-debar", "Lystra": "Lystra",
    "Nob": "Nob", "Ophrah": "Ophrah", "Philistine territory": "Philistine Territory",
    "Riblah": "Riblah", "Timnah": "Timnah", "Tyre": "Tyre", "Valley of Elah": "Valley of Elah",
    "Zoar": "Zoar", "Nineveh": "Nineveh", "Anathoth": "Anathoth", "Athens": "Athens",
    "Casiphia": "Casiphia", "Crete": "Crete", "Gallim": "Gallim", "Joppa": "Joppa",
    "Malta": "Malta", "Maon": "Maon", "Megiddo": "Megiddo", "Philistia": "Philistia",
    "Ramoth-gilead": "Ramoth-gilead", "Sodom": "Sodom", "Succoth": "Succoth", "Tekoa": "Tekoa",
    "Thessalonica": "Thessalonica", "Thyatira": "Thyatira", "Ziklag": "Ziklag", "Zorah": "Zorah",
    "Abel Beth-maacah": "Abel Beth-maacah", "Abel-meholah": "Abel-meholah", "Adullam": "Adullam",
    "Ai": "Ai", "Amalek": "Amalek", "Aphek": "Aphek", "Arimathea": "Arimathea", "Ashdod": "Ashdod",
    "Benjamin": "Benjamin", "Bezek": "Bezek", "Cenchrea": "Cenchrea", "Eglon": "Eglon",
    "Elkosh": "Elkosh", "Ellasar": "Ellasar", "Emmaus": "Emmaus", "Ephraim forest": "Ephraim Forest",
    "Ezion-geber": "Ezion-geber", "Gath-hepher": "Gath-hepher", "Gaza": "Gaza", "Gaza road": "Gaza Road",
    "Geshur": "Geshur", "Gezer": "Gezer", "Gibbethon": "Gibbethon", "Giloh": "Giloh",
    "Gomorrah": "Gomorrah", "Harosheth-hagoyim": "Harosheth-hagoyim", "Hazor": "Hazor",
    "Helam": "Helam", "Heshbon": "Heshbon", "Jabesh-gilead": "Jabesh-gilead", "Jarmuth": "Jarmuth",
    "Kabzeel": "Kabzeel", "Kir-hareseth": "Kir-hareseth", "Laodicea": "Laodicea", "Lydda": "Lydda",
    "Madon": "Madon", "Magog": "Magog", "Mareshah": "Mareshah",
    "Meshech and Tubal": "Meshech and Tubal", "Michmash": "Michmash", "Miletus": "Miletus",
    "Moresheth": "Moresheth", "Naamah": "Naamah", "Negev": "Negev", "Paphos": "Paphos",
    "Pas-dammim": "Pas-dammim", "Patmos": "Patmos", "Perea": "Perea", "Pergamum": "Pergamum",
    "Pirathon": "Pirathon", "Pontus": "Pontus", "Rephidim": "Rephidim", "Sidon": "Sidon",
    "Tarsus": "Tarsus", "Thebez": "Thebez", "Troas": "Troas", "Valley of Achor": "Valley of Achor",
    "Valley of Sorek": "Valley of Sorek", "Wilderness of Shur": "Wilderness of Shur",
    "Shuah": "Shuah", "Shunem": "Shunem", "Naphtali": None,
    "waters of Merom": "Waters of Merom",
}


def canon(raw):
    return NORM[raw] if raw in NORM else raw.strip()


def slugify(name):
    s = name.lower().replace("'", "").replace("(", "").replace(")", "")
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")


ABBREV = {
    "Genesis": "Gen", "Exodus": "Exod", "Leviticus": "Lev", "Numbers": "Num",
    "Deuteronomy": "Deut", "Joshua": "Josh", "Judges": "Judg", "Ruth": "Ruth",
    "1 Samuel": "1 Sam", "2 Samuel": "2 Sam", "1 Kings": "1 Kgs", "2 Kings": "2 Kgs",
    "1 Chronicles": "1 Chr", "2 Chronicles": "2 Chr", "Ezra": "Ezra", "Nehemiah": "Neh",
    "Esther": "Esth", "Job": "Job", "Psalm": "Ps", "Psalms": "Ps", "Proverbs": "Prov",
    "Ecclesiastes": "Eccl", "Isaiah": "Isa", "Jeremiah": "Jer", "Lamentations": "Lam",
    "Ezekiel": "Ezek", "Daniel": "Dan", "Hosea": "Hos", "Joel": "Joel", "Amos": "Amos",
    "Obadiah": "Obad", "Jonah": "Jonah", "Micah": "Mic", "Nahum": "Nah", "Habakkuk": "Hab",
    "Zephaniah": "Zeph", "Haggai": "Hag", "Zechariah": "Zech", "Malachi": "Mal",
    "Matthew": "Matt", "Mark": "Mark", "Luke": "Luke", "John": "John", "Acts": "Acts",
    "Romans": "Rom", "1 Corinthians": "1 Cor", "2 Corinthians": "2 Cor", "Galatians": "Gal",
    "Ephesians": "Eph", "Philippians": "Phil", "Colossians": "Col",
    "1 Thessalonians": "1 Thess", "2 Thessalonians": "2 Thess", "1 Timothy": "1 Tim",
    "2 Timothy": "2 Tim", "Titus": "Titus", "Philemon": "Phlm", "Hebrews": "Heb",
    "James": "James", "1 Peter": "1 Pet", "2 Peter": "2 Pet", "1 John": "1 John",
    "2 John": "2 John", "3 John": "3 John", "Jude": "Jude", "Revelation": "Rev",
}


def abbrev_reference(ref):
    m = re.match(r"^((?:[123]\s)?[A-Za-z]+)\s(.+)$", ref)
    if not m:
        return ref
    book, rest = m.groups()
    return f"{ABBREV.get(book, book)} {rest}"


def name_grouping_key(name):
    return name.strip().lower()


def main():
    curated = {}
    for d in (PLACES_MAJOR, PLACES_MID, PLACES_MINOR):
        curated.update(d)

    index = json.loads((ROOT / "data" / "people.json").read_text())
    tier_by_id = {e["person_id"]: e["tier"] for e in index}
    name_by_id = {e["person_id"]: e["name"] for e in index}
    gender_by_id = {e["person_id"]: e.get("gender") for e in index}

    # slug -> {eras: set, people: [person_id, ...]}
    extracted = defaultdict(lambda: {"eras": set(), "people": []})
    for person_path in sorted((ROOT / "data" / "people").glob("*.json")):
        person = json.loads(person_path.read_text())
        pid = person["person_id"]
        for raw in person.get("geographic_setting", []) or []:
            name = canon(raw)
            if name is None:
                continue
            slug = slugify(name)
            if slug not in curated:
                print(f"warning: {pid!r} geographic_setting {raw!r} -> {name!r} "
                      f"({slug!r}) has no curated entry in places_data.py, skipping")
                continue
            rec = extracted[slug]
            era = person.get("era")
            if era:
                rec["eras"].add(era)
            rec["people"].append(pid)

    for slug in curated:
        extracted[slug]  # touch so every curated place exists even with 0 people

    # Which minor (1-2 person) places are narratively significant enough to
    # get full (indexed) treatment despite their thin person count -- hand
    # curated, see CLAUDE.md's Places section.
    FORCE_FULL_MINOR = {
        "gethsemane", "sodom", "gomorrah", "patmos", "cana", "emmaus", "joppa",
        "arimathea", "cave-of-machpelah", "salem", "region-of-the-gerasenes",
        "valley-of-achor", "baal-peor", "shittim", "land-of-nod", "ai", "ashdod",
        "gaza", "thebez", "valley-of-sorek", "wilderness-of-judea", "mount-carmel",
        "mount-gerizim", "kir-hareseth", "jabesh-gilead", "hazor", "magdala",
        "laodicea", "pergamum", "thyatira", "athens", "malta", "megiddo", "crete",
        "dan", "smyrna", "sardis", "philadelphia",
    }

    places = []
    disamb_groups = defaultdict(list)

    for slug, c in curated.items():
        rec = extracted[slug]
        n_people = len(rec["people"])
        is_major_or_mid = slug in PLACES_MAJOR or slug in PLACES_MID
        tier = "full" if (is_major_or_mid or n_people >= 3 or slug in FORCE_FULL_MINOR) else "stub"

        eras = sorted(rec["eras"], key=lambda e: ERA_RANK.get(e, 99))
        first_ref = c["first_reference"]
        references = c.get("references") or [first_ref]
        if first_ref not in references:
            references = [first_ref] + references

        # dict.fromkeys dedupes while preserving encounter order; sorting by
        # (name, person_id) rather than name alone keeps output
        # byte-for-byte deterministic even when two people share a name
        # (plain `set()` iteration order is hash-randomized per process and
        # is NOT safe here -- this bit a first version of this script).
        full_people = sorted(
            dict.fromkeys(p for p in rec["people"] if tier_by_id.get(p) == "full"),
            key=lambda p: (name_by_id.get(p, p), p),
        )
        place_roles = ROLES.get(slug, {})
        related_people = []
        for p in full_people:
            rp = {"person_id": p, "name": name_by_id.get(p, p), "gender": gender_by_id.get(p)}
            role_entry = place_roles.get(p)
            if role_entry:
                role, refs = role_entry
                rp["role"] = role
                rp["references"] = list(refs)
            related_people.append(rp)

        entry = {
            "place_id": slug,
            "name": c["name"],
            "alt_names": c.get("alt", []),
            "tier": tier,
            "type": c["type"],
            "region": c["region"],
            "eras": eras,
            "first_reference": first_ref,
            "references": references,
            "identification": {
                "status": c.get("id_status", "secure"),
                "note": c.get("id_note", ""),
            },
            "modern_name": c.get("modern"),
            "n_people": n_people,
            "related_people": related_people,
        }
        if tier == "full":
            entry["description"] = c.get("desc", "")
            if c.get("major"):
                entry["family_friendly_summary"] = c.get("ff", "")
        else:
            entry["description"] = c.get("desc", "")

        geo = PLACE_COORDS.get(slug)
        if geo:
            # `geojson` is a build-time pointer for generate_maps.py only —
            # keep it out of the shipped per-place file.
            entry["geo"] = {k: v for k, v in geo.items() if k != "geojson"}

        places.append(entry)
        disamb_groups[name_grouping_key(c["name"])].append(slug)

        # Flag curated role blurbs that don't match a full-tier person at this
        # place (typo, tier change, or a conflated person_id) -- see CLAUDE.md.
        known = {rp["person_id"] for rp in related_people}
        for pid in ROLES.get(slug, {}):
            if pid not in known:
                print(f"warning: place_people_roles.py has role for {pid!r} at "
                      f"{slug!r}, but that person is not a full-tier person here")

    # Disambiguation -- same rule chain as person entries (see CLAUDE.md's
    # Name Disambiguation section), adapted for places: epithet (curated,
    # via alt_names carrying an "of X"/"in X" qualifier) -> region -> era ->
    # abbreviated first-mention reference. Present but expected to rarely
    # fire today: the geographic_setting normalization pass above already
    # resolved every known same-name collision (Bethlehem, Mizpah, Gilgal,
    # Antioch, Caesarea, Carmel, Kadesh/Kedesh) into one canonical entry
    # each with an identification-note caveat, rather than split entries.
    by_id = {e["place_id"]: e for e in places}
    for key, slugs in disamb_groups.items():
        if len(slugs) < 2:
            continue
        phrases = {}
        for slug in slugs:
            e = by_id[slug]
            region_label = e["region"].replace("-", " ")
            era_label = e["eras"][0] if e["eras"] else None
            parts = [p for p in [region_label, era_label] if p]
            phrase = ", ".join(parts)
            phrases.setdefault(phrase, []).append(slug)
        for phrase, slugs_for_phrase in phrases.items():
            if len(slugs_for_phrase) > 1:
                # Ambiguous even after region/era -- fall back to reference-only.
                for slug in slugs_for_phrase:
                    by_id[slug]["disambiguation"] = f"({abbrev_reference(by_id[slug]['first_reference'])})"
            else:
                slug = slugs_for_phrase[0]
                ref = abbrev_reference(by_id[slug]["first_reference"])
                by_id[slug]["disambiguation"] = f"{phrase} ({ref})" if phrase else f"({ref})"

    # --- write per-place files ---
    places_dir = ROOT / "data" / "places"
    places_dir.mkdir(exist_ok=True)
    for e in places:
        (places_dir / f"{e['place_id']}.json").write_text(json.dumps(e, indent=2) + "\n")

    # --- write lightweight index ---
    index_entries = []
    for e in places:
        ie = {
            "place_id": e["place_id"],
            "name": e["name"],
            "alt_names": e["alt_names"],
            "tier": e["tier"],
            "type": e["type"],
            "region": e["region"],
            "eras": e["eras"],
            "n_people": e["n_people"],
            "disambiguation": e.get("disambiguation", ""),
        }
        if e.get("geo"):
            ie["lat"] = e["geo"]["lat"]
            ie["lng"] = e["geo"]["lng"]
        index_entries.append(ie)
    index_entries.sort(key=lambda e: e["name"])
    (ROOT / "data" / "places-index.json").write_text(json.dumps(index_entries, indent=2) + "\n")

    # --- write person<->place graph edges (separate file from connections.json) ---
    edges = []
    for e in places:
        for rp in e["related_people"]:
            edges.append({
                "from": rp["person_id"],
                "to": f"place:{e['place_id']}",
                "label": "associated with",
                "type": "person-place",
                "mutual": True,
            })
    (ROOT / "data" / "place-connections.json").write_text(json.dumps(edges, indent=2) + "\n")

    all_slugs = {e["place_id"] for e in places}
    for slug in ROLES:
        if slug not in all_slugs:
            print(f"warning: place_people_roles.py has an entry for unknown place {slug!r}")

    full_count = sum(1 for e in places if e["tier"] == "full")
    n_roles = sum(1 for e in places for rp in e["related_people"] if rp.get("role"))
    print(f"Generated {len(places)} places ({full_count} full, {len(places) - full_count} stub), "
          f"{len(edges)} person-place edges, {n_roles} person blurbs.")


if __name__ == "__main__":
    main()
