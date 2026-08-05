#!/usr/bin/env python3
"""One-time backfill of the "genealogy" field onto data/people.json index
entries, copied from each person's data/people/<id>.json file.

_build/sync_promoted_tiers.py only copies genealogy across at the moment a
person is promoted from stub to full tier -- it skips anyone whose index
entry is already tier "full", so a genealogy edit made to a per-person file
after that point (or an index entry that was simply never synced once)
silently never reaches data/people.json. Found while fixing the Timeline
ordering bug: Lamech (son of Methushael, Genesis 4) had genealogy on his
person file but `null` genealogy on his index entry, so the Timeline's
parent-relaxation pass had nothing to anchor him to and misordered him
relative to Cain and Abel even after first_reference was backfilled.

Same flattening rule as sync_promoted_tiers.py's flat_genealogy(): only
non-empty father/mother/spouses/children keys are kept, and an entry with
none of those becomes `None` rather than an empty dict.

Never creates new entries; only adds/updates the genealogy key on existing
index entries whose person file's flattened genealogy differs. Safe to
re-run.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PEOPLE_DIR = ROOT / "data" / "people"
PEOPLE_INDEX = ROOT / "data" / "people.json"


def flat_genealogy(g):
    if not g:
        return None
    out = {}
    for key in ("father", "mother", "spouses", "children"):
        val = g.get(key)
        if val:
            out[key] = val
    return out or None


def main():
    index = json.loads(PEOPLE_INDEX.read_text())

    updated = 0
    skipped_no_file = 0

    for entry in index:
        pid = entry["person_id"]
        file_path = PEOPLE_DIR / f"{pid}.json"
        if not file_path.exists():
            skipped_no_file += 1
            continue

        person = json.loads(file_path.read_text())
        flat = flat_genealogy(person.get("genealogy"))
        if flat != entry.get("genealogy"):
            if flat is None:
                entry.pop("genealogy", None)
            else:
                entry["genealogy"] = flat
            updated += 1

    PEOPLE_INDEX.write_text(json.dumps(index, indent=2, ensure_ascii=False) + "\n")

    print(f"Index entries updated with genealogy: {updated}")
    print(f"Skipped (no matching data/people/<id>.json on disk): {skipped_no_file}")


if __name__ == "__main__":
    main()
