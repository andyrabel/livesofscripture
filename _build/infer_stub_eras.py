#!/usr/bin/env python3
"""Infer an `era` (and where possible `region` and a minimal `genealogy`)
for every stub person, and bake it into data/people.json (the lightweight
index), so the timeline page can place everyone named in a genealogical
chain -- not just full-tier entries -- without fetching all ~3,000
individual data/people/<id>.json files.

Two sources feed each stub's era, in priority order:

1. Genealogy proximity: a bounded-hop breadth-first search out from every
   full-tier person (whose era is already known and human-authored) across
   father/mother/spouse/children links. Capped at MAX_HOPS so a small
   family cluster around a full-tier anchor (e.g. a 1 Chronicles tribal
   list) gets corrected accurately, but the search cannot leap across the
   many unanchored generations of Genesis 5/11 and mislabel, say, Adam with
   Abraham's "Patriarchal" era just because a long chain of begats
   eventually connects them.
2. Book/chapter default: for anyone the bounded search doesn't reach, a
   coarse era guess based on which book (and, for Genesis and the
   Chronicles genealogies, which chapter) their first_reference falls in.

This is a derived visualization aid, not curated content -- see the
Timeline section of CLAUDE.md. Re-run this script (before
generate_static_site.py) whenever genealogy data or full-tier era/timeline
values change.
"""
import json
import re
from collections import deque
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MAX_HOPS = 6

BOOK_ORDER = [
    "Genesis", "Exodus", "Leviticus", "Numbers", "Deuteronomy",
    "Joshua", "Judges", "Ruth",
    "1 Samuel", "2 Samuel", "1 Kings", "2 Kings",
    "1 Chronicles", "2 Chronicles", "Ezra", "Nehemiah", "Esther",
    "Job", "Psalms", "Proverbs", "Ecclesiastes", "Song of Solomon",
    "Isaiah", "Jeremiah", "Lamentations", "Ezekiel", "Daniel",
    "Hosea", "Joel", "Amos", "Obadiah", "Jonah", "Micah", "Nahum",
    "Habakkuk", "Zephaniah", "Haggai", "Zechariah", "Malachi",
    "Matthew", "Mark", "Luke", "John", "Acts",
    "Romans", "1 Corinthians", "2 Corinthians", "Galatians", "Ephesians",
    "Philippians", "Colossians", "1 Thessalonians", "2 Thessalonians",
    "1 Timothy", "2 Timothy", "Titus", "Philemon", "Hebrews",
    "James", "1 Peter", "2 Peter", "1 John", "2 John", "3 John", "Jude",
    "Revelation",
]

SIMPLE_BOOK_ERA = {
    "Exodus": "Exodus/Wilderness", "Leviticus": "Exodus/Wilderness",
    "Numbers": "Exodus/Wilderness", "Deuteronomy": "Exodus/Wilderness",
    "Joshua": "Judges", "Judges": "Judges", "Ruth": "Judges",
    "1 Samuel": "United Monarchy", "2 Samuel": "United Monarchy",
    "2 Kings": "Divided Monarchy",
    "Ezra": "Post-Exile/Intertestamental", "Nehemiah": "Post-Exile/Intertestamental",
    "Esther": "Post-Exile/Intertestamental",
    "Job": "Patriarchal",
    "Psalms": "United Monarchy", "Proverbs": "United Monarchy",
    "Ecclesiastes": "United Monarchy", "Song of Solomon": "United Monarchy",
    "Isaiah": "Divided Monarchy", "Jeremiah": "Divided Monarchy",
    "Lamentations": "Divided Monarchy",
    "Ezekiel": "Exile", "Daniel": "Exile",
    "Hosea": "Divided Monarchy", "Joel": "Divided Monarchy", "Amos": "Divided Monarchy",
    "Obadiah": "Divided Monarchy", "Jonah": "Divided Monarchy", "Micah": "Divided Monarchy",
    "Nahum": "Divided Monarchy", "Habakkuk": "Divided Monarchy", "Zephaniah": "Divided Monarchy",
    "Haggai": "Post-Exile/Intertestamental", "Zechariah": "Post-Exile/Intertestamental",
    "Malachi": "Post-Exile/Intertestamental",
    "Matthew": "Gospels", "Mark": "Gospels", "Luke": "Gospels", "John": "Gospels",
}
APOSTOLIC_BOOKS = {
    "Acts", "Romans", "1 Corinthians", "2 Corinthians", "Galatians", "Ephesians",
    "Philippians", "Colossians", "1 Thessalonians", "2 Thessalonians",
    "1 Timothy", "2 Timothy", "Titus", "Philemon", "Hebrews",
    "James", "1 Peter", "2 Peter", "1 John", "2 John", "3 John", "Jude",
    "Revelation",
}
for _b in APOSTOLIC_BOOKS:
    SIMPLE_BOOK_ERA[_b] = "Apostolic"


def parse_reference(ref):
    if not ref:
        return None, None, None
    best_book = None
    for book in BOOK_ORDER:
        if (ref == book or ref.startswith(f"{book} ")) and (not best_book or len(book) > len(best_book)):
            best_book = book
    if not best_book:
        return None, None, None
    rest = ref[len(best_book):].strip()
    m = re.match(r"^(\d+)(?::(\d+))?", rest)
    if not m:
        return best_book, None, None
    chapter = int(m.group(1))
    verse = int(m.group(2)) if m.group(2) else None
    return best_book, chapter, verse


# HIGH confidence: this book/chapter (sometimes verse) range names a specific
# era clearly enough that genealogy BFS should not override it (BFS hop
# distance can cross a major era boundary, e.g. the exile, in as few as 3-4
# hops for a royal line, which is not a signal we trust over an explicit
# textual placement). LOW confidence: a coarse whole-book/chapter-range
# guess, used only as a last resort when BFS doesn't reach a person at all.
def book_default_era(ref):
    book, chapter, verse = parse_reference(ref)
    if not book:
        return None, None
    if book == "Genesis":
        if chapter is not None and chapter <= 11:
            return "Primeval History", "high"
        return "Patriarchal", "low"
    if book == "1 Kings":
        if chapter is not None and chapter <= 11:
            return "United Monarchy", "low"
        return "Divided Monarchy", "low"
    if book == "2 Chronicles":
        if chapter is not None and chapter <= 9:
            return "United Monarchy", "low"
        return "Divided Monarchy", "low"
    if book == "1 Chronicles":
        if chapter == 1:
            return "Patriarchal", "low"  # spans Adam-to-Edom; BFS refines the antediluvian part
        if chapter == 3:
            # The Chronicler's Davidic king-list, uniquely spanning three
            # eras in one chapter: David's sons, then the kings of Judah
            # down to the exile, then Jeconiah's post-exilic descendants
            # (Zerubbabel and later) -- verse position is decisive here.
            if verse is not None and verse <= 9:
                return "United Monarchy", "high"
            if verse is not None and verse <= 16:
                return "Divided Monarchy", "high"
            return "Post-Exile/Intertestamental", "high"
        if chapter is not None and chapter >= 9:
            return "Post-Exile/Intertestamental", "high"
        return "Divided Monarchy", "low"  # ch2-8 tribal lists: coarse guess
    era = SIMPLE_BOOK_ERA.get(book)
    return (era, "low") if era else (None, None)


def main():
    people_dir = ROOT / "data" / "people"
    index_path = ROOT / "data" / "people.json"

    index = json.loads(index_path.read_text())
    genealogy = {}
    first_ref = {}
    known_era = {}
    known_region = {}
    known_kingdom = {}
    full_timeline = {}

    for entry in index:
        pid = entry["person_id"]
        path = people_dir / f"{pid}.json"
        if not path.exists():
            continue
        person = json.loads(path.read_text())
        gen = person.get("genealogy") or {}
        genealogy[pid] = gen
        first_ref[pid] = person.get("first_reference")
        if entry["tier"] == "full":
            if person.get("era"):
                known_era[pid] = person["era"]
            if person.get("region"):
                known_region[pid] = person["region"]
            if person.get("kingdom"):
                known_kingdom[pid] = person["kingdom"]
            if person.get("timeline"):
                full_timeline[pid] = person["timeline"]

    # Undirected adjacency: father/mother/spouses/children edges.
    adjacency = {pid: set() for pid in genealogy}
    for pid, gen in genealogy.items():
        neighbors = []
        if gen.get("father"):
            neighbors.append(gen["father"])
        if gen.get("mother"):
            neighbors.append(gen["mother"])
        neighbors.extend(gen.get("spouses") or [])
        neighbors.extend(gen.get("children") or [])
        for n in neighbors:
            if n in adjacency:
                adjacency[pid].add(n)
                adjacency[n].add(pid)

    # High-confidence book/chapter defaults are computed first and are
    # authoritative -- they win over genealogy BFS, because a bounded hop
    # search can still cross a major era boundary in just a few hops for a
    # tightly-recorded royal line (e.g. Josiah -> Jehoiakim -> Jehoiachin ->
    # Zerubbabel spans Divided Monarchy to Post-Exile in 4 hops), which is
    # not a signal worth trusting over an explicit textual placement.
    high_conf_era = {}
    low_conf_era = {}
    for pid in genealogy:
        era, confidence = book_default_era(first_ref.get(pid))
        if confidence == "high":
            high_conf_era[pid] = era
        elif confidence == "low":
            low_conf_era[pid] = era

    # Multi-source bounded BFS for era, seeded from full-tier anchors.
    # Skips anyone with a high-confidence book default -- those are already
    # decided -- but still uses them as BFS sources so their neighbors can
    # benefit from a more specific placement than the low-confidence
    # book/chapter guess would give.
    #
    # known_era must win when a pid has both: a full-tier person's own
    # human-authored era is always more trustworthy than a book/chapter
    # guess derived from their first_reference. Bug found 2026-08-06: this
    # used to be `dict(known_era); .update(high_conf_era)`, so the guess
    # silently overwrote the curated era for anyone whose first_reference
    # happens to trigger a high-confidence book default -- e.g. Abraham's
    # first_reference "Genesis 11:26-25:11" starts in Genesis ch. 11, so his
    # curated "Patriarchal" era was overwritten with "Primeval History" in
    # this internal map (his own index entry was unaffected -- see the
    # "Full-tier entries keep their ... era ... untouched" comment below --
    # but any stub whose nearest full-tier anchor was Abraham, Sarah, Lot,
    # or 12 similar cases got BFS-propagated the wrong era from that
    # corrupted seed). Affected Bichri (2 Samuel 20, wrongly landing in
    # Primeval History via a duplicate "sheba" entry with a bad
    # first_reference) surfaced this while debugging a Timeline gap.
    era_result = dict(high_conf_era)
    era_result.update(known_era)
    region_result = dict(known_region)
    visited_hops = {pid: 0 for pid in era_result}
    queue = deque((pid, 0) for pid in era_result)
    while queue:
        pid, hops = queue.popleft()
        if hops >= MAX_HOPS:
            continue
        for nb in adjacency.get(pid, ()):
            if nb not in visited_hops and nb not in high_conf_era:
                visited_hops[nb] = hops + 1
                era_result[nb] = era_result[pid]
                if pid in region_result and nb not in region_result:
                    region_result[nb] = region_result[pid]
                queue.append((nb, hops + 1))

    # Low-confidence book/chapter fallback for anyone BFS never reached.
    fallback_count = 0
    for pid in genealogy:
        if pid not in era_result and pid in low_conf_era:
            era_result[pid] = low_conf_era[pid]
            fallback_count += 1

    # Kingdom propagation (Israel = Northern Kingdom vs Judah = Southern
    # Kingdom), seeded only from full-tier anchors with a hand-curated
    # `kingdom` and bounded much tighter than era (KINGDOM_MAX_HOPS) since
    # dynastic affiliation is a far more local signal than era placement.
    # Only ever propagates between two people who have already resolved to
    # the Divided Monarchy era -- a genealogy edge that crosses into another
    # era (e.g. a Divided-Monarchy figure's descendant born into the Exile)
    # says nothing about which pre-exilic kingdom anyone belonged to.
    KINGDOM_MAX_HOPS = 4
    kingdom_result = dict(known_kingdom)
    kingdom_queue = deque((pid, 0) for pid in kingdom_result)
    while kingdom_queue:
        pid, hops = kingdom_queue.popleft()
        if hops >= KINGDOM_MAX_HOPS:
            continue
        for nb in adjacency.get(pid, ()):
            if nb in kingdom_result:
                continue
            if era_result.get(nb) != "Divided Monarchy":
                continue
            kingdom_result[nb] = kingdom_result[pid]
            kingdom_queue.append((nb, hops + 1))

    # Write results back into the index. Full-tier entries keep their
    # human-authored era/region/genealogy untouched, but still get their
    # `timeline` object copied into the index so the timeline page can read
    # everyone -- both tiers -- from the index alone, without fetching
    # ~3,000 individual per-person files.
    updated = 0
    for entry in index:
        pid = entry["person_id"]
        if entry["tier"] == "full":
            if pid in full_timeline:
                entry["timeline"] = full_timeline[pid]
            continue
        era = era_result.get(pid)
        if not era:
            continue
        entry["era"] = era
        # Preserve a stub's own `timeline.lifespan_years` (see
        # _build/backfill_lifespan_years.py) across re-runs instead of
        # blowing it away -- that field has no source of truth other than
        # the index for stub entries, so unconditionally replacing the
        # whole `timeline` object here would silently discard it whenever
        # this script runs after the lifespan backfill.
        lifespan_years = (entry.get("timeline") or {}).get("lifespan_years")
        new_timeline = {"precision": "era"}
        if lifespan_years is not None:
            new_timeline["lifespan_years"] = lifespan_years
        entry["timeline"] = new_timeline
        region = region_result.get(pid)
        if region:
            entry["region"] = region
        kingdom = kingdom_result.get(pid)
        if kingdom:
            entry["kingdom"] = kingdom
        gen = genealogy.get(pid) or {}
        minimal_gen = {
            k: v for k, v in {
                "father": gen.get("father"),
                "mother": gen.get("mother"),
                "spouses": gen.get("spouses") or None,
            }.items() if v
        }
        if minimal_gen:
            entry["genealogy"] = minimal_gen
        updated += 1

    index_path.write_text(json.dumps(index, indent=2, ensure_ascii=False) + "\n")

    bfs_count = len(era_result) - len(known_era) - len(high_conf_era) - fallback_count
    print(f"Resolved era for {len(era_result)} people total "
          f"({len(known_era)} full-tier anchors, {len(high_conf_era)} high-confidence book/verse defaults, "
          f"{bfs_count} via genealogy BFS, {fallback_count} via low-confidence book fallback).")
    unresolved = [pid for pid in genealogy if pid not in era_result]
    print(f"Updated {updated} stub index entries. {len(unresolved)} people still unresolved (no first_reference match).")
    print(f"Resolved kingdom (Israel/Judah) for {len(kingdom_result)} Divided Monarchy people "
          f"({len(known_kingdom)} full-tier anchors, {len(kingdom_result) - len(known_kingdom)} via genealogy BFS).")


if __name__ == "__main__":
    main()
