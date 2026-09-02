#!/usr/bin/env python3
"""Render the site's own base maps as SVG from Natural Earth vector data.

Why: a Scripture site should not pull modern slippy-map tiles (modern labels,
roads, borders, an external dependency, attribution overhead). Instead we
build our own label-free base layers once, from public-domain Natural Earth
geometry, and add our own place labels/markers from our own data at render
time -- on per-place mini-maps (baked into the static HTML) and on the
interactive map explorer page.

Output:
  images/maps/<extent>-<style>.svg   -- one label-free base map per
      (extent, style) pair. Self-contained: an embedded <style> gives it
      sensible light/dark colors when used via <img>, and CSS custom
      properties let an inlining page override them.
  data/maps.json                     -- the projection parameters for each
      extent, so client code (and generate_static_site.py) can convert a
      lon/lat to the same SVG x/y the base layer was drawn with:
          x = (lon - lon_min) * lon_scale
          y = (lat_max - lat) * lat_scale

Source data (gitignored, fetch with --refresh):
  _build/maps-source/ne_10m_land.geojson
  _build/maps-source/ne_10m_lakes.geojson
  _build/maps-source/ne_10m_rivers_lake_centerlines.geojson

Deterministic: geometry is rounded and emitted in file order, so a clean
checkout regenerates byte-for-byte. Safe to re-run.
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
    "land": "ne_10m_land.geojson",
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
    ),
    "biblical-world": dict(
        title="The Biblical World",
        lon=(24.0, 50.0), lat=(26.0, 42.5), width=1200,
    ),
}

# Per-style fill/stroke. Kept in sync with the embedded <style> block; the
# SVG uses CSS custom properties so an inlining page can re-theme it.
STYLES = {
    # Tuned to the site's parchment palette (css/style.css --color-bg etc.).
    "parchment": dict(
        water="#e4ddca", land="#faf6ef", lake="#dcd4bd", river="#c3b48c",
        land_stroke="#e3d9c6", coast="#c9b58c",
        dark=dict(water="#1c1a16", land="#2b2620", lake="#232c30", river="#5b6f78",
                  land_stroke="#3a342b", coast="#4a4238"),
    ),
    # A cooler, more conventional atlas look.
    "plain": dict(
        water="#d7e5ec", land="#f3efe6", lake="#cadfe9", river="#9fc0d2",
        land_stroke="#ddd2bd", coast="#c2b08a",
        dark=dict(water="#141b20", land="#262b2e", lake="#1e2a30", river="#4f6b78",
                  land_stroke="#343a3d", coast="#454b4e"),
    ),
}

RIVER_MIN_SCALERANK = {"holy-land": 12, "biblical-world": 7}


def refresh():
    SRC.mkdir(exist_ok=True)
    for name, fn in LAYERS.items():
        url = NE_BASE + fn
        print(f"downloading {fn} ...")
        urllib.request.urlretrieve(url, SRC / fn)


def load(fn):
    return json.loads((SRC / fn).read_text())


def projector(ext):
    lon0, lon1 = ext["lon"]
    lat0, lat1 = ext["lat"]
    mid = math.radians((lat0 + lat1) / 2)
    k = math.cos(mid)
    w = ext["width"]
    lon_scale = w / ((lon1 - lon0) * k)
    lat_scale = lon_scale  # equal-scale: 1 degree lat == 1 degree lon * k already folded in
    h = (lat1 - lat0) * lat_scale
    lon_px = lambda lon: (lon - lon0) * k * lon_scale
    lat_px = lambda lat: (lat1 - lat) * lat_scale
    return lon_px, lat_px, w, h, lon_scale * k, lat_scale


def ring_to_path(coords, lon_px, lat_px):
    pts = []
    for lon, lat in coords:
        pts.append(f"{lon_px(lon):.1f},{lat_px(lat):.1f}")
    return "M" + "L".join(pts) + "Z"


def geom_to_paths(geom, lon_px, lat_px):
    """Polygon/MultiPolygon -> list of subpath strings (outer + holes)."""
    gj = mapping(geom)
    polys = []
    if gj["type"] == "Polygon":
        polys = [gj["coordinates"]]
    elif gj["type"] == "MultiPolygon":
        polys = gj["coordinates"]
    out = []
    for poly in polys:
        for ring in poly:
            out.append(ring_to_path(ring, lon_px, lat_px))
    return out


def line_to_path(geom, lon_px, lat_px):
    gj = mapping(geom)
    lines = []
    if gj["type"] == "LineString":
        lines = [gj["coordinates"]]
    elif gj["type"] == "MultiLineString":
        lines = gj["coordinates"]
    out = []
    for ln in lines:
        pts = [f"{lon_px(lon):.1f},{lat_px(lat):.1f}" for lon, lat in ln]
        if len(pts) >= 2:
            out.append("M" + "L".join(pts))
    return out


STYLE_BLOCK = """
    :root {{
      --map-water: {water}; --map-land: {land}; --map-lake: {lake};
      --map-river: {river}; --map-land-stroke: {land_stroke}; --map-coast: {coast};
    }}
    @media (prefers-color-scheme: dark) {{
      :root:not([data-theme="light"]) {{
        --map-water: {d_water}; --map-land: {d_land}; --map-lake: {d_lake};
        --map-river: {d_river}; --map-land-stroke: {d_land_stroke}; --map-coast: {d_coast};
      }}
    }}
    :root[data-theme="dark"] {{
      --map-water: {d_water}; --map-land: {d_land}; --map-lake: {d_lake};
      --map-river: {d_river}; --map-land-stroke: {d_land_stroke}; --map-coast: {d_coast};
    }}
    .map-water {{ fill: var(--map-water); }}
    .map-land  {{ fill: var(--map-land); stroke: var(--map-coast); stroke-width: 1; stroke-linejoin: round; }}
    .map-lake  {{ fill: var(--map-lake); stroke: var(--map-coast); stroke-width: .6; }}
    .map-river {{ fill: none; stroke: var(--map-river); stroke-width: 1.1; stroke-linecap: round; stroke-linejoin: round; }}
""".strip("\n")


def build(ext_name, style_name, layers):
    ext = EXTENTS[ext_name]
    style = STYLES[style_name]
    lon_px, lat_px, w, h, lon_scale, lat_scale = projector(ext)
    clip = box(ext["lon"][0], ext["lat"][0], ext["lon"][1], ext["lat"][1])

    land = unary_union([shape(f["geometry"]) for f in layers["land"]["features"]])
    land = land.intersection(clip)

    lake_geoms = []
    for f in layers["lakes"]["features"]:
        g = shape(f["geometry"])
        if g.intersects(clip):
            lake_geoms.append(g.intersection(clip))

    rmin = RIVER_MIN_SCALERANK[ext_name]
    river_geoms = []
    for f in layers["rivers"]["features"]:
        if (f["properties"].get("scalerank") or 99) > rmin:
            continue
        g = shape(f["geometry"])
        if g.intersects(clip):
            river_geoms.append(g.intersection(clip))

    land_paths = geom_to_paths(land, lon_px, lat_px)
    lake_paths = [p for g in lake_geoms for p in geom_to_paths(g, lon_px, lat_px)]
    river_paths = [p for g in river_geoms for p in line_to_path(g, lon_px, lat_px)]

    svg = []
    svg.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w:.0f} {h:.0f}" '
        f'width="{w:.0f}" height="{h:.0f}" role="img" '
        f'aria-label="Base map: {ext["title"]}">'
    )
    fmt = {k: v for k, v in style.items() if k != "dark"}
    fmt.update({f"d_{k}": v for k, v in style["dark"].items()})
    svg.append(f"<style>{STYLE_BLOCK.format(**fmt)}</style>")
    svg.append(f'<rect class="map-water" x="0" y="0" width="{w:.0f}" height="{h:.0f}"/>')
    svg.append(f'<path class="map-land" d="{"".join(land_paths)}"/>')
    for p in lake_paths:
        svg.append(f'<path class="map-lake" d="{p}"/>')
    for p in river_paths:
        svg.append(f'<path class="map-river" d="{p}"/>')
    svg.append("</svg>")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / f"{ext_name}-{style_name}.svg").write_text("\n".join(svg) + "\n")
    return w, h, lon_scale, lat_scale


def main():
    if "--refresh" in sys.argv:
        refresh()
    for fn in LAYERS.values():
        if not (SRC / fn).exists():
            sys.exit(f"missing {SRC / fn}; run with --refresh")

    layers = {k: load(fn) for k, fn in LAYERS.items()}

    maps_meta = {}
    for ext_name, ext in EXTENTS.items():
        for style_name in STYLES:
            w, h, lon_scale, lat_scale = build(ext_name, style_name, layers)
        maps_meta[ext_name] = {
            "title": ext["title"],
            "lon_min": ext["lon"][0],
            "lon_max": ext["lon"][1],
            "lat_min": ext["lat"][0],
            "lat_max": ext["lat"][1],
            "width": round(w, 2),
            "height": round(h, 2),
            "lon_scale": round(lon_scale, 6),
            "lat_scale": round(lat_scale, 6),
            "styles": sorted(STYLES),
        }
        print(f"{ext_name}: {w:.0f}x{h:.0f}  styles={sorted(STYLES)}")

    MAPS_JSON.write_text(json.dumps(
        {"_note": "Base-map projection parameters. x=(lon-lon_min)*lon_scale, "
                  "y=(lat_max-lat)*lat_scale. Generated by _build/generate_maps.py "
                  "from Natural Earth (public domain).",
         "extents": maps_meta},
        indent=2) + "\n")


if __name__ == "__main__":
    main()
