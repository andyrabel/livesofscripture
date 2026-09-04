#!/usr/bin/env python3
"""In-prose place cross-links for the static site generator.

Sibling module to `link_person_mentions.py`, same conservative philosophy
(see that file's docstring and CLAUDE.md's Factual Accuracy section): a
wrong cross-link is worse than no link, so a mention is only turned into a
link to `places/<id>.html` when it is unambiguous.

Threaded into `link_person_mentions.link_paragraph` as a fallback -- a
capitalised single-token word that doesn't resolve to a person mention is
then tried against the place index. Rules:

  * A word that also matches a person's name or alt-name (any tier) is
    never linked as a place. This is what keeps tribal/national eponyms
    that double as a patriarch's own name -- "Judah" (Kingdom of Judah vs.
    the patriarch), "Dan", "Edom" (Esau's alt-name), "Moab"/"Ammon" (Lot's
    sons) -- unlinked here rather than guessed, the same policy that put
    those words in `link_person_mentions.STOPWORDS` for person-linking.
  * Only single-token place names/alt-names are indexed (multi-word names
    like "Mount Sinai" or "Kingdom of Israel" are a separate problem, same
    as multi-word person names -- left for overrides if ever needed).
  * A name unique to one place links to it, but only if that place is
    full-tier (stub place pages are thin genealogy-style entries with no
    story of their own).
  * A name shared by several places links only when exactly one candidate
    is both a full-tier entry and a neighbour of the subject person in
    `data/place-connections.json`.
  * Only the first mention of a given place per story panel is linked
    (tracked by the caller, mirroring person-link dedup).
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def build_context(places_index, person_name_index, place_connections):
    """Return an opaque dict threaded into link_person_mentions.link_paragraph.

    `person_name_index` is `link_person_mentions.build_context(...)["name_index"]`
    -- reused as the person/place collision guard described above.
    """
    valid_pids = set()
    tier_by_id = {}
    name_index = {}   # lowercased single-token name -> set(place_id)
    names_by_id = {}  # place_id -> set(lowercased single-token own names)
    for entry in places_index:
        pid = entry["place_id"]
        valid_pids.add(pid)
        tier_by_id[pid] = entry.get("tier")
        names = [entry["name"]] + list(entry.get("alt_names") or [])
        for nm in names:
            nm = nm.strip()
            if not nm or " " in nm:
                continue
            name_index.setdefault(nm.lower(), set()).add(pid)
            names_by_id.setdefault(pid, set()).add(nm.lower())

    # data/place-connections.json edges are {"from": <person_id>, "to":
    # "place:<place_id>", ...} (or the reverse) -- collapse to
    # person_id -> set(place_id) for the disambiguation-by-neighbour rule.
    adjacency = {}
    for edge in place_connections:
        frm, to = edge.get("from"), edge.get("to")
        if isinstance(to, str) and to.startswith("place:"):
            person_id, place_id = frm, to[len("place:"):]
        elif isinstance(frm, str) and frm.startswith("place:"):
            person_id, place_id = to, frm[len("place:"):]
        else:
            continue
        adjacency.setdefault(person_id, set()).add(place_id)

    return {
        "valid_pids": valid_pids,
        "tier_by_id": tier_by_id,
        "name_index": name_index,
        "names_by_id": names_by_id,
        "adjacency": adjacency,
        "person_name_index": person_name_index,
    }


def classify(key, subject_id, ctx):
    """Lowercased word -> (target place_id or None, reason string).

    Reasons: "person-name-collision", "self", "no-match", "stub-target",
    "unique", "connection", "ambiguous".
    """
    if key in ctx["person_name_index"]:
        return None, "person-name-collision"

    if key in ctx["names_by_id"].get(subject_id, ()):
        return None, "self"

    tier_by_id = ctx["tier_by_id"]
    ids = ctx["name_index"].get(key, set()) - {subject_id}
    if not ids:
        return None, "no-match"
    if len(ids) == 1:
        only = next(iter(ids))
        if tier_by_id.get(only) != "full":
            return None, "stub-target"
        return only, "unique"

    neighbours = ids & ctx["adjacency"].get(subject_id, set())
    full_neighbours = {i for i in neighbours if tier_by_id.get(i) == "full"}
    if len(full_neighbours) == 1:
        return next(iter(full_neighbours)), "connection"
    return None, "ambiguous"
