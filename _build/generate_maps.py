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
  images/maps/relief-<extent>.jpg    -- a shaded-relief raster cropped to
      each extent, normalised so flat ground sits at mid-grey (128) and
      water is flattened to 128, so it composites over any themed land
      colour with `mix-blend-mode: soft-light`. Backs the map explorer's
      "Topographic" base style.
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
  _build/maps-source/SR_HR.tif  -- Natural Earth "Shaded Relief, high res"
      (public domain), 21600x10800 equirectangular grey hillshade. Only
      needed to rebuild the relief rasters; the vector maps build without
      it. Fetched + unzipped by --refresh.

Not run by CI -- its output is committed and trusted. Deterministic; safe to
re-run. Re-run generate_static_site.py afterwards.
"""
import json
import math
import sys
import urllib.request
import zipfile
from pathlib import Path

from shapely.geometry import box, shape, mapping
from shapely.ops import unary_union

ROOT = Path(__file__).resolve().parent.parent
SRC = Path(__file__).resolve().parent / "maps-source"
REGION_SRC = SRC / "regions"
OUT_DIR = ROOT / "images" / "maps"
MAPS_JSON = ROOT / "data" / "maps.json"
PLACE_COORDS = Path(__file__).resolve().parent / "place_coords.json"

# Region/nation outlines: fetched from OpenBible.info's geometry/ files
# (CC BY 4.0) named by each region place's `geojson` in place_coords.json.
# Simplified per extent -- these are context outlines, not precise borders
# (many biblical region boundaries are themselves disputed). The Holy Land
# view is small, so it needs a finer tolerance than the continental one.
REGION_SIMPLIFY = {"holy-land": 0.012, "biblical-world": 0.05}
REGION_GEOJSON_BASE = "https://raw.githubusercontent.com/openbibleinfo/Bible-Geocoding-Data/main/geometry/"

NE_BASE = "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/"
LAYERS = {
    "land10": "ne_10m_land.geojson",
    "land50": "ne_50m_land.geojson",
    "lakes": "ne_10m_lakes.geojson",
    "rivers": "ne_10m_rivers_lake_centerlines.geojson",
}

# Natural Earth "Shaded Relief, high resolution" -- a public-domain grey
# hillshade, equirectangular (EPSG:4326), 21600x10800. Our own projection is
# equirectangular too (constant cos(lat0) x-scale), so a relief crop only
# needs a lon/lat box crop + a non-uniform resize to the extent's SVG box.
RELIEF_ZIP = "https://naturalearth.s3.amazonaws.com/10m_raster/SR_HR.zip"
RELIEF_TIF = SRC / "SR_HR.tif"

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
    # "Topographic": a warm land/teal water palette that a grey shaded-relief
    # raster (images/maps/relief-<extent>.jpg) is composited over with
    # mix-blend-mode: soft-light. Colours mirror css/style.css
    # #map-explorer[data-mapstyle="topo"].
    "topo": dict(
        water="#bcd4d8", land="#ece1c8", lake="#b9d2d6", river="#8fb3bd",
        coast="#b09a72", relief=True,
        dark=dict(water="#10171a", land="#2f2b22", lake="#17242a", river="#4f6b78",
                  coast="#4a4436"),
    ),
}

RIVER_MIN_SCALERANK = {"holy-land": 12, "biblical-world": 4}


def refresh():
    SRC.mkdir(exist_ok=True)
    for fn in LAYERS.values():
        print(f"downloading {fn} ...")
        urllib.request.urlretrieve(NE_BASE + fn, SRC / fn)
    refresh_relief()
    refresh_regions()


def refresh_relief():
    """Fetch + unzip the Natural Earth shaded-relief raster (skips if present)."""
    if RELIEF_TIF.exists() and RELIEF_TIF.stat().st_size:
        return
    zpath = SRC / "SR_HR.zip"
    print("downloading SR_HR.zip (~44 MB) ...")
    urllib.request.urlretrieve(RELIEF_ZIP, zpath)
    with zipfile.ZipFile(zpath) as z:
        for member in z.namelist():
            if member.endswith(".tif"):
                z.extract(member, SRC)
    zpath.unlink()


def refresh_regions():
    """Fetch each region place's OpenBible geometry file named in
    place_coords.json (skips ones already on disk)."""
    if not PLACE_COORDS.exists():
        print("no place_coords.json; skipping region geometry")
        return
    REGION_SRC.mkdir(parents=True, exist_ok=True)
    coords = json.loads(PLACE_COORDS.read_text())["coords"]
    files = {v["geojson"] for v in coords.values() if v.get("geojson")}
    for fn in sorted(files):
        dst = REGION_SRC / fn
        if dst.exists() and dst.stat().st_size:
            continue
        try:
            urllib.request.urlretrieve(REGION_GEOJSON_BASE + fn, dst)
        except Exception as exc:  # noqa: BLE001
            print(f"  region {fn}: {exc}")


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

    out = {
        "title": ext["title"],
        "lon_min": ext["lon"][0], "lon_max": ext["lon"][1],
        "lat_min": ext["lat"][0], "lat_max": ext["lat"][1],
        "width": round(w, 2), "height": round(h, 2),
        "lon_scale": round(lon_scale, 6), "lat_scale": round(lat_scale, 6),
        "styles": sorted(STYLES),
        "land": "".join(geom_to_paths(land, lon_px, lat_px)),
        "lakes": [p for g in lake_geoms for p in geom_to_paths(g, lon_px, lat_px)],
        "rivers": [p for g in river_geoms for p in line_to_path(g, lon_px, lat_px)],
        "regions": region_paths(ext_name, clip, lon_px, lat_px),
    }
    rel = bake_relief(ext_name, ext, land, w, h)
    if rel:
        out["relief"] = rel
    return out


def _land_mask(land, ext, tw, th):
    """Boolean (th, tw) array, True over land. Sampled with shapely at each
    pixel centre -- our projection is equirectangular (linear in lon and lat),
    so pixel (col,row) maps back to lon/lat by a plain linear interpolation.
    (PIL polygon fill can't be trusted on coastlines this convoluted.)"""
    import numpy as np
    import shapely

    lon0, lon1 = ext["lon"]
    lat0, lat1 = ext["lat"]
    xs = lon0 + (np.arange(tw) + 0.5) / tw * (lon1 - lon0)
    ys = lat1 - (np.arange(th) + 0.5) / th * (lat1 - lat0)
    gx, gy = np.meshgrid(xs, ys)
    shapely.prepare(land)
    return shapely.contains_xy(land, gx, gy)


def bake_relief(ext_name, ext, land, w, h):
    """Crop the Natural Earth hillshade to this extent, normalise it so flat
    ground and water sit at mid-grey (128), and write a small JPEG. Composited
    on the client over the themed land colour with mix-blend-mode: soft-light,
    so one neutral raster works in light and dark. Returns the output filename,
    or None when the source raster isn't present."""
    if not RELIEF_TIF.exists():
        print(f"  {ext_name}: no SR_HR.tif, skipping relief (run with --refresh)")
        return None
    import numpy as np
    from PIL import Image

    Image.MAX_IMAGE_PIXELS = None
    src = Image.open(RELIEF_TIF)
    sw, sh = src.size
    ppd_x, ppd_y = sw / 360.0, sh / 180.0
    lon0, lon1 = ext["lon"]
    lat0, lat1 = ext["lat"]
    crop_box = (
        int(round((lon0 + 180) * ppd_x)), int(round((90 - lat1) * ppd_y)),
        int(round((lon1 + 180) * ppd_x)), int(round((90 - lat0) * ppd_y)),
    )
    # Target size: the SVG user-unit box, capped. The resize is deliberately
    # non-uniform -- it applies the same cos(lat) longitude squeeze the vector
    # projection does.
    tw = min(int(round(w)), 1400)
    th = int(round(tw * h / w))
    crop = src.crop(crop_box).convert("L").resize((tw, th), Image.LANCZOS)

    a = np.asarray(crop).astype(np.float32)
    med = float(np.median(a))
    a = 128.0 + (a - med) * 1.4          # recentre flat ground on mid-grey
    a[~_land_mask(land, ext, tw, th)] = 128.0  # flatten water to a soft-light no-op
    a = np.clip(a, 0, 255).astype(np.uint8)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    fn = f"relief-{ext_name}.jpg"
    Image.fromarray(a, "L").save(OUT_DIR / fn, quality=82, optimize=True)
    print(f"  {ext_name}: relief {tw}x{th} -> {fn} "
          f"({(OUT_DIR / fn).stat().st_size // 1024} KB)")
    return fn


def _feature_geom(gj):
    """The polygon/line geometry from a region file (a Feature or a
    FeatureCollection that also carries a Point we ignore)."""
    feats = gj["features"] if gj.get("type") == "FeatureCollection" else [gj]
    for f in feats:
        g = f.get("geometry", f)
        if g and g.get("type") in ("Polygon", "MultiPolygon", "LineString", "MultiLineString"):
            return shape(g)
    return None


def region_paths(ext_name, clip, lon_px, lat_px):
    if not PLACE_COORDS.exists():
        return {}
    tol = REGION_SIMPLIFY[ext_name]
    coords = json.loads(PLACE_COORDS.read_text())["coords"]
    out = {}
    for slug, v in sorted(coords.items()):
        fn = v.get("geojson")
        if not fn:
            continue
        src = REGION_SRC / fn
        if not src.exists():
            continue
        geom = _feature_geom(json.loads(src.read_text()))
        if geom is None:
            continue
        if geom.geom_type.endswith("Polygon") and not geom.is_valid:
            geom = geom.buffer(0)
        if geom.is_empty or not geom.intersects(clip):
            continue
        geom = geom.intersection(clip).simplify(tol)
        if geom.is_empty:
            continue
        if geom.geom_type in ("Polygon", "MultiPolygon"):
            d = "".join(geom_to_paths(geom, lon_px, lat_px))
            kind = "poly"
        else:
            d = "".join(line_to_path(geom, lon_px, lat_px))
            kind = "line"
        if d:
            out[slug] = {"t": kind, "d": d}
    return out


def write_svg(ext_name, style_name, paths):
    style = STYLES[style_name]
    w, h = paths["width"], paths["height"]
    fmt = {k: v for k, v in style.items() if k not in ("dark", "relief")}
    fmt.update({f"d_{k}": v for k, v in style["dark"].items()})
    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w:.0f} {h:.0f}" '
        f'width="{w:.0f}" height="{h:.0f}" role="img" aria-label="Base map: {paths["title"]}">',
        f"<style>{STYLE_BLOCK.format(**fmt)}</style>",
        f'<rect class="w" x="0" y="0" width="{w:.0f}" height="{h:.0f}"/>',
        f'<path class="l" d="{paths["land"]}"/>',
    ]
    if style.get("relief") and paths.get("relief"):
        svg.append(
            f'<image href="{paths["relief"]}" x="0" y="0" width="{w:.0f}" '
            f'height="{h:.0f}" preserveAspectRatio="none" '
            f'style="mix-blend-mode:soft-light"/>'
        )
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
                  "are pre-projected SVG path data; `relief` (when present) is a "
                  "shaded-relief JPEG (filename relative to images/maps/) for the map "
                  "explorer's Topographic style, drawn at 0,0 width x height and "
                  "composited with mix-blend-mode:soft-light. "
                  "Generated by _build/generate_maps.py "
                  "from Natural Earth (public domain); style colors are css/style.css --map-*.",
         "extents": extents},
        indent=2) + "\n")


if __name__ == "__main__":
    main()
