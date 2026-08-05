#!/usr/bin/env python3
"""Bulk-import genealogy data from BradyStephenson/bible-data (CC BY 4.0).

Source CSVs are vendored under _build/bible-data-source/ (see that directory's
LICENSE/CITATION.cff). This script reads BibleData-Person, -PersonLabel,
-PersonRelationship, -PersonVerse, and -Book, then:

  - Creates a stub entry (data/people/<id>.json) for every named individual
    not already covered by a hand-authored entry.
  - Fills in missing genealogy links (father/mother/spouses/children) on the
    26 existing hand-authored entries, without touching their story text.
  - Appends deduplicated parent-child and marriage edges to
    data/connections.json.
  - Rewrites data/people.json (the lightweight index).

Deliberately excluded: YHVH_1 and YHVH_2 (the dataset's rows for God/the
Father) are not "a person named in the Bible" in the sense this site profiles
-- every full entry's story is meant to point TO Christ, so God cannot be a
subject alongside Ruth or Peter. Everything else the dataset treats as a
person (including named angels and Satan) is imported normally.

Only relationship_type in {father, mother, husband} is imported (source data
double-records each fact from both sides, e.g. father/son pairs -- using one
direction per relationship avoids duplicate edges). Non-family relationship
types (killer, servant, disciple, etc.) are out of scope: per CLAUDE.md,
narrative relationship edges are hand-added per full entry from the story
text, not bulk-imported.

Re-run after re-vendoring updated source CSVs. Safe to re-run: existing full
entries are only ever enriched (missing fields filled), never overwritten;
existing connections are never duplicated.
"""
import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = Path(__file__).resolve().parent / "bible-data-source"
PEOPLE_DIR = ROOT / "data" / "people"
PEOPLE_INDEX = ROOT / "data" / "people.json"
CONNECTIONS = ROOT / "data" / "connections.json"

EXCLUDED_PERSON_IDS = {"YHVH_1", "YHVH_2"}

# Map the 26 hand-authored site entries to their BibleData person_id, found
# by cross-referencing each entry's source_summary against BibleData-Person.csv
# person_notes (verified by hand -- see conversation this was built in).
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
    books = load_csv("BibleData-Book.csv")
    book_by_usx = {b["usx_code"]: b for b in books}

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
    verses_by_person = {}
    for v in verses:
        pid = v["person_id"]
        if pid in EXCLUDED_PERSON_IDS:
            continue
        label_freq[v["person_label_id"]] = label_freq.get(v["person_label_id"], 0) + 1
        verses_by_person.setdefault(pid, []).append(v)

    relationships = load_csv("BibleData-PersonRelationship.csv")

    # ------------------------------------------------------------------
    # Canonical name + alt_names per person, chosen by text frequency of
    # each "proper name" label (handles renames: Abram->Abraham, Simon->
    # Peter, Saul->Paul, Sarai->Sarah -- picks whichever name Scripture
    # actually uses most, not just the earliest or the last given).
    # ------------------------------------------------------------------
    canonical_name = {}
    alt_names = {}
    for p in persons:
        pid = p["person_id"]
        proper = [l for l in labels_by_person.get(pid, []) if l["label_type"] == "proper name"]
        if not proper:
            canonical_name[pid] = p["person_name"]
            alt_names[pid] = []
            continue
        proper.sort(key=lambda l: (-label_freq.get(l["person_label_id"], 0), int(l["label_sequence"])))
        best = proper[0]["english_label"]
        canonical_name[pid] = best
        seen = []
        for l in proper[1:]:
            nm = l["english_label"]
            if nm != best and nm not in seen:
                seen.append(nm)
        alt_names[pid] = seen

    # ------------------------------------------------------------------
    # Slug assignment: reserved ids keep their existing site person_id;
    # everyone else gets slugify(canonical_name), disambiguated with a
    # numeric suffix on collision, processed in canonical (person_sequence)
    # order so results are deterministic.
    # ------------------------------------------------------------------
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

    # ------------------------------------------------------------------
    # References + testament, from each person's verse mentions.
    # ------------------------------------------------------------------
    def refs_and_testament(pid):
        vlist = verses_by_person.get(pid)
        if not vlist:
            return [], "OT"
        vlist = sorted(vlist, key=lambda v: int(v["person_verse_sequence"]))
        chapters = {}  # (book_name, chapter) -> [min_verse, max_verse, min_seq]
        for v in vlist:
            ref = v["reference_id"]  # e.g. "GEN 1:1"
            m = re.match(r"^(\S+) (\d+):(\d+)", ref)
            if not m:
                continue
            usx, chap, vs = m.group(1), int(m.group(2)), int(m.group(3))
            book = book_by_usx.get(usx)
            if not book:
                continue
            book_name = book["book_name"]
            seq = int(v["person_verse_sequence"])
            key = (int(book["christian_sequence"]), book_name, chap)
            if key not in chapters:
                chapters[key] = [vs, vs, seq]
            else:
                chapters[key][0] = min(chapters[key][0], vs)
                chapters[key][1] = max(chapters[key][1], vs)
                chapters[key][2] = min(chapters[key][2], seq)

        ordered = sorted(chapters.items(), key=lambda kv: kv[1][2])
        refs = []
        for (christian_seq, book_name, chap), (vmin, vmax, _seq) in ordered:
            if vmin == vmax:
                refs.append(f"{book_name} {chap}:{vmin}")
            else:
                refs.append(f"{book_name} {chap}:{vmin}-{vmax}")

        first_christian_seq = ordered[0][0][0] if ordered else 1
        testament = "OT" if first_christian_seq <= 39 else "NT"
        return refs, testament

    # ------------------------------------------------------------------
    # Parent-child + marriage edges (one direction per fact; see docstring).
    # ------------------------------------------------------------------
    parent_child = []  # (parent_pid, child_pid, label)
    married = []  # (husband_pid, wife_pid)
    for r in relationships:
        p1, p2, rtype = r["person_id_1"], r["person_id_2"], r["relationship_type"]
        if p1 in EXCLUDED_PERSON_IDS or p2 in EXCLUDED_PERSON_IDS:
            continue
        if p1 not in slug_of or p2 not in slug_of:
            continue
        if rtype == "father":
            parent_child.append((p1, p2, "begot"))
        elif rtype == "mother":
            parent_child.append((p1, p2, "bore"))
        elif rtype == "husband":
            married.append((p1, p2))

    father_of = {}
    mother_of = {}
    children_of = {}
    for parent, child, label in parent_child:
        if label == "begot":
            father_of.setdefault(child, parent)
        else:
            mother_of.setdefault(child, parent)
        children_of.setdefault(parent, []).append(child)

    spouses_of = {}
    for husband, wife in married:
        spouses_of.setdefault(husband, []).append(wife)
        spouses_of.setdefault(wife, []).append(husband)

    # ------------------------------------------------------------------
    # Write/merge person JSON files + index.
    # ------------------------------------------------------------------
    index = json.loads(PEOPLE_INDEX.read_text())
    index_by_id = {e["person_id"]: e for e in index}

    created = 0
    enriched = 0

    for p in persons:
        pid = p["person_id"]
        slug = slug_of[pid]
        file_path = PEOPLE_DIR / f"{slug}.json"

        father_slug = slug_of.get(father_of.get(pid))
        mother_slug = slug_of.get(mother_of.get(pid))
        spouse_slugs = sorted({slug_of[s] for s in spouses_of.get(pid, []) if s in slug_of})
        child_slugs = sorted({slug_of[c] for c in children_of.get(pid, []) if c in slug_of})

        if file_path.exists():
            # Existing hand-authored entry: fill genealogy gaps only.
            entry = json.loads(file_path.read_text())
            g = entry.setdefault("genealogy", {"father": None, "mother": None, "spouses": [], "children": []})
            changed = False
            if g.get("father") is None and father_slug:
                g["father"] = father_slug
                changed = True
            if g.get("mother") is None and mother_slug:
                g["mother"] = mother_slug
                changed = True
            existing_spouses = set(g.get("spouses") or [])
            new_spouses = existing_spouses | set(spouse_slugs)
            if new_spouses != existing_spouses:
                g["spouses"] = sorted(new_spouses)
                changed = True
            existing_children = set(g.get("children") or [])
            new_children = existing_children | set(child_slugs)
            if new_children != existing_children:
                g["children"] = sorted(new_children)
                changed = True
            if changed:
                file_path.write_text(json.dumps(entry, indent=2, ensure_ascii=False) + "\n")
                enriched += 1
            continue

        refs, testament = refs_and_testament(pid)
        entry = {
            "person_id": slug,
            "name": canonical_name[pid],
            "alt_names": alt_names[pid],
            "tier": "stub",
            "testament": testament,
            "references": refs,
            "genealogy": {
                "father": father_slug,
                "mother": mother_slug,
                "spouses": spouse_slugs,
                "children": child_slugs,
            },
        }
        file_path.write_text(json.dumps(entry, indent=2, ensure_ascii=False) + "\n")
        index_by_id[slug] = {
            "person_id": slug,
            "name": canonical_name[pid],
            "alt_names": alt_names[pid],
            "tier": "stub",
            "testament": testament,
            "first_reference": refs[0] if refs else None,
        }
        created += 1

    new_index = list(index_by_id.values())
    PEOPLE_INDEX.write_text(json.dumps(new_index, indent=2, ensure_ascii=False) + "\n")

    # ------------------------------------------------------------------
    # Append deduplicated edges to connections.json.
    # ------------------------------------------------------------------
    connections = json.loads(CONNECTIONS.read_text())
    existing_edges = {(e["from"], e["to"], e["type"]) for e in connections}

    new_edges = []
    for parent, child, label in parent_child:
        pslug, cslug = slug_of[parent], slug_of[child]
        key = (pslug, cslug, "parent-child")
        if key in existing_edges:
            continue
        existing_edges.add(key)
        new_edges.append({"from": pslug, "to": cslug, "label": label, "type": "parent-child", "mutual": False})

    seen_couples = set()
    for husband, wife in married:
        hslug, wslug = slug_of[husband], slug_of[wife]
        key = (hslug, wslug, "married")
        if key in existing_edges or (hslug, wslug) in seen_couples or (wslug, hslug) in seen_couples:
            continue
        existing_edges.add(key)
        seen_couples.add((hslug, wslug))
        new_edges.append({"from": hslug, "to": wslug, "label": "married", "type": "married", "mutual": True})

    # Insert after the last existing parent-child/married edge, ahead of
    # the hand-curated narrative-relationship block, to keep the file
    # organized the same way it already is.
    insert_at = 0
    for i, e in enumerate(connections):
        if e.get("type") in ("parent-child", "married"):
            insert_at = i + 1
    connections[insert_at:insert_at] = new_edges
    CONNECTIONS.write_text(json.dumps(connections, indent=2, ensure_ascii=False) + "\n")

    print(f"Persons processed (excluding YHVH_1/2): {len(persons)}")
    print(f"New stub entries created: {created}")
    print(f"Existing entries enriched with genealogy links: {enriched}")
    print(f"New connection edges added: {len(new_edges)}")


if __name__ == "__main__":
    main()
