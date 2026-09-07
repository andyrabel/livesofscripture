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

A stub place target is allowed (unlike the person linker, which never
auto-links a stub) when the place is unambiguous: stub place pages are
thin but real, and "link every place name" is what the site wants for
locations. The person-name collision guard above is what keeps the
dangerous cases (tribal/national eponyms) out.
"""
import json
import re
from pathlib import Path

import link_person_mentions

ROOT = Path(__file__).resolve().parent.parent
PLACES_DIR = ROOT / "data" / "places"


def build_context(places_index, person_ctx, place_connections):
    """Return an opaque dict threaded into link_person_mentions.link_paragraph.

    `person_ctx` is the full `link_person_mentions.build_context(...)` dict
    -- its `name_index` is reused as the person/place collision guard, and
    its `refs_by_id` / `geo_by_id` supply the subject-person signals used
    to disambiguate (and to license a stub target).
    """
    person_name_index = person_ctx["name_index"]
    valid_pids = set()
    tier_by_id = {}
    name_index = {}   # lowercased single-token name -> set(place_id)
    names_by_id = {}  # place_id -> set(lowercased single-token own names)
    refs_by_id = {}   # place_id -> set("Book|chapter")
    related_by_id = {}  # place_id -> set(person_id) from its related_people
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
        refs = None
        fp = PLACES_DIR / f"{pid}.json"
        if fp.exists():
            try:
                data = json.loads(fp.read_text())
                refs = data.get("references")
                related_by_id[pid] = {
                    rp["person_id"] for rp in (data.get("related_people") or [])
                    if rp.get("person_id")
                }
            except (OSError, ValueError):
                pass
        if not refs and entry.get("first_reference"):
            refs = [entry["first_reference"]]
        refs_by_id[pid] = link_person_mentions._ref_chapters(refs)

    # data/place-connections.json edges are {"from": <person_id>, "to":
    # "place:<place_id>", ...} (or the reverse) -- collapse to both
    # person_id -> set(place_id) (disambiguation-by-neighbour on person
    # pages) and place_id -> set(person_id) (the reverse, for person
    # mentions on a *place* page).
    adjacency = {}
    place_people = {}
    for edge in place_connections:
        frm, to = edge.get("from"), edge.get("to")
        if isinstance(to, str) and to.startswith("place:"):
            person_id, place_id = frm, to[len("place:"):]
        elif isinstance(frm, str) and frm.startswith("place:"):
            person_id, place_id = to, frm[len("place:"):]
        else:
            continue
        adjacency.setdefault(person_id, set()).add(place_id)
        place_people.setdefault(place_id, set()).add(person_id)

    return {
        "related_by_id": related_by_id,
        "place_people": place_people,
        "valid_pids": valid_pids,
        "tier_by_id": tier_by_id,
        "name_index": name_index,
        "names_by_id": names_by_id,
        "refs_by_id": refs_by_id,
        "adjacency": adjacency,
        "person_name_index": person_name_index,
        "person_refs_by_id": person_ctx.get("refs_by_id", {}),
        "person_geo_by_id": person_ctx.get("geo_by_id", {}),
    }


def classify(key, subject_id, ctx, subject_is_place=False):
    """Lowercased word -> (target place_id or None, reason string).

    Reasons: "person-name-collision", "self", "no-match", "stub-target",
    "unique", "connection", "reference", "ambiguous".

    `subject_is_place=True` when this runs for a *place* detail page --
    there is no `geographic_setting` or person<->place edge to lean on, so
    only a shared Bible chapter (from the subject place's own
    `references`) or a globally unique name resolves a place<->place link.
    """
    if key in ctx["names_by_id"].get(subject_id, ()):
        return None, "self"

    tier_by_id = ctx["tier_by_id"]
    ids = ctx["name_index"].get(key, set()) - {subject_id}
    if not ids:
        return None, "no-match"

    if subject_is_place:
        subj_ch = ctx["refs_by_id"].get(subject_id) or set()
        geo = set()
        neighbours = set()
    else:
        geo = ctx["person_geo_by_id"].get(subject_id) or set()
        neighbours = ctx["adjacency"].get(subject_id, set())
        subj_ch = ctx["person_refs_by_id"].get(subject_id) or set()

    # Named in this person's own curated `geographic_setting`: a tightly
    # curated per-person signal, strong enough to link even a stub and
    # even when the word doubles as a person's name -- "Tirzah" in a
    # king's story is the capital city, not Zelophehad's daughter.
    geo_strong = {i for i in ids if geo and ctx["names_by_id"].get(i, set()) & geo}
    if len(geo_strong) == 1:
        return next(iter(geo_strong)), "reference"
    if len(geo_strong) > 1:
        return None, "ambiguous"

    # Weaker signals stop here if the word doubles as a person's name
    # (tribal / national eponyms -- Judah, Dan, Edom, Moab).
    if key in ctx["person_name_index"]:
        return None, "person-name-collision"

    # Neighbour in the person<->place graph -- the strongest curated
    # disambiguator, checked before the weaker reference-overlap signal.
    graph_hits = {i for i in ids if i in neighbours}
    if len(graph_hits) == 1:
        return next(iter(graph_hits)), "connection"

    # A place named in a Bible chapter this person's story cites. Only
    # when exactly one candidate overlaps; licenses a stub target.
    if subj_ch:
        overlap = {i for i in ids if (ctx["refs_by_id"].get(i) or set()) & subj_ch}
        if len(overlap) == 1:
            return next(iter(overlap)), "reference"
        if len(overlap) > 1:
            return None, "ambiguous"

    if len(graph_hits) > 1:
        return None, "ambiguous"

    if len(ids) == 1:
        only = next(iter(ids))
        if tier_by_id.get(only) != "full":
            # Unique name, but only a thin stub page and nothing ties it to
            # this subject -- leave it plain rather than guess.
            return None, "stub-target"
        return only, "unique"

    return None, "ambiguous"
