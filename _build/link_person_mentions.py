#!/usr/bin/env python3
"""In-prose person cross-links for the static site generator.

The `adult_story` / `family_friendly_summary` narratives name many other
people who have their own pages. This module turns the *safe* subset of
those name mentions into links to `people/<id>.html`, so a reader can move
through Scripture's web of people the same way the Connections section
already lets them.

"Safe" is deliberately narrow, because a wrong cross-link on a Bible
reference site is worse than no link (see CLAUDE.md, Factual Accuracy):

  * Parenthetical Scripture citations -- "(1 Samuel 16:1-13)", "(Luke
    1:32-33)" -- are masked out first, so a book name that is also a
    person name (Luke, Samuel, John, ...) is never linked from a citation.
  * A name that belongs to exactly one person in the whole dataset is
    linked to that person.
  * A name shared by several people is linked only when exactly one
    candidate is BOTH a connections-graph neighbour of the person whose
    page this is AND a full-tier entry. (This keeps "Nathan" in David's
    story from linking to David's infant son Nathan -- a stub, so it does
    not count even though it is a graph neighbour -- and it also declines
    to link when two full-tier namesakes are both neighbours.)
  * Anything still ambiguous is left as plain text unless
    `_build/link_overrides.json` maps the lowercased name to a specific
    person_id (or to null / "" to force it to stay plain text).
  * Only the first mention of a given person per story panel is linked.

Everything here is deterministic so `generate_static_site.py` stays
CI-reproducible. Re-run the generator after editing the overrides file.
"""
import html
import json
import re
from pathlib import Path

import link_place_mentions

ROOT = Path(__file__).resolve().parent.parent
OVERRIDES_PATH = ROOT / "_build" / "link_overrides.json"
PEOPLE_DIR = ROOT / "data" / "people"

# "1 Kings 15:16-33", "Ruth 1-4", "1 Kings 17-19", "Malachi 4:5-6",
# "Song of Solomon 1:1" -> the set of "Book|chapter" tokens it covers.
# Used as a disambiguation signal: two people who share a name and are
# both named in the same Bible chapter are almost always the two actors
# of that passage.
_REF_RE = re.compile(
    r"\s*((?:[1-3]\s)?[A-Z][A-Za-z]+(?:\s(?:of\s)?[A-Z][a-z]+)*?)\s+"
    r"(\d+)(?::\d+[\dab,\s-]*)?(?:\s*-\s*(\d+)(?::\d+)?)?\s*$"
)


def _ref_chapters(refs):
    out = set()
    for entry in refs or []:
        for piece in re.split(r"\s*;\s*", str(entry)):
            m = _REF_RE.match(piece)
            if not m:
                m2 = re.match(r"\s*((?:[1-3]\s)?[A-Za-z][A-Za-z. ]*?)\s+(\d+)", piece)
                if m2:
                    out.add(f"{m2.group(1).strip()}|{int(m2.group(2))}")
                continue
            book = m.group(1).strip()
            c1 = int(m.group(2))
            c2 = int(m.group(3)) if m.group(3) else c1
            if not c1 <= c2 <= c1 + 50:
                c2 = c1
            for c in range(c1, c2 + 1):
                out.add(f"{book}|{c}")
    return out

# A capitalised word (optionally hyphen-compounded, e.g. "Ben-hadad",
# "Abed-nego"), 3+ letters in the first part so 2-letter place words like
# "Ur" are ignored.
_CANDIDATE_RE = re.compile(r"[A-Z][a-z]{2,}(?:-[A-Za-z]+)*")

# Parenthetical span that contains a digit -- the house style always
# parenthesises Scripture citations, so this catches "(2 Samuel 11)",
# "(Luke 1:32-33)", "(Genesis 5:18-24; 1 Chronicles 1:3)" etc. without
# touching ordinary parentheticals.
_CITATION_RE = re.compile(r"\([^()]*\d[^()]*\)")

# Capitalised words that are never a person link: the divine names, common
# theological nouns, nations/peoples, and places that share a name with a
# person entry but read overwhelmingly as the place/nation/title.
STOPWORDS = {
    "god", "lord", "jesus", "christ", "messiah", "holy", "spirit", "father",
    "son", "king", "queen", "prince", "lord's", "almighty", "creator",
    "saviour", "savior", "redeemer",
    "israel", "judah", "ephraim", "manasseh", "benjamin", "dan", "gad",
    "asher", "reuben", "levi", "levites", "simeon", "naphtali", "zebulun",
    "issachar",
    "egypt", "canaan", "canaanites", "moab", "moabites", "edom", "edomites",
    "ammon", "ammonites", "amalek", "amalekites", "midian", "midianites",
    "philistines", "assyria", "assyrians", "babylon", "babylonians",
    "persia", "persians", "rome", "romans", "greece", "greeks", "syria",
    "arameans", "hittites", "jebusites", "gentiles", "jews", "hebrews",
    "pharisees", "sadducees", "samaritans", "scribes",
    "pharaoh", "caesar", "aram", "baal", "immanuel",
    "jerusalem", "zion", "bethlehem", "nazareth", "galilee", "judea",
    "samaria", "eden", "sinai", "horeb", "jordan", "gilead", "bashan",
    "sabbath", "passover", "pentecost", "tabernacle", "temple", "torah",
    "law", "gospel", "scripture", "scriptures", "psalm", "psalms",
    "proverbs", "sheol", "hades", "heaven", "hell", "eden",
    "then", "when", "there", "these", "those", "they", "their",
}


def _load_overrides():
    if not OVERRIDES_PATH.exists():
        return {}
    raw = json.loads(OVERRIDES_PATH.read_text())
    return {
        k.lower(): (v or None)
        for k, v in raw.items()
        if not k.startswith("_")
    }


def build_context(index, connections):
    """Return an opaque dict threaded into the render functions."""
    valid_pids = set()
    tier_by_id = {}
    name_index = {}  # lowercased single-token name -> set(person_id)
    names_by_id = {}  # person_id -> set(lowercased single-token own names)
    for entry in index:
        pid = entry["person_id"]
        valid_pids.add(pid)
        tier_by_id[pid] = entry.get("tier")
        names = [entry["name"]] + list(entry.get("alt_names") or [])
        for nm in names:
            nm = nm.strip()
            # Single token only. Hyphen-compounds (Ben-hadad) count as one
            # token; anything with whitespace (Mary Magdalene, John the
            # Baptist) is skipped -- matching those safely in running prose
            # is a separate problem, handled case-by-case via overrides.
            if not nm or " " in nm:
                continue
            name_index.setdefault(nm.lower(), set()).add(pid)
            names_by_id.setdefault(pid, set()).add(nm.lower())

    adjacency = {}
    for edge in connections:
        adjacency.setdefault(edge["from"], set()).add(edge["to"])
        adjacency.setdefault(edge["to"], set()).add(edge["from"])

    # Per-person Bible chapters (from the full `references` array where the
    # per-person file exists, else the index `first_reference`) and the set
    # of person_ids that are the subject's own curated genealogical kin --
    # both used by `classify` to resolve name collisions that the graph
    # alone leaves ambiguous.
    refs_by_id = {}
    kin_by_id = {}
    geo_by_id = {}
    first_ref_by_id = {e["person_id"]: e.get("first_reference") for e in index}
    for entry in index:
        pid = entry["person_id"]
        g = entry.get("genealogy") or {}
        kin = set()
        for k in ("father", "mother"):
            if g.get(k):
                kin.add(g[k])
        for k in ("spouses", "children"):
            kin.update(x for x in (g.get(k) or []) if x)
        kin_by_id[pid] = kin

        refs = None
        fp = PEOPLE_DIR / f"{pid}.json"
        if fp.exists():
            try:
                data = json.loads(fp.read_text())
                refs = data.get("references")
                geo_by_id[pid] = {
                    s.strip().lower()
                    for s in (data.get("geographic_setting") or [])
                    if s and s.strip()
                }
            except (OSError, ValueError):
                pass
        if not refs and first_ref_by_id.get(pid):
            refs = [first_ref_by_id[pid]]
        refs_by_id[pid] = _ref_chapters(refs)

    return {
        "valid_pids": valid_pids,
        "tier_by_id": tier_by_id,
        "name_index": name_index,
        "names_by_id": names_by_id,
        "adjacency": adjacency,
        "refs_by_id": refs_by_id,
        "kin_by_id": kin_by_id,
        "geo_by_id": geo_by_id,
        "overrides": _load_overrides(),
    }


def classify(key, subject_id, ctx):
    """Lowercased word -> (target person_id or None, reason string).

    Reasons: "stopword", "override", "override-suppressed", "override-bad",
    "no-match", "unique", "connection", "kin", "reference", "ambiguous".
    """
    if key in STOPWORDS:
        return None, "stopword"

    # A word that is one of the subject's own names / alt-names refers to
    # the subject (e.g. "Saul" in Paul's story, "Abram" in Abraham's) and
    # must never become a link to a namesake.
    if key in ctx["names_by_id"].get(subject_id, ()):
        return None, "self"

    overrides = ctx["overrides"]
    if key in overrides:
        tgt = overrides[key]
        if tgt is None:
            return None, "override-suppressed"
        if tgt != subject_id and tgt in ctx["valid_pids"]:
            return tgt, "override"
        return None, "override-bad"

    tier_by_id = ctx["tier_by_id"]

    # The subject's own curated genealogical kin (father/mother/spouse/
    # child). When a name in the story matches one of them, it is that
    # relative -- Scripture routinely introduces a person as "X son of Y"
    # and Y is then only a name. Safe even for a stub target because the
    # match is anchored to the subject's own genealogy, not a bare name
    # collision (this is checked after `overrides`, so a name a curated
    # override already claims for someone else -- e.g. "Nathan" the
    # prophet in David's story, not David's infant son Nathan -- is
    # unaffected).
    kin = ctx["kin_by_id"].get(subject_id, ())
    same_name = ctx["name_index"].get(key, set())
    adj = ctx["adjacency"].get(subject_id, set())
    for rel in kin:
        if rel == subject_id or key not in ctx["names_by_id"].get(rel, ()):
            continue
        # Defer to the graph if another full-tier person of the same name
        # is also connected to this subject -- e.g. "Joseph" in Mary's
        # story is her husband (a graph neighbour), not her son Joses,
        # even though Joses is kin and also went by Joseph.
        if any(
            j != rel and j in adj and tier_by_id.get(j) == "full"
            for j in same_name
        ):
            break
        return rel, "kin"

    ids = ctx["name_index"].get(key, set()) - {subject_id}
    if not ids:
        return None, "no-match"
    if len(ids) == 1:
        only = next(iter(ids))
        # Stub entries are thin, noindex genealogy-listing pages, and many
        # of them carry a place / nation / city name (Gibeon, Sidon, Put,
        # Hamath, "Ark", ...) that collides with ordinary prose. Auto-link
        # only to full-tier pages; a genuinely wanted stub link (a famous
        # person's otherwise-unmentioned father) can be added by name in
        # _build/link_overrides.json.
        if tier_by_id.get(only) != "full":
            return None, "stub-target"
        return only, "unique"
    neighbours = ids & ctx["adjacency"].get(subject_id, set())
    full_neighbours = {i for i in neighbours if tier_by_id.get(i) == "full"}
    # Link only when exactly one namesake is both a full-tier entry and
    # directly connected to this person in the graph. A stub namesake that
    # happens to be a graph neighbour (e.g. David's infant son Nathan vs.
    # Nathan the prophet) does not count, and if two full-tier namesakes
    # are both neighbours the mention stays plain text.
    if len(full_neighbours) == 1:
        return next(iter(full_neighbours)), "connection"

    # Reference-overlap fallback: among the full-tier namesakes, the one
    # named in a Bible chapter this subject's own `references` also cover.
    # Two same-named people appearing in the same chapter are almost
    # always the two actors of that passage (verified on a full corpus
    # sample -- it correctly resolves e.g. David's "Saul", Paul's
    # "Gamaliel", Rachel's "Herod" in the Matthew 2 lament). Only fires
    # when exactly one full-tier namesake overlaps.
    subj_ch = ctx["refs_by_id"].get(subject_id) or set()
    if subj_ch:
        overlap = {
            i for i in ids
            if tier_by_id.get(i) == "full" and (ctx["refs_by_id"].get(i) or set()) & subj_ch
        }
        if len(overlap) == 1:
            return next(iter(overlap)), "reference"
    return None, "ambiguous"


def _resolve(key, subject_id, ctx):
    """Lowercased word -> target person_id, or None to leave as plain text."""
    return classify(key, subject_id, ctx)[0]


def link_paragraph(text, subject_id, ctx, base, linked_pids, place_ctx=None, linked_place_ids=None):
    """Escape `text` and wrap the safe person/place-name mentions in it as links.

    `linked_pids` (people) and `linked_place_ids` (places) are mutable sets
    shared across the paragraphs of one story panel so only the first
    mention of each person/place is linked. A word is tried as a person
    mention first; only if that fails is it tried as a place mention (see
    link_place_mentions.classify for why that order matters -- a word that
    is also a person's name is never linked as a place).
    """
    if not ctx and not place_ctx:
        return html.escape(text, quote=True)

    protected = [(m.start(), m.end()) for m in _CITATION_RE.finditer(text)]

    def is_protected(pos):
        return any(a <= pos < b for a, b in protected)

    out = []
    last = 0
    for m in _CANDIDATE_RE.finditer(text):
        if is_protected(m.start()):
            continue
        word = m.group(0)
        key = word.lower()

        tgt, reason = classify(key, subject_id, ctx) if ctx else (None, "")
        href_prefix = "people/"
        seen = linked_pids

        # Try the word as a place when it did not resolve to a person, or
        # when it resolved only to a bare same-name person ("unique") while
        # a place is tied to this subject by geography / the place graph /
        # a shared chapter -- e.g. "Tirzah" in a king's story is the city,
        # not Zelophehad's daughter of the same name.
        if place_ctx is not None and (not tgt or reason == "unique"):
            place_tgt, place_reason = link_place_mentions.classify(key, subject_id, place_ctx)
            if place_tgt and (not tgt or place_reason == "reference"):
                tgt, href_prefix, seen = place_tgt, "places/", linked_place_ids

        if not tgt or tgt in seen:
            continue
        seen.add(tgt)
        out.append(html.escape(text[last:m.start()], quote=True))
        out.append(
            f'<a class="story-link" href="{base}{href_prefix}{tgt}.html">'
            f'{html.escape(word, quote=True)}</a>'
        )
        last = m.end()
    out.append(html.escape(text[last:], quote=True))
    return "".join(out)
