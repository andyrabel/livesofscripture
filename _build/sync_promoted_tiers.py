#!/usr/bin/env python3
"""Sync data/people.json index entries for people whose per-person file in
data/people/*.json has been promoted to tier "full" but whose index entry
was never updated to match (found while investigating Joseph son of Jacob
missing from the People page's full-tier view).

Overwrites the fields that come from the full record (tier, name, alt_names,
testament, gender, era, kingdom, topics, image, timeline, genealogy,
first_reference) while leaving index-only derived fields (disambiguation,
region) untouched.
"""
import json
import glob

INDEX_PATH = "data/people.json"

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
    index = json.load(open(INDEX_PATH))
    by_id = {p["person_id"]: p for p in index}

    updated = []
    for path in sorted(glob.glob("data/people/*.json")):
        full = json.load(open(path))
        pid = full.get("person_id")
        if full.get("tier") != "full":
            continue
        entry = by_id.get(pid)
        if entry is None or entry.get("tier") == "full":
            continue

        entry["name"] = full.get("name", entry.get("name"))
        entry["alt_names"] = full.get("alt_names", [])
        entry["tier"] = "full"
        entry["testament"] = full.get("testament", entry.get("testament"))
        if full.get("era"):
            entry["era"] = full["era"]
        if full.get("kingdom"):
            entry["kingdom"] = full["kingdom"]
        elif "kingdom" in entry:
            del entry["kingdom"]
        if full.get("topics"):
            entry["topics"] = full["topics"]
        img = full.get("image")
        if isinstance(img, dict) and img.get("file"):
            entry["image"] = img["file"]
        if full.get("timeline"):
            entry["timeline"] = full["timeline"]
        gen = flat_genealogy(full.get("genealogy"))
        if gen:
            entry["genealogy"] = gen
        elif "genealogy" in entry:
            del entry["genealogy"]
        entry["gender"] = full.get("gender", entry.get("gender"))
        if full.get("first_reference"):
            entry["first_reference"] = full["first_reference"]

        updated.append(pid)

    json.dump(index, open(INDEX_PATH, "w"), indent=2, ensure_ascii=False)
    with open(INDEX_PATH, "a") as f:
        f.write("\n")

    print(f"Synced {len(updated)} people from stub to full in {INDEX_PATH}")
    for pid in updated:
        print(f"  {pid}")

if __name__ == "__main__":
    main()
