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

    return {
        "valid_pids": valid_pids,
        "tier_by_id": tier_by_id,
        "name_index": name_index,
        "names_by_id": names_by_id,
        "adjacency": adjacency,
        "overrides": _load_overrides(),
    }


def classify(key, subject_id, ctx):
    """Lowercased word -> (target person_id or None, reason string).

    Reasons: "stopword", "override", "override-suppressed", "override-bad",
    "no-match", "unique", "connection", "ambiguous".
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

        tgt = _resolve(key, subject_id, ctx) if ctx else None
        href_prefix = "people/"
        seen = linked_pids

        if not tgt and place_ctx is not None:
            place_tgt, _ = link_place_mentions.classify(key, subject_id, place_ctx)
            if place_tgt:
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
