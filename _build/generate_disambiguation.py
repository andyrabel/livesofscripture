#!/usr/bin/env python3
"""Compute a short `disambiguation` string for every person who shares
their `name` with at least one other person in the dataset, and bake it
into data/people.json (the lightweight index) so the People List page can
render it without fetching every data/people/<id>.json file -- same
pattern as infer_stub_eras.py.

Follows the three disambiguation rules decided 2026-08-03 (see CLAUDE.md,
"Name Disambiguation"):

1. Distinguishing name/nickname/title -- only applied where the dataset
   already encodes it (an alt_name that extends the base name, e.g. base
   "Judas" + alt_name "Judas Iscariot" -> "Iscariot"). Never fabricated:
   most collisions get no text from this rule until a future hand-curation
   pass adds textual epithets (e.g. "Sons of Thunder") for well-known cases.
2. Relationship to a named person -- father, else mother, else first
   spouse, else first child, from the person's own genealogy edges (which
   are literal biblical genealogy data, not invented). Worded as "son of"/
   "daughter of"/"husband of"/"wife of"/"father of"/"mother of" by the
   subject's gender, falling back to "child of"/"spouse of"/"parent of"
   when gender is unknown.
3. Abbreviated first reference -- `first_reference` with its book name
   swapped for a standard abbreviation.

Whichever rules have data are joined; rules with no data are simply
omitted (a bare "(Gen 4:1)" is a valid, honest result). Re-run this script
(before generate_static_site.py) whenever `data/people/*.json` genealogy,
name, alt_names, or first_reference values change.
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

BOOK_ABBREV = {
    "Genesis": "Gen", "Exodus": "Exod", "Leviticus": "Lev", "Numbers": "Num",
    "Deuteronomy": "Deut", "Joshua": "Josh", "Judges": "Judg", "Ruth": "Ruth",
    "1 Samuel": "1 Sam", "2 Samuel": "2 Sam", "1 Kings": "1 Kings", "2 Kings": "2 Kings",
    "1 Chronicles": "1 Chr", "2 Chronicles": "2 Chr", "Ezra": "Ezra", "Nehemiah": "Neh",
    "Esther": "Esth", "Job": "Job", "Psalms": "Ps", "Proverbs": "Prov",
    "Ecclesiastes": "Eccl", "Song of Solomon": "Song", "Isaiah": "Isa", "Jeremiah": "Jer",
    "Lamentations": "Lam", "Ezekiel": "Ezek", "Daniel": "Dan", "Hosea": "Hos",
    "Joel": "Joel", "Amos": "Amos", "Obadiah": "Obad", "Jonah": "Jonah", "Micah": "Mic",
    "Nahum": "Nah", "Habakkuk": "Hab", "Zephaniah": "Zeph", "Haggai": "Hag",
    "Zechariah": "Zech", "Malachi": "Mal", "Matthew": "Matt", "Mark": "Mark",
    "Luke": "Luke", "John": "John", "Acts": "Acts", "Romans": "Rom",
    "1 Corinthians": "1 Cor", "2 Corinthians": "2 Cor", "Galatians": "Gal",
    "Ephesians": "Eph", "Philippians": "Phil", "Colossians": "Col",
    "1 Thessalonians": "1 Thess", "2 Thessalonians": "2 Thess", "1 Timothy": "1 Tim",
    "2 Timothy": "2 Tim", "Titus": "Titus", "Philemon": "Phlm", "Hebrews": "Heb",
    "James": "James", "1 Peter": "1 Pet", "2 Peter": "2 Pet", "1 John": "1 John",
    "2 John": "2 John", "3 John": "3 John", "Jude": "Jude", "Revelation": "Rev",
}
# Longest book name first, so "1 Kings" doesn't get shadowed by a partial match.
_BOOK_NAMES_BY_LEN = sorted(BOOK_ABBREV, key=len, reverse=True)


def abbreviate_reference(ref):
    if not ref:
        return None
    for book in _BOOK_NAMES_BY_LEN:
        if ref == book or ref.startswith(book + " "):
            return BOOK_ABBREV[book] + ref[len(book):]
    return ref


def alt_name_suffix(name, alt_names):
    base = name.strip().lower()
    for alt in alt_names or []:
        alt = alt.strip()
        if alt.lower().startswith(base + " ") and len(alt) > len(base) + 1:
            return alt[len(name.strip()) + 1:]
    return None


def relationship_phrase(gen, gender, names_by_id):
    if not gen:
        return None
    father = gen.get("father")
    mother = gen.get("mother")
    spouses = gen.get("spouses") or []
    children = gen.get("children") or []

    if father and father in names_by_id:
        rel = "son of" if gender == "male" else "daughter of" if gender == "female" else "child of"
        return f"{rel} {names_by_id[father]}"
    if mother and mother in names_by_id:
        rel = "son of" if gender == "male" else "daughter of" if gender == "female" else "child of"
        return f"{rel} {names_by_id[mother]}"
    if spouses and spouses[0] in names_by_id:
        rel = "husband of" if gender == "male" else "wife of" if gender == "female" else "spouse of"
        return f"{rel} {names_by_id[spouses[0]]}"
    if children and children[0] in names_by_id:
        rel = "father of" if gender == "male" else "mother of" if gender == "female" else "parent of"
        return f"{rel} {names_by_id[children[0]]}"
    return None


def build_disambiguation(person, rel):
    parts = []
    suffix = alt_name_suffix(person["name"], person.get("alt_names"))
    if suffix:
        parts.append(suffix)
    if rel:
        parts.append(rel)
    text = ", ".join(parts)
    abbrev_ref = abbreviate_reference(person.get("first_reference"))
    if abbrev_ref:
        return f"{text} ({abbrev_ref})" if text else f"({abbrev_ref})"
    return text or None


def main():
    people_dir = ROOT / "data" / "people"
    index_path = ROOT / "data" / "people.json"
    index = json.loads(index_path.read_text())

    people = {}
    for entry in index:
        pid = entry["person_id"]
        path = people_dir / f"{pid}.json"
        if not path.exists():
            continue
        people[pid] = json.loads(path.read_text())

    names_by_id = {pid: p["name"] for pid, p in people.items()}

    groups = {}
    for pid, p in people.items():
        groups.setdefault(p["name"].strip().lower(), []).append(pid)
    collisions = {k: v for k, v in groups.items() if len(v) > 1}

    # A relationship phrase that's shared by two-plus people in the same
    # name collision fails to disambiguate them and usually signals a
    # pre-existing data problem (e.g. a duplicate person entry, or two
    # distinct genealogy ancestors that got collapsed onto one person_id
    # upstream) rather than a genuine "we don't know more" case -- see
    # CLAUDE.md "Name Disambiguation" for examples found 2026-08-03.
    # Suppress it rather than display a misleading non-distinguishing
    # phrase; the reference-only fallback still applies.
    rel_by_pid = {}
    for key, ids in collisions.items():
        phrase_counts = {}
        for pid in ids:
            rel = relationship_phrase(people[pid].get("genealogy"), people[pid].get("gender"), names_by_id)
            rel_by_pid[pid] = rel
            if rel:
                phrase_counts[rel] = phrase_counts.get(rel, 0) + 1
        for pid in ids:
            if rel_by_pid[pid] and phrase_counts[rel_by_pid[pid]] > 1:
                rel_by_pid[pid] = None

    count = 0
    for entry in index:
        pid = entry["person_id"]
        if pid not in people:
            continue
        key = people[pid]["name"].strip().lower()
        if key in collisions:
            disamb = build_disambiguation(people[pid], rel_by_pid.get(pid))
            if disamb:
                entry["disambiguation"] = disamb
                count += 1
            else:
                entry.pop("disambiguation", None)
        else:
            entry.pop("disambiguation", None)

    index_path.write_text(json.dumps(index, indent=2, ensure_ascii=False) + "\n")
    affected = sum(len(v) for v in collisions.values())
    print(f"{len(collisions)} colliding names, {affected} people affected, {count} got disambiguation text")


if __name__ == "__main__":
    main()
