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

Run after any change under data/. Re-run via `python3 _build/generate_static_site.py`
and commit its output with the source-data change. A GitHub Actions workflow
(.github/workflows/build.yml) runs it on every push to main and fails if the
committed generated output is stale; the workflow does not commit or push.
"""
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE_URL = "https://livesofscripture.org"
DEFAULT_OG_IMAGE = f"{SITE_URL}/images/social/og-image.png"
NAV_PAGES = [
    ("index.html", "Home"),
    ("people.html", "People"),
    ("timeline.html", "Timeline"),
    ("connections.html", "Connections"),
    ("churches.html", "Churches"),
    ("charts.html", "Charts"),
    ("quiz.html", "Quiz"),
    ("about.html", "About"),
]


def esc(text):
    return html.escape(text or "", quote=True)


def resolve_portrait_file(person):
    """Prefer the lightweight web JPEG (images/portraits2-web/) over the
    full-resolution stained-glass source (images/portraits2/) over the
    legacy image (images/portraits/), falling back to whichever one actually
    exists on disk. Returns (dir_name, file_name) or (None, None).

    images/portraits2/*.png are 1024x1024 lossless PNGs (~2MB each) kept
    around for other uses (see _build/generate_web_portraits.py); nothing
    on-site ever displays a portrait above 140px, so the site itself should
    always prefer the resized, branded JPEG when one exists. The web JPEG is
    looked up by person_id directly rather than trusting the image2 field's
    filename, since a handful of image2 values carry a full path prefix
    instead of a bare filename (a known data-quality bug) — resolving by
    person_id sidesteps that rather than needing it fixed first.

    Tier-agnostic on purpose: stub entries never get a *generated* portrait
    (see images/portraits2/STAINED_GLASS_QUEUE.md), but if one already
    carries an image/image2 field (e.g. from before a tier change), it
    should still resolve and display rather than being silently hidden."""
    web_file = f'{person["person_id"]}.jpg'
    if (ROOT / "images" / "portraits2-web" / web_file).exists():
        return "portraits2-web", web_file
    image2 = person.get("image2")
    if image2:
        image2_file = Path(image2).name
        if (ROOT / "images" / "portraits2" / image2_file).exists():
            return "portraits2", image2_file
    image = person.get("image")
    image_file = image.get("file") if isinstance(image, dict) else None
    if image_file and (ROOT / "images" / "portraits" / image_file).exists():
        return "portraits", image_file
    return None, None


def resolve_full_portrait_file(person):
    """The larger (1024px) captioned JPEG generated alongside the inline
    thumbnail by _build/generate_web_portraits.py, used only as the
    click-to-enlarge target on a person's own detail page. Returns a bare
    filename or None — falls back to no link when a person only has a
    legacy images/portraits/ icon (hand-drawn/generic, nothing larger to
    show) rather than a portraits2-web thumbnail."""
    full_file = f'{person["person_id"]}-full.jpg'
    if (ROOT / "images" / "portraits2-web" / full_file).exists():
        return full_file
    return None


def portrait_img_html(person, base):
    """Renders an <img> for whichever portrait resolve_portrait_file finds,
    wrapped in a link to the full-size version when one exists so clicking
    the portrait opens it larger (see js/app.js's initPortraitLightbox).
    Caller must check portrait_exists first. Falls back to a plain alt text
    when there's no image.caption to draw on (stub entries never carry the
    full-tier image dict, only a bare image2 filename if one exists)."""
    portrait_dir, portrait_file = resolve_portrait_file(person)
    img_url = f'{base}images/{portrait_dir}/{esc(portrait_file)}'
    image_meta = person.get("image") if isinstance(person.get("image"), dict) else None
    caption = image_meta.get("caption") if image_meta else None
    alt = f'{esc(person["name"])} — {esc(caption)}' if caption else esc(person["name"])
    img_tag = f'<img src="{img_url}" alt="{alt}">'
    full_file = resolve_full_portrait_file(person)
    if not full_file:
        return img_tag
    full_url = f'{base}images/portraits2-web/{esc(full_file)}'
    return (
        f'<a href="{full_url}" class="portrait-lightbox" target="_blank" rel="noopener" '
        f'aria-label="View full-size image of {esc(person["name"])}">{img_tag}</a>'
    )


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
    <div class="brand-block">
      <h1><a href="{base}index.html" class="brand">
        <img src="{base}favicon.svg" class="brand-mark" alt="" width="28" height="28">
        Lives of Scripture
      </a></h1>
      <p class="brand-subtitle">Every person named in the Bible</p>
    </div>
    <button type="button" class="nav-toggle" id="nav-toggle" aria-expanded="false" aria-controls="site-nav">
      <span class="sr-only">Menu</span>
      <span class="nav-toggle__bar"></span>
      <span class="nav-toggle__bar"></span>
      <span class="nav-toggle__bar"></span>
    </button>
    <nav id="site-nav">
      {nav}
    </nav>
  </div>
</header>"""


def footer_html(base):
    return f"""<footer class="site-footer">
  <p>Lives of Scripture — a reference for every person named in the Bible. See <a href="{base}about.html">About</a> for sources and how name spelling works.</p>
  <details class="footer-notice">
    <summary>Usage &amp; licensing</summary>
    <p>No Bible verse text is quoted or stored on this site, in any translation —
    references are chapter:verse only. Genealogy data is seeded from
    <a href="https://github.com/bradystephenson/bible-data">BibleData</a> by Brady
    Stephenson (<a href="https://creativecommons.org/licenses/by/4.0/">CC BY 4.0</a>).
    Portrait illustrations are AI-generated or hand-authored line art — no claim of
    historical likeness. See <a href="{base}about.html">About</a> for full sourcing.</p>
  </details>
  <p class="footer-notice"><a href="{base}about.html#cookies-analytics" id="manage-cookie-preferences">Manage cookie preferences</a></p>
  <p class="footer-social">
    <a href="https://www.facebook.com/profile.php?id=61592929856079" target="_blank" rel="noopener noreferrer" aria-label="Lives of Scripture on Facebook"><svg viewBox="0 0 24 24" fill="none" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M15.5 8.5h-1.8c-.9 0-1.4.5-1.4 1.4V12h3.1l-.4 3h-2.7v7h-3v-7H7v-3h2.2V9.6C9.2 7 10.7 5.3 13.2 5.3h2.3v3.2z"/></svg></a>
    <a href="https://www.instagram.com/livesofscripture/" target="_blank" rel="noopener noreferrer" aria-label="Lives of Scripture on Instagram"><svg viewBox="0 0 24 24" fill="none" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="4" y="4" width="16" height="16" rx="4.5"/><circle cx="12" cy="12" r="3.6"/><circle cx="16.7" cy="7.3" r="0.9" fill="currentColor" stroke="none"/></svg></a>
  </p>
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


def references_list(refs):
    return f'<p class="references-list">References: {esc("; ".join(refs))}</p>'


def first_reference_line(person, css_class="first-reference"):
    ref = person.get("first_reference")
    if not ref:
        return ""
    return f'<p class="{css_class}">First named in {esc(ref)}</p>'


def format_bc_year(year):
    return f"{-year} BC" if year < 0 else f"AD {year}"


KINGDOM_LABELS = {"united": "the united kingdom", "israel": "Israel", "judah": "Judah"}
NATION_LABELS = {"united": "the united kingdom", "israel": "Israel", "judah": "Judah", "assyria": "Assyria"}


def reign_line(person):
    reign = person.get("reign")
    if not reign:
        return ""
    kingdom_label = KINGDOM_LABELS.get(reign.get("kingdom"), reign.get("kingdom"))
    span = f"{format_bc_year(reign['start'])}&ndash;{format_bc_year(reign['end'])}" if isinstance(reign.get("start"), int) else ""
    return f'<div class="reign-line">Reigned over {esc(kingdom_label)}, c. {span}</div>'


def prophesied_to_line(person):
    prophesied = person.get("prophesied_to")
    if not prophesied:
        return ""
    nation_label = NATION_LABELS.get(prophesied.get("nation"), prophesied.get("nation"))
    period = person.get("ministry_period") or {}
    start, end = period.get("start"), period.get("end")
    if isinstance(start, int) and isinstance(end, int):
        span = f", c. {format_bc_year(start)}&ndash;{format_bc_year(end)}"
    else:
        span = " (date disputed)"
    return f'<div class="prophesied-to-line">Prophesied to {esc(nation_label)}{span}</div>'


def connections_graph_link(person_id, base):
    return f'<p><a href="{base}connections.html?id={person_id}">View full connections graph →</a></p>'


def timeline_link(person_id, base):
    return f'<p><a href="{base}timeline.html?highlight={person_id}">See on the full timeline →</a></p>'


def gender_tag(gender):
    if gender == "male":
        return ' <span class="gender-tag gender-tag--male">(M)</span>'
    if gender == "female":
        return ' <span class="gender-tag gender-tag--female">(F)</span>'
    return ""


def connection_edge_line(edge, index_by_id, gender_by_id, base):
    from_link = (
        f'<a href="{base}people/{esc(edge["from"])}.html">{esc(index_by_id.get(edge["from"], edge["from"]))}</a>'
        f"{gender_tag(gender_by_id.get(edge['from']))}"
    )
    to_link = (
        f'<a href="{base}people/{esc(edge["to"])}.html">{esc(index_by_id.get(edge["to"], edge["to"]))}</a>'
        f"{gender_tag(gender_by_id.get(edge['to']))}"
    )
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


CHRIST_CONNECTION_LABELS = {
    "ancestor": "Ancestor of Christ",
    "family": "Family of Christ",
    "apostle": "Apostle of Christ",
    "disciple": "Disciple of Christ",
    "forerunner": "Forerunner of Christ",
    "type": "A type of Christ",
    "prophecy": "Prophesied of Christ",
    "witness": "Witness to Christ",
}


def christ_connection_lines(person):
    """Bible-explicit connections to Christ (see CLAUDE.md's Coverage and
    Two-Tier Depth section, "christ_connections reintroduced 2026-08-10").
    Rendered first in the Connections list, ahead of person-to-person edges,
    since these matter most and there are rarely more than a couple."""
    conns = person.get("christ_connections") or []
    lines = []
    for c in conns:
        label = CHRIST_CONNECTION_LABELS.get(c.get("type"), esc((c.get("type") or "").capitalize()))
        ref = c.get("reference", "")
        lines.append(f'<li class="connections-list__christ">{esc(label)} ({esc(ref)})</li>')
    return lines


def connections_section(person, index_by_id, gender_by_id, connections, base):
    pid = person["person_id"]
    related = [e for e in connections if e["from"] == pid or e["to"] == pid]
    christ_lines = christ_connection_lines(person)
    if not related and not christ_lines:
        return ""
    items = "\n    ".join(
        christ_lines + [connection_edge_line(e, index_by_id, gender_by_id, base) for e in related]
    )
    return f"""<section>
    <h3>Connections</h3>
    <ul class="connections-list">
    {items}
    </ul>
  </section>"""


def church_membership_section(person_id, membership_by_person, base):
    """Reverse lookup into data/nt_churches.json: which New Testament
    churches (if any) this person is explicitly tied to by name, per the
    Coverage section's Factual Accuracy rules -- only churches.json's own
    curated affiliations, never inferred. Renders for full and stub people
    alike, since most named church members (e.g. the Romans 16 greetings)
    are stub-tier."""
    memberships = membership_by_person.get(person_id) if membership_by_person else None
    if not memberships:
        return ""
    items = []
    for mem in memberships:
        link = f'<a href="{base}churches/{esc(mem["church_id"])}.html">{esc(mem["church_name"])}</a>'
        role = f' — {esc(mem["role"])}' if mem.get("role") else ""
        parts = [f"<li>{link}{role}"]
        if mem.get("references"):
            parts.append(f'<p class="connections-list__refs">{esc("; ".join(mem["references"]))}</p>')
        parts.append("</li>")
        items.append("\n".join(parts))
    items_html = "\n    ".join(items)
    return f"""<section>
    <h3>New Testament Church{"es" if len(memberships) != 1 else ""}</h3>
    <ul class="connections-list">
    {items_html}
    </ul>
  </section>"""


def devotional_section(person):
    devotionals = person.get("devotionals")
    if not devotionals:
        return ""
    # Static output must be reproducible so CI can detect genuinely stale files.
    # The client can still rotate devotionals dynamically; pre-render the first.
    chosen = devotionals[0]
    return f"""<section class="devotional">
    <h3>Thought for Today</h3>
    <p>{esc(chosen)}</p>
  </section>"""


def story_panel_html(version, story):
    paras = [p for p in (story or "").split("\n\n") if p.strip()]
    if not paras:
        paras = [story or ""]
    paragraphs_html = "\n      ".join(f"<p>{esc(p)}</p>" for p in paras)
    hidden = "" if version == "adult" else " hidden"
    return f"""<div class="story-panel{hidden}" data-version="{version}" role="tabpanel" aria-labelledby="tab-{version}" id="panel-{version}">
      <div class="story-text">
      {paragraphs_html}
      </div>
      <div class="story-panel-footer">
        <button class="btn-story" data-copy-version="{version}">Copy</button>
        <button class="btn-story" data-read-version="{version}" disabled>&#128266; Read Aloud</button>
      </div>
    </div>"""


def story_tabs_section(person):
    adult_panel = story_panel_html("adult", person.get("adult_story"))
    family_panel = story_panel_html("family", person.get("family_friendly_summary"))
    return f"""<div class="story-tabs-wrapper" data-person-name="{esc(person['name'])}">
    <div class="story-tabs-nav" role="tablist" aria-label="Story version">
      <button class="story-tab active" role="tab" aria-selected="true" aria-controls="panel-adult" id="tab-adult" data-version="adult">For Worship &amp; Teaching</button>
      <button class="story-tab" role="tab" aria-selected="false" aria-controls="panel-family" id="tab-family" data-version="family">Family Version</button>
    </div>
    {adult_panel}
    {family_panel}
  </div>"""


def disambiguation_section(person_name, same_name, base):
    if not same_name:
        return ""
    cards = []
    for e in same_name:
        if e["portrait_exists"]:
            img_html = f'<img src="{base}images/{e["portrait_dir"]}/{esc(e["portrait_file"])}" alt="{esc(e["name"])}">'
        else:
            img_html = '<div class="image-placeholder image-placeholder--thumb">Illustration pending</div>'
        blurb = truncate(e.get("source_summary", ""), 90)
        cards.append(f"""<a class="disambiguation-card" href="{base}people/{esc(e['person_id'])}.html">
      {img_html}
      <div class="disambiguation-card__text">
        <div class="disambiguation-card__name">{esc(e['name'])}</div>
        <div class="disambiguation-card__blurb">{esc(blurb)}</div>
      </div>
    </a>""")
    cards_html = "\n    ".join(cards)
    return f"""<section class="disambiguation">
    <h3>Other people named {esc(person_name)}</h3>
    <div class="disambiguation-grid">
    {cards_html}
    </div>
  </section>"""


def render_full_person_body(person, index_by_id, gender_by_id, connections, base, portrait_exists, full_people_by_name=None, church_membership_by_person=None):
    parts = []

    first_ref = first_reference_line(person)

    if portrait_exists:
        img_html = portrait_img_html(person, base)
    else:
        img_html = '<div class="image-placeholder">Illustration pending</div>'

    alt_html = ""
    if person.get("alt_names"):
        alt_html = f'<div class="alt-names">Also called: {esc(", ".join(person["alt_names"]))}</div>'

    name_meaning_html = ""
    name_meaning = person.get("name_meaning")
    if name_meaning and name_meaning.get("meaning"):
        language = name_meaning.get("language")
        language_suffix = f" &mdash; {esc(language)}" if language else ""
        name_meaning_html = (
            f'<div class="name-meaning">Name means &ldquo;{esc(name_meaning["meaning"])}&rdquo;'
            f"{language_suffix}</div>"
        )

    testament_class = "ot" if person.get("testament") == "OT" else "nt"
    era_badge = f'<span class="badge">{esc(person["era"])}</span>' if person.get("era") else ""

    parts.append(f"""<div class="person-header">
    <div class="person-portrait-col">
      {img_html}
    </div>
    <div class="person-title">
      <h2>{esc(person["name"])}{gender_tag(person.get("gender"))}</h2>
      {alt_html}
      {name_meaning_html}
      {reign_line(person)}
      {prophesied_to_line(person)}
      {first_ref}
      <div class="tags">
        <span class="badge {testament_class}">{esc(person.get("testament", ""))}</span>
        {era_badge}
      </div>
    </div>
  </div>""")

    parts.append(story_tabs_section(person))

    devotional = devotional_section(person)
    if devotional:
        parts.append(devotional)

    if person.get("references"):
        parts.append(references_list(person["references"]))

    parts.append(genealogy_section(person, index_by_id, base))

    conn_section = connections_section(person, index_by_id, gender_by_id, connections, base)
    if conn_section:
        parts.append(conn_section)

    church_section = church_membership_section(person["person_id"], church_membership_by_person, base)
    if church_section:
        parts.append(church_section)

    parts.append(connections_graph_link(person["person_id"], base))

    if person.get("timeline"):
        parts.append(timeline_link(person["person_id"], base))

    if full_people_by_name:
        same_name = [
            e
            for e in full_people_by_name.get(person["name"].strip().lower(), [])
            if e["person_id"] != person["person_id"]
        ]
        disamb = disambiguation_section(person["name"], same_name, base)
        if disamb:
            parts.append(disamb)

    return "\n  ".join(parts)


def render_stub_person_body(person, index_by_id, gender_by_id, connections, base, portrait_exists=False, church_membership_by_person=None):
    heading = f"<h2>{esc(person['name'])}{gender_tag(person.get('gender'))}</h2>"
    if portrait_exists:
        parts = [f"""<div class="person-header">
    <div class="person-portrait-col">
      {portrait_img_html(person, base)}
    </div>
    <div class="person-title">
      {heading}
    </div>
  </div>"""]
    else:
        parts = [heading]

    if person.get("alt_names"):
        parts.append(f'<div class="alt-names">Also called: {esc(", ".join(person["alt_names"]))}</div>')

    first_ref = first_reference_line(person)
    if first_ref:
        parts.append(first_ref)

    parts.append(
        '<div class="stub-notice">Named in Scripture, but with no narrative of their own — '
        "kept here for the connections graph.</div>"
    )

    if person.get("references"):
        parts.append(references_list(person["references"]))

    parts.append(genealogy_section(person, index_by_id, base))

    conn_section = connections_section(person, index_by_id, gender_by_id, connections, base)
    if conn_section:
        parts.append(conn_section)

    church_section = church_membership_section(person["person_id"], church_membership_by_person, base)
    if church_section:
        parts.append(church_section)

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


def build_person_page(person, index_by_id, gender_by_id, connections, full_people_by_name=None, church_membership_by_person=None):
    pid = person["person_id"]
    base = "../"
    canonical = f"{SITE_URL}/people/{pid}.html"
    portrait_dir, portrait_file = resolve_portrait_file(person)
    # Tier-agnostic: a stub never gets a *generated* portrait (see
    # images/portraits2/STAINED_GLASS_QUEUE.md), but one that already
    # carries an image/image2 field still displays it rather than hiding it.
    portrait_exists = bool(portrait_file)
    og_image = f'{SITE_URL}/images/{portrait_dir}/{portrait_file}' if portrait_exists else DEFAULT_OG_IMAGE
    description = meta_description_for(person)
    title = f'{person["name"]} — Lives of Scripture'

    if person["tier"] == "full":
        body = render_full_person_body(person, index_by_id, gender_by_id, connections, base, portrait_exists, full_people_by_name, church_membership_by_person)
    else:
        body = render_stub_person_body(person, index_by_id, gender_by_id, connections, base, portrait_exists, church_membership_by_person)

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
<script>initNavToggle();initPersonStory();initPortraitLightbox();</script>
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
    name_tag = "strong" if entry["tier"] != "stub" else "span"
    name_gender = f'<{name_tag} class="name-text">{esc(entry["name"])}</{name_tag}>{gender_tag(entry.get("gender"))}'
    disamb_html = ""
    if entry.get("disambiguation"):
        disamb_html = f'\n      <div class="disambiguation">{esc(entry["disambiguation"])}</div>'
    return f"""<a class="person-card" href="people/{entry['person_id']}.html">
      <div class="name">{name_gender}</div>{disamb_html}
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
# NT Churches — churches.html list page + churches/<id>.html detail pages
# ---------------------------------------------------------------------


def church_card_html(church):
    member_count = len(church["members"])
    count_label = f'{member_count} named {"person" if member_count == 1 else "people"}' if member_count else "no named individuals"
    return f"""<a class="person-card" href="churches/{esc(church['church_id'])}.html">
      <div class="name"><strong class="name-text">{esc(church["name"])}</strong></div>
      <div class="meta"><span class="badge nt">NT</span><span class="badge">{esc(church["region"])}</span><span class="badge">{esc(count_label)}</span></div>
    </a>"""


def build_churches_list_page(churches):
    base = ""
    canonical = f"{SITE_URL}/churches.html"
    title = "New Testament Churches — Lives of Scripture"
    description = "Every local church named in the New Testament, with the people Scripture explicitly ties to each by name and reference."
    cards = "\n    ".join(church_card_html(c) for c in sorted(churches, key=lambda c: c["name"]))

    return f"""<!DOCTYPE html>
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

<meta property="og:type" content="website">
<meta property="og:site_name" content="Lives of Scripture">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(description)}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{DEFAULT_OG_IMAGE}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{esc(title)}">
<meta name="twitter:description" content="{esc(description)}">
<meta name="twitter:image" content="{DEFAULT_OG_IMAGE}">

<link rel="stylesheet" href="{base}css/style.css">
</head>
<body>
{header_html(base, "churches.html")}

<main>
  <h2>New Testament Churches</h2>
  <p class="page-intro">Every local church named in the New Testament, from Jerusalem at Pentecost to
  the seven churches of Revelation. Click a church to see everyone Scripture explicitly ties to it by
  name — founders, hosts, elders, deacons, and members greeted by name — along with the reference that
  supports each one. A person who appears under more than one church reflects Scripture recording them
  at more than one congregation over time.</p>

  <div class="person-grid">
    {cards}
  </div>
</main>

{footer_html(base)}

<script src="{base}js/app.js"></script>
<script>initNavToggle();</script>
</body>
</html>
"""


def church_member_line_html(member, index_by_id, gender_by_id, base):
    pid = member["person_id"]
    name = index_by_id.get(pid, pid)
    link = f'<a href="{base}people/{esc(pid)}.html">{esc(name)}</a>{gender_tag(gender_by_id.get(pid))}'
    role = f' — {esc(member["role"])}' if member.get("role") else ""
    parts = [f"<li>{link}{role}"]
    if member.get("note"):
        parts.append(f'<p class="connections-list__note">{esc(member["note"])}</p>')
    if member.get("references"):
        parts.append(f'<p class="connections-list__refs">{esc("; ".join(member["references"]))}</p>')
    parts.append("</li>")
    return "\n".join(parts)


def church_json_ld(church, index_by_id, canonical):
    data = {
        "@context": "https://schema.org",
        "@type": "Organization",
        "name": f'Church at {church["name"]}',
        "url": canonical,
        "mainEntityOfPage": canonical,
        "description": church["description"],
        "isPartOf": {"@type": "WebSite", "name": "Lives of Scripture", "url": f"{SITE_URL}/"},
    }
    if church.get("references"):
        data["citation"] = church["references"]
    if church["members"]:
        data["member"] = [
            {
                "@type": "Person",
                "name": index_by_id.get(m["person_id"], m["person_id"]),
                "url": f'{SITE_URL}/people/{m["person_id"]}.html',
            }
            for m in church["members"]
        ]
    return json.dumps(data, indent=2, ensure_ascii=False)


def build_church_detail_page(church, index_by_id, gender_by_id):
    base = "../"
    church_id = church["church_id"]
    canonical = f"{SITE_URL}/churches/{church_id}.html"
    title = f'{church["name"]} — New Testament Churches — Lives of Scripture'
    description = truncate(church["description"])

    if church["members"]:
        items = "\n    ".join(church_member_line_html(m, index_by_id, gender_by_id, base) for m in church["members"])
        members_html = f"""<section>
    <h3>Named in Scripture at {esc(church["name"])}</h3>
    <ul class="connections-list">
    {items}
    </ul>
  </section>"""
    else:
        members_html = (
            '<p class="stub-notice">No individual is named by Scripture in connection with this church — '
            "it is addressed only as a congregation.</p>"
        )

    references_html = references_list(church["references"]) if church.get("references") else ""
    json_ld = church_json_ld(church, index_by_id, canonical)

    return f"""<!DOCTYPE html>
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

<meta property="og:type" content="article">
<meta property="og:site_name" content="Lives of Scripture">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(description)}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{DEFAULT_OG_IMAGE}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{esc(title)}">
<meta name="twitter:description" content="{esc(description)}">
<meta name="twitter:image" content="{DEFAULT_OG_IMAGE}">

<link rel="stylesheet" href="{base}css/style.css">
<script type="application/ld+json">
{json_ld}
</script>
</head>
<body>
{header_html(base, "churches.html")}

<main id="person-main">
  <p><a href="{base}churches.html" class="back-link">&#8592; Back to all churches</a></p>

  <div class="person-title">
    <h2>{esc(church["name"])}</h2>
    <div class="tags">
      <span class="badge nt">NT</span>
      <span class="badge">{esc(church["region"])}</span>
    </div>
  </div>

  <p>{esc(church["description"])}</p>
  {references_html}

  {members_html}
</main>

{footer_html(base)}

<script src="{base}js/app.js"></script>
<script>initNavToggle();</script>
</body>
</html>
"""


def build_church_membership_index(churches, index_by_id):
    """person_id -> list of {church_id, church_name, role, references}, the
    reverse of nt_churches.json's per-church member lists, for the "NT
    Church(es)" section rendered on a person's own page."""
    by_person = {}
    for church in churches:
        for member in church["members"]:
            by_person.setdefault(member["person_id"], []).append({
                "church_id": church["church_id"],
                "church_name": church["name"],
                "role": member.get("role"),
                "references": member.get("references", []),
            })
    return by_person


# ---------------------------------------------------------------------
# Kings & Prophets timeline chart (charts.html hub + charts/kings-and-prophets.html)
# ---------------------------------------------------------------------

KP_NATION_LABELS = {
    "united": "United Kingdom",
    "israel": "Kingdom of Israel",
    "judah": "Kingdom of Judah",
    "assyria": "Assyria",
}
KP_COLOR_VAR = {
    "united": "var(--kp-united)",
    "israel": "var(--kp-israel)",
    "judah": "var(--kp-judah)",
    "assyria": "var(--kp-assyria)",
}
KP_ROW_ORDER = ["united", "israel", "judah", "prophets"]
KP_ROW_LABELS = {
    "united": "United Kingdom (kings)",
    "israel": "Kingdom of Israel (kings)",
    "judah": "Kingdom of Judah (kings)",
    "prophets": "Prophets",
}


def collect_kings_and_prophets():
    """Scan every full-tier person file for a `reign` (a king) or
    `prophesied_to` (a prophet) field -- see _build/backfill_reigns.py and
    _build/backfill_prophets.py for how those fields are curated. Returns
    (rows, unplotted): `rows` maps each of KP_ROW_ORDER to a list of chart
    entries; `unplotted` lists prophets whose dating is too disputed to plot
    (currently just Joel -- see backfill_prophets.py's note)."""
    rows = {key: [] for key in KP_ROW_ORDER}
    unplotted = []
    people_dir = ROOT / "data" / "people"
    for path in sorted(people_dir.glob("*.json")):
        person = json.loads(path.read_text())
        pid = person["person_id"]

        reign = person.get("reign")
        if reign:
            rows[reign["kingdom"]].append({
                "person_id": pid,
                "name": person["name"],
                "kind": "king",
                "nation": reign["kingdom"],
                "start": reign["start"],
                "end": reign["end"],
                "reference": reign["reference"],
                "note": reign.get("note", ""),
            })
            continue

        prophesied = person.get("prophesied_to")
        if prophesied:
            period = person.get("ministry_period") or {}
            entry = {
                "person_id": pid,
                "name": person["name"],
                "kind": "prophet",
                "nation": prophesied["nation"],
                "start": period.get("start"),
                "end": period.get("end"),
                "reference": prophesied["reference"],
                "note": prophesied.get("note", ""),
            }
            if entry["start"] is None or entry["end"] is None:
                unplotted.append(entry)
            else:
                rows["prophets"].append(entry)

    return rows, unplotted


def kp_pack_lanes(entries):
    """Greedy interval-scheduling packer: sort by start year, place each
    entry in the first lane whose last entry already ends at or before this
    one's start -- so a straight succession (Saul's reign ending exactly
    where Ish-bosheth's begins) shares a lane and reads as one continuous
    row, while a real overlap (a co-regency like Uzziah and Jotham) forces
    the later entry into a new stacked lane instead of clipping into the
    first one -- else open a new lane."""
    lanes = []
    for entry in sorted(entries, key=lambda e: (e["start"], e["end"])):
        for lane in lanes:
            if lane[-1]["end"] <= entry["start"]:
                lane.append(entry)
                break
        else:
            lanes.append([entry])
    return lanes


def kp_format_year(year):
    return f"{-year} BC" if year < 0 else f"AD {year}"


def kp_text_width(text, font_size):
    # Rough average glyph width for the site's sans body font -- good enough
    # to lay text out at generation time, not real text measurement (there's
    # no layout engine available then).
    return len(text) * font_size * 0.56


def kp_bar_label_fits(text, width_px, font_size=10.5):
    return kp_text_width(text, font_size) + 8 <= width_px


def kp_place_callouts(entries_with_lane, get_bar_x, min_x, max_x):
    """Greedy left-to-right label layout for bars too narrow to hold their
    own name (see kp_bar_label_fits): each callout label wants to sit
    centered above its bar, but slides right just far enough to clear the
    previous label when two bars are close together in time, the same
    technique used for beeswarm/dense scatter labels. A cluster of several
    narrow bars near either edge of the chart (e.g. the last five kings of
    Judah) can cascade past that edge -- a second pass shifts the whole run
    back inside [min_x, max_x] rather than letting labels run off the
    chart. Returns a list of (lane_idx, entry, label_center_x) in the same
    order as the input."""
    font_size = 9.5
    gap = 4
    placed = []
    cursor = float("-inf")
    for lane_idx, entry in sorted(entries_with_lane, key=lambda le: get_bar_x(le[1])):
        bar_center = get_bar_x(entry)
        lw = kp_text_width(entry["name"], font_size)
        ideal_left = bar_center - lw / 2
        left = max(ideal_left, cursor + gap)
        cursor = left + lw
        placed.append([lane_idx, entry, left, lw])

    if placed:
        overflow_right = max(0.0, placed[-1][2] + placed[-1][3] - max_x)
        overflow_left = max(0.0, min_x - placed[0][2])
        shift = overflow_left - overflow_right
        if shift:
            for p in placed:
                p[2] += shift

    return [(lane_idx, entry, left + lw / 2) for lane_idx, entry, left, lw in placed]


def render_kings_and_prophets_svg(rows):
    min_year, max_year = -1060, -580
    margin_left, margin_right = 16, 16
    plot_width = 1760
    bar_h = 20
    lane_gap = 4
    row_label_h = 22
    callout_h = 20
    row_gap = 18
    tick_step = 50

    def x_of(year):
        year = max(min_year, min(max_year, year))
        return margin_left + (year - min_year) / (max_year - min_year) * plot_width

    packed_rows = {key: kp_pack_lanes(rows[key]) for key in KP_ROW_ORDER}

    # Bars too narrow for their own name (see kp_bar_label_fits) get a
    # callout label in a reserved strip above the row instead, connected to
    # their bar by a thin leader line -- otherwise a short reign like
    # Zimri's seven days would be name-less unless a reader hovers it.
    row_callouts = {}
    for key in KP_ROW_ORDER:
        needs_callout = []
        for lane_idx, lane in enumerate(packed_rows[key]):
            for entry in lane:
                bw = x_of(entry["end"]) - x_of(entry["start"])
                if not kp_bar_label_fits(entry["name"], bw):
                    needs_callout.append((lane_idx, entry))
        row_callouts[key] = (
            kp_place_callouts(
                needs_callout,
                lambda e: x_of(e["start"]) + (x_of(e["end"]) - x_of(e["start"])) / 2,
                margin_left,
                margin_left + plot_width,
            )
            if needs_callout
            else []
        )

    row_heights = {
        key: (
            row_label_h
            + (callout_h if row_callouts[key] else 0)
            + max(1, len(lanes)) * bar_h
            + max(0, len(lanes) - 1) * lane_gap
        )
        for key, lanes in packed_rows.items()
    }

    axis_h = 24
    total_h = axis_h + sum(row_heights.values()) + row_gap * (len(KP_ROW_ORDER) - 1) + 12
    total_w = margin_left + plot_width + margin_right

    parts = [
        f'<svg id="kp-chart-svg" viewBox="0 0 {total_w} {total_h}" width="{total_w}" height="{total_h}" role="img" '
        f'aria-label="Timeline of the kings of the United and Divided Monarchy and the prophets active in the same period" '
        f'xmlns="http://www.w3.org/2000/svg" class="kp-chart-svg">'
    ]

    # Year gridlines + axis labels, spanning the full plot height.
    first_tick = min_year - (min_year % tick_step)
    y_axis_top = axis_h
    y_axis_bottom = total_h - 4
    tick = first_tick
    while tick <= max_year:
        if min_year <= tick <= max_year:
            tx = x_of(tick)
            parts.append(
                f'<line x1="{tx:.1f}" y1="{y_axis_top}" x2="{tx:.1f}" y2="{y_axis_bottom}" class="kp-gridline" />'
            )
            parts.append(
                f'<text x="{tx:.1f}" y="14" class="kp-axis-label" text-anchor="middle">{esc(kp_format_year(tick))}</text>'
            )
        tick += tick_step

    y = axis_h
    for key in KP_ROW_ORDER:
        lanes = packed_rows[key]
        callouts = row_callouts[key]
        parts.append(
            f'<text x="{margin_left}" y="{y + 14}" class="kp-row-label">{esc(KP_ROW_LABELS[key])}</text>'
        )
        lanes_top = y + row_label_h + (callout_h if callouts else 0)

        # Compute each bar's geometry up front so the callout leader lines
        # (drawn next, reaching down into the lanes) know where to land.
        bar_geometry = {}
        lane_y = lanes_top
        for lane_idx, lane in enumerate(lanes):
            for entry in lane:
                bx = x_of(entry["start"])
                bw = max(2.0, x_of(entry["end"]) - bx)
                bar_geometry[entry["person_id"]] = (bx, bw, lane_y)
            lane_y += bar_h + lane_gap

        for lane in lanes:
            for entry in lane:
                bx, bw, ly = bar_geometry[entry["person_id"]]
                color = KP_COLOR_VAR[entry["nation"]]
                title = (
                    f'{entry["name"]} — {KP_NATION_LABELS.get(entry["nation"], entry["nation"])}, '
                    f'c. {kp_format_year(entry["start"])}–{kp_format_year(entry["end"])} ({entry["reference"]})'
                )
                href = f'people/{entry["person_id"]}.html'
                parts.append(f'<a href="{href}">')
                parts.append(
                    f'<rect x="{bx:.1f}" y="{ly:.1f}" width="{bw:.1f}" height="{bar_h}" rx="4" '
                    f'fill="{color}" class="kp-bar" tabindex="0" '
                    f'data-name="{esc(entry["name"])}" data-nation="{esc(KP_NATION_LABELS.get(entry["nation"], entry["nation"]))}" '
                    f'data-span="c. {esc(kp_format_year(entry["start"]))}–{esc(kp_format_year(entry["end"]))}" '
                    f'data-reference="{esc(entry["reference"])}">'
                    f'<title>{esc(title)}</title></rect>'
                )
                if kp_bar_label_fits(entry["name"], bw):
                    parts.append(
                        f'<text x="{bx + bw / 2:.1f}" y="{ly + bar_h / 2 + 3.5:.1f}" '
                        f'class="kp-bar-label" text-anchor="middle">{esc(entry["name"])}</text>'
                    )
                parts.append("</a>")

        # Callout labels + leader lines, drawn after the bars so they sit on
        # top and are never hidden behind an adjacent bar.
        label_y = y + row_label_h + callout_h - 7
        for lane_idx, entry, label_cx in callouts:
            bx, bw, ly = bar_geometry[entry["person_id"]]
            bar_cx = bx + bw / 2
            parts.append(f'<line x1="{label_cx:.1f}" y1="{label_y + 3:.1f}" x2="{bar_cx:.1f}" y2="{ly:.1f}" class="kp-leader-line" />')
            parts.append(
                f'<text x="{label_cx:.1f}" y="{label_y:.1f}" class="kp-callout-label" text-anchor="middle">{esc(entry["name"])}</text>'
            )

        y += row_heights[key] + row_gap

    parts.append("</svg>")
    return "\n".join(parts)


def render_kings_and_prophets_table(rows, unplotted):
    all_entries = []
    for key in KP_ROW_ORDER:
        all_entries.extend(rows[key])
    all_entries.sort(key=lambda e: (e["start"], e["name"]))

    def row_html(e, disputed=False):
        span = "Date disputed" if disputed else f'c. {esc(kp_format_year(e["start"]))}&ndash;{esc(kp_format_year(e["end"]))}'
        return (
            f'<tr><td><a href="people/{e["person_id"]}.html">{esc(e["name"])}</a></td>'
            f'<td>{"King" if e["kind"] == "king" else "Prophet"}</td>'
            f'<td>{esc(KP_NATION_LABELS.get(e["nation"], e["nation"]))}</td>'
            f'<td>{span}</td>'
            f'<td>{esc(e["reference"])}</td></tr>'
        )

    body_rows = "\n    ".join(row_html(e) for e in all_entries)
    body_rows += "\n    " + "\n    ".join(row_html(e, disputed=True) for e in unplotted)

    return f"""<details class="kp-table-details">
    <summary>View as a table</summary>
    <div class="table-scroll">
    <table class="kp-table">
      <thead><tr><th>Name</th><th>Role</th><th>Kingdom / nation</th><th>Dates</th><th>Reference</th></tr></thead>
      <tbody>
    {body_rows}
      </tbody>
    </table>
    </div>
  </details>"""


def render_kings_and_prophets_legend():
    items = "\n    ".join(
        f'<span class="kp-legend-item"><span class="kp-legend-swatch" style="background:{KP_COLOR_VAR[key]}"></span>{esc(label)}</span>'
        for key, label in KP_NATION_LABELS.items()
    )
    return f'<div class="kp-legend">{items}</div>'


def build_charts_list_page():
    base = ""
    canonical = f"{SITE_URL}/charts.html"
    title = "Charts — Lives of Scripture"
    description = "Visual charts across the whole dataset, starting with the kings of Israel and Judah and the prophets active in their reigns."

    return f"""<!DOCTYPE html>
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

<meta property="og:type" content="website">
<meta property="og:site_name" content="Lives of Scripture">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(description)}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{DEFAULT_OG_IMAGE}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{esc(title)}">
<meta name="twitter:description" content="{esc(description)}">
<meta name="twitter:image" content="{DEFAULT_OG_IMAGE}">

<link rel="stylesheet" href="{base}css/style.css">
</head>
<body>
{header_html(base, "charts.html")}

<main>
  <h2>Charts</h2>
  <p class="page-intro">Visual charts across the whole dataset. Starting with one: the kings of the
  United and Divided Monarchy alongside the prophets active in the same period.</p>

  <div class="person-grid">
    <a class="person-card" href="{base}charts/kings-and-prophets.html">
      <div class="name"><strong>Kings &amp; Prophets of the Monarchy</strong></div>
      <p class="chart-card-desc">Every king of the United Kingdom, Israel, and Judah, and every prophet
      active in that period, laid out on one timeline.</p>
    </a>
  </div>
</main>

{footer_html(base)}

<script src="{base}js/app.js"></script>
<script>initNavToggle();</script>
</body>
</html>
"""


def build_kings_and_prophets_chart_page(rows, unplotted):
    base = "../"
    canonical = f"{SITE_URL}/charts/kings-and-prophets.html"
    title = "Kings & Prophets of the Monarchy — Lives of Scripture"
    description = "The kings of the United Kingdom, Israel, and Judah, and the prophets active in their reigns, on one timeline."

    svg = render_kings_and_prophets_svg(rows)
    legend = render_kings_and_prophets_legend()
    table = render_kings_and_prophets_table(rows, unplotted)

    unplotted_html = ""
    if unplotted:
        items = "\n      ".join(
            f'<li><a href="{base}people/{e["person_id"]}.html">{esc(e["name"])}</a> &mdash; {esc(e["note"])}</li>'
            for e in unplotted
        )
        unplotted_html = f"""<div class="kp-unplotted">
      <p>Not plotted (disputed dating):</p>
      <ul>
      {items}
      </ul>
    </div>"""

    return f"""<!DOCTYPE html>
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

<meta property="og:type" content="website">
<meta property="og:site_name" content="Lives of Scripture">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(description)}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{DEFAULT_OG_IMAGE}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{esc(title)}">
<meta name="twitter:description" content="{esc(description)}">
<meta name="twitter:image" content="{DEFAULT_OG_IMAGE}">

<link rel="stylesheet" href="{base}css/style.css">
</head>
<body>
{header_html(base, "charts.html")}

<main>
  <p><a href="{base}charts.html">&larr; Charts</a></p>
  <h2>Kings &amp; Prophets of the Monarchy</h2>
  <p class="page-intro">Every king of the United Kingdom, the Kingdom of Israel, and the Kingdom of
  Judah, alongside every prophet active in that period and the kingdom or nation each one addressed.
  Bars are clickable and link to that person's page; hover or focus a bar for exact dates.</p>

  <p class="kp-disclaimer">Reign and ministry years follow a single widely-used evangelical regnal
  chronology (the Thiele/synchronistic framework already used elsewhere on this site &mdash; see e.g.
  <a href="{base}people/david.html">David's</a> page), marked &ldquo;c.&rdquo; throughout. Other
  evangelical chronological frameworks shift several of these dates, especially where a co-regency is
  involved (Uzziah/Jotham, Amaziah/Uzziah, Hezekiah/Manasseh). Every entry cites the verse stating its
  reign length or ministry's dating; hover, focus, or open the table below for the reference.</p>

  <div class="kp-legend-row">
    {legend}
    <button type="button" class="kp-chart-expand" id="kp-chart-expand">&#128269; View larger</button>
  </div>

  <div class="kp-chart-scroll">
  {svg}
  </div>

  {table}

  {unplotted_html}
</main>

{footer_html(base)}

<script src="{base}js/app.js"></script>
<script>initNavToggle(); initKpChartTooltips(); initKpChartLightbox();</script>
</body>
</html>
"""


# ---------------------------------------------------------------------
# sitemap.xml
# ---------------------------------------------------------------------


def build_sitemap(index, churches):
    urls = [
        (f"{SITE_URL}/", "weekly", "1.0"),
        (f"{SITE_URL}/people.html", "weekly", "0.9"),
        (f"{SITE_URL}/timeline.html", "monthly", "0.6"),
        (f"{SITE_URL}/connections.html", "monthly", "0.6"),
        (f"{SITE_URL}/churches.html", "monthly", "0.6"),
        (f"{SITE_URL}/charts.html", "monthly", "0.6"),
        (f"{SITE_URL}/charts/kings-and-prophets.html", "monthly", "0.6"),
        (f"{SITE_URL}/quiz.html", "monthly", "0.5"),
        (f"{SITE_URL}/about.html", "monthly", "0.4"),
    ]
    for entry in index:
        priority = "0.8" if entry["tier"] == "full" else "0.3"
        urls.append((f'{SITE_URL}/people/{entry["person_id"]}.html', "monthly", priority))
    for church in churches:
        urls.append((f'{SITE_URL}/churches/{church["church_id"]}.html', "monthly", "0.6"))

    entries = "\n".join(
        f"  <url>\n    <loc>{loc}</loc>\n"
        f"    <changefreq>{freq}</changefreq>\n    <priority>{prio}</priority>\n  </url>"
        for loc, freq, prio in urls
    )
    sitemap = f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{entries}\n</urlset>\n'
    (ROOT / "sitemap.xml").write_text(sitemap)


# ---------------------------------------------------------------------


def build_full_people_by_name(index):
    """Full-tier people ("major people... with a description") grouped by
    exact name match, so a person's page can point to other full entries
    sharing their name (e.g. the several Jehoshaphats, Jehus, and Zechariahs
    in the underlying genealogy dataset) instead of leaving the reader to
    guess which one is meant."""
    by_name = {}
    for entry in index:
        if entry["tier"] != "full":
            continue
        pid = entry["person_id"]
        person_path = ROOT / "data" / "people" / f"{pid}.json"
        if not person_path.exists():
            continue
        fp = json.loads(person_path.read_text())
        portrait_dir, portrait_file = resolve_portrait_file(fp)
        by_name.setdefault(fp["name"].strip().lower(), []).append({
            "person_id": pid,
            "name": fp["name"],
            "source_summary": fp.get("source_summary", ""),
            "portrait_dir": portrait_dir,
            "portrait_file": portrait_file,
            "portrait_exists": bool(portrait_file),
        })
    return by_name


def main():
    index = json.loads((ROOT / "data" / "people.json").read_text())
    connections = json.loads((ROOT / "data" / "connections.json").read_text())
    churches = json.loads((ROOT / "data" / "nt_churches.json").read_text())["churches"]
    index_by_id = {e["person_id"]: e["name"] for e in index}
    gender_by_id = {e["person_id"]: e.get("gender") for e in index}
    full_people_by_name = build_full_people_by_name(index)
    church_membership_by_person = build_church_membership_index(churches, index_by_id)

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
        page = build_person_page(person, index_by_id, gender_by_id, connections, full_people_by_name, church_membership_by_person)
        (people_dir / f"{pid}.html").write_text(page)
        generated += 1

    update_people_grid(index)

    churches_dir = ROOT / "churches"
    churches_dir.mkdir(exist_ok=True)
    for church in churches:
        page = build_church_detail_page(church, index_by_id, gender_by_id)
        (churches_dir / f'{church["church_id"]}.html').write_text(page)
    (ROOT / "churches.html").write_text(build_churches_list_page(churches))

    charts_dir = ROOT / "charts"
    charts_dir.mkdir(exist_ok=True)
    kp_rows, kp_unplotted = collect_kings_and_prophets()
    (charts_dir / "kings-and-prophets.html").write_text(build_kings_and_prophets_chart_page(kp_rows, kp_unplotted))
    (ROOT / "charts.html").write_text(build_charts_list_page())

    build_sitemap(index, churches)

    print(f"Generated {generated} person pages, {len(churches)} church pages, sitemap.xml, and people.html/churches.html/charts.html static output.")


if __name__ == "__main__":
    main()
