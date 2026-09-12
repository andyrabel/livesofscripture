#!/usr/bin/env python3
"""Attach a lon/lat (and identification confidence) to the OpenBible.info
gazetteer stubs (data/places_gazetteer.json) -- the ~955 name-only places
added by import_openbible_places.py that have no entry in places_data.py.

Why: backfill_place_coords.py only ever covered the ~227 hand-curated
places, so a gazetteer stub (Abana, Bether, Cherith...) had no coordinate at
all and so no way to render its own per-place locator map
(place_mini_map_html in generate_static_site.py). This closes that gap for
individual place pages *without* adding these ~950 points to the map
explorer's default "show every placed marker" view (data/places-index.json
deliberately does not get a flat lat/lng for a gazetteer-only place -- see
generate_places.py's index-building step, and CLAUDE.md's Places section) --
Andrew asked specifically for a per-page map, not a main map flooded with
name-only dots.

Output: _build/gazetteer_place_coords.json (force-committed like
place_coords.json), same shape:
    { "<place_id>": {
        "lat": float, "lng": float,
        "confidence": 0-1000,          # OpenBible time_total; 1000 = no doubt
        "kind": "point" | "representative",
        "openbible": "<friendly_id>",
      } }

generate_places.py reads this at lowest priority (place_coords.json always
wins if a slug is somehow in both) and writes a `geo` block onto the
gazetteer stub's data/places/<id>.json -- but not onto the index -- so
place_mini_map_html can render for it. No `candidates`/`geojson` support
here (unlike the curated backfill): gazetteer stubs don't get disputed-site
alternate points or region outlines, just a single best point.

Input: _build/openbible-source/ancient.jsonl -- the full upstream file
(~11 MB, gitignored). Fetch it with `import_openbible_places.py --refresh`.

Matching: a gazetteer slug's `name` field is OpenBible's un-numbered base
name (e.g. "Bether" for friendly_id "Bether 1"). Where the site's own
numeric suffix on the slug (e.g. "bether-2") tells us which numbered
instance to use, try that first; otherwise try the bare name, then fall
back to scanning numbered variants ("Bether 1".."Bether 8") and keeping
whichever has the highest-confidence point. That fallback is needed for two
distinct cases: (1) a numbered instance that happens to be the only one
with recorded verses (Bether, Joktheel), and (2) import_openbible_places.py's
COLLAPSE_INSTANCES merge (Red Sea, Holy Place, Most Holy Place), which
combines several numbered OpenBible records into one gazetteer stub and so
loses the specific friendly_id needed for a direct lookup.

A handful of gazetteer places (Azazel, Bamah, Biziothiah, Nohah, as of
2026-09-11) have no resolvable point in OpenBible at all -- left with no
`geo`, same as any other place lacking coordinates; their page just renders
without a mini-map rather than guessing.

Deterministic; safe to re-run. Re-run (then generate_places.py, then
generate_static_site.py) if data/places_gazetteer.json is regenerated.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ANCIENT = Path(__file__).resolve().parent / "openbible-source" / "ancient.jsonl"
GAZ = ROOT / "data" / "places_gazetteer.json"
OUT = Path(__file__).resolve().parent / "gazetteer_place_coords.json"


def best_point(rec):
    """Highest-confidence (lng, lat, confidence, kind) for a record, or None."""
    best = None
    for idn in rec.get("identifications") or []:
        conf = (idn.get("score") or {}).get("time_total", 0)
        for res in idn.get("resolutions") or []:
            ll = res.get("lonlat")
            if not ll:
                continue
            lng, lat = (float(x) for x in ll.split(","))
            kind = "point" if res.get("lonlat_type") == "point" else "representative"
            if best is None or conf > best[2]:
                best = (lng, lat, conf, kind)
            break
    return best


def resolve(by_fid, name, slug):
    tries = []
    m = re.search(r"-(\d+)$", slug)
    if m:
        tries.append(f"{name} {m.group(1)}")
    tries.append(name)
    for t in tries:
        rec = by_fid.get(t)
        if rec:
            bp = best_point(rec)
            if bp:
                return bp, rec["friendly_id"]
    best = None
    best_fid = None
    for n in range(1, 9):
        rec = by_fid.get(f"{name} {n}")
        if not rec:
            continue
        bp = best_point(rec)
        if bp and (best is None or bp[2] > best[2]):
            best, best_fid = bp, rec["friendly_id"]
    return (best, best_fid) if best else (None, None)


def main():
    if not ANCIENT.exists():
        sys.exit(f"missing {ANCIENT}; run import_openbible_places.py --refresh to fetch it")
    if not GAZ.exists():
        sys.exit(f"missing {GAZ}; run import_openbible_places.py first")

    by_fid = {}
    for line in ANCIENT.open():
        rec = json.loads(line)
        by_fid[rec["friendly_id"]] = rec

    gaz = json.loads(GAZ.read_text())["places"]

    coords = {}
    unmatched = []
    for slug in sorted(gaz):
        e = gaz[slug]
        bp, fid = resolve(by_fid, e["name"], slug)
        if bp is None:
            unmatched.append((slug, e["name"]))
            continue
        lng, lat, conf, kind = bp
        coords[slug] = {
            "lat": round(lat, 5),
            "lng": round(lng, 5),
            "confidence": conf,
            "kind": kind,
            "openbible": fid,
        }

    OUT.write_text(json.dumps(
        {"_note": "lon/lat + OpenBible confidence per OpenBible.info gazetteer stub "
                  "(data/places_gazetteer.json). Generated by "
                  "_build/backfill_gazetteer_place_coords.py from OpenBible.info "
                  "Bible-Geocoding-Data (CC BY 4.0). Consumed by generate_places.py "
                  "for a per-place locator map only -- deliberately NOT surfaced as a "
                  "flat lat/lng on data/places-index.json, so these ~950 name-only "
                  "places don't appear on the main map explorer. See CLAUDE.md's "
                  "Places / Map section.",
         "coords": {k: coords[k] for k in sorted(coords)}},
        indent=2) + "\n")
    print(f"wrote {OUT.name}: {len(coords)}/{len(gaz)} placed")
    if unmatched:
        print(f"{len(unmatched)} unplaced (no resolvable OpenBible point):")
        for slug, name in unmatched:
            print(f"  {slug}  ({name})")


if __name__ == "__main__":
    main()
