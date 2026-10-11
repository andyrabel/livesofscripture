#!/usr/bin/env python3
"""Build `_build/place_name_meanings.json`: the meaning of each place's name,
quoted verbatim from Hitchcock's Bible Names Dictionary (Roswell D.
Hitchcock, 1869, public domain), plus a Scripture reference where the text
itself explains the name (Genesis 11:9 for Babel, Acts 1:19 for Akeldama).

The sibling of `backfill_name_meaning.py` (people), with two differences:
  * The meaning is never paraphrased. It is Hitchcock's gloss exactly as he
    printed it, so the place page can present it as a quotation. Each
    source keeps the entry line(s) it came from.
  * It covers stub places too. A quotation from a public-domain reference
    work is not generated content, and most stub places are only names, so
    the name's meaning is often the one thing worth saying about them.

Source text: CCEL's complete single-page copy
(https://ccel.org/ccel/hitchcock/bible_names/bible_names.html). That copy
is used rather than bible-history.com's per-name pages, which cut entries
off at the first comma (see CLAUDE.md, name_meaning "Per-definition
sources"). Cached at `_build/hitchcock-source/bible_names.html`
(gitignored), and fetched with `--refresh` or when missing.

`generate_places.py` reads the output and writes it onto each
`data/places/<id>.json` as `name_meaning`. Re-run order:
backfill_place_name_meaning.py -> generate_places.py ->
generate_static_site.py.

Matching, in order (the first that finds a Hitchcock headword wins):
  1. HEADWORD_OVERRIDES: a hand-picked headword (a spelling variant, such as
     Kirjath-jearim for Kiriath-jearim) or None to suppress a match.
  2. The place's own name, ignoring case, hyphens and spaces (so Bethlehem
     matches "Beth-lehem").
  3. A place name with a generic prefix or suffix ("Mount Carmel", "Valley
     of Achor", "Jordan River") matches its core word. The page then says
     "Carmel" means..., not that the whole name does.
Entries that are only cross-references ("Babylon, same as Babel", "Ai, or
Hai, ...") are followed to the entry that holds the gloss, and both lines
are kept as the quoted source.
"""
import html
import json
import re
import sys
import urllib.parse
import urllib.request
from pathlib import Path

BUILD = Path(__file__).resolve().parent
ROOT = BUILD.parent
SOURCE_URL = "https://ccel.org/ccel/hitchcock/bible_names/bible_names.html"
CACHE = BUILD / "hitchcock-source" / "bible_names.html"
OUT = BUILD / "place_name_meanings.json"

# place_id -> Hitchcock headword (spelling variant) or None (no match).
HEADWORD_OVERRIDES = {
    "kiriath-jearim": "Kirjath-jearim",
    "colossae": "Colosse",
    "pergamum": "Pergamos",
    "malta": "Melita",
    "paddan-aram": "Padan-aram",
    "susa": "Shushan",
    "jabesh-gilead": "Jabesh-gilead",
}

# Generic geographic words around a core name ("Mount X", "X River").
PREFIXES = [
    "mount of", "mount", "valley of the", "valley of", "wilderness of",
    "plains of", "plain of", "cave of", "garden of", "land of", "hill country of",
    "kingdom of", "brook", "pool of", "sea of", "river", "desert of", "gate of the",
    "gate of", "tower of", "field of", "well of", "waters of",
]
SUFFIXES = ["river", "of the chaldeans", "of pisidia", "of syria"]

# place_id -> reference where Scripture itself explains the name: a
# "therefore it was called..." clause or "which means...". Same bar as
# SCRIPTURE_EXPLAINED for people: explicit statements only, never an
# implied pun (Lo-debar in Amos 6:13), and never a naming without a stated
# reason (Allon-bacuth in Genesis 35:8).
SCRIPTURE_EXPLAINED = {
    "babel": "Genesis 11:9",
    "beer-lahai-roi": "Genesis 16:13-14",
    "zoar": "Genesis 19:20-22",
    "beersheba": "Genesis 21:31",
    "the-lord-will-provide": "Genesis 22:14",
    "esek": "Genesis 26:20",
    "sitnah": "Genesis 26:21",
    "rehoboth-1": "Genesis 26:22",
    "bethel": "Genesis 28:17-19",
    "mahanaim": "Genesis 32:2",
    "penuel": "Genesis 32:30",
    "succoth": "Genesis 33:17",
    "abel-mizraim": "Genesis 50:11",
    "marah": "Exodus 15:23",
    "massah": "Exodus 17:7",
    "meribah-2": "Exodus 17:7",
    "taberah": "Numbers 11:3",
    "kibroth-hattaavah": "Numbers 11:34",
    "valley-of-eshcol": "Numbers 13:24",
    "meribah-1": "Numbers 20:13",
    "hormah": "Numbers 21:3",
    "gilgal": "Joshua 5:9",
    "valley-of-achor": "Joshua 7:26",
    "bochim": "Judges 2:4-5",
    "ramath-lehi": "Judges 15:17",
    "en-hakkore": "Judges 15:19",
    "ebenezer-2": "1 Samuel 7:12",
    "baal-perazim": "2 Samuel 5:20",
    "perez-uzzah": "2 Samuel 6:8",
    "golgotha": "Matthew 27:33",
    "siloam": "John 9:7",
    "akeldama": "Acts 1:19",
    "salem": "Hebrews 7:2",
}

# place_id -> meaning, for the few names whose meaning Scripture itself
# translates (John 9:7, "which is translated, Sent"), where Hitchcock either
# has no entry or follows a cross-reference to a different word (he sends
# Siloam to Shilhi, "bough; weapon; armor"), or where his gloss reads against
# the verse. Used instead of Hitchcock and
# shown as explained in the SCRIPTURE_EXPLAINED reference, not as a quote.
SCRIPTURE_MEANINGS = {
    "siloam": "Sent",
    "akeldama": "Field of Blood",
    "perez-uzzah": "Breaking out against Uzzah",
    # Hitchcock: "god of divisions". David names it for the LORD breaking
    # through his enemies; "baal" here is "master", not a pagan god.
    "baal-perazim": "Master of breaking through",
}

# Headwords that are really the first word of a gloss ("Eliel, God, my God").
NOT_HEADWORDS = {"God", "Lord"}


def norm(s):
    return re.sub(r"[^a-z]", "", s.lower())


def load_source(refresh=False):
    if refresh or not CACHE.exists():
        CACHE.parent.mkdir(parents=True, exist_ok=True)
        req = urllib.request.Request(SOURCE_URL, headers={"User-Agent": "livesofscripture-build"})
        CACHE.write_bytes(urllib.request.urlopen(req, timeout=60).read())
    return CACHE.read_bytes().decode("latin-1")


def parse_entries(src):
    """-> list of {"line", "heads", "gloss"}. Entries end with <br> and may
    wrap across source lines."""
    body = src.split('<a name="A">', 1)[1]
    body = re.sub(r"<(?!br)[^>]+>", "\n", body, flags=re.I)
    text = re.sub(r"\s*\n\s*", " ", body)
    entries = []
    for raw in re.split(r"<br>", text, flags=re.I):
        line = html.unescape(raw).strip()
        if "," not in line:
            continue
        parts = [p.strip() for p in line.split(",")]
        heads = []
        while parts and parts[0][:1].isupper() and parts[0] not in NOT_HEADWORDS and len(heads) < 4:
            heads.append(parts.pop(0))
        if not heads or not parts:
            continue
        gloss = ", ".join(parts)
        m = re.match(r"or ([A-Z][\w-]*), (.*)", gloss)  # "Ai, or Hai, mass; heap"
        if m:
            heads.append(m.group(1))
            gloss = m.group(2)
        entries.append({"line": line, "heads": heads, "gloss": gloss})
    return entries


XREF = re.compile(r"^(?:same as|same with|see) ([A-Z][\w-]*)(?:;\s*(.*))?$")


def resolve(entry, by_head, depth=0):
    """Follow "same as X" cross-references. -> (gloss, [entry lines])."""
    m = XREF.match(entry["gloss"])
    if not m:
        return entry["gloss"], [entry["line"]]
    target, own_gloss = m.group(1), m.group(2)
    if own_gloss:  # "Aiath, same as Ai; an hour; eye; fountain"
        return own_gloss, [entry["line"]]
    cands = [e for e in by_head.get(norm(target), []) if e is not entry]
    if not cands or depth > 3:
        return None, None
    gloss, lines = resolve(cands[0], by_head, depth + 1)
    return gloss, ([entry["line"]] + lines) if gloss else None


def core_name(name):
    low = name.lower()
    for p in PREFIXES:
        if low.startswith(p + " "):
            return name[len(p) + 1:]
    for s in SUFFIXES:
        if low.endswith(" " + s):
            return name[: -len(s) - 1]
    return None


def text_fragment_url(line):
    return f"{SOURCE_URL}#:~:text=" + urllib.parse.quote(line, safe="")


def main():
    entries = parse_entries(load_source("--refresh" in sys.argv))
    by_head = {}
    for e in entries:
        for h in e["heads"]:
            by_head.setdefault(norm(h), []).append(e)

    places = json.loads((ROOT / "data" / "places-index.json").read_text())
    out, ambiguous, unmatched = {}, [], []
    for p in places:
        pid, name = p["place_id"], p["name"]
        term = None  # set when only part of the name was matched
        if pid in HEADWORD_OVERRIDES:
            head = HEADWORD_OVERRIDES[pid]
            cands = by_head.get(norm(head), []) if head else []
        else:
            cands = by_head.get(norm(name), [])
            if not cands and core_name(name):
                term = core_name(name)
                cands = by_head.get(norm(term), [])
        # A spelling with two entries (a person and a city): prefer the one
        # that holds a gloss over a bare cross-reference, and flag any real
        # conflict for review rather than guessing.
        glossed = [e for e in cands if not XREF.match(e["gloss"])] or cands
        if len({e["gloss"] for e in glossed}) > 1:
            ambiguous.append((pid, [e["line"] for e in glossed]))
            glossed = []
        mm = {}
        if pid in SCRIPTURE_MEANINGS:
            mm = {"meaning": SCRIPTURE_MEANINGS[pid], "sources": []}
        elif glossed:
            gloss, lines = resolve(glossed[0], by_head)
            if gloss:
                mm["meaning"] = gloss
                if term:
                    mm["term"] = term
                mm["sources"] = [{
                    "type": "hitchcock",
                    "entries": lines,
                    "url": text_fragment_url(lines[-1]),
                }]
        if pid in SCRIPTURE_EXPLAINED:
            if not mm:
                unmatched.append(pid)  # explained in Scripture, but nothing to quote
                continue
            mm["sources"].insert(0, {"type": "scripture", "reference": SCRIPTURE_EXPLAINED[pid]})
        if mm:
            out[pid] = mm

    missing = sorted(set(SCRIPTURE_EXPLAINED) - {p["place_id"] for p in places})
    OUT.write_text(json.dumps({
        "_source": f"Hitchcock's Bible Names Dictionary (1869, public domain), via {SOURCE_URL}",
        "meanings": dict(sorted(out.items())),
    }, indent=1, ensure_ascii=False) + "\n")
    print(f"wrote {len(out)} of {len(places)} places to {OUT.relative_to(ROOT)}")
    for pid, lines in ambiguous:
        print(f"AMBIGUOUS {pid}: {lines}")
    if unmatched:
        print(f"Scripture-explained but no Hitchcock entry (skipped): {unmatched}")
    if missing:
        print(f"SCRIPTURE_EXPLAINED ids not in places-index: {missing}")


if __name__ == "__main__":
    main()
