#!/usr/bin/env python3
"""Static-site generator for Lives of Scripture.

The site's data lives in data/people.json (index) and data/people/<id>.json
(full entries), and js/app.js renders person pages client-side from that
data. That's fine for browsers, but crawlers that don't execute JavaScript
(GPTBot, ClaudeBot, PerplexityBot, CCBot, and most other LLM-search bots)
would see an empty "Loading…" page for every person entry.

This script pre-renders one fully-baked static HTML page per person at
people/<id>.html — real text content, per-person <title>/meta/OG tags,
canonical URL, and schema.org Person JSON-LD — so that content is visible
to any client, JS or not. It also regenerates sitemap.xml and the static
fallback grid embedded in people.html.

Run after any change under data/. Re-run via `python3 _build/generate_static_site.py`.
A GitHub Actions workflow (.github/workflows/build.yml) runs it on every push
to main and commits the regenerated output.
"""
import html
import json
import re
from datetime import date, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE_URL = "https://livesofscripture.org"
DEFAULT_OG_IMAGE = f"{SITE_URL}/images/social/og-image.png"
BUILD_DATE = date.today().isoformat()

NAV_PAGES = [
    ("index.html", "Home"),
    ("people.html", "People"),
    ("timeline.html", "Timeline"),
    ("connections.html", "Connections"),
    ("quiz.html", "Quiz"),
    ("about.html", "About"),
]


def esc(text):
    return html.escape(text or "", quote=True)


def truncate(text, max_len=155):
    if not text:
        return ""
    if len(text) <= max_len:
        return text
    cut = text[:max_len]
    last_space = cut.rfind(" ")
    if last_space > 0:
        cut = cut[:last_space]
    return cut + "…"


def header_html(base, active):
    links = []
    for href, label in NAV_PAGES:
        current = ' aria-current="page"' if href == active else ""
        links.append(f'<a href="{base}{href}"{current}>{label}</a>')
    nav = "\n      ".join(links)
    return f"""<header class="site-header">
  <div class="header-inner">
    <h1><a href="{base}index.html" class="brand">
      <img src="{base}favicon.svg" class="brand-mark" alt="" width="28" height="28">
      Lives of Scripture
    </a></h1>
    <button type="button" class="nav-toggle" id="nav-toggle" aria-expanded="false" aria-controls="site-nav">
      <span class="sr-only">Menu</span>
      <span class="nav-toggle__bar"></span>
      <span class="nav-toggle__bar"></span>
      <span class="nav-toggle__bar"></span>
    </button>
    <nav id="site-nav">
      {nav}
    </nav>
    <details class="header-notice">
      <summary>Usage &amp; licensing</summary>
      <p>No Bible verse text is quoted or stored on this site, in any translation —
      references are chapter:verse only. Genealogy data is seeded from
      <a href="https://github.com/bradystephenson/bible-data">BibleData</a> by Brady
      Stephenson (<a href="https://creativecommons.org/licenses/by/4.0/">CC BY 4.0</a>).
      Portrait illustrations are AI-generated or hand-authored line art — no claim of
      historical likeness. See <a href="{base}about.html">About</a> for full sourcing.</p>
    </details>
  </div>
</header>"""


def footer_html(base):
    return f"""<footer class="site-footer">
  <p>Lives of Scripture — a reference for every person named in the Bible. See <a href="{base}about.html">About</a> for sources and translation handling.</p>
</footer>"""


# ---------------------------------------------------------------------
# Person page body (mirrors renderFullPerson / renderStubPerson in js/app.js)
# ---------------------------------------------------------------------


def genealogy_block(title, ids, index_by_id, base):
    if not ids:
        return f"""<div class="genealogy-block">
      <h4>{esc(title)}</h4>
      <span style="color: var(--color-text-muted)">—</span>
    </div>"""
    id_list = ids if isinstance(ids, list) else [ids]
    links = ", ".join(
        f'<a href="{base}people/{esc(pid)}.html">{esc(index_by_id.get(pid, pid))}</a>'
        for pid in id_list
    )
    return f"""<div class="genealogy-block">
      <h4>{esc(title)}</h4>
      {links}
    </div>"""


def review_badge(review):
    if review and review.get("human_reviewed"):
        return '<span class="review-badge reviewed">✅ Reviewed for accuracy</span>'
    return '<span class="review-badge unreviewed">⚠️ AI-generated — not yet human reviewed</span>'


def references_list(refs):
    return f'<p class="references-list">References: {esc("; ".join(refs))}</p>'


def connections_graph_link(person_id, base):
    return f'<p><a href="{base}connections.html?id={person_id}">View full connections graph →</a></p>'


def timeline_link(person_id, base):
    return f'<p><a href="{base}timeline.html?highlight={person_id}">See on the full timeline →</a></p>'


def connection_edge_line(edge, index_by_id, base):
    from_link = f'<a href="{base}people/{esc(edge["from"])}.html">{esc(index_by_id.get(edge["from"], edge["from"]))}</a>'
    to_link = f'<a href="{base}people/{esc(edge["to"])}.html">{esc(index_by_id.get(edge["to"], edge["to"]))}</a>'
    sep = f' ↔ {esc(edge["label"])} ↔ ' if edge.get("mutual") else f' — {esc(edge["label"])} → '
    parts = [f"<li>{from_link}{sep}{to_link}"]
    if edge.get("note"):
        parts.append(f'<p class="connections-list__note">{esc(edge["note"])}</p>')
    if edge.get("references"):
        parts.append(f'<p class="connections-list__refs">{esc("; ".join(edge["references"]))}</p>')
    parts.append("</li>")
    return "\n".join(parts)


def genealogy_section(person, index_by_id, base):
    gen = person.get("genealogy") or {}
    blocks = "\n    ".join(
        [
            genealogy_block("Father", gen.get("father"), index_by_id, base),
            genealogy_block("Mother", gen.get("mother"), index_by_id, base),
            genealogy_block("Spouse(s)", gen.get("spouses"), index_by_id, base),
            genealogy_block("Children", gen.get("children"), index_by_id, base),
        ]
    )
    return f"""<section>
    <h3>Genealogy</h3>
    <div class="genealogy-grid">
    {blocks}
    </div>
  </section>"""


def connections_section(person, index_by_id, connections, base):
    pid = person["person_id"]
    related = [e for e in connections if e["from"] == pid or e["to"] == pid]
    if not related:
        return ""
    items = "\n    ".join(connection_edge_line(e, index_by_id, base) for e in related)
    return f"""<section>
    <h3>Connections</h3>
    <ul class="connections-list">
    {items}
    </ul>
  </section>"""


def render_full_person_body(person, index_by_id, connections, base, portrait_exists):
    parts = []

    if portrait_exists:
        img_url = f'{base}images/portraits/{esc(person["image"]["file"])}'
        img_html = f'<img src="{img_url}" alt="{esc(person["name"])} — {esc(person["image"]["caption"])}">'
    else:
        img_html = '<div class="image-placeholder">Illustration pending</div>'

    alt_html = ""
    if person.get("alt_names"):
        alt_html = f'<div class="alt-names">Also called: {esc(", ".join(person["alt_names"]))}</div>'

    testament_class = "ot" if person.get("testament") == "OT" else "nt"
    era_badge = f'<span class="badge">{esc(person["era"])}</span>' if person.get("era") else ""

    parts.append(f"""<div class="person-header">
    {img_html}
    <div class="person-title">
      <h2>{esc(person["name"])}</h2>
      {alt_html}
      <div class="tags">
        <span class="badge {testament_class}">{esc(person.get("testament", ""))}</span>
        {era_badge}
      </div>
      <p>{review_badge(person.get("review"))}</p>
    </div>
  </div>""")

    if person.get("source_summary"):
        parts.append(f"<p>{esc(person['source_summary'])}</p>")

    if person.get("family_friendly_summary"):
        parts.append(f"""<div class="family-friendly">
    <span class="family-friendly-label">For younger readers</span>
    <p>{esc(person["family_friendly_summary"])}</p>
  </div>""")

    if person.get("interpretive_dispute") and person.get("interpretive_note"):
        parts.append(f'<div class="interpretive-note">Interpretive note: {esc(person["interpretive_note"])}</div>')

    parts.append(f"""<section class="story">
    <h3>Life Story</h3>
    <p>{esc(person.get("adult_story"))}</p>
    <h3>Family</h3>
    <p>{esc(person.get("family_story"))}</p>
  </section>""")

    if person.get("references"):
        parts.append(references_list(person["references"]))

    parts.append(genealogy_section(person, index_by_id, base))

    conn_section = connections_section(person, index_by_id, connections, base)
    if conn_section:
        parts.append(conn_section)

    parts.append(connections_graph_link(person["person_id"], base))

    if person.get("timeline"):
        parts.append(timeline_link(person["person_id"], base))

    return "\n  ".join(parts)


def render_stub_person_body(person, index_by_id, connections, base):
    parts = [f"<h2>{esc(person['name'])}</h2>"]

    if person.get("alt_names"):
        parts.append(f'<div class="alt-names">Also called: {esc(", ".join(person["alt_names"]))}</div>')

    parts.append(
        '<div class="stub-notice">Named in Scripture, but with no narrative of their own — '
        "kept here for the connections graph.</div>"
    )

    if person.get("references"):
        parts.append(references_list(person["references"]))

    parts.append(genealogy_section(person, index_by_id, base))

    conn_section = connections_section(person, index_by_id, connections, base)
    if conn_section:
        parts.append(conn_section)

    parts.append(connections_graph_link(person["person_id"], base))

    return "\n  ".join(parts)


def meta_description_for(person):
    if person["tier"] == "full" and person.get("source_summary"):
        return truncate(person["source_summary"])
    refs = "; ".join(person.get("references", []))
    text = f"{person['name']} is named in Scripture ({refs}) — see how they connect in the genealogy graph."
    return truncate(text)


def person_json_ld(person, index_by_id, base_url, canonical, og_image, portrait_exists):
    data = {
        "@context": "https://schema.org",
        "@type": "Person",
        "name": person["name"],
        "url": canonical,
        "mainEntityOfPage": canonical,
        "description": meta_description_for(person),
        "isPartOf": {"@type": "WebSite", "name": "Lives of Scripture", "url": f"{base_url}/"},
    }
    if person.get("alt_names"):
        data["alternateName"] = person["alt_names"]
    if portrait_exists:
        data["image"] = og_image
    if person.get("references"):
        data["citation"] = person["references"]
    if person.get("topics"):
        data["knowsAbout"] = person["topics"]

    def person_ref(pid):
        return {"@type": "Person", "name": index_by_id.get(pid, pid), "url": f"{base_url}/people/{pid}.html"}

    gen = person.get("genealogy") or {}
    parents = [person_ref(p) for p in [gen.get("father"), gen.get("mother")] if p]
    if parents:
        data["parent"] = parents
    if gen.get("children"):
        data["children"] = [person_ref(p) for p in gen["children"]]
    if gen.get("spouses"):
        data["spouse"] = [person_ref(p) for p in gen["spouses"]]

    return json.dumps(data, indent=2, ensure_ascii=False)


def build_person_page(person, index_by_id, connections):
    pid = person["person_id"]
    base = "../"
    canonical = f"{SITE_URL}/people/{pid}.html"
    portrait_exists = person["tier"] == "full" and (
        ROOT / "images" / "portraits" / person.get("image", {}).get("file", "")
    ).exists()
    og_image = f'{SITE_URL}/images/portraits/{person["image"]["file"]}' if portrait_exists else DEFAULT_OG_IMAGE
    description = meta_description_for(person)
    title = f'{person["name"]} — Lives of Scripture'

    if person["tier"] == "full":
        body = render_full_person_body(person, index_by_id, connections, base, portrait_exists)
    else:
        body = render_stub_person_body(person, index_by_id, connections, base)

    json_ld = person_json_ld(person, index_by_id, SITE_URL, canonical, og_image, portrait_exists)

    html_out = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(title)}</title>
<meta name="description" content="{esc(description)}">
<link rel="canonical" href="{canonical}">

<link rel="icon" href="{base}favicon.svg" type="image/svg+xml">
<link rel="alternate icon" href="{base}favicon.ico">
<link rel="icon" type="image/png" sizes="32x32" href="{base}images/favicon-32x32.png">
<link rel="icon" type="image/png" sizes="16x16" href="{base}images/favicon-16x16.png">
<link rel="apple-touch-icon" href="{base}apple-touch-icon.png">

<meta property="og:type" content="profile">
<meta property="og:site_name" content="Lives of Scripture">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(description)}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{og_image}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{esc(title)}">
<meta name="twitter:description" content="{esc(description)}">
<meta name="twitter:image" content="{og_image}">

<link rel="stylesheet" href="{base}css/style.css">
<script type="application/ld+json">
{json_ld}
</script>
</head>
<body>
{header_html(base, "people.html")}

<main id="person-main">
  {body}
</main>

{footer_html(base)}

<script src="{base}js/app.js"></script>
<script>initNavToggle();</script>
</body>
</html>
"""
    return html_out


# ---------------------------------------------------------------------
# people.html static fallback grid
# ---------------------------------------------------------------------


def person_card_html(entry):
    if entry["tier"] == "stub":
        meta_badge = '<span class="badge stub">name only</span>'
    elif entry.get("era"):
        meta_badge = f'<span class="badge">{esc(entry["era"])}</span>'
    else:
        meta_badge = ""
    testament_class = "ot" if entry.get("testament") == "OT" else "nt"
    return f"""<a class="person-card" href="people/{entry['person_id']}.html">
      <div class="name">{esc(entry["name"])}</div>
      <div class="meta"><span class="badge {testament_class}">{esc(entry.get("testament", ""))}</span>{meta_badge}</div>
    </a>"""


def update_people_grid(index):
    path = ROOT / "people.html"
    text = path.read_text()
    cards = "\n    ".join(person_card_html(e) for e in index)
    new_block = f"    <!-- STATIC_PERSON_GRID_START — regenerated by _build/generate_static_site.py, replaced client-side by renderIndexPage() when JS runs -->\n    {cards}\n    <!-- STATIC_PERSON_GRID_END -->"
    pattern = re.compile(
        r"    <!-- STATIC_PERSON_GRID_START.*?STATIC_PERSON_GRID_END -->", re.DOTALL
    )
    if not pattern.search(text):
        raise SystemExit("people.html: STATIC_PERSON_GRID markers not found")
    text = pattern.sub(new_block, text)
    path.write_text(text)


# ---------------------------------------------------------------------
# sitemap.xml
# ---------------------------------------------------------------------


def build_sitemap(index):
    urls = [
        (f"{SITE_URL}/", "weekly", "1.0"),
        (f"{SITE_URL}/people.html", "weekly", "0.9"),
        (f"{SITE_URL}/timeline.html", "monthly", "0.6"),
        (f"{SITE_URL}/connections.html", "monthly", "0.6"),
        (f"{SITE_URL}/quiz.html", "monthly", "0.5"),
        (f"{SITE_URL}/about.html", "monthly", "0.4"),
    ]
    for entry in index:
        priority = "0.8" if entry["tier"] == "full" else "0.3"
        urls.append((f'{SITE_URL}/people/{entry["person_id"]}.html', "monthly", priority))

    entries = "\n".join(
        f"  <url>\n    <loc>{loc}</loc>\n    <lastmod>{BUILD_DATE}</lastmod>\n"
        f"    <changefreq>{freq}</changefreq>\n    <priority>{prio}</priority>\n  </url>"
        for loc, freq, prio in urls
    )
    sitemap = f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{entries}\n</urlset>\n'
    (ROOT / "sitemap.xml").write_text(sitemap)


# ---------------------------------------------------------------------


def main():
    index = json.loads((ROOT / "data" / "people.json").read_text())
    connections = json.loads((ROOT / "data" / "connections.json").read_text())
    index_by_id = {e["person_id"]: e["name"] for e in index}

    people_dir = ROOT / "people"
    people_dir.mkdir(exist_ok=True)

    generated = 0
    for entry in index:
        pid = entry["person_id"]
        person_path = ROOT / "data" / "people" / f"{pid}.json"
        if not person_path.exists():
            print(f"warning: no data/people/{pid}.json, skipping")
            continue
        person = json.loads(person_path.read_text())
        page = build_person_page(person, index_by_id, connections)
        (people_dir / f"{pid}.html").write_text(page)
        generated += 1

    update_people_grid(index)
    build_sitemap(index)

    print(f"Generated {generated} person pages, sitemap.xml, and people.html static grid.")


if __name__ == "__main__":
    main()
