#!/usr/bin/env python3
"""Render the site's own base maps from Natural Earth vector data.

Why: a Scripture site should not pull modern slippy-map tiles (modern labels,
roads, borders, an external dependency, attribution overhead). Instead we
build our own label-free base layers once, from public-domain Natural Earth
geometry, and add our own place labels/markers from our own data at render
time -- on per-place mini-maps (baked into the static HTML) and on the
interactive map explorer page.

Output:
  images/maps/<extent>-<style>.svg   -- one label-free base map per
      (extent, style) pair. Self-contained: an embedded <style> gives it
      sensible light/dark colors when used via <img>.
  data/maps.json                     -- per-extent projection parameters
      PLUS pre-projected SVG path data for land/lakes/rivers, so both
      generate_static_site.py (stdlib only -- no shapely there) and the
      map explorer client can draw the base map. To place a lon/lat:
          x = (lon - lon_min) * lon_scale
          y = (lat_max - lat) * lat_scale   (SVG units, north up)
      Style colors live in css/style.css (--map-*), never in this file.

Source data (gitignored, fetch with --refresh):
  _build/maps-source/ne_10m_land.geojson  ne_50m_land.geojson
  _build/maps-source/ne_10m_lakes.geojson
  _build/maps-source/ne_10m_rivers_lake_centerlines.geojson

Not run by CI -- its output is committed and trusted. Deterministic; safe to
re-run. Re-run generate_static_site.py afterwards.
"""
import json
import math
import sys
import urllib.request
from pathlib import Path

from shapely.geometry import box, shape, mapping
from shapely.ops import unary_union

ROOT = Path(__file__).resolve().parent.parent
SRC = Path(__file__).resolve().parent / "maps-source"
OUT_DIR = ROOT / "images" / "maps"
MAPS_JSON = ROOT / "data" / "maps.json"

NE_BASE = "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/"
LAYERS = {
    "land10": "ne_10m_land.geojson",
    "land50": "ne_50m_land.geojson",
    "lakes": "ne_10m_lakes.geojson",
    "rivers": "ne_10m_rivers_lake_centerlines.geojson",
}

# Fixed map extents. lon/lat are decimal degrees (WGS84). `width` is the SVG
# viewBox width in user units; height is derived from the aspect ratio after
# the cos(lat) correction so shapes aren't stretched.
EXTENTS = {
    "holy-land": dict(
        title="The Holy Land",
        lon=(33.8, 36.7), lat=(29.4, 33.9), width=760,
        land="land10", simplify=0.0,
    ),
    "biblical-world": dict(
        title="The Biblical World",
        # Wide enough to hold Rome and Malta in the west and Ur/Susa in the
        # east -- the full reach of the New Testament journeys and the exile.
        lon=(11.0, 50.0), lat=(24.0, 43.5), width=1400,
        # 50m coastline, lightly simplified: a continental view doesn't need
        # 10m detail, and the path ships inline in every wide-extent mini-map.
        land="land50", simplify=0.02,
    ),
}

# Per-style fill/stroke for the standalone .svg files (the inlined maps use
# css/style.css --map-* tokens instead). `dark` mirrors the site's dark theme.
STYLES = {
    "parchment": dict(
        water="#e4ddca", land="#faf6ef", lake="#dcd4bd", river="#c3b48c",
        coast="#c9b58c",
        dark=dict(water="#1c1a16", land="#2b2620", lake="#232c30", river="#5b6f78",
                  coast="#4a4238"),
    ),
    "plain": dict(
        water="#d7e5ec", land="#f3efe6", lake="#cadfe9", river="#9fc0d2",
        coast="#c2b08a",
        dark=dict(water="#141b20", land="#262b2e", lake="#1e2a30", river="#4f6b78",
                  coast="#454b4e"),
    ),
}

RIVER_MIN_SCALERANK = {"holy-land": 12, "biblical-world": 4}


def refresh():
    SRC.mkdir(exist_ok=True)
    for fn in LAYERS.values():
        print(f"downloading {fn} ...")
        urllib.request.urlretrieve(NE_BASE + fn, SRC / fn)


def load(fn):
    return json.loads((SRC / fn).read_text())


def projector(ext):
    lon0, lon1 = ext["lon"]
    lat0, lat1 = ext["lat"]
    k = math.cos(math.radians((lat0 + lat1) / 2))
    w = ext["width"]
    lon_scale = w / ((lon1 - lon0) * k)
    h = (lat1 - lat0) * lon_scale
    lon_px = lambda lon: (lon - lon0) * k * lon_scale
    lat_px = lambda lat: (lat1 - lat) * lon_scale
    return lon_px, lat_px, w, h, lon_scale * k, lon_scale


def ring_to_path(coords, lon_px, lat_px):
    pts = [f"{lon_px(lon):.1f},{lat_px(lat):.1f}" for lon, lat in coords]
    return "M" + "L".join(pts) + "Z"


def geom_to_paths(geom, lon_px, lat_px):
    gj = mapping(geom)
    if gj["type"] == "Polygon":
        polys = [gj["coordinates"]]
    elif gj["type"] == "MultiPolygon":
        polys = gj["coordinates"]
    else:
        return []
    return [ring_to_path(ring, lon_px, lat_px) for poly in polys for ring in poly]


def line_to_path(geom, lon_px, lat_px):
    gj = mapping(geom)
    if gj["type"] == "LineString":
        lines = [gj["coordinates"]]
    elif gj["type"] == "MultiLineString":
        lines = gj["coordinates"]
    else:
        return []
    out = []
    for ln in lines:
        pts = [f"{lon_px(lon):.1f},{lat_px(lat):.1f}" for lon, lat in ln]
        if len(pts) >= 2:
            out.append("M" + "L".join(pts))
    return out


STYLE_BLOCK = """
    :root {{ --w:{water}; --l:{land}; --k:{lake}; --r:{river}; --c:{coast}; }}
    @media (prefers-color-scheme: dark) {{ :root:not([data-theme="light"]) {{
      --w:{d_water}; --l:{d_land}; --k:{d_lake}; --r:{d_river}; --c:{d_coast}; }} }}
    :root[data-theme="dark"] {{ --w:{d_water}; --l:{d_land}; --k:{d_lake}; --r:{d_river}; --c:{d_coast}; }}
    .w {{ fill: var(--w); }}
    .l {{ fill: var(--l); stroke: var(--c); stroke-width: 1; stroke-linejoin: round; }}
    .k {{ fill: var(--k); stroke: var(--c); stroke-width: .6; }}
    .r {{ fill: none; stroke: var(--r); stroke-width: 1.1; stroke-linecap: round; stroke-linejoin: round; }}
""".strip("\n")


def compute_paths(ext_name, layers):
    """Project + clip the three layers for one extent. Style-independent."""
    ext = EXTENTS[ext_name]
    lon_px, lat_px, w, h, lon_scale, lat_scale = projector(ext)
    clip = box(ext["lon"][0], ext["lat"][0], ext["lon"][1], ext["lat"][1])
    simp = ext.get("simplify") or 0.0

    land = unary_union([shape(f["geometry"]) for f in layers[ext["land"]]["features"]])
    land = land.intersection(clip)
    if simp:
        land = land.simplify(simp)

    lake_geoms = []
    for f in layers["lakes"]["features"]:
        g = shape(f["geometry"])
        if g.intersects(clip):
            g = g.intersection(clip)
            if simp:
                g = g.simplify(simp)
            if not g.is_empty:
                lake_geoms.append(g)

    rmin = RIVER_MIN_SCALERANK[ext_name]
    river_geoms = []
    for f in layers["rivers"]["features"]:
        if (f["properties"].get("scalerank") or 99) > rmin:
            continue
        g = shape(f["geometry"])
        if g.intersects(clip):
            g = g.intersection(clip)
            if simp:
                g = g.simplify(simp)
            if not g.is_empty:
                river_geoms.append(g)

    return {
        "title": ext["title"],
        "lon_min": ext["lon"][0], "lon_max": ext["lon"][1],
        "lat_min": ext["lat"][0], "lat_max": ext["lat"][1],
        "width": round(w, 2), "height": round(h, 2),
        "lon_scale": round(lon_scale, 6), "lat_scale": round(lat_scale, 6),
        "styles": sorted(STYLES),
        "land": "".join(geom_to_paths(land, lon_px, lat_px)),
        "lakes": [p for g in lake_geoms for p in geom_to_paths(g, lon_px, lat_px)],
        "rivers": [p for g in river_geoms for p in line_to_path(g, lon_px, lat_px)],
    }


def write_svg(ext_name, style_name, paths):
    style = STYLES[style_name]
    w, h = paths["width"], paths["height"]
    fmt = {k: v for k, v in style.items() if k != "dark"}
    fmt.update({f"d_{k}": v for k, v in style["dark"].items()})
    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w:.0f} {h:.0f}" '
        f'width="{w:.0f}" height="{h:.0f}" role="img" aria-label="Base map: {paths["title"]}">',
        f"<style>{STYLE_BLOCK.format(**fmt)}</style>",
        f'<rect class="w" x="0" y="0" width="{w:.0f}" height="{h:.0f}"/>',
        f'<path class="l" d="{paths["land"]}"/>',
    ]
    svg += [f'<path class="k" d="{p}"/>' for p in paths["lakes"]]
    svg += [f'<path class="r" d="{p}"/>' for p in paths["rivers"]]
    svg.append("</svg>")
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / f"{ext_name}-{style_name}.svg").write_text("\n".join(svg) + "\n")


def main():
    if "--refresh" in sys.argv:
        refresh()
    for fn in LAYERS.values():
        if not (SRC / fn).exists():
            sys.exit(f"missing {SRC / fn}; run with --refresh")

    layers = {k: load(fn) for k, fn in LAYERS.items()}

    extents = {}
    for ext_name in EXTENTS:
        paths = compute_paths(ext_name, layers)
        for style_name in STYLES:
            write_svg(ext_name, style_name, paths)
        extents[ext_name] = paths
        print(f"{ext_name}: {paths['width']:.0f}x{paths['height']:.0f}  "
              f"land {len(paths['land'])}b, {len(paths['lakes'])} lakes, "
              f"{len(paths['rivers'])} rivers")

    MAPS_JSON.write_text(json.dumps(
        {"_note": "Base-map geometry + projection. x=(lon-lon_min)*lon_scale, "
                  "y=(lat_max-lat)*lat_scale (SVG units, north up). land/lakes/rivers "
                  "are pre-projected SVG path data. Generated by _build/generate_maps.py "
                  "from Natural Earth (public domain); style colors are css/style.css --map-*.",
         "extents": extents},
        indent=2) + "\n")


if __name__ == "__main__":
    main()
