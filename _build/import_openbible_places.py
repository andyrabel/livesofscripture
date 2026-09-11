#!/usr/bin/env python3
"""Bulk-import a gazetteer of every named place in the Protestant canon from
OpenBible.info's Bible-Geocoding-Data (CC BY 4.0).

Why: the Places feature's own pipeline (generate_places.py) only knows about
places that some person's curated `geographic_setting` points at, plus the
hand-curated roster in places_data.py -- so a place nobody "lives in"
(Tarshish, Cherith, the Nile, Ophir, most of the Nehemiah wall gates) was
structurally invisible. This script closes that gap so the site can honestly
claim to list *every* named place in Scripture.

Output: data/places_gazetteer.json -- a `{slug: {curated-shaped fields}}`
map that generate_places.py merges in at lowest priority (hand curation in
places_data.py always wins). Every entry lands as a name-only "stub" (tier
decided downstream by generate_places.py: 0 associated people -> stub), i.e.
noindex + excluded from the sitemap, exactly like the 2,253 stub *person*
pages. No prose descriptions are generated -- promoting a gazetteer stub to a
real entry is a curation pass in places_data.py, not this script's job.

Source data:
  _build/openbible-source/ancient.slim.jsonl   -- committed, trimmed to the
      fields used here (see slim_record()). Regenerate with --refresh.
  _build/openbible-source/ancient.jsonl        -- the full upstream file
      (~11 MB, gitignored). Only needed for --refresh.

Usage:
  python3 _build/import_openbible_places.py            # slim file -> gazetteer
  python3 _build/import_openbible_places.py --refresh   # re-download, re-slim, then import

Re-run generate_places.py (then generate_static_site.py) afterwards. Safe to
re-run; deterministic (output is sorted).
"""
import json
import re
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = Path(__file__).resolve().parent / "openbible-source"
FULL = SRC_DIR / "ancient.jsonl"
SLIM = SRC_DIR / "ancient.slim.jsonl"
OUT = ROOT / "data" / "places_gazetteer.json"
UPSTREAM = "https://raw.githubusercontent.com/openbibleinfo/Bible-Geocoding-Data/main/data/ancient.jsonl"

sys.path.insert(0, str(Path(__file__).resolve().parent))
from places_data import PLACES_MAJOR, PLACES_MID, PLACES_MINOR  # noqa: E402

# OpenBible's readable references abbreviate book names; map to the site's
# canonical (NASB) full names. Books with no place mentions are omitted.
BOOK = {
    "Gen": "Genesis", "Ex": "Exodus", "Lev": "Leviticus", "Num": "Numbers",
    "Deut": "Deuteronomy", "Josh": "Joshua", "Judg": "Judges", "Ruth": "Ruth",
    "1 Sam": "1 Samuel", "2 Sam": "2 Samuel", "1 Kgs": "1 Kings", "2 Kgs": "2 Kings",
    "1 Chr": "1 Chronicles", "2 Chr": "2 Chronicles", "Ezra": "Ezra", "Neh": "Nehemiah",
    "Est": "Esther", "Job": "Job", "Ps": "Psalm", "Prov": "Proverbs", "Eccl": "Ecclesiastes",
    "Sng": "Song of Solomon", "Isa": "Isaiah", "Jer": "Jeremiah", "Lam": "Lamentations",
    "Ezek": "Ezekiel", "Dan": "Daniel", "Hos": "Hosea", "Joel": "Joel", "Amos": "Amos",
    "Obad": "Obadiah", "Jonah": "Jonah", "Mic": "Micah", "Nahum": "Nahum", "Hab": "Habakkuk",
    "Zeph": "Zephaniah", "Hag": "Haggai", "Zech": "Zechariah", "Mal": "Malachi",
    "Matt": "Matthew", "Mark": "Mark", "Luke": "Luke", "John": "John", "Acts": "Acts",
    "Rom": "Romans", "1 Cor": "1 Corinthians", "2 Cor": "2 Corinthians", "Gal": "Galatians",
    "Eph": "Ephesians", "Phil": "Philippians", "Col": "Colossians",
    "1 Thes": "1 Thessalonians", "2 Thes": "2 Thessalonians", "1 Tim": "1 Timothy",
    "2 Tim": "2 Timothy", "Titus": "Titus", "Phlm": "Philemon", "Heb": "Hebrews",
    "Jas": "James", "1 Pet": "1 Peter", "2 Pet": "2 Peter", "1 John": "1 John",
    "2 John": "2 John", "3 John": "3 John", "Jude": "Jude", "Rev": "Revelation",
}

# OpenBible tags a place with one or more of these; first match wins, in
# priority order, mapped to the site's place-type vocabulary.
TYPE_PRIORITY = [
    ("people group", "nation"),
    ("region", "region"), ("natural area", "region"), ("forest", "region"),
    ("river", "river"), ("wadi", "river"), ("canal", "river"),
    ("spring", "spring"), ("well", "spring"),
    ("body of water", "body-of-water"), ("pool", "body-of-water"), ("ford", "body-of-water"),
    ("valley", "valley"),
    ("mountain", "mountain"), ("mountain range", "mountain"), ("mountain ridge", "mountain"),
    ("mountain pass", "mountain"), ("hill", "mountain"), ("promontory", "mountain"),
    ("island", "island"),
    ("settlement", "town"),
    ("campsite", "site"),
]

# Base names that are not really a discrete place (compass points OpenBible
# lists because the text personifies them, a bare generic noun).
SKIP_NAMES = {"east", "west", "north", "south", "river"}

# OpenBible base name (lowercased) -> the site already has this place under a
# different spelling; skip rather than create a near-duplicate stub.
ALIAS_COVERED = {
    "negeb",       # -> Negev
    "great sea",   # -> Mediterranean Sea
}

# OpenBible splits these into numbered instances that are really one referent
# to a lay reader (which gulf "the Red Sea" means, tabernacle vs. temple
# "Holy Place"). Collapse to a single stub -- union of references and alt
# names -- rather than showing three near-identical "Red Sea" cards. Towns
# that genuinely share a name (three different Beth-shemeshes) are NOT listed
# here and stay split, disambiguated by first reference.
COLLAPSE_INSTANCES = {
    "red sea", "holy place", "most holy place", "salt sea",
}

FEATURE_WORDS = {
    "mount", "mountain", "wilderness", "desert", "valley", "brook", "wadi",
    "river", "lake", "sea", "plain", "plains", "city", "of", "the", "land",
    "region", "cave", "gate", "pool", "spring", "well", "tower", "hall",
}


def core_key(name):
    """Loose identity key: drop parentheticals, feature words, punctuation.
    Used only to decide 'the site already covers this', deliberately
    aggressive so we skip rather than risk a confusable duplicate."""
    n = re.sub(r"\(.*?\)", " ", name.lower())
    n = " ".join(w for w in re.split(r"[^a-z0-9]+", n) if w and w not in FEATURE_WORDS)
    return re.sub(r"[^a-z0-9]+", "", n)


def slugify(name):
    s = name.lower().replace("'", "").replace("’", "")
    s = s.replace("(", "").replace(")", "")
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")


def base_name(friendly_id):
    return re.sub(r"\s+\d+$", "", friendly_id).strip()


def map_type(types):
    tset = set(types or [])
    for key, mapped in TYPE_PRIORITY:
        if key in tset:
            return mapped
    return "site"


def map_identification(best_score):
    if best_score >= 500:
        return "secure", ""
    if best_score >= 150:
        return "disputed", ("Its location is disputed; scholars have proposed several "
                            "different modern sites for it.")
    return "unknown", "No location has been identified with confidence."


def expand_ref(readable):
    m = re.match(r"^((?:[123]\s)?[A-Za-z]+)\s+(\d+:\d+(?:-\d+)?)$", readable)
    if not m:
        return None
    book, rest = m.groups()
    full = BOOK.get(book)
    return f"{full} {rest}" if full else None


def collapse_alt_names(name_counts, canonical):
    """Cross-translation spellings worth keeping as alt_names: distinct
    enough from the canonical name that a KJV reader might search them.
    Collapse 'Kerith Brook' / 'Wadi Kerith' / 'Kerith Valley' to one."""
    canon_root = core_key(canonical)
    kept = {}  # root -> shortest surface form
    for variant in name_counts:
        if variant.strip().lower() == canonical.strip().lower():
            continue
        root = core_key(variant)
        if not root or root == canon_root:
            continue
        cur = kept.get(root)
        if cur is None or (len(variant), variant) < (len(cur), cur):
            kept[root] = variant
    return sorted(kept.values(), key=lambda v: (len(v), v))[:6]


def slim_record(rec):
    verses = rec.get("verses") or []
    best_score = 0
    for v in (rec.get("modern_associations") or {}).values():
        best_score = max(best_score, v.get("score", 0))
    return {
        "friendly_id": rec["friendly_id"],
        "types": rec.get("types") or [],
        "readables": [v["readable"] for v in verses],
        "sorts": [v["sort"] for v in verses],
        "name_counts": list((rec.get("translation_name_counts") or {}).keys()),
        "best_score": best_score,
    }


def refresh_slim():
    SRC_DIR.mkdir(exist_ok=True)
    print(f"downloading {UPSTREAM} ...")
    urllib.request.urlretrieve(UPSTREAM, FULL)
    n = 0
    with FULL.open() as fin, SLIM.open("w") as fout:
        for line in fin:
            rec = json.loads(line)
            if not (rec.get("verses")):
                continue
            fout.write(json.dumps(slim_record(rec), sort_keys=True) + "\n")
            n += 1
    print(f"wrote {SLIM.name} ({n} places with verses)")


def main():
    if "--refresh" in sys.argv:
        refresh_slim()

    if not SLIM.exists():
        sys.exit(f"missing {SLIM}; run with --refresh to fetch it")

    curated = {}
    for d in (PLACES_MAJOR, PLACES_MID, PLACES_MINOR):
        curated.update(d)
    covered = set(curated)
    curated_names_lower = set()
    for slug, c in curated.items():
        covered.add(core_key(c["name"]))
        curated_names_lower.add(c["name"].lower())
        for alt in c.get("alt", []):
            covered.add(core_key(alt))
            curated_names_lower.add(alt.lower())

    records = [json.loads(l) for l in SLIM.open()]

    # Group by base name so OpenBible's "Ramah 1".."Ramah 6" become one
    # disambiguated cluster of stubs rather than six unrelated ones.
    groups = {}
    skipped_covered = skipped_name = 0
    for rec in records:
        bn = base_name(rec["friendly_id"])
        low = bn.lower()
        if low in SKIP_NAMES:
            skipped_name += 1
            continue
        if low in ALIAS_COVERED or core_key(bn) in covered or slugify(bn) in covered:
            skipped_covered += 1
            continue
        groups.setdefault(bn, []).append(rec)

    gazetteer = {}
    used_slugs = set(covered)
    for bn in sorted(groups):
        members = sorted(groups[bn], key=lambda r: min(r["sorts"]) if r["sorts"] else "99999999")
        if bn.lower() in COLLAPSE_INSTANCES:
            merged = {
                "friendly_id": bn,
                "types": sorted({t for r in members for t in r["types"]}),
                "readables": [x for r in members for x in r["readables"]],
                "sorts": [x for r in members for x in r["sorts"]],
                "name_counts": sorted({n for r in members for n in r["name_counts"]}),
                "best_score": max(r["best_score"] for r in members),
            }
            members = [merged]

        for i, rec in enumerate(members):
            slug = slugify(bn)
            if len(members) > 1:
                m = re.search(r"\s+(\d+)$", rec["friendly_id"])
                slug = f"{slug}-{m.group(1) if m else i + 1}"
            while slug in used_slugs:
                slug += "-x"
            used_slugs.add(slug)

            refs = []
            for readable, srt in sorted(zip(rec["readables"], rec["sorts"]), key=lambda t: t[1]):
                full = expand_ref(readable)
                if full and full not in refs:
                    refs.append(full)
            if not refs:
                continue

            status, note = map_identification(rec["best_score"])
            # Drop any collapsed alt spelling that is itself another,
            # already-curated place's own name (e.g. OpenBible cross-
            # translation data lists "Babylon" as an alt spelling of the
            # separate region "Babylonia") -- keeping it would make the
            # in-prose place linker treat every mention of that name site-
            # wide as ambiguous between two genuinely different places.
            alts = [a for a in collapse_alt_names(rec["name_counts"], bn)
                    if a.lower() not in curated_names_lower]
            gazetteer[slug] = {
                "name": bn,
                "alt": alts,
                "type": map_type(rec["types"]),
                "region": "undetermined",
                "first_reference": refs[0],
                "references": refs,
                "id_status": status,
                "id_note": note,
                "modern": None,
                "source": "openbible",
            }

    payload = {
        "_note": (
            "Gazetteer of every named place in the Protestant canon, imported from "
            "OpenBible.info's Bible-Geocoding-Data (CC BY 4.0) by "
            "_build/import_openbible_places.py. Merged at lowest priority by "
            "generate_places.py; hand curation in _build/places_data.py always wins. "
            "Every entry is a name-only stub -- promote one by writing it a real "
            "entry in places_data.py, not by editing this file."
        ),
        "places": {k: gazetteer[k] for k in sorted(gazetteer)},
    }
    OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")
    print(f"wrote {OUT.relative_to(ROOT)}: {len(gazetteer)} gazetteer stubs "
          f"({skipped_covered} already covered, {skipped_name} skipped as non-places)")


if __name__ == "__main__":
    main()
