#!/usr/bin/env python3
"""One-time backfill of a "gender" field ("male"/"female") onto existing
person entries, sourced from BibleData-Person.csv's "sex" column (see
_build/import_bible_data.py for the same CSV and the same person_id -> site
slug mapping logic, duplicated here deliberately so this script only ever
touches the gender field -- never creates new entries and never touches
genealogy, matching the site's existing "gender-free" file layout except for
this one added key).

Only writes to data/people/<id>.json files that already exist and to
data/people.json (the lightweight index); never creates new person files.
Safe to re-run.
"""
import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = Path(__file__).resolve().parent / "bible-data-source"
PEOPLE_DIR = ROOT / "data" / "people"
PEOPLE_INDEX = ROOT / "data" / "people.json"

EXCLUDED_PERSON_IDS = {"YHVH_1", "YHVH_2"}

# Kept identical to _build/import_bible_data.py's RESERVED map.
RESERVED = {
    "Aaron_1": "aaron",
    "Abram_1": "abraham",
    "Bathsheba_1": "bathsheba",
    "Boaz_1": "boaz",
    "David_1": "david",
    "Hagar_1": "hagar",
    "Isaac_1": "isaac",
    "Ishmael_1": "ishmael",
    "Jesse_1": "jesse",
    "Jochebed_1": "jochebed",
    "Jonathan_2": "jonathan",
    "Moses_1": "moses",
    "Naomi_1": "naomi",
    "Saul_2": "paul",
    "Simon_1": "peter",
    "Ruth_1": "ruth",
    "Samuel_2": "samuel",
    "Sarai_1": "sarah",
    "Solomon_1": "solomon",
    "Zipporah_1": "zipporah",
    "Amram_1": "amram",
    "Elimelech_1": "elimelech",
    "Gershom_1": "gershom",
    "Mahlon_1": "mahlon",
    "Obed_1": "obed",
    "Terah_1": "terah",
}


def slugify(name):
    s = name.lower()
    s = re.sub(r"[’']", "", s)
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")


def load_csv(name):
    path = SRC / name
    with open(path, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def main():
    persons = load_csv("BibleData-Person.csv")
    persons = [p for p in persons if p["person_id"] not in EXCLUDED_PERSON_IDS]
    persons.sort(key=lambda p: int(p["person_sequence"]))

    labels = load_csv("BibleData-PersonLabel.csv")
    labels_by_person = {}
    for l in labels:
        if l["person_id"] in EXCLUDED_PERSON_IDS:
            continue
        labels_by_person.setdefault(l["person_id"], []).append(l)

    verses = load_csv("BibleData-PersonVerse.csv")
    label_freq = {}
    for v in verses:
        if v["person_id"] in EXCLUDED_PERSON_IDS:
            continue
        label_freq[v["person_label_id"]] = label_freq.get(v["person_label_id"], 0) + 1

    canonical_name = {}
    for p in persons:
        pid = p["person_id"]
        proper = [l for l in labels_by_person.get(pid, []) if l["label_type"] == "proper name"]
        if not proper:
            canonical_name[pid] = p["person_name"]
            continue
        proper.sort(key=lambda l: (-label_freq.get(l["person_label_id"], 0), int(l["label_sequence"])))
        canonical_name[pid] = proper[0]["english_label"]

    # Same slug-assignment algorithm as import_bible_data.py, so this
    # reproduces the exact same slugs already on disk.
    slug_of = {}
    taken = set()
    next_suffix = {}
    for pid, slug in RESERVED.items():
        base = slugify(slug)
        slug_of[pid] = slug
        taken.add(slug)
        next_suffix[base] = 2

    for p in persons:
        pid = p["person_id"]
        if pid in slug_of:
            continue
        base = slugify(canonical_name[pid])
        if base not in taken:
            slug_of[pid] = base
            taken.add(base)
            next_suffix[base] = 2
        else:
            n = next_suffix.get(base, 2)
            candidate = f"{base}-{n}"
            while candidate in taken:
                n += 1
                candidate = f"{base}-{n}"
            slug_of[pid] = candidate
            taken.add(candidate)
            next_suffix[base] = n + 1

    index = json.loads(PEOPLE_INDEX.read_text())
    index_by_id = {e["person_id"]: e for e in index}

    updated_files = 0
    updated_index = 0
    skipped_no_file = 0

    for p in persons:
        pid = p["person_id"]
        slug = slug_of[pid]
        gender = p.get("sex") or None
        if not gender:
            continue

        file_path = PEOPLE_DIR / f"{slug}.json"
        if not file_path.exists():
            skipped_no_file += 1
            continue

        entry = json.loads(file_path.read_text())
        if entry.get("gender") != gender:
            entry["gender"] = gender
            file_path.write_text(json.dumps(entry, indent=2, ensure_ascii=False) + "\n")
            updated_files += 1

        idx_entry = index_by_id.get(slug)
        if idx_entry is not None and idx_entry.get("gender") != gender:
            idx_entry["gender"] = gender
            updated_index += 1

    PEOPLE_INDEX.write_text(json.dumps(index, indent=2, ensure_ascii=False) + "\n")

    print(f"Persons processed (excluding YHVH_1/2): {len(persons)}")
    print(f"Person files updated with gender: {updated_files}")
    print(f"Index entries updated with gender: {updated_index}")
    print(f"Skipped (no matching data/people/<slug>.json on disk): {skipped_no_file}")


if __name__ == "__main__":
    main()
