#!/usr/bin/env python3
"""One-time backfill of the "first_reference" field onto data/people.json
index entries, copied from each person's data/people/<id>.json file.

Every per-person file already carries first_reference (references[0]), but
the lightweight index never picked it up when entries were created or synced
from stub to full -- see js/app.js's timelineNarrativeRank(), which reads
person.first_reference off the INDEX (not the per-person file) to order
era-only people left-to-right on the Timeline page. Without it, that
function always returned null, so era-only ordering silently fell back to
whatever the sort's tie-break happened to produce instead of narrative
(book/chapter) order.

Never creates new entries; only adds/updates the first_reference key on
existing index entries whose person file has one. Safe to re-run.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PEOPLE_DIR = ROOT / "data" / "people"
PEOPLE_INDEX = ROOT / "data" / "people.json"


def main():
    index = json.loads(PEOPLE_INDEX.read_text())

    updated = 0
    skipped_no_ref = 0
    skipped_no_file = 0

    for entry in index:
        pid = entry["person_id"]
        file_path = PEOPLE_DIR / f"{pid}.json"
        if not file_path.exists():
            skipped_no_file += 1
            continue

        person = json.loads(file_path.read_text())
        ref = person.get("first_reference")
        if not ref:
            skipped_no_ref += 1
            continue

        if entry.get("first_reference") != ref:
            entry["first_reference"] = ref
            updated += 1

    PEOPLE_INDEX.write_text(json.dumps(index, indent=2, ensure_ascii=False) + "\n")

    print(f"Index entries updated with first_reference: {updated}")
    print(f"Skipped (no first_reference on person file): {skipped_no_ref}")
    print(f"Skipped (no matching data/people/<id>.json on disk): {skipped_no_file}")


if __name__ == "__main__":
    main()
