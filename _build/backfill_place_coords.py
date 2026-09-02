#!/usr/bin/env python3
"""Attach a lon/lat (and identification confidence) to every curated place,
from OpenBible.info's Bible-Geocoding-Data (CC BY 4.0 -- already attributed
on the site for the gazetteer import).

Why: the Places feature had no coordinates at all, so the site could not
draw its own maps. OpenBible catalogs a best-guess location and a confidence
score for essentially every identifiable biblical place, plus alternate
candidate points for disputed sites.

Output: _build/place_coords.json  (force-added like link_overrides.json)
    { "<place_id>": {
        "lat": float, "lng": float,
        "confidence": 0-1000,          # OpenBible time_total; 1000 = no doubt
        "kind": "point" | "representative",   # representative = region label anchor
        "openbible": "<friendly_id>",
        "candidates": [[lng, lat, confidence], ...]   # only when >1 identification
      } }

generate_places.py reads this and writes a `geo` block onto each
data/places/<id>.json plus flat lat/lng on the index. Re-run this script
(then generate_places.py, then generate_static_site.py) if the curated
place roster changes. Deterministic; safe to re-run.

Input: _build/openbible-source/ancient.jsonl -- the full upstream file
(~11 MB, gitignored). Fetch it with `import_openbible_places.py --refresh`,
which downloads the same file for the gazetteer import.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ANCIENT = Path(__file__).resolve().parent / "openbible-source" / "ancient.jsonl"
OUT = Path(__file__).resolve().parent / "place_coords.json"

sys.path.insert(0, str(Path(__file__).resolve().parent))
from places_data import PLACES_MAJOR, PLACES_MID, PLACES_MINOR  # noqa: E402

# place_id -> OpenBible friendly_id, for the handful the name match misses or
# would get wrong. "" means "deliberately no coordinate" (unlocatable).
OVERRIDES = {
    "asia-minor": "Asia",
    "kingdom-of-israel": "Samaria",          # the northern kingdom, capital region
    "kingdom-of-judah": "Judea 1",           # the southern kingdom's territory
    "region-of-the-gerasenes": "Gerasa",
    "hill-country-of-judea": "Judea 1",
    "chebar-river": "Chebar",
    "meshech-and-tubal": "Meshech",
    "cave-of-machpelah": "Machpelah",
    "galilee": "Galilee 1",
    "gibeah": "Gibeah 1",                    # Gibeah of Saul/Benjamin
    "shuah": "",                             # a people/region, no fixed point
    "land-of-nod": "",                       # "east of Eden" -- unlocatable
    "gaza-road": "",                         # a route, not a point
}

# place_id -> (lng, lat, note) for approximate anchors OpenBible has no entry
# for -- regions/spots known only in general terms. `confidence` is recorded
# as 0 to flag them as approximate label anchors, not identified sites.
MANUAL = {
    "benjamin": (35.22, 31.85, "Approximate: the tribal territory north of Jerusalem."),
    "ephraim-forest": (35.70, 32.20, "Approximate: a wood in Gilead, east of the Jordan (2 Samuel 18:6)."),
    "perea": (35.70, 31.95, "Approximate: the region east of the Jordan opposite Judea and Samaria."),
    "rock-of-oreb": (35.55, 32.00, "Approximate: a crossing near the Jordan where Oreb was killed (Judges 7:25)."),
    "wilderness-of-judea": (35.35, 31.60, "Approximate: the arid country between the Judean hills and the Dead Sea."),
}


def norm(s):
    s = s.lower()
    s = re.sub(r"\(.*?\)", " ", s)
    s = re.sub(r"[^a-z0-9 ]", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def best_point(rec):
    """Return (lng, lat, confidence, kind) for the top identification, or None."""
    for idn in rec.get("identifications") or []:
        conf = (idn.get("score") or {}).get("time_total", 0)
        for res in idn.get("resolutions") or []:
            ll = res.get("lonlat")
            if not ll:
                continue
            lng, lat = (float(x) for x in ll.split(","))
            kind = "point" if res.get("lonlat_type") == "point" else "representative"
            return (lng, lat, conf, kind)
    return None


def all_candidates(rec):
    """Alternate identified points for a disputed site. OpenBible confidence
    is a fraction of 1000; drop <=0 (readme: negative == 'identification is
    wrong') and keep at most the five strongest so a famously-contested site
    like Mount Sinai doesn't carry a 14-entry list."""
    out = []
    for idn in rec.get("identifications") or []:
        conf = (idn.get("score") or {}).get("time_total", 0)
        if conf <= 0:
            continue
        for res in idn.get("resolutions") or []:
            ll = res.get("lonlat")
            if ll:
                lng, lat = (round(float(x), 5) for x in ll.split(","))
                out.append([lng, lat, conf])
                break
    out.sort(key=lambda c: -c[2])
    return out[:5]


def main():
    by_fid = {}
    by_base = {}   # normalized base friendly_id -> [records]  (primary match)
    by_alt = {}    # normalized translation-name -> record     (fallback, first wins)
    for line in ANCIENT.open():
        rec = json.loads(line)
        fid = rec["friendly_id"]
        by_fid[fid] = rec
        base = re.sub(r"\s+\d+$", "", fid).strip()
        by_base.setdefault(norm(base), []).append(rec)
        for n in rec.get("translation_name_counts", {}):
            by_alt.setdefault(norm(n), rec)

    def resolve(cands):
        for cand in cands:
            hits = by_base.get(norm(cand))
            if hits:
                return max(hits, key=lambda r: (best_point(r) or (0, 0, -1, ""))[2])
        for cand in cands:
            if norm(cand) in by_alt:
                return by_alt[norm(cand)]
        return None

    curated = {}
    for d in (PLACES_MAJOR, PLACES_MID, PLACES_MINOR):
        curated.update(d)

    coords = {}
    unmatched = []
    for slug, c in sorted(curated.items()):
        if slug in MANUAL:
            lng, lat, note = MANUAL[slug]
            coords[slug] = {"lat": lat, "lng": lng, "confidence": 0,
                            "kind": "representative", "note": note}
            continue
        rec = None
        if slug in OVERRIDES:
            ov = OVERRIDES[slug]
            if ov == "":
                continue
            rec = by_fid.get(ov) or resolve([ov])
        if rec is None:
            rec = resolve([c["name"], *c.get("alt", []), slug.replace("-", " ")])
        if rec is None:
            unmatched.append((slug, c["name"]))
            continue

        bp = best_point(rec)
        if bp is None:
            unmatched.append((slug, c["name"]))
            continue
        lng, lat, conf, kind = bp
        entry = {
            "lat": round(lat, 5),
            "lng": round(lng, 5),
            "confidence": conf,
            "kind": kind,
            "openbible": rec["friendly_id"],
        }
        cand = all_candidates(rec)
        if len(cand) > 1:
            entry["candidates"] = cand
        coords[slug] = entry

    OUT.write_text(json.dumps(
        {"_note": "lon/lat + OpenBible confidence per curated place. Generated by "
                  "_build/backfill_place_coords.py from OpenBible.info Bible-Geocoding-Data "
                  "(CC BY 4.0). Consumed by generate_places.py. Hand-edit OVERRIDES in "
                  "the script, not this file.",
         "coords": {k: coords[k] for k in sorted(coords)}},
        indent=2) + "\n")
    print(f"wrote {OUT.name}: {len(coords)}/{len(curated)} placed")
    if unmatched:
        print(f"{len(unmatched)} unplaced (add to OVERRIDES if locatable):")
        for slug, name in unmatched:
            print(f"  {slug}  ({name})")


if __name__ == "__main__":
    main()
