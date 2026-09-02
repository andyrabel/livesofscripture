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
import math
import re
from pathlib import Path

import link_person_mentions

ROOT = Path(__file__).resolve().parent.parent
SITE_URL = "https://livesofscripture.org"
DEFAULT_OG_IMAGE = f"{SITE_URL}/images/social/og-image.png"
NAV_PAGES = [
    ("index.html", "Home"),
    ("people.html", "People"),
    ("timeline.html", "Timeline"),
    ("connections.html", "Connections"),
    ("churches.html", "Churches"),
    ("places.html", "Places"),
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
    Caller must check portrait_exists first.

    A person with a unique stained-glass portrait (portraits2-web) gets a
    name-specific alt text — built from the person's name rather than the
    stored image.caption field, which for anyone who moved from a shared
    generic icon to a stained-glass portrait still holds the old
    generic-icon wording (e.g. "Generic line-art icon for figures...").
    That stale text would misdescribe the actual displayed image and give
    Google Images no person-specific signal for this page. Anyone still on
    a shared generic/legacy icon keeps the old image.caption-based alt
    text, since that image genuinely isn't unique to them."""
    portrait_dir, portrait_file = resolve_portrait_file(person)
    img_url = f'{base}images/{portrait_dir}/{esc(portrait_file)}'
    full_file = resolve_full_portrait_file(person)
    if full_file:
        alt = esc(f'{person["name"]} — stained-glass style portrait')
    else:
        image_meta = person.get("image") if isinstance(person.get("image"), dict) else None
        caption = image_meta.get("caption") if image_meta else None
        alt = f'{esc(person["name"])} — {esc(caption)}' if caption else esc(person["name"])
    img_tag = f'<img src="{img_url}" alt="{alt}">'
    if not full_file:
        return img_tag
    full_url = f'{base}images/portraits2-web/{esc(full_file)}'
    linked_img = (
        f'<a href="{full_url}" class="portrait-lightbox" target="_blank" rel="noopener" '
        f'aria-label="View full-size image of {esc(person["name"])}">{img_tag}</a>'
    )
    return linked_img


def resolve_church_photo(church_id):
    """True when a web-optimized NT church group photo exists (see
    _build/generate_church_web_images.py, images/nt_churches-web/), which
    mirrors resolve_full_portrait_file's "not every entry has generated
    art yet" tolerance for churches whose group photo hasn't been
    generated."""
    return (ROOT / "images" / "nt_churches-web" / f"{church_id}.jpg").exists()


def church_photo_html(church, base):
    """Renders the church's group photo linked to its full-size version,
    same click-to-enlarge lightbox pattern as portrait_img_html (see
    js/app.js's initPortraitLightbox)."""
    church_id = church["church_id"]
    name = church["name"]
    thumb_url = f'{base}images/nt_churches-web/{esc(church_id)}.jpg'
    full_url = f'{base}images/nt_churches-web/{esc(church_id)}-full.jpg'
    alt = esc(f'The church in {name} — stained-glass style group portrait')
    img_tag = f'<img src="{thumb_url}" alt="{alt}" class="church-photo">'
    return (
        f'<a href="{full_url}" class="portrait-lightbox church-photo-link" target="_blank" rel="noopener" '
        f'aria-label="View full-size image of the church in {esc(name)}">{img_tag}</a>'
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
      <p class="brand-subtitle">A reference for every person named in the Bible</p>
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


def story_panel_html(version, story, link_ctx=None, subject_id=None, base=""):
    paras = [p for p in (story or "").split("\n\n") if p.strip()]
    if not paras:
        paras = [story or ""]
    # First mention of a given person is linked once per panel.
    linked_pids = set()
    paragraphs_html = "\n      ".join(
        f"<p>{link_person_mentions.link_paragraph(p, subject_id, link_ctx, base, linked_pids)}</p>"
        for p in paras
    )
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


def story_tabs_section(person, link_ctx=None, base=""):
    subject_id = person["person_id"]
    adult_panel = story_panel_html("adult", person.get("adult_story"), link_ctx, subject_id, base)
    family_panel = story_panel_html("family", person.get("family_friendly_summary"), link_ctx, subject_id, base)
    return f"""<div class="story-tabs-wrapper" data-person-name="{esc(person['name'])}">
    <div class="story-tabs-nav" role="tablist" aria-label="Story version">
      <button class="story-tab active" role="tab" aria-selected="true" aria-controls="panel-adult" id="tab-adult" data-version="adult">For Worship &amp; Teaching</button>
      <button class="story-tab" role="tab" aria-selected="false" aria-controls="panel-family" id="tab-family" data-version="family">Family Version</button>
    </div>
    {adult_panel}
    {family_panel}
  </div>"""


_NAME_QUALIFIER_RE = re.compile(r"^(.*?)\s+of\s+.+$", re.IGNORECASE)


def name_grouping_key(name):
    """Base name used to group namesakes for disambiguation, stripping a
    trailing " of <Place>" epithet (e.g. "Hiram of Tyre" -> "Hiram") so a
    person whose canonical name bakes in that epithet still groups with a
    bare-named namesake (e.g. Eliezer/Eliezer of Damascus, Judas/Judas of
    Galilee, Lucius/Lucius of Cyrene) instead of the exact-name match
    silently missing them, per the "Known gap" pattern in CLAUDE.md."""
    stripped = name.strip()
    m = _NAME_QUALIFIER_RE.match(stripped)
    return m.group(1).strip() if m else stripped


def disambiguation_section(person_name, same_name, base):
    if not same_name:
        return ""
    cards = []
    for e in same_name:
        if e["portrait_exists"]:
            img_html = f'<img src="{base}images/{e["portrait_dir"]}/{esc(e["portrait_file"])}" alt="{esc(e["name"])}">'
        else:
            img_html = '<div class="image-placeholder image-placeholder--thumb">Illustration pending</div>'
        if e["tier"] == "stub":
            name_badge = ' <span class="badge stub">name only</span>'
            blurb = f'Named in Scripture ({e["first_reference"]}) -- no narrative of their own' if e.get("first_reference") else "Named in Scripture -- no narrative of their own"
        else:
            name_badge = ""
            blurb = e.get("source_summary", "")
        blurb = truncate(blurb, 90)
        cards.append(f"""<a class="disambiguation-card" href="{base}people/{esc(e['person_id'])}.html">
      {img_html}
      <div class="disambiguation-card__text">
        <div class="disambiguation-card__name">{esc(e['name'])}{name_badge}</div>
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


def render_full_person_body(person, index_by_id, gender_by_id, connections, base, portrait_exists, people_by_name=None, church_membership_by_person=None, link_ctx=None, place_membership_by_person=None):
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

    parts.append(story_tabs_section(person, link_ctx, base))

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

    places_sec = places_section(person["person_id"], place_membership_by_person, base)
    if places_sec:
        parts.append(places_sec)

    parts.append(connections_graph_link(person["person_id"], base))

    if person.get("timeline"):
        parts.append(timeline_link(person["person_id"], base))

    if people_by_name:
        group_key = name_grouping_key(person["name"])
        same_name = [
            e
            for e in people_by_name.get(group_key.lower(), [])
            if e["person_id"] != person["person_id"]
        ]
        disamb = disambiguation_section(group_key, same_name, base)
        if disamb:
            parts.append(disamb)

    return "\n  ".join(parts)


def render_stub_person_body(person, index_by_id, gender_by_id, connections, base, portrait_exists=False, church_membership_by_person=None, people_by_name=None):
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

    if people_by_name:
        group_key = name_grouping_key(person["name"])
        same_name = [
            e
            for e in people_by_name.get(group_key.lower(), [])
            if e["person_id"] != person["person_id"]
        ]
        disamb = disambiguation_section(group_key, same_name, base)
        if disamb:
            parts.append(disamb)

    return "\n  ".join(parts)


def meta_description_for(person):
    if person["tier"] == "full" and person.get("source_summary"):
        return truncate(person["source_summary"])
    refs = "; ".join(person.get("references", []))
    text = f"{person['name']} is named in Scripture ({refs}) — see how they connect in the genealogy graph."
    return truncate(text)


def breadcrumb_json_ld(items):
    """items: list of (name, url_or_None) tuples, in order from the site
    root to the current page. The current (last) page's url is normally
    None — Google's breadcrumb guidance doesn't require an item URL for the
    final crumb since it's the page the breadcrumb is already on."""
    element_list = []
    for position, (name, url) in enumerate(items, start=1):
        entry = {"@type": "ListItem", "position": position, "name": name}
        if url:
            entry["item"] = url
        element_list.append(entry)
    data = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": element_list,
    }
    return json.dumps(data, indent=2, ensure_ascii=False)


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
        # Structured ImageObject (contentUrl + caption) only for the unique
        # stained-glass portrait — Google's image-SEO guidance uses this
        # metadata to attribute an image to a specific page. A shared
        # generic/legacy icon isn't unique to this person, so it keeps the
        # plain image-URL form instead of a person-specific caption claim.
        if resolve_full_portrait_file(person):
            data["image"] = {
                "@type": "ImageObject",
                "contentUrl": og_image,
                "url": og_image,
                "caption": f'{person["name"]} — stained-glass style portrait',
            }
        else:
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


def build_person_page(person, index_by_id, gender_by_id, connections, people_by_name=None, church_membership_by_person=None, link_ctx=None, place_membership_by_person=None):
    pid = person["person_id"]
    base = "../"
    canonical = f"{SITE_URL}/people/{pid}.html"
    portrait_dir, portrait_file = resolve_portrait_file(person)
    # Tier-agnostic: a stub never gets a *generated* portrait (see
    # images/portraits2/STAINED_GLASS_QUEUE.md), but one that already
    # carries an image/image2 field still displays it rather than hiding it.
    portrait_exists = bool(portrait_file)
    # Prefer the larger 1024x1024 stained-glass version for og:image/JSON-LD
    # over the 500x500 on-page thumbnail — Google Images and social-card
    # unfurls both favor a higher-resolution source, and this file already
    # exists solely for the click-to-enlarge lightbox, so this is free.
    full_file = resolve_full_portrait_file(person)
    if full_file:
        og_image = f'{SITE_URL}/images/portraits2-web/{full_file}'
    elif portrait_exists:
        og_image = f'{SITE_URL}/images/{portrait_dir}/{portrait_file}'
    else:
        og_image = DEFAULT_OG_IMAGE
    description = meta_description_for(person)
    title = f'{person["name"]} — Lives of Scripture'

    if person["tier"] == "full":
        body = render_full_person_body(person, index_by_id, gender_by_id, connections, base, portrait_exists, people_by_name, church_membership_by_person, link_ctx, place_membership_by_person)
    else:
        body = render_stub_person_body(person, index_by_id, gender_by_id, connections, base, portrait_exists, church_membership_by_person, people_by_name)

    json_ld = person_json_ld(person, index_by_id, SITE_URL, canonical, og_image, portrait_exists)
    breadcrumb_ld = breadcrumb_json_ld([
        ("Home", f"{SITE_URL}/"),
        ("People", f"{SITE_URL}/people.html"),
        (person["name"], None),
    ])
    # Stub entries are single-reference genealogy listings with no
    # narrative — real content for the connections graph, but too thin to
    # ask Google to index 2,000+ of as standalone search results. Keeping
    # them "follow" (not "nofollow") still lets crawlers reach every page
    # through the genealogy links, just without indexing each one.
    robots_meta = (
        '<meta name="robots" content="noindex, follow">\n' if person["tier"] != "full" else ""
    )

    html_out = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(title)}</title>
<meta name="description" content="{esc(description)}">
<link rel="canonical" href="{canonical}">
{robots_meta}
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
<script type="application/ld+json">
{breadcrumb_ld}
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
    breadcrumb_ld = breadcrumb_json_ld([("Home", f"{SITE_URL}/"), ("Churches", None)])

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
<script type="application/ld+json">
{breadcrumb_ld}
</script>
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
    breadcrumb_ld = breadcrumb_json_ld([
        ("Home", f"{SITE_URL}/"),
        ("Churches", f"{SITE_URL}/churches.html"),
        (church["name"], None),
    ])

    photo_exists = resolve_church_photo(church_id)
    photo_html = f'<div class="church-photo-wrap">{church_photo_html(church, base)}</div>' if photo_exists else ""
    og_image = f'{SITE_URL}/images/nt_churches-web/{church_id}-full.jpg' if photo_exists else DEFAULT_OG_IMAGE
    lightbox_script = "initPortraitLightbox();" if photo_exists else ""

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
<meta property="og:image" content="{og_image}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{esc(title)}">
<meta name="twitter:description" content="{esc(description)}">
<meta name="twitter:image" content="{og_image}">

<link rel="stylesheet" href="{base}css/style.css">
<script type="application/ld+json">
{json_ld}
</script>
<script type="application/ld+json">
{breadcrumb_ld}
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

  {photo_html}

  <p>{esc(church["description"])}</p>
  {references_html}

  {members_html}
</main>

{footer_html(base)}

<script src="{base}js/app.js"></script>
<script>initNavToggle();{lightbox_script}</script>
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
# Places — places.html list page + places/<id>.html detail pages
#
# Data comes from data/places-index.json + data/places/<id>.json, both
# built by _build/generate_places.py from data/people/*.json's curated
# geographic_setting field plus _build/places_data.py's hand-curated
# content. Re-run generate_places.py (before this script) whenever either
# input changes. See CLAUDE.md's Places section.
# ---------------------------------------------------------------------

PLACE_TYPE_LABELS = {
    "nation": "Nation", "region": "Region", "city": "City", "town": "Town",
    "village": "Village", "mountain": "Mountain", "wilderness": "Wilderness",
    "valley": "Valley", "body-of-water": "Body of Water", "site": "Site",
}


def place_type_label(place_type):
    return PLACE_TYPE_LABELS.get(place_type, place_type.replace("-", " ").title())


def place_region_label(region):
    return region.replace("-", " ").title()


def build_place_membership_index(places_index):
    """person_id -> list of {place_id, place_name}, the reverse of each
    place's related_people list, for the "Places" section rendered on a
    person's own page. Sourced from data/places/<id>.json rather than
    data/place-connections.json so it stays in lockstep with each place's
    own curated related_people list (identical data, this just avoids a
    second file read per person)."""
    by_person = {}
    for entry in places_index:
        place_path = ROOT / "data" / "places" / f"{entry['place_id']}.json"
        if not place_path.exists():
            continue
        place = json.loads(place_path.read_text())
        for rp in place.get("related_people", []):
            by_person.setdefault(rp["person_id"], []).append({
                "place_id": place["place_id"],
                "place_name": place["name"],
                "role": rp.get("role"),
                "references": rp.get("references") or [],
            })
    return by_person


def places_section(person_id, place_membership_by_person, base):
    memberships = place_membership_by_person.get(person_id) if place_membership_by_person else None
    if not memberships:
        return ""
    lis = []
    for m in memberships:
        li = [f'<li><a href="{base}places/{esc(m["place_id"])}.html">{esc(m["place_name"])}</a>']
        if m.get("role"):
            li.append(f' — {esc(m["role"])}')
        if m.get("references"):
            li.append(f'<p class="connections-list__refs">{esc("; ".join(m["references"]))}</p>')
        li.append("</li>")
        lis.append("".join(li))
    items = "\n    ".join(lis)
    return f"""<section>
    <h3>Places</h3>
    <ul class="connections-list">
    {items}
    </ul>
    <p><a href="{base}place-connections.html?id={esc(person_id)}">View on the place connections graph &#8594;</a></p>
  </section>"""


def build_places_by_name(places_index):
    """Every place grouped by exact name match, for the "Other places named
    X" grid -- mirrors build_people_by_name. Expected to rarely produce a
    group of 2+ today: the geographic_setting normalization pass in
    generate_places.py already resolved every known same-name collision
    (Bethlehem, Mizpah, Gilgal, Antioch, Caesarea, Carmel, Kadesh/Kedesh)
    into one canonical entry with an identification-note caveat, rather
    than split entries. Kept so the mechanism is ready if that changes."""
    by_name = {}
    for entry in places_index:
        by_name.setdefault(entry["name"].strip().lower(), []).append(entry)
    return by_name


def place_disambiguation_section(place_name, same_name, base):
    if not same_name:
        return ""
    cards = []
    for e in same_name:
        blurb = f"{place_type_label(e['type'])} — {place_region_label(e['region'])}"
        cards.append(f"""<a class="disambiguation-card" href="{base}places/{esc(e['place_id'])}.html">
      <div class="image-placeholder image-placeholder--thumb">{esc(place_type_label(e["type"])[:1])}</div>
      <div class="disambiguation-card__text">
        <div class="disambiguation-card__name">{esc(e['name'])}</div>
        <div class="disambiguation-card__blurb">{esc(blurb)}</div>
      </div>
    </a>""")
    cards_html = "\n    ".join(cards)
    return f"""<section class="disambiguation">
    <h3>Other places named {esc(place_name)}</h3>
    <div class="disambiguation-grid">
    {cards_html}
    </div>
  </section>"""


def _place_person_link(p, base):
    return (f'<a href="{base}people/{esc(p["person_id"])}.html">{esc(p["name"])}</a>'
            f'{gender_tag(p.get("gender"))}')


def place_related_people_html(place, gender_by_id, base):
    people = place.get("related_people", [])
    if not people:
        return '<p class="stub-notice">No full-tier person is named in Scripture at this place — kept here for the connections graph.</p>'

    # People with a curated place-specific blurb (see _build/place_people_roles.py)
    # render like church members — name, a short note on what Scripture ties them
    # to this place, and the reference. The rest (and, on the largest places,
    # everyone past the most significant figures) fall to a plain name list.
    with_role = [p for p in people if p.get("role")]
    without_role = [p for p in people if not p.get("role")]

    if not with_role:
        items = "\n    ".join(f'<li>{_place_person_link(p, base)}</li>' for p in people)
        return f'<ul class="connections-list">\n    {items}\n    </ul>'

    lis = []
    for p in with_role:
        li = [f'<li>{_place_person_link(p, base)} — {esc(p["role"])}']
        if p.get("references"):
            li.append(f'<p class="connections-list__refs">{esc("; ".join(p["references"]))}</p>')
        li.append("</li>")
        lis.append("\n".join(li))
    html_out = '<ul class="connections-list">\n    ' + "\n    ".join(lis) + "\n    </ul>"

    if without_role:
        links = ", ".join(_place_person_link(p, base) for p in without_role)
        html_out += (f'\n  <p class="place-people-more">Also named in Scripture at '
                     f'{esc(place["name"])}: {links}.</p>')
    return html_out


def place_identification_html(place):
    ident = place.get("identification") or {}
    status = ident.get("status", "secure")
    note = ident.get("note", "")
    if status == "secure" or not note:
        return ""
    status_labels = {
        "traditional": "Traditional identification",
        "disputed": "Disputed identification",
        "unknown": "Location uncertain",
    }
    label = status_labels.get(status, "Identification note")
    return f'<div class="identification-note"><strong>{esc(label)}:</strong> {esc(note)}</div>'


def place_json_ld(place, canonical):
    data = {
        "@context": "https://schema.org",
        "@type": "Place",
        "name": place["name"],
        "url": canonical,
        "description": place.get("description", "")[:300],
    }
    if place.get("alt_names"):
        data["alternateName"] = place["alt_names"]
    return json.dumps(data, indent=2)


def place_card_html(entry):
    count_label = f'{entry["n_people"]} named {"person" if entry["n_people"] == 1 else "people"}' if entry["n_people"] else "no named people"
    name_html = f'<strong class="name-text">{esc(entry["name"])}</strong>' if entry["tier"] == "full" else f'<span class="name-text">{esc(entry["name"])}</span>'
    disamb_html = f'\n      <div class="disambiguation">{esc(entry["disambiguation"])}</div>' if entry.get("disambiguation") else ""
    stub_badge = ' <span class="badge stub">name only</span>' if entry["tier"] == "stub" else ""
    stub_cls = " place-card--stub" if entry["tier"] == "stub" else ""
    return f"""<a class="person-card{stub_cls}" href="places/{esc(entry['place_id'])}.html">
      <div class="name">{name_html}{stub_badge}</div>{disamb_html}
      <div class="meta"><span class="badge">{esc(place_type_label(entry["type"]))}</span><span class="badge">{esc(count_label)}</span></div>
    </a>"""


def build_places_list_page(places_index):
    base = ""
    canonical = f"{SITE_URL}/places.html"
    title = "Places — Lives of Scripture"
    description = "Every named place in Scripture with a documented connection to a person's story — cities, regions, mountains, and more — cross-linked to the people found there."
    full = [e for e in places_index if e["tier"] == "full"]
    stub = [e for e in places_index if e["tier"] == "stub"]
    # All places render into the grid, sorted alphabetically; the name-only
    # (stub) cards carry .place-card--stub and are hidden by CSS until the
    # "Include name-only places" checkbox toggles .show-stub-places on the grid.
    cards = "\n    ".join(
        place_card_html(e) for e in sorted(places_index, key=lambda e: (e["name"], e["place_id"]))
    )
    breadcrumb_ld = breadcrumb_json_ld([("Home", f"{SITE_URL}/"), ("Places", None)])

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
<script type="application/ld+json">
{breadcrumb_ld}
</script>
</head>
<body>
{header_html(base, "places.html")}

<main>
  <p><a href="people.html" class="back-link">&#8592; Back to all people</a></p>

  <h2>Places</h2>
  <p class="page-intro">Every named place in Scripture with a documented connection to a person's
  story — cities, regions, mountains, wildernesses, and more. Click a place to see who Scripture
  ties to it, the reference where it's first named, and (where relevant) how confidently it can be
  identified with a location on today's map. By default this list shows the {len(full)} places
  with a narrative of their own; tick the box below to also fold in the {len(stub)} name-only
  places (mentioned in Scripture but with no story here, kept for the connections graph).
  Prefer a visual web? Explore the <a href="place-connections.html">place connections graph</a>,
  or plot places on a map in the <a href="map.html">map explorer</a>.</p>

  <div class="controls">
    <label class="controls__checkbox">
      <input type="checkbox" id="places-include-stubs">
      Include name-only places ({len(stub)})
    </label>
  </div>

  <div id="place-grid" class="person-grid">
    {cards}
  </div>
</main>

{footer_html(base)}

<script src="{base}js/app.js"></script>
<script>initNavToggle();initPlacesToggle();</script>
</body>
</html>
"""


_MAPS = None
_GEO_BY_ID = None


def maps_data():
    global _MAPS
    if _MAPS is None:
        _MAPS = json.loads((ROOT / "data" / "maps.json").read_text())["extents"]
    return _MAPS


def _lookup_geo(index_entry):
    """Index entries carry only flat lat/lng; read kind/confidence from the
    per-place file (cached)."""
    global _GEO_BY_ID
    if _GEO_BY_ID is None:
        _GEO_BY_ID = {}
        for f in sorted((ROOT / "data" / "places").glob("*.json")):
            d = json.loads(f.read_text())
            if d.get("geo"):
                _GEO_BY_ID[d["place_id"]] = d["geo"]
    return _GEO_BY_ID.get(index_entry["place_id"])


def _haversine_km(lat1, lng1, lat2, lng2):
    r = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lng2 - lng1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def _extent_contains(ext, lat, lng, margin=0.02):
    mlon = (ext["lon_max"] - ext["lon_min"]) * margin
    mlat = (ext["lat_max"] - ext["lat_min"]) * margin
    return (ext["lon_min"] - mlon <= lng <= ext["lon_max"] + mlon
            and ext["lat_min"] - mlat <= lat <= ext["lat_max"] + mlat)


def _proj(ext, lat, lng):
    return ((lng - ext["lon_min"]) * ext["lon_scale"],
            (ext["lat_max"] - lat) * ext["lat_scale"])


def _mk_class(geo):
    conf = geo.get("confidence", 0)
    if geo.get("kind") == "representative" and conf == 0:
        return "mk-approx"
    if conf >= 500:
        return "mk-secure"
    if conf > 0:
        return "mk-disputed"
    return "mk-approx"


def base_map_svg(ext_name, extra_attrs=""):
    """Marker-free base map for one extent, inline SVG using --map-* tokens
    (no embedded <style>). For the map explorer's no-JS fallback."""
    ext = maps_data()[ext_name]
    w, h = ext["width"], ext["height"]
    lakes = "".join(f'<path class="map-lake" d="{d}"/>' for d in ext["lakes"])
    rivers = "".join(f'<path class="map-river" d="{d}"/>' for d in ext["rivers"])
    return (f'<svg viewBox="0 0 {w:.0f} {h:.0f}" preserveAspectRatio="xMidYMid meet" '
            f'role="img" aria-label="Base map: {esc(ext["title"])}"{extra_attrs}>'
            f'<rect class="map-water-rect" x="0" y="0" width="{w:.0f}" height="{h:.0f}"/>'
            f'<path class="map-land" d="{ext["land"]}"/>{lakes}{rivers}</svg>')


def place_mini_map_html(place, placed_places, base, n_neighbors=6):
    """A small locator map: the place itself plus its nearest placed
    neighbours, on our own Natural Earth base map cropped to fit them."""
    geo = place.get("geo")
    if not geo or geo.get("lat") is None:
        return ""
    slat, slng = geo["lat"], geo["lng"]

    others = []
    for e in placed_places:
        if e["place_id"] == place["place_id"]:
            continue
        d = _haversine_km(slat, slng, e["lat"], e["lng"])
        others.append((d, e["place_id"], e))
    others.sort(key=lambda t: (t[0], t[1]))
    # Prefer settlements as neighbours; allow at most two nearby regions so a
    # place ringed by overlapping region anchors (Jerusalem) still shows towns.
    pts, regs = [], []
    for _d, _pid, e in others:
        (regs if (_lookup_geo(e) or {}).get("kind") == "representative" else pts).append(e)
    neighbours = sorted(
        pts[:n_neighbors] + regs[:2],
        key=lambda e: _haversine_km(slat, slng, e["lat"], e["lng"]),
    )[:n_neighbors]

    exts = maps_data()
    pts_ll = [(slat, slng)] + [(e["lat"], e["lng"]) for e in neighbours]
    if all(_extent_contains(exts["holy-land"], la, lo) for la, lo in pts_ll):
        ext_name = "holy-land"
    elif (_extent_contains(exts["holy-land"], slat, slng)
          and sum(_extent_contains(exts["holy-land"], la, lo) for la, lo in pts_ll) >= 3):
        ext_name = "holy-land"
        neighbours = [e for e in neighbours
                      if _extent_contains(exts["holy-land"], e["lat"], e["lng"])]
        pts_ll = [(slat, slng)] + [(e["lat"], e["lng"]) for e in neighbours]
    else:
        ext_name = "biblical-world"
    ext = exts[ext_name]

    xs, ys = zip(*[_proj(ext, la, lo) for la, lo in pts_ll])
    pad_x = max((max(xs) - min(xs)) * 0.28, 60)
    pad_y = max((max(ys) - min(ys)) * 0.28, 60)
    vx = max(0, min(xs) - pad_x)
    vy = max(0, min(ys) - pad_y)
    vw = min(ext["width"], max(xs) + pad_x) - vx
    vh = min(ext["height"], max(ys) + pad_y) - vy
    if vw / vh > 2.2:
        grow = (vw / 2.2 - vh) / 2
        vy = max(0, vy - grow)
        vh = min(ext["height"] - vy, vh + 2 * grow)
    elif vh / vw > 1.6:
        grow = (vh / 1.6 - vw) / 2
        vx = max(0, vx - grow)
        vw = min(ext["width"] - vx, vw + 2 * grow)

    scale = max(vw / 760, 1)
    lakes = "".join(f'<path class="map-lake" d="{d}"/>' for d in ext["lakes"])
    rivers = "".join(f'<path class="map-river" d="{d}"/>' for d in ext["rivers"])

    def marker(e, subject=False):
        la, lo = (slat, slng) if subject else (e["lat"], e["lng"])
        x, y = _proj(ext, la, lo)
        pgeo = place["geo"] if subject else (_lookup_geo(e) or {})
        region = pgeo.get("kind") == "representative"
        cls = "map-mk" + (" mk-subject" if subject else "") + (" mk-region" if region else "")
        conf_cls = "" if subject else _mk_class(pgeo)
        r = round((5.2 if subject else 3.4) * scale * (0.85 if region and not subject else 1), 1)
        fs = round(13 * scale, 1)
        name = place["name"] if subject else e["name"]
        anchor_end = x > vx + vw * 0.62
        tx = -(r + 3) if anchor_end else (r + 3)
        ta = ' text-anchor="end"' if anchor_end else ""
        return (f'<g class="{cls}" transform="translate({x:.1f},{y:.1f})">'
                f'<circle r="{r}" class="{conf_cls}"/>'
                f'<text x="{tx}" y="{fs * 0.34:.1f}" style="font-size:{fs}px"{ta}>{esc(name)}</text></g>')

    markers = "".join(marker(e) for e in neighbours) + marker(place, subject=True)
    explorer_ids = ",".join([place["place_id"]] + [e["place_id"] for e in neighbours])
    explorer_href = f'{base}map.html?ext={ext_name}&amp;places={explorer_ids}'

    return f"""<figure class="placemap">
    <svg viewBox="{vx:.1f} {vy:.1f} {vw:.1f} {vh:.1f}" role="img" aria-label="Locator map for {esc(place['name'])}">
      <rect class="map-water-rect" x="{vx:.1f}" y="{vy:.1f}" width="{vw:.1f}" height="{vh:.1f}"/>
      <path class="map-land" d="{ext['land']}"/>
      {lakes}
      {rivers}
      {markers}
    </svg>
    <figcaption><span>Base map &copy; Natural Earth (public domain); locations from <a href="https://www.openbible.info/geo/">OpenBible.info</a> (CC BY 4.0)</span> <a href="{explorer_href}">Open in the map explorer &#8594;</a></figcaption>
  </figure>"""


def build_map_explorer_page(places_index):
    base = ""
    canonical = f"{SITE_URL}/map.html"
    title = "Map explorer — Lives of Scripture"
    description = ("Plot biblical places on our own maps. Start from a preset group — the Exodus "
                  "route, Paul's journeys, the seven churches of Revelation — then add or remove "
                  "towns and share the result.")
    groups = json.loads((ROOT / "data" / "map-groups.json").read_text())["groups"]
    breadcrumb_ld = breadcrumb_json_ld([("Home", f"{SITE_URL}/"), ("Map explorer", None)])
    group_links = "\n      ".join(
        f'<li><a href="{base}map.html?group={esc(g["id"])}">{esc(g["name"])}</a> — {esc(g["blurb"])}</li>'
        for g in groups
    )

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
<script type="application/ld+json">
{breadcrumb_ld}
</script>
</head>
<body>
{header_html(base, "places.html")}

<main>
  <p><a href="places.html" class="back-link">&#8592; Back to all places</a></p>
  <h2>Map explorer</h2>
  <p class="page-intro">Our own maps, drawn from public-domain Natural Earth geometry, with places
  plotted from <a href="https://www.openbible.info/geo/">OpenBible.info</a> coordinates. Pick a base
  style and extent, load a preset group, then add or remove places and copy a link to what you built.</p>

  <div class="mapx-layout" id="map-explorer" data-mapstyle="parchment">
    <aside class="mapx-rail">
      <div>
        <h3>Extent</h3>
        <div class="mapx-seg" id="mapx-extent">
          <button type="button" data-v="holy-land" aria-pressed="true">Holy Land</button>
          <button type="button" data-v="biblical-world">Biblical World</button>
        </div>
      </div>
      <div>
        <h3>Base style</h3>
        <div class="mapx-seg" id="mapx-style">
          <button type="button" data-v="parchment" aria-pressed="true">Parchment</button>
          <button type="button" data-v="plain">Plain</button>
        </div>
      </div>
      <div>
        <h3>Preset group</h3>
        <div class="mapx-groups" id="mapx-groups"></div>
      </div>
      <details class="mapx-picker" id="mapx-picker">
        <summary>Add or remove places</summary>
        <div class="mapx-list" id="mapx-list"></div>
      </details>
      <div>
        <h3>Share this map</h3>
        <div class="mapx-share">
          <input type="text" id="mapx-url" readonly aria-label="Shareable link to this map">
          <button type="button" id="mapx-copy">Copy</button>
        </div>
      </div>
      <label class="mapx-labels"><input type="checkbox" id="mapx-all-labels"> Show every label</label>
    </aside>

    <div class="mapx-stage">
      <div class="mapx-bar">
        <strong id="mapx-title">All places</strong>
        <span class="mapx-count" id="mapx-count"></span>
        <span class="mapx-zoom"><button type="button" id="mapx-zoom-out" aria-label="Zoom out">&minus;</button><button type="button" id="mapx-zoom-in" aria-label="Zoom in">+</button></span>
      </div>
      <div class="mapx-viewport" id="mapx-viewport">
        {base_map_svg("holy-land", ' id="mapx-fallback"')}
      </div>
    </div>
  </div>

  <noscript>
    <p>The interactive map needs JavaScript. Preset groups you can still browse:</p>
    <ul>
      {group_links}
    </ul>
  </noscript>
</main>

{footer_html(base)}

<script src="{base}js/app.js"></script>
<script>renderMapExplorer();initNavToggle();</script>
</body>
</html>
"""


def build_place_detail_page(place, gender_by_id, places_by_name, link_ctx=None, placed_places=None):
    base = "../"
    place_id = place["place_id"]
    canonical = f"{SITE_URL}/places/{place_id}.html"
    title = f'{place["name"]} — Places — Lives of Scripture'
    description = truncate(place.get("description") or f'{place["name"]} is named in Scripture ({place["first_reference"]}).')

    alt_html = ""
    if place.get("alt_names"):
        alt_html = f'<div class="alt-names">Also called: {esc(", ".join(place["alt_names"]))}</div>'

    modern_html = ""
    if place.get("modern_name"):
        modern_html = f'<div class="name-meaning">Modern location: {esc(place["modern_name"])}</div>'

    first_ref = f'<div class="first-reference">First named: {esc(place["first_reference"])}</div>'

    era_badges = "".join(
        f'<a href="{base}timeline.html" class="badge badge-link">{esc(era)}</a>'
        for era in place.get("eras", [])
    )
    tags = f"""<div class="tags">
        <span class="badge">{esc(place_type_label(place["type"]))}</span>
        <span class="badge">{esc(place_region_label(place["region"]))}</span>
        {era_badges}
      </div>"""

    if place["tier"] == "full":
        desc_text = place.get("description", "")
        if link_ctx is not None and desc_text:
            linked_pids = set()
            desc_html = f'<p>{link_person_mentions.link_paragraph(desc_text, place_id, link_ctx, base, linked_pids)}</p>'
        else:
            desc_html = f"<p>{esc(desc_text)}</p>"
        ff = place.get("family_friendly_summary")
        ff_html = ""
        if ff:
            ff_html = f"""<details class="family-friendly">
    <summary>Family-friendly summary</summary>
    <p>{esc(ff)}</p>
  </details>"""
        story_html = desc_html + ("\n  " + ff_html if ff_html else "")
    else:
        story_html = (
            '<div class="stub-notice">Named in Scripture, but with no story of its own here — '
            "kept for the connections graph.</div>"
        )

    ident_html = place_identification_html(place)

    mini_map_html = place_mini_map_html(place, placed_places or [], base)

    people_html = place_related_people_html(place, gender_by_id, base)

    group_key = place["name"].strip().lower()
    same_name = [e for e in places_by_name.get(group_key, []) if e["place_id"] != place_id]
    disamb = place_disambiguation_section(place["name"], same_name, base)

    breadcrumb_ld = breadcrumb_json_ld([
        ("Home", f"{SITE_URL}/"),
        ("Places", f"{SITE_URL}/places.html"),
        (place["name"], None),
    ])
    json_ld = place_json_ld(place, canonical)
    references_html = references_list(place.get("references", []))
    robots = "" if place["tier"] == "full" else '\n<meta name="robots" content="noindex, follow">'

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(title)}</title>
<meta name="description" content="{esc(description)}">
<link rel="canonical" href="{canonical}">{robots}

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
<script type="application/ld+json">
{breadcrumb_ld}
</script>
</head>
<body>
{header_html(base, "places.html")}

<main id="person-main">
  <p><a href="{base}places.html" class="back-link">&#8592; Back to all places</a></p>

  <div class="person-title">
    <h2>{esc(place["name"])}</h2>
    {alt_html}
    {modern_html}
    {first_ref}
    {tags}
  </div>

  {ident_html}

  {mini_map_html}

  <section>
    {story_html}
  </section>

  {references_html}

  <section>
    <h3>People connected to {esc(place["name"])}</h3>
    {people_html}
  </section>

  <p><a href="{base}place-connections.html?id=place:{esc(place_id)}" class="back-link">View on the place connections graph &#8594;</a></p>

  {disamb}
</main>

{footer_html(base)}

<script src="{base}js/app.js"></script>
<script>initNavToggle();</script>
</body>
</html>
"""


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
                href = f'../people/{entry["person_id"]}.html'
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
            f'<tr><td><a href="../people/{e["person_id"]}.html">{esc(e["name"])}</a></td>'
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


# ---------------------------------------------------------------------
# "Two Genealogies of Jesus" chart (charts.html hub + charts/genealogies-of-jesus.html)
# ---------------------------------------------------------------------

# Matthew 1:2-16, Abraham to Joseph (husband of Mary) -- the "royal" line
# through Solomon. Matthew's own text groups this into 3 sets of 14
# generations (Matthew 1:17); the middle and final sets are stylized --
# Matthew's text skips Ahaziah, Joash, and Amaziah between Joram and
# Uzziah, and skips Jehoiakim between Josiah and Jeconiah (all fully
# attested elsewhere, in 2 Kings) -- a well-known feature of the Hebrew
# "father of" idiom used to hit a round count of 14, not a data error.
# See GEN_DISPLAY_NAME_OVERRIDE for two spots where Matthew's own wording
# (Joram, Jeconiah) differs from this site's canonical `name` field for
# the same person (Jehoram, Jehoiachin).
GEN_MATTHEW_LINE = [
    "abraham", "isaac", "israel", "judah", "perez", "hezron-2", "ram",
    "amminadab", "nahshon", "salmon", "boaz", "obed", "jesse", "david",
    "solomon", "rehoboam", "abijah-3", "asa", "jehoshaphat-3", "jehoram",
    "uzziah", "jotham-2", "ahaz", "hezekiah", "manasseh-3", "amon-2",
    "josiah", "jehoiachin",
    "shealtiel", "zerubbabel", "abihud-2", "eliakim-3", "azor", "zadok-7",
    "achim", "eliud", "eleazar-9", "matthan", "jacob", "joseph-6",
]

# Luke 3:23-38, Adam to Joseph. Luke's text actually lists these in the
# opposite direction (son back to father, ending "...the son of Adam, the
# son of God") -- this list runs oldest-to-youngest instead, to lay out as
# a family tree in the same direction as Matthew's list above. Luke's
# Greek text (the reading behind both NASB and KJV) also names a second
# "Cainan" between Arpachshad and Shelah (Luke 3:36) with no equivalent in
# the Hebrew genealogies of Genesis 10-11 and so no person entry in this
# dataset -- see GEN_LUKE_TEXT_ONLY_GAP and the chart page's own
# disclaimer text, which states this as a textual difference rather than
# silently resolving it either way (per CLAUDE.md's Factual Accuracy
# rules).
GEN_LUKE_LINE = [
    "adam", "seth", "enosh", "kenan", "mahalalel", "jared", "enoch",
    "methuselah", "lamech-2", "noah", "shem", "arpachshad", "shelah",
    "eber", "peleg", "reu", "serug", "nahor", "terah",
    "abraham", "isaac", "israel", "judah", "perez", "hezron-2", "ram",
    "amminadab", "nahshon", "salmon", "boaz", "obed", "jesse", "david",
    "nathan", "mattatha", "menna", "melea", "eliakim-4", "jonam",
    "joseph-9", "judah-5", "simeon-3", "levi-3", "matthat-2", "jorim",
    "eliezer-9", "joshua-5", "er-3", "elmadam", "cosam", "addi",
    "melchi-2", "neri",
    "shealtiel", "zerubbabel", "rhesa", "joanan", "joda", "josech",
    "semein", "mattathias-2", "maath", "naggai", "hesli", "nahum-2",
    "amos-2", "mattathias", "joseph-8", "jannai", "melchi", "levi-2",
    "matthat", "eli-2", "joseph-6",
]

GEN_LUKE_TEXT_ONLY_GAP = {
    "after": "arpachshad",
    "name": "Cainan",
    "reference": "Luke 3:36",
}

GEN_DISPLAY_NAME_OVERRIDE = {
    "jehoram": "Joram",
    "jehoiachin": "Jeconiah",
}

GEN_COLOR_VAR = {
    "matthew": "var(--gen-matthew)",
    "luke": "var(--gen-luke)",
    "shared": "var(--gen-shared)",
}
GEN_LEGEND_LABEL = {
    "matthew": "Named only in Matthew’s genealogy (Matthew 1:1-16)",
    "luke": "Named only in Luke’s genealogy (Luke 3:23-38)",
    "shared": "Named in both genealogies",
}


def gen_shared_ids():
    return set(GEN_MATTHEW_LINE) & set(GEN_LUKE_LINE)


def gen_line_for(pid, shared):
    if pid in shared:
        return "shared"
    if pid in GEN_MATTHEW_LINE:
        return "matthew"
    return "luke"


def gen_slice_between(line, start_id, end_id):
    """person_ids strictly between two anchors in an ordered genealogy line."""
    i0 = line.index(start_id)
    i1 = line.index(end_id)
    return line[i0 + 1:i1]


def gen_display_name(pid, index_by_id):
    return GEN_DISPLAY_NAME_OVERRIDE.get(pid, index_by_id.get(pid, pid))


def render_genealogies_svg(index_by_id, ref_by_id):
    shared = gen_shared_ids()
    box_w, box_h, term_h = 170, 36, 46
    center_cx, left_cx, right_cx = 340, 140, 540
    total_w = 680
    parts = []
    node_pos = {}

    def box(key, pid, cx, top_y, linekey, height=box_h, display=None, linked=True, note=None):
        name = display or gen_display_name(pid, index_by_id) if pid else display
        ref = ref_by_id.get(pid, "") if pid else ""
        color = GEN_COLOR_VAR[linekey]
        href = f"../people/{pid}.html" if (linked and pid) else None
        label_class = "gen-node-terminus-label" if height != box_h else "gen-node-label"
        node_class = "gen-node-terminus" if height != box_h else "gen-node"
        title = f"{name} — {esc(note or GEN_LEGEND_LABEL[linekey])}" + (f" ({ref})" if ref else "")
        rect = (
            f'<rect x="{cx - box_w / 2:.1f}" y="{top_y:.1f}" width="{box_w}" height="{height}" rx="6" '
            f'fill="{color}" class="{node_class}" tabindex="0" '
            f'data-name="{esc(name)}" data-note="{esc(note or GEN_LEGEND_LABEL[linekey])}" '
            f'data-reference="{esc(ref)}">'
            f'<title>{title}</title></rect>'
        )
        text = (
            f'<text x="{cx:.1f}" y="{top_y + height / 2 + 4:.1f}" class="{label_class}" '
            f'text-anchor="middle">{esc(name)}</text>'
        )
        if href:
            parts.append(f'<a href="{href}">{rect}{text}</a>')
        else:
            parts.append(rect + text)
        node_pos[key] = {"cx": cx, "top": top_y, "bottom": top_y + height, "mid": top_y + height / 2}

    def vline(x, y1, y2, colorkey="shared", dashed=False):
        cls = "gen-connector-marriage" if dashed else "gen-connector"
        stroke = f' stroke="{GEN_COLOR_VAR[colorkey]}"' if colorkey != "shared" else ""
        parts.append(f'<line x1="{x:.1f}" y1="{y1:.1f}" x2="{x:.1f}" y2="{y2:.1f}" class="{cls}"{stroke} />')

    def dline(x1, y1, x2, y2):
        parts.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" class="gen-connector" />')

    def collapsed_label(cx, y1, y2, colorkey, count, noun, ref_range):
        vline(cx, y1, y2, colorkey)
        mid = (y1 + y2) / 2
        parts.append(
            f'<text x="{cx:.1f}" y="{mid - 4:.1f}" class="gen-connector-label" text-anchor="middle">'
            f'{esc(f"{count} more {noun}")}</text>'
        )
        parts.append(
            f'<text x="{cx:.1f}" y="{mid + 9:.1f}" class="gen-connector-label" text-anchor="middle">'
            f'{esc(ref_range)}</text>'
        )

    def column_label(cx, y, colorkey, text):
        parts.append(
            f'<text x="{cx:.1f}" y="{y:.1f}" class="gen-column-label" fill="{GEN_COLOR_VAR[colorkey]}" '
            f'text-anchor="middle">{esc(text)}</text>'
        )

    y = 20

    # Adam -- Luke-only pre-Abraham trunk
    box("adam", "adam", center_cx, y, "luke")
    y1 = node_pos["adam"]["bottom"]
    mid = gen_slice_between(GEN_LUKE_LINE, "adam", "abraham")
    collapsed_label(center_cx, y1, y1 + 50, "luke", len(mid), "generations", "Genesis 5, 11 — Luke only")
    y = y1 + 50

    # Abraham -- shared
    box("abraham", "abraham", center_cx, y, "shared")
    y1 = node_pos["abraham"]["bottom"]
    mid = gen_slice_between(GEN_MATTHEW_LINE, "abraham", "david")
    collapsed_label(center_cx, y1, y1 + 50, "shared", len(mid), "generations", "Genesis; Ruth — named in both")
    y = y1 + 50

    # David -- shared, then splits
    box("david", "david", center_cx, y, "shared")
    y1 = node_pos["david"]["bottom"]
    split_y = y1 + 26
    dline(center_cx, y1, left_cx, split_y)
    dline(center_cx, y1, right_cx, split_y)
    column_label(left_cx, split_y - 4, "matthew", "Matthew’s line")
    column_label(right_cx, split_y - 4, "luke", "Luke’s line")
    y = split_y

    # Solomon (Matthew) / Nathan (Luke)
    box("solomon", "solomon", left_cx, y, "matthew")
    box("nathan", "nathan", right_cx, y, "luke")
    y1 = node_pos["solomon"]["bottom"]
    mid_m = gen_slice_between(GEN_MATTHEW_LINE, "solomon", "jehoiachin")
    mid_l = gen_slice_between(GEN_LUKE_LINE, "nathan", "neri")
    collapsed_label(left_cx, y1, y1 + 50, "matthew", len(mid_m), "kings", "Matthew 1:7-11 only")
    collapsed_label(right_cx, y1, y1 + 50, "luke", len(mid_l), "generations", "Luke 3:23-31 only")
    y = y1 + 50

    # Jeconiah (Matthew) / Neri (Luke) -- both merge into Shealtiel
    box("jeconiah", "jehoiachin", left_cx, y, "matthew", display="Jeconiah")
    box("neri", "neri", right_cx, y, "luke")
    y1 = node_pos["jeconiah"]["bottom"]
    merge_y = y1 + 26
    dline(left_cx, y1, center_cx, merge_y)
    dline(right_cx, y1, center_cx, merge_y)
    y = merge_y

    # Shealtiel, Zerubbabel -- shared, then split again
    box("shealtiel", "shealtiel", center_cx, y, "shared")
    y1 = node_pos["shealtiel"]["bottom"]
    vline(center_cx, y1, y1 + 22, "shared")
    y = y1 + 22
    box("zerubbabel", "zerubbabel", center_cx, y, "shared")
    y1 = node_pos["zerubbabel"]["bottom"]
    split_y = y1 + 26
    dline(center_cx, y1, left_cx, split_y)
    dline(center_cx, y1, right_cx, split_y)
    column_label(left_cx, split_y - 4, "matthew", "Matthew’s line")
    column_label(right_cx, split_y - 4, "luke", "Luke’s line")
    y = split_y

    # Abihud (Matthew) / Rhesa (Luke)
    box("abihud", "abihud-2", left_cx, y, "matthew")
    box("rhesa", "rhesa", right_cx, y, "luke")
    y1 = node_pos["abihud"]["bottom"]
    mid_m = gen_slice_between(GEN_MATTHEW_LINE, "abihud-2", "jacob")
    mid_l = gen_slice_between(GEN_LUKE_LINE, "rhesa", "eli-2")
    collapsed_label(left_cx, y1, y1 + 50, "matthew", len(mid_m), "generations", "Matthew 1:13-15 only")
    collapsed_label(right_cx, y1, y1 + 50, "luke", len(mid_l), "generations", "Luke 3:23-27 only")
    y = y1 + 50

    # Jacob (Matthew) / Eli (Luke) -- both merge into Joseph
    box("jacob", "jacob", left_cx, y, "matthew")
    box("eli", "eli-2", right_cx, y, "luke")
    y1 = node_pos["jacob"]["bottom"]
    merge_y = y1 + 26
    dline(left_cx, y1, center_cx, merge_y)
    dline(right_cx, y1, center_cx, merge_y)
    y = merge_y

    # Joseph (shared terminus of both male lines) + Mary (named only in
    # Matthew's genealogy text, Matthew 1:16) as a side node joined by a
    # dashed marriage line, both flowing down into Jesus.
    box("joseph", "joseph-6", center_cx, y, "shared",
        note="Named at the end of both genealogies — Matthew 1:16; Luke 3:23")
    box("mary", "mary", right_cx, y, "matthew", note="Named only in Matthew’s genealogy — Matthew 1:16")
    jy = node_pos["joseph"]
    my = node_pos["mary"]
    parts.append(
        f'<line x1="{jy["cx"] + box_w / 2:.1f}" y1="{jy["mid"]:.1f}" x2="{my["cx"] - box_w / 2:.1f}" '
        f'y2="{my["mid"]:.1f}" class="gen-connector-marriage" />'
    )
    y1 = jy["bottom"]
    merge_y = y1 + 34
    dline(center_cx, y1, center_cx, merge_y)
    dline(right_cx, my["bottom"], center_cx, merge_y)
    y = merge_y

    # Jesus -- both genealogies converge here (Matthew 1:16; Luke 3:23).
    # No person_id links this node: this dataset's "jesus" entry is a
    # different New Testament figure ("Jesus who is called Justus",
    # Colossians 4:11) -- see the chart page's disclaimer.
    box("jesus", None, center_cx, y, "shared", height=term_h, display="Jesus",
        linked=False, note="Both genealogies converge here — Matthew 1:16; Luke 3:23")

    total_h = node_pos["jesus"]["bottom"] + 20
    header = (
        f'<svg id="gen-chart-svg" viewBox="0 0 {total_w} {total_h:.0f}" width="{total_w}" height="{total_h:.0f}" '
        f'role="img" aria-label="The two genealogies of Jesus, from Matthew 1 and Luke 3, shown as one '
        f'joined family tree" xmlns="http://www.w3.org/2000/svg" class="gen-chart-svg">'
    )
    return header + "\n" + "\n".join(parts) + "\n</svg>"


def render_genealogies_legend():
    items = "\n    ".join(
        f'<span class="gen-legend-item"><span class="gen-legend-swatch" style="background:{GEN_COLOR_VAR[key]}"></span>{esc(label)}</span>'
        for key, label in GEN_LEGEND_LABEL.items()
    )
    return f'<div class="gen-legend">{items}</div>'


def render_genealogies_table(line, gospel_label, index_by_id, ref_by_id, text_only_gap=None):
    rows = []
    for pid in line:
        if text_only_gap and pid == text_only_gap["after"]:
            rows.append(
                f'<tr><td>{esc(text_only_gap["name"])}</td>'
                f'<td>{esc(text_only_gap["reference"])}</td>'
                f'<td class="gen-table-note">Named in the Greek text (NASB, KJV) but not in the Hebrew '
                f'genealogies of Genesis 10–11 — no person entry in this dataset.</td></tr>'
            )
        name = gen_display_name(pid, index_by_id)
        ref = ref_by_id.get(pid, "")
        rows.append(
            f'<tr><td><a href="../people/{pid}.html">{esc(name)}</a></td>'
            f'<td>{esc(ref)}</td><td></td></tr>'
        )
    body = "\n    ".join(rows)
    return f"""<details class="kp-table-details">
    <summary>View {esc(gospel_label)}'s full list</summary>
    <div class="table-scroll">
    <table class="kp-table">
      <thead><tr><th>Name</th><th>First reference</th><th>Note</th></tr></thead>
      <tbody>
    {body}
      </tbody>
    </table>
    </div>
  </details>"""


def build_genealogies_chart_page(index_by_id, ref_by_id):
    base = "../"
    canonical = f"{SITE_URL}/charts/genealogies-of-jesus.html"
    title = "The Two Genealogies of Jesus — Lives of Scripture"
    description = "Matthew's and Luke's genealogies of Jesus, compared and joined on one family-tree chart."
    breadcrumb_ld = breadcrumb_json_ld([
        ("Home", f"{SITE_URL}/"), ("Charts", f"{SITE_URL}/charts.html"),
        (title.replace(" — Lives of Scripture", ""), None),
    ])

    svg = render_genealogies_svg(index_by_id, ref_by_id)
    legend = render_genealogies_legend()
    matthew_table = render_genealogies_table(GEN_MATTHEW_LINE, "Matthew", index_by_id, ref_by_id)
    luke_table = render_genealogies_table(GEN_LUKE_LINE, "Luke", index_by_id, ref_by_id, GEN_LUKE_TEXT_ONLY_GAP)

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
<script type="application/ld+json">
{breadcrumb_ld}
</script>
</head>
<body>
{header_html(base, "charts.html")}

<main>
  <p><a href="{base}charts.html">&larr; Charts</a></p>
  <h2>The Two Genealogies of Jesus</h2>
  <p class="page-intro">Matthew 1:1-16 and Luke 3:23-38 both trace Jesus' descent back through David and
  Abraham, but by different routes. This chart lays both out as one joined family tree: where they run
  through the same names, where each has its own line, and the two places their lists rejoin.</p>

  {legend}

  <div class="kp-legend-row" style="justify-content: flex-end;">
    <div class="kp-chart-toolbar">
    <button type="button" class="kp-chart-copy" id="gen-chart-copy">&#128203; Copy image</button>
    </div>
  </div>

  <div class="kp-chart-scroll">
  {svg}
  </div>

  <p class="kp-disclaimer">Both genealogies list Joseph, Mary's husband, as their final named generation
  (Matthew 1:16; Luke 3:23) — but Matthew names Joseph's father as Jacob, while Luke names him as Eli
  ("as was supposed," Luke 3:23). Scripture never states directly how the two fit together; two
  harmonizations are traditionally offered — that Jacob and Eli were half-brothers joined by a levirate
  marriage (so Joseph was Jacob's son by birth and Eli's by law), or that Luke traces Mary's own descent
  through her father Eli, with Joseph named because a genealogy was reckoned through the husband. Both are
  traditional harmonizations, not something the text states outright, so neither is asserted here as fact.
  Two smaller textual points: some Luke manuscripts read a name ("Admin") between Amminadab and Ram in
  Luke 3:33 that most manuscripts, and this chart, don't include; and Luke 3:36 names a second "Cainan"
  between Arpachshad and Shelah that has no counterpart in Genesis 10–11's Hebrew text — see the note
  in Luke's full list below. This dataset does not yet have a dedicated profile page for Jesus himself
  (the person_id "jesus" belongs to a different New Testament figure, "Jesus who is called Justus,"
  Colossians 4:11), so the final "Jesus" box below is not a link.</p>

  {matthew_table}

  {luke_table}
</main>

{footer_html(base)}

<script src="{base}js/app.js"></script>
<script>initNavToggle(); initGenChartTooltips(); initChartCopyButton("gen-chart-copy", "gen-chart-svg");</script>
</body>
</html>
"""


# ---------------------------------------------------------------------
# "The Twelve Tribes, By Mother" chart (charts.html hub + charts/twelve-tribes.html)
# ---------------------------------------------------------------------

# Tribe -> (mother key, birth-order index within that mother), used only to
# group and shade this sunburst -- see CLAUDE.md's Tribal Affiliation
# section for how the underlying `tribe` field itself is curated. Order
# within each mother follows Genesis 29-30 (Leah's own sons, then the two
# handmaids' sons, born while Leah and Rachel were each giving Jacob their
# maid). Manasseh is listed before Ephraim here to match their actual birth
# order (Genesis 41:51-52), even though Jacob's blessing later reverses
# their precedence (Genesis 48:14-20) and TIMELINE_TRIBES in js/app.js
# lists Ephraim first for that reason -- the two lists are independent.
TRIBE_MOTHER = {
    "Reuben": ("leah", 0), "Simeon": ("leah", 1), "Levi": ("leah", 2), "Judah": ("leah", 3),
    "Issachar": ("leah", 4), "Zebulun": ("leah", 5),
    "Benjamin": ("rachel", 0), "Manasseh": ("rachel", 1), "Ephraim": ("rachel", 2),
    "Dan": ("bilhah", 0), "Naphtali": ("bilhah", 1),
    "Gad": ("zilpah", 0), "Asher": ("zilpah", 1),
}
TRIBE_N_IN_MOTHER = {"leah": 6, "rachel": 3, "bilhah": 2, "zilpah": 2}

# Fresh names for this chart's inner ring, reusing the existing era
# palette's hex values (era-patriarchal/exodus/judges/united-monarchy)
# rather than the --tribe-* colors one ring further out -- a mother and her
# own tribes would otherwise fight for the same hue family. Never displayed
# alongside the era-coded charts that own those hex values, so the reuse is
# safe (same precedent as --gen-matthew/--gen-luke reusing
# --era-exodus/--era-patriarchal's hex under this chart's own name).
TRIBE_MOTHERS = [
    {"key": "leah", "label": "Leah", "color": "var(--era-patriarchal)",
     "desc": "Jacob's first wife, Laban's elder daughter (Genesis 29:16-35)"},
    {"key": "rachel", "label": "Rachel", "color": "var(--era-exodus)",
     "desc": "Jacob's beloved wife, Laban's younger daughter (Genesis 29:16-30)"},
    {"key": "bilhah", "label": "Bilhah", "color": "var(--era-judges)",
     "desc": "Rachel's maid, given to Jacob (Genesis 30:1-8)"},
    {"key": "zilpah", "label": "Zilpah", "color": "var(--era-united-monarchy)",
     "desc": "Leah's maid, given to Jacob (Genesis 30:9-13)"},
]

# Reuses the site's existing per-tribe --tribe-* palette (css/style.css),
# already validated and already the color key on timeline.html's tribe
# filter, so a tribe reads the same color on both charts. That palette's
# fixed adjacency order (see the CSS comment above --tribe-reuben) doesn't
# match this chart's mother-grouped layout, which puts some non-adjacent
# tribes next to each other; every arc and leaf here carries its own text
# label, the same mitigation timeline.html's own comment already relies on
# for its packed, chronologically-ordered bars.
TRIBE_COLOR_VAR = {name: f"var(--tribe-{name.lower()})" for name in TRIBE_MOTHER}

TRIBE_MEGA_THRESHOLD = 15  # tribes above this many people become a solid band, not individual spokes

TRIBE_CX = TRIBE_CY = 430
TRIBE_HUB_R = 82
TRIBE_MOTHER_R0, TRIBE_MOTHER_R1 = 100, 148
TRIBE_TRIBE_R0, TRIBE_TRIBE_R1 = 148, 194
TRIBE_MEGA_R1 = TRIBE_TRIBE_R1 + 78
TRIBE_LEAF_DOT_R = 320
TRIBE_LEAF_LABEL_R = 330
TRIBE_MOTHER_GAP = 2.2
TRIBE_GAP = 1.0


def collect_tribes():
    """Every full-tier person with a curated `tribe` field (CLAUDE.md's
    Tribal Affiliation section), grouped by tribe name. Reads the per-person
    files directly since the lightweight index only mirrors the tribe name,
    not its reference."""
    by_tribe = {}
    people_dir = ROOT / "data" / "people"
    for path in sorted(people_dir.glob("*.json")):
        person = json.loads(path.read_text())
        tribe = person.get("tribe")
        if not tribe or tribe["name"] not in TRIBE_MOTHER:
            continue
        by_tribe.setdefault(tribe["name"], []).append({
            "person_id": person["person_id"],
            "name": person["name"],
            "testament": person["testament"],
            "reference": tribe["reference"],
        })
    for people in by_tribe.values():
        people.sort(key=lambda p: (p["testament"] != "OT", p["name"]))
    return by_tribe


def tribe_polar(cx, cy, r, deg):
    rad = math.radians(deg)
    return cx + r * math.sin(rad), cy - r * math.cos(rad)


def tribe_arc_path(cx, cy, r0, r1, start, end):
    x0a, y0a = tribe_polar(cx, cy, r0, start)
    x1a, y1a = tribe_polar(cx, cy, r1, start)
    x1b, y1b = tribe_polar(cx, cy, r1, end)
    x0b, y0b = tribe_polar(cx, cy, r0, end)
    large = 1 if (end - start) > 180 else 0
    return (
        f"M {x0a:.2f},{y0a:.2f} L {x1a:.2f},{y1a:.2f} "
        f"A {r1:.2f},{r1:.2f} 0 {large} 1 {x1b:.2f},{y1b:.2f} "
        f"L {x0b:.2f},{y0b:.2f} "
        f"A {r0:.2f},{r0:.2f} 0 {large} 0 {x0a:.2f},{y0a:.2f} Z"
    )


def tribe_is_bottom(angle):
    """For tangential (arc-following) ring labels -- mother/tribe/mega band
    text runs along the arc at rotation `a`; left unflipped, the bottom
    half of the circle reads upside-down, so add 180 degrees there."""
    return 90 < (angle % 360) < 270


def tribe_arc_label_fits(text, width_deg, radius, font_size):
    """Whether a tangential band label fits the arc length available to it
    -- reuses kp_text_width's rough glyph-width estimate (see the Kings &
    Prophets chart above) against the arc's chord length at this radius.
    Small tribes/mothers (e.g. Zilpah's 6 people, Asher's 2) get too narrow
    an arc for their own name at any reasonable font size; skipping the
    label there rather than letting it overflow into a neighboring band is
    the same "selective direct labels" call already made for the mega-tribe
    bands and the minor-tribe leaves -- the sidebar legend and hover tooltip
    both still name every tribe."""
    arc_length = 2 * math.pi * radius * (width_deg / 360)
    return kp_text_width(text, font_size) + 6 <= arc_length


def tribe_is_left(angle):
    """For radial (outward-pointing) leaf labels -- text runs along the
    radius at rotation `a - 90`; left unflipped, the left half of the
    circle (not the bottom half -- a different boundary than
    tribe_is_bottom above) reads mirrored instead of outward, so add 180
    degrees (via `a + 90` and text-anchor "end") there."""
    return 180 < (angle % 360) < 360


def build_tribe_layout():
    """Pure data: mother -> tribe -> person angular layout, proportional to
    person counts at every level (a true nested sunburst). Tribes above
    TRIBE_MEGA_THRESHOLD get no individual leaf positions (render_tribe_
    sunburst_svg draws those as a solid band instead) since their per-leaf
    angular width would be too thin to label radially at any reasonable
    chart size."""
    by_tribe = collect_tribes()

    tribes = []
    for name, (mother_key, order) in TRIBE_MOTHER.items():
        people = by_tribe.get(name, [])
        tribes.append({
            "name": name, "mother": mother_key, "order": order,
            "color": TRIBE_COLOR_VAR[name],
            "is_mega": len(people) > TRIBE_MEGA_THRESHOLD,
            "people": people, "n": len(people),
        })
    mother_order = [m["key"] for m in TRIBE_MOTHERS]
    tribes.sort(key=lambda t: (mother_order.index(t["mother"]), t["order"]))

    total_people = sum(t["n"] for t in tribes)
    mother_totals = {m["key"]: 0 for m in TRIBE_MOTHERS}
    for t in tribes:
        mother_totals[t["mother"]] += t["n"]

    total_gap = TRIBE_MOTHER_GAP * len(TRIBE_MOTHERS)
    usable = 360 - total_gap
    cursor = -90
    mother_layout = {}
    for m in TRIBE_MOTHERS:
        frac = mother_totals[m["key"]] / total_people
        width = usable * frac
        mother_layout[m["key"]] = {"start": cursor, "end": cursor + width, "n": mother_totals[m["key"]]}
        cursor += width + TRIBE_MOTHER_GAP

    layout_tribes = []
    for m in TRIBE_MOTHERS:
        mkey = m["key"]
        mstart, mend = mother_layout[mkey]["start"], mother_layout[mkey]["end"]
        tribes_here = [t for t in tribes if t["mother"] == mkey]
        inner_span = (mend - mstart) - TRIBE_GAP * len(tribes_here)
        tcursor = mstart
        for t in tribes_here:
            tfrac = t["n"] / mother_totals[mkey] if mother_totals[mkey] else 0
            twidth = inner_span * tfrac
            t_start, t_end = tcursor, tcursor + twidth
            tcursor += twidth + TRIBE_GAP

            leaves = []
            if not t["is_mega"] and t["n"] > 0:
                step = (t_end - t_start) / t["n"]
                for i, person in enumerate(t["people"]):
                    leaves.append({**person, "angle": t_start + step * (i + 0.5)})

            layout_tribes.append({**t, "start": t_start, "end": t_end, "leaves": leaves})

    return {
        "mothers": [{**m, **mother_layout[m["key"]]} for m in TRIBE_MOTHERS],
        "tribes": layout_tribes,
        "total_people": total_people,
    }


def render_tribe_sunburst_svg(layout):
    cx, cy = TRIBE_CX, TRIBE_CY
    aria = (f'Sunburst of {layout["total_people"]} biblical people grouped by mother '
            f'(Leah, Rachel, Bilhah, Zilpah) and tribe')
    parts = [
        f'<svg id="tribe-chart-svg" viewBox="0 0 {cx*2} {cy*2}" width="{cx*2}" height="{cy*2}" '
        f'role="img" aria-label="{esc(aria)}" xmlns="http://www.w3.org/2000/svg" class="tsun-chart-svg">'
    ]

    # mother band
    parts.append("<g>")
    for m in layout["mothers"]:
        d = tribe_arc_path(cx, cy, TRIBE_MOTHER_R0, TRIBE_MOTHER_R1, m["start"], m["end"])
        parts.append(f'<path class="tsun-mother-arc" d="{d}" fill="{m["color"]}"></path>')
    parts.append("</g><g>")
    for m in layout["mothers"]:
        a = (m["start"] + m["end"]) / 2
        r = (TRIBE_MOTHER_R0 + TRIBE_MOTHER_R1) / 2
        width_deg = m["end"] - m["start"]
        label_text = f'{m["label"]} · {m["n"]}'
        font_size = 13.5
        if not tribe_arc_label_fits(label_text, width_deg, r, font_size):
            label_text = m["label"]
        if tribe_arc_label_fits(label_text, width_deg, r, font_size):
            x, y = tribe_polar(cx, cy, r, a)
            rot = a if not tribe_is_bottom(a) else a + 180
            parts.append(
                f'<text class="tsun-mother-label" x="{x:.1f}" y="{y:.1f}" text-anchor="middle" '
                f'transform="rotate({rot:.2f} {x:.1f} {y:.1f})" dominant-baseline="middle">'
                f"{esc(label_text)}</text>"
            )
    parts.append("</g>")

    # tribe band
    parts.append("<g>")
    for t in layout["tribes"]:
        d = tribe_arc_path(cx, cy, TRIBE_TRIBE_R0, TRIBE_TRIBE_R1, t["start"], t["end"])
        parts.append(f'<path class="tsun-tribe-arc" d="{d}" fill="{t["color"]}"></path>')
    parts.append("</g><g>")
    for t in layout["tribes"]:
        a = (t["start"] + t["end"]) / 2
        r = (TRIBE_TRIBE_R0 + TRIBE_TRIBE_R1) / 2
        width_deg = t["end"] - t["start"]
        fs = 10.5 if width_deg < 7 else 12.5
        if tribe_arc_label_fits(t["name"], width_deg, r, fs):
            x, y = tribe_polar(cx, cy, r, a)
            rot = a if not tribe_is_bottom(a) else a + 180
            parts.append(
                f'<text class="tsun-tribe-label" x="{x:.1f}" y="{y:.1f}" text-anchor="middle" '
                f'transform="rotate({rot:.2f} {x:.1f} {y:.1f})" dominant-baseline="middle" '
                f'style="font-size:{fs}px">{esc(t["name"])}</text>'
            )
    parts.append("</g>")

    # mega bands (Judah, Levi, Benjamin -- too many people to label radially)
    parts.append("<g>")
    for t in layout["tribes"]:
        if not t["is_mega"]:
            continue
        d = tribe_arc_path(cx, cy, TRIBE_TRIBE_R1, TRIBE_MEGA_R1, t["start"], t["end"])
        title = f'{t["n"]} people of the tribe of {t["name"]} — see the full list below the chart'
        parts.append(
            f'<path class="tsun-mega-arc" tabindex="0" data-tribe="{esc(t["name"])}" data-n="{t["n"]}" '
            f'd="{d}" fill="{t["color"]}">'
            f"<title>{esc(title)}</title></path>"
        )
        a = (t["start"] + t["end"]) / 2
        r = (TRIBE_TRIBE_R1 + TRIBE_MEGA_R1) / 2
        x, y = tribe_polar(cx, cy, r, a)
        rot = a if not tribe_is_bottom(a) else a + 180
        parts.append(
            f'<text class="tsun-mega-label" x="{x:.1f}" y="{y:.1f}" text-anchor="middle" '
            f'transform="rotate({rot:.2f} {x:.1f} {y:.1f})" dominant-baseline="middle">{t["n"]} people</text>'
        )
    parts.append("</g>")

    # minor-tribe individual leaves, each linked to its person page
    parts.append("<g>")
    for t in layout["tribes"]:
        if t["is_mega"]:
            continue
        for leaf in t["leaves"]:
            a = leaf["angle"]
            x0, y0 = tribe_polar(cx, cy, TRIBE_TRIBE_R1, a)
            x1, y1 = tribe_polar(cx, cy, TRIBE_LEAF_DOT_R, a)
            title = f'{leaf["name"]} — tribe of {t["name"]}, {leaf["reference"]}'
            if leaf["testament"] == "NT":
                # A New Testament tie to an Old Testament tribe is the
                # surprising fact this chart is built to surface (e.g. Anna
                # the prophetess, tribe of Asher, Luke 2:36) -- colored with
                # the site's existing --color-nt token (same one the "NT"
                # badge on person pages uses) rather than the tribe's own
                # hue, so it reads as "New Testament" at a glance instead of
                # blending into whichever tribe it happens to be under.
                dot = f'<circle class="tsun-leaf-dot-nt" cx="{x1:.1f}" cy="{y1:.1f}" r="5.5"></circle>'
            else:
                dot = f'<circle class="tsun-leaf-dot-ot" cx="{x1:.1f}" cy="{y1:.1f}" r="4"></circle>'
            parts.append(
                f'<a href="../people/{leaf["person_id"]}.html">'
                f'<g class="tsun-leaf" tabindex="0" data-name="{esc(leaf["name"])}" '
                f'data-tribe="{esc(t["name"])}" data-ref="{esc(leaf["reference"])}" '
                f'data-testament="{leaf["testament"]}">'
                f'<line class="tsun-leaf-hit" x1="{x0:.1f}" y1="{y0:.1f}" x2="{x1:.1f}" y2="{y1:.1f}"></line>'
                f'<line class="tsun-leaf-spoke" x1="{x0:.1f}" y1="{y0:.1f}" x2="{x1:.1f}" y2="{y1:.1f}" stroke="{t["color"]}"></line>'
                f"{dot}"
                f"<title>{esc(title)}</title>"
                f"</g></a>"
            )
    parts.append("</g><g>")
    for t in layout["tribes"]:
        if t["is_mega"]:
            continue
        for leaf in t["leaves"]:
            a = leaf["angle"]
            x, y = tribe_polar(cx, cy, TRIBE_LEAF_LABEL_R, a)
            left = tribe_is_left(a)
            rot = a - 90 if not left else a + 90
            anchor = "start" if not left else "end"
            label_cls = "tsun-leaf-label tsun-leaf-label-nt" if leaf["testament"] == "NT" else "tsun-leaf-label"
            parts.append(
                f'<text class="{label_cls}" x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}" '
                f'transform="rotate({rot:.2f} {x:.1f} {y:.1f})" dominant-baseline="middle">{esc(leaf["name"])}</text>'
            )
    parts.append("</g>")

    # hub
    parts.append(
        f'<g class="tsun-hub">'
        f'<circle cx="{cx}" cy="{cy}" r="{TRIBE_HUB_R}"></circle>'
        f'<text x="{cx}" y="{cy - 6}" text-anchor="middle" class="tsun-hub-title">JACOB</text>'
        f'<text x="{cx}" y="{cy + 13}" text-anchor="middle" class="tsun-hub-sub">ISRAEL</text>'
        f"</g>"
    )

    parts.append("</svg>")
    return "\n".join(parts)


def render_tribe_legend(layout):
    rows = []
    for m in layout["mothers"]:
        chips = "\n      ".join(
            f'<span class="tsun-chip"><span class="tsun-chip-dot" style="background:{t["color"]}"></span>'
            f'{esc(t["name"])} <span class="tsun-chip-n">{t["n"]}</span></span>'
            for t in layout["tribes"] if t["mother"] == m["key"]
        )
        rows.append(
            f'<div class="tsun-legend-row">'
            f'<div class="tsun-legend-head"><span class="tsun-swatch" style="background:{m["color"]}"></span>'
            f'<span class="tsun-legend-name">{esc(m["label"])} <span class="tsun-legend-count">{m["n"]}</span></span></div>'
            f'<span class="tsun-legend-desc">{esc(m["desc"])}</span>'
            f'<div class="tsun-chips">{chips}</div>'
            f"</div>"
        )
    return '<div class="tsun-legend">' + "\n    ".join(rows) + "</div>"


def render_tribe_table(layout):
    rows = []
    for t in layout["tribes"]:
        people = t["people"]
        rows.append(f'<tr><th colspan="3">{esc(t["name"])} <span class="tsun-table-count">({len(people)})</span></th></tr>')
        for p in people:
            row_cls = ' class="tsun-table-row-nt"' if p["testament"] == "NT" else ""
            rows.append(
                f'<tr{row_cls}><td><a href="../people/{p["person_id"]}.html">{esc(p["name"])}</a></td>'
                f'<td>{esc(p["testament"])}</td><td>{esc(p["reference"])}</td></tr>'
            )
    body = "\n    ".join(rows)
    return f"""<details class="kp-table-details">
    <summary>View all {layout["total_people"]} people as a table</summary>
    <div class="table-scroll">
    <table class="kp-table">
      <thead><tr><th>Name</th><th>Testament</th><th>Reference</th></tr></thead>
      <tbody>
    {body}
      </tbody>
    </table>
    </div>
  </details>"""


def build_tribe_sunburst_chart_page(layout):
    base = "../"
    canonical = f"{SITE_URL}/charts/twelve-tribes.html"
    title = "The Twelve Tribes, By Mother — Lives of Scripture"
    description = (f'{layout["total_people"]} biblical people grouped by which of Jacob\'s four wives they '
                    f"descend from, then by tribe, in one sunburst chart.")
    breadcrumb_ld = breadcrumb_json_ld([
        ("Home", f"{SITE_URL}/"), ("Charts", f"{SITE_URL}/charts.html"),
        (title.replace(" — Lives of Scripture", ""), None),
    ])

    svg = render_tribe_sunburst_svg(layout)
    legend = render_tribe_legend(layout)
    table = render_tribe_table(layout)
    mega_names = ", ".join(t["name"] for t in layout["tribes"] if t["is_mega"])

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
<script type="application/ld+json">
{breadcrumb_ld}
</script>
</head>
<body>
{header_html(base, "charts.html")}

<main>
  <p><a href="{base}charts.html">&larr; Charts</a></p>
  <h2>The Twelve Tribes, By Mother</h2>
  <p class="page-intro">{layout["total_people"]} people whose tribal descent Scripture states or the genealogy
  record traces, grouped first by which of Jacob's four wives they descend from, then by tribe. This is
  deliberately a minority of the site's full-tier people — see the disclaimer below.</p>

  {legend}

  <div class="kp-legend-row">
    <span class="tsun-testament-key"><span class="tsun-tk-dot tsun-tk-ot"></span> Old Testament
      &nbsp;&nbsp;<span class="tsun-tk-dot tsun-tk-nt"></span> New Testament</span>
    <div class="kp-chart-toolbar">
    <button type="button" class="kp-chart-copy" id="tribe-chart-copy">&#128203; Copy image</button>
    <button type="button" class="kp-chart-expand" id="tribe-chart-expand">&#128269; View larger</button>
    </div>
  </div>

  <div class="kp-chart-scroll">
  {svg}
  </div>

  <p class="kp-disclaimer">Only people whose tribe Scripture states explicitly, or whose genealogy chain
  traces back to one of the twelve tribal heads, carry this field — most full-tier people (pre-Jacob
  patriarchs, Gentiles, foreign officials, and virtually every New Testament figure) simply have no tribe
  the text ever states. {esc(mega_names)} are shown as solid bands rather than individual spokes — too many
  people to label radially at a readable size — see the full list in the table below the chart. A tribe is
  an Old Testament concept; the few New Testament figures here (filled purple dots and bold names below) are
  people the NT text itself states descend from that tribe — Anna the prophetess, tribe of Asher
  (Luke 2:36), is the only one small enough a tribe to show up as her own spoke; Jesus' own family (Judah),
  Zacharias, Elizabeth, John the Baptist, and Barnabas (Levi), and Paul (Benjamin) are all folded into
  those tribes' solid bands and named in the table instead.</p>

  {table}
</main>

{footer_html(base)}

<script src="{base}js/app.js"></script>
<script>initNavToggle(); initTribeChartTooltips(); initChartLightbox("tribe-chart-expand", "tribe-chart-svg", "Twelve Tribes sunburst, enlarged"); initChartCopyButton("tribe-chart-copy", "tribe-chart-svg");</script>
</body>
</html>
"""


# ---------------------------------------------------------------------
# "Job — Main Speaker by Chapter" chart (charts.html hub + charts/job-chapters.html)
# ---------------------------------------------------------------------

# The book of Job is unusually well suited to a "who's speaking this
# chapter" chart: apart from the prologue (1-2) and epilogue portion of 42,
# its chapters are structured as a strict sequence of monologues, each
# introduced by the text's own "Then X answered and said" formula (e.g.
# Job 4:1, 8:1, 11:1, 32:6, 38:1) -- the same verses already cited as each
# speaker's `references` entries on their person pages. This mapping is a
# direct reading of those speech-introduction formulas, not an inference or
# extra-biblical tradition -- see CLAUDE.md's Factual Accuracy section.
#
# Two spots are genuinely disputed rather than picked silently (see the
# on-page disclaimer below): Bildad's third speech (ch. 25) is unusually
# short and Zophar never gets a stated third speech, which some scholars
# read as a sign of textual displacement in chs. 26-27; and ch. 28's wisdom
# poem has no new speech-introduction formula of its own, so it's kept as
# a continuation of Job's discourse (the received-text reading) rather than
# treated as a separate narratorial interlude, a view some scholars hold.
JC_SPEAKERS = {
    "job": {"label": "Job", "person_id": "job", "color_var": "var(--jc-job)"},
    "eliphaz": {"label": "Eliphaz", "person_id": "eliphaz-2", "color_var": "var(--jc-eliphaz)"},
    "bildad": {"label": "Bildad", "person_id": "bildad", "color_var": "var(--jc-bildad)"},
    "zophar": {"label": "Zophar", "person_id": "zophar", "color_var": "var(--jc-zophar)"},
    "elihu": {"label": "Elihu", "person_id": "elihu-5", "color_var": "var(--jc-elihu)"},
    "lord": {"label": "The LORD", "person_id": None, "color_var": "var(--jc-lord)"},
    "prologue": {"label": "Prologue", "person_id": None, "color_var": "var(--gen-shared)"},
}

JC_CHAPTERS = [
    {"chapter": 1, "speaker": "prologue", "reference": "Job 1:1-22",
     "note": "Job's character and prosperity; the LORD and Satan's exchange; Job loses his children and possessions."},
    {"chapter": 2, "speaker": "prologue", "reference": "Job 2:1-13",
     "note": "Job's health is struck; his wife's words; Eliphaz, Bildad, and Zophar arrive and sit with him in silence."},
    {"chapter": 3, "speaker": "job", "reference": "Job 3:1-26", "note": "Job breaks his silence and curses the day of his birth."},
    {"chapter": 4, "speaker": "eliphaz", "reference": "Job 4:1", "note": "Eliphaz's first speech (chs. 4-5)."},
    {"chapter": 5, "speaker": "eliphaz", "reference": "Job 4:1", "note": "Eliphaz's first speech continues."},
    {"chapter": 6, "speaker": "job", "reference": "Job 6:1", "note": "Job's reply (chs. 6-7)."},
    {"chapter": 7, "speaker": "job", "reference": "Job 6:1", "note": "Job's reply continues."},
    {"chapter": 8, "speaker": "bildad", "reference": "Job 8:1", "note": "Bildad's first speech."},
    {"chapter": 9, "speaker": "job", "reference": "Job 9:1", "note": "Job's reply (chs. 9-10)."},
    {"chapter": 10, "speaker": "job", "reference": "Job 9:1", "note": "Job's reply continues."},
    {"chapter": 11, "speaker": "zophar", "reference": "Job 11:1", "note": "Zophar's first speech."},
    {"chapter": 12, "speaker": "job", "reference": "Job 12:1", "note": "Job's reply (chs. 12-14)."},
    {"chapter": 13, "speaker": "job", "reference": "Job 12:1", "note": "Job's reply continues."},
    {"chapter": 14, "speaker": "job", "reference": "Job 12:1", "note": "Job's reply continues."},
    {"chapter": 15, "speaker": "eliphaz", "reference": "Job 15:1", "note": "Eliphaz's second speech."},
    {"chapter": 16, "speaker": "job", "reference": "Job 16:1", "note": "Job's reply (chs. 16-17)."},
    {"chapter": 17, "speaker": "job", "reference": "Job 16:1", "note": "Job's reply continues."},
    {"chapter": 18, "speaker": "bildad", "reference": "Job 18:1", "note": "Bildad's second speech."},
    {"chapter": 19, "speaker": "job", "reference": "Job 19:1", "note": "Job's reply, including “I know that my Redeemer lives” (19:25)."},
    {"chapter": 20, "speaker": "zophar", "reference": "Job 20:1", "note": "Zophar's second speech."},
    {"chapter": 21, "speaker": "job", "reference": "Job 21:1", "note": "Job's reply."},
    {"chapter": 22, "speaker": "eliphaz", "reference": "Job 22:1", "note": "Eliphaz's third speech."},
    {"chapter": 23, "speaker": "job", "reference": "Job 23:1", "note": "Job's reply (chs. 23-24)."},
    {"chapter": 24, "speaker": "job", "reference": "Job 23:1", "note": "Job's reply continues."},
    {"chapter": 25, "speaker": "bildad", "reference": "Job 25:1",
     "note": "Bildad's third speech — unusually brief, six verses. Zophar never gives a stated third speech; see the chart disclaimer."},
    {"chapter": 26, "speaker": "job", "reference": "Job 26:1", "note": "Job's reply, continuing through ch. 31."},
    {"chapter": 27, "speaker": "job", "reference": "Job 27:1", "note": "Job continues his discourse, maintaining his innocence."},
    {"chapter": 28, "speaker": "job", "reference": "Job 28:1", "note": "A meditation on where wisdom is found; see the chart disclaimer."},
    {"chapter": 29, "speaker": "job", "reference": "Job 29:1", "note": "Job recalls his former honor."},
    {"chapter": 30, "speaker": "job", "reference": "Job 29:1", "note": "Job describes his present humiliation."},
    {"chapter": 31, "speaker": "job", "reference": "Job 31:1", "note": "Job's closing oath of innocence; “the words of Job are ended” (31:40)."},
    {"chapter": 32, "speaker": "elihu", "reference": "Job 32:1-6", "note": "Elihu, a younger bystander, speaks after the three friends fall silent."},
    {"chapter": 33, "speaker": "elihu", "reference": "Job 33:1", "note": "Elihu's first speech continues, addressed directly to Job."},
    {"chapter": 34, "speaker": "elihu", "reference": "Job 34:1", "note": "Elihu's second speech."},
    {"chapter": 35, "speaker": "elihu", "reference": "Job 35:1", "note": "Elihu's third speech."},
    {"chapter": 36, "speaker": "elihu", "reference": "Job 36:1", "note": "Elihu's fourth speech (chs. 36-37)."},
    {"chapter": 37, "speaker": "elihu", "reference": "Job 36:1", "note": "Elihu's fourth speech continues."},
    {"chapter": 38, "speaker": "lord", "reference": "Job 38:1", "note": "The LORD answers Job out of the whirlwind (38:1-40:2)."},
    {"chapter": 39, "speaker": "lord", "reference": "Job 38:1", "note": "The LORD's first speech continues, describing His creation."},
    {"chapter": 40, "speaker": "lord", "reference": "Job 40:1-6", "note": "The LORD's first speech ends; Job briefly answers (40:3-5); the LORD's second speech begins."},
    {"chapter": 41, "speaker": "lord", "reference": "Job 40:6", "note": "The LORD's second speech continues, describing Leviathan."},
    {"chapter": 42, "speaker": "job", "reference": "Job 42:1-17",
     "note": "Job's final answer to God (42:1-6); the LORD rebukes the three friends and restores Job's fortunes, family, and long life (42:7-17)."},
]


JC_ROW_ORDER = ["prologue", "job", "eliphaz", "bildad", "zophar", "elihu", "lord"]


def jc_group_runs(chapters):
    """Collapse the 42 per-chapter entries into per-speech runs -- e.g.
    Job's chs. 6-7 reply is one continuous run, not two separate chapters
    -- by merging consecutive chapters that share a speaker. This is what
    turns the flat chapter list into timeline bars, one bar per speech."""
    runs = []
    for entry in chapters:
        if runs and runs[-1]["speaker"] == entry["speaker"] and runs[-1]["end"] == entry["chapter"] - 1:
            runs[-1]["end"] = entry["chapter"]
        else:
            runs.append({
                "speaker": entry["speaker"],
                "start": entry["chapter"],
                "end": entry["chapter"],
                "reference": entry["reference"],
                "note": entry["note"],
            })
    return runs


def render_job_chapters_svg(chapters):
    runs = jc_group_runs(chapters)
    rows = {key: [r for r in runs if r["speaker"] == key] for key in JC_ROW_ORDER}

    total_chapters = 42
    margin_left, margin_right = 16, 16
    plot_width = 1760
    bar_h = 34
    row_label_h = 38
    row_gap = 16
    axis_h = 34
    bar_font_size = 22
    tick_step = 5

    def x_of(boundary):
        return margin_left + boundary / total_chapters * plot_width

    total_h = axis_h + len(JC_ROW_ORDER) * (row_label_h + bar_h) + (len(JC_ROW_ORDER) - 1) * row_gap + 8
    total_w = margin_left + plot_width + margin_right

    parts = [
        f'<svg id="job-chart-svg" viewBox="0 0 {total_w} {total_h}" width="{total_w}" height="{total_h}" role="img" '
        f'aria-label="Timeline of all 42 chapters of Job, one row per speaker, showing which chapters each one speaks in" '
        f'xmlns="http://www.w3.org/2000/svg" class="kp-chart-svg jc-timeline-svg">'
    ]

    # Chapter gridlines + axis labels, spanning the full plot height. Text
    # sizes here (see the CSS ".jc-timeline-svg" rules) are bumped up from
    # the Kings & Prophets chart this layout is based on -- not to render
    # bigger natively (this chart is scaled responsively to fit its
    # container width, see ".kp-chart-scroll .jc-timeline-svg" in the CSS,
    # so it never needs the horizontal scrolling the other three charts
    # rely on), but so the *displayed* text, after that scale-down, reads
    # larger than the other charts' native size rather than smaller. Row
    # labels and axis ticks sit in open space and can run large; bar_font_size
    # stays more modest because it's the one genuinely space-constrained
    # element -- some two-chapter runs (e.g. "16–17") are only just wide
    # enough to hold their own label inline at this size, verified against
    # kp_bar_label_fits's width estimate with a safety margin, and the
    # geometry below (bar_h/row_label_h/axis_h/plot_width) matches.
    y_axis_top = axis_h
    y_axis_bottom = total_h - 4
    tick_chapters = sorted(set([1] + list(range(tick_step, total_chapters, tick_step)) + [total_chapters]))
    for tick in tick_chapters:
        boundary = tick - 1 if tick < total_chapters else total_chapters
        tx = x_of(boundary)
        parts.append(f'<line x1="{tx:.1f}" y1="{y_axis_top}" x2="{tx:.1f}" y2="{y_axis_bottom}" class="kp-gridline" />')
        parts.append(f'<text x="{tx:.1f}" y="26" class="kp-axis-label" text-anchor="middle">{tick}</text>')

    y = axis_h
    for key in JC_ROW_ORDER:
        speaker = JC_SPEAKERS[key]
        parts.append(f'<text x="{margin_left}" y="{y + 30}" class="kp-row-label">{esc(speaker["label"])}</text>')
        lane_y = y + row_label_h

        for run in rows[key]:
            x1 = x_of(run["start"] - 1)
            x2 = x_of(run["end"])
            bw = max(2.0, x2 - x1)
            chapter_label = str(run["start"]) if run["start"] == run["end"] else f'{run["start"]}–{run["end"]}'
            title = f'Job {chapter_label} — {speaker["label"]}. {run["note"]} ({run["reference"]})'
            rect = (
                f'<rect x="{x1:.1f}" y="{lane_y:.1f}" width="{bw:.1f}" height="{bar_h}" rx="4" '
                f'fill="{speaker["color_var"]}" class="kp-bar" tabindex="0" '
                f'data-name="{esc(speaker["label"])}" data-nation="Job {esc(chapter_label)}" '
                f'data-span="{esc(run["note"])}" data-reference="{esc(run["reference"])}">'
                f'<title>{esc(title)}</title></rect>'
            )
            label_el = ""
            if kp_bar_label_fits(chapter_label, bw, font_size=bar_font_size):
                label_el = (
                    f'<text x="{x1 + bw / 2:.1f}" y="{lane_y + bar_h / 2 + 7.5:.1f}" '
                    f'class="kp-bar-label" text-anchor="middle">{esc(chapter_label)}</text>'
                )
            if speaker["person_id"]:
                href = f'../people/{speaker["person_id"]}.html'
                parts.append(f'<a href="{href}">{rect}{label_el}</a>')
            else:
                parts.append(rect + label_el)

        y += row_label_h + bar_h + row_gap

    parts.append("</svg>")
    return "\n".join(parts)


def render_job_chapters_legend():
    items = "\n    ".join(
        f'<span class="kp-legend-item"><span class="kp-legend-swatch" style="background:{s["color_var"]}"></span>{esc(s["label"])}</span>'
        for s in JC_SPEAKERS.values()
    )
    return f'<div class="kp-legend jc-timeline-legend">{items}</div>'


def render_job_chapters_table(chapters):
    def row_html(entry):
        speaker = JC_SPEAKERS[entry["speaker"]]
        name_cell = (
            f'<a href="../people/{speaker["person_id"]}.html">{esc(speaker["label"])}</a>'
            if speaker["person_id"] else esc(speaker["label"])
        )
        return (
            f'<tr><td>{entry["chapter"]}</td><td>{name_cell}</td>'
            f'<td>{esc(entry["reference"])}</td><td>{esc(entry["note"])}</td></tr>'
        )

    body_rows = "\n    ".join(row_html(e) for e in chapters)
    return f"""<details class="kp-table-details">
    <summary>View as a table</summary>
    <div class="table-scroll">
    <table class="kp-table">
      <thead><tr><th>Chapter</th><th>Speaker</th><th>Reference</th><th>Note</th></tr></thead>
      <tbody>
    {body_rows}
      </tbody>
    </table>
    </div>
  </details>"""


def build_job_chapters_chart_page(chapters):
    base = "../"
    canonical = f"{SITE_URL}/charts/job-chapters.html"
    title = "Job — Main Speaker by Chapter — Lives of Scripture"
    description = "Every speech in the book of Job, one row per speaker, laid out across all 42 chapters as a timeline."
    breadcrumb_ld = breadcrumb_json_ld([
        ("Home", f"{SITE_URL}/"), ("Charts", f"{SITE_URL}/charts.html"),
        (title.replace(" — Lives of Scripture", ""), None),
    ])

    svg = render_job_chapters_svg(chapters)
    legend = render_job_chapters_legend()
    table = render_job_chapters_table(chapters)

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
<script type="application/ld+json">
{breadcrumb_ld}
</script>
</head>
<body>
{header_html(base, "charts.html")}

<main>
  <p><a href="{base}charts.html">&larr; Charts</a></p>
  <h2>Job &mdash; Main Speaker by Chapter</h2>
  <p class="page-intro">Apart from the prologue and part of the epilogue, the book of Job is a sequence of
  monologues — Job, his three friends, Elihu, and finally the LORD, each in turn. Each row below is one
  speaker; each bar is one unbroken speech, laid out across Job's 42 chapters left to right, so you can see
  at a glance how often — and how briefly — Job's three friends get a turn compared to his own replies.
  Bars are clickable and link to that person's page. Hover or focus a bar for the verse where that speech
  begins.</p>

  <div class="kp-legend-row">
    {legend}
    <div class="kp-chart-toolbar">
    <button type="button" class="kp-chart-copy" id="job-chart-copy">&#128203; Copy image</button>
    <button type="button" class="kp-chart-expand" id="job-chart-expand">&#128269; View larger</button>
    </div>
  </div>

  <div class="kp-chart-scroll">
  {svg}
  </div>

  <p class="kp-disclaimer">Bildad's third speech (ch. 25) is unusually short, and Zophar never gives a
  stated third speech. This chart follows the received text as printed, which continuously credits
  chs. 26-31 to Job (see 27:1, &ldquo;Then Job continued his discourse&rdquo;), including the meditation
  on wisdom in ch. 28.</p>

  {table}
</main>

{footer_html(base)}

<script src="{base}js/app.js"></script>
<script>initNavToggle(); initKpChartTooltips(); initChartLightbox("job-chart-expand", "job-chart-svg", "Job — Main Speaker by Chapter, enlarged"); initChartCopyButton("job-chart-copy", "job-chart-svg");</script>
</body>
</html>
"""


# ---------------------------------------------------------------------
# "Genesis — Main Characters by Chapter" chart (charts.html hub +
# charts/genesis-chapters.html)
# ---------------------------------------------------------------------

# Genesis follows several overlapping generations rather than one continuous
# drama, so unlike Job's "who is speaking" question, this chart asks "whose
# story is the text following" in each chapter -- the person whose actions
# or words drive that chapter's narrative. Chapters with no single human
# protagonist (the creation week; the "these are the generations of..."
# genealogical lists in chs. 5, 10, 11, and 36) are grouped under
# "Creation & Genealogies" and reuse --gen-shared, the same "not a
# competing identity" role that variable plays on the Job and genealogies
# charts (see CLAUDE.md's Genealogy / Connections Graph section on why
# these lists matter to the site even without narrative content).
#
# A handful of chapters required a judgment call rather than a clean single
# answer -- flagged on the page itself rather than picked silently, per
# CLAUDE.md's Factual Accuracy section:
#   - Ch. 25 covers both Abraham's death (25:1-11) and the birth of Esau
#     and Jacob plus the birthright sale (25:19-34); it's grouped under
#     Jacob since that event sets up the rest of the book, but the chapter
#     note says so explicitly.
#   - Ch. 44 (the planted silver cup) is grouped under Judah, not Joseph --
#     Joseph's steward sets up the test in the first half, but the
#     chapter's back half is Judah's extended, pivotal plea to take
#     Benjamin's place as a slave (44:18-34), usually read as the turning
#     point of his own character arc.
#   - Jacob is renamed Israel partway through the book (32:22-32); the row
#     is labeled "Jacob" throughout for a single consistent label (as
#     Genesis itself keeps calling him through most of the following
#     chapters) but links to the person page at "israel", the site's
#     full-tier person_id for him -- see CLAUDE.md's Name Disambiguation
#     section on the same "jacob" stub / "israel" full-tier split.
#
# Sarah, Rebekah, and Rachel each get their own overlapping secondary-worker
# row (added 2026-08-12, same pattern as --acc-barnabas on the Acts chart --
# see GC_SECONDARY_SPANS below): each is a major figure with sustained,
# independently-narrated agency across chapters already colored for the
# patriarch whose row they share, not a competing "whose story" assignment
# for those chapters. Esau, Leah, and Hagar were considered and left out --
# a scope decision, not a claim their roles were minor -- since none has as
# many chapters of *independent* narrated agency (dialogue, decisive action)
# as the three included; Tamar's ch. 38 role is folded into Judah's row
# without a secondary bar for the same reason (a single chapter, already the
# kind of single-chapter judgment call this page flags via disclaimer rather
# than a dedicated row, matching how Acts ch. 9's Peter/Paul split was
# handled).
GC_SPEAKERS = {
    "narrator": {"label": "Creation & Genealogies", "person_id": None, "color_var": "var(--gen-shared)"},
    "adam_eve": {"label": "Adam & Eve", "person_id": "adam", "color_var": "var(--gnc-adam-eve)"},
    "cain": {"label": "Cain", "person_id": "cain", "color_var": "var(--gnc-cain)"},
    "noah": {"label": "Noah", "person_id": "noah", "color_var": "var(--gnc-noah)"},
    "abraham": {"label": "Abraham", "person_id": "abraham", "color_var": "var(--gnc-abraham)"},
    "sarah": {"label": "Sarah", "person_id": "sarah", "color_var": "var(--gnc-sarah)"},
    "lot": {"label": "Lot", "person_id": "lot", "color_var": "var(--gnc-lot)"},
    "isaac": {"label": "Isaac", "person_id": "isaac", "color_var": "var(--gnc-isaac)"},
    "rebekah": {"label": "Rebekah", "person_id": "rebekah", "color_var": "var(--gnc-rebekah)"},
    "jacob": {"label": "Jacob", "person_id": "israel", "color_var": "var(--gnc-jacob)"},
    "rachel": {"label": "Rachel", "person_id": "rachel", "color_var": "var(--gnc-rachel)"},
    "dinah": {"label": "Dinah", "person_id": "dinah", "color_var": "var(--gnc-dinah)"},
    "joseph": {"label": "Joseph", "person_id": "joseph", "color_var": "var(--gnc-joseph)"},
    "judah": {"label": "Judah", "person_id": "judah", "color_var": "var(--gnc-judah)"},
}

GC_ROW_ORDER = [
    "narrator", "adam_eve", "cain", "noah", "abraham", "sarah", "lot", "isaac",
    "rebekah", "jacob", "rachel", "dinah", "joseph", "judah",
]

GC_SECONDARY_ROWS = ("sarah", "rebekah", "rachel")

# Secondary-worker presence spans -- independent of GC_CHAPTERS/jc_group_runs,
# since that mechanism assigns exactly one "whose story" speaker per chapter
# and these three rows are deliberately overlapping, not a replacement for
# an existing chapter's speaker (same approach as ACC_BARNABAS_SPANS above).
GC_SECONDARY_SPANS = {
    "sarah": [
        {"start": 16, "end": 18, "reference": "Genesis 16",
         "note": "Sarai gives her servant Hagar to Abram, then deals harshly with her after Hagar conceives; renamed Sarah, she laughs to herself when the LORD's visitors promise her a son within the year."},
        {"start": 20, "end": 21, "reference": "Genesis 20",
         "note": "Abraham again passes Sarah off as his sister, this time to Abimelech; after Isaac is born to her, Sarah insists that Hagar and Ishmael be sent away."},
        {"start": 23, "end": 23, "reference": "Genesis 23",
         "note": "Sarah dies at Kiriath-arba, and Abraham buys the cave of Machpelah from the Hittites as her burial site."},
    ],
    "rebekah": [
        {"start": 24, "end": 24, "reference": "Genesis 24",
         "note": "Abraham's servant meets Rebekah at the well and asks her family for her hand; she agrees to leave home at once and marries Isaac."},
        {"start": 27, "end": 27, "reference": "Genesis 27",
         "note": "Overhearing Isaac's plan to bless Esau, Rebekah orchestrates Jacob's deception, dressing him in Esau's clothes and preparing his father's favorite food."},
    ],
    "rachel": [
        {"start": 30, "end": 31, "reference": "Genesis 30",
         "note": "Rachel demands children from Jacob and gives him her servant Bilhah; fleeing with Jacob from Laban, she secretly steals her father's household idols and lies about it."},
        {"start": 35, "end": 35, "reference": "Genesis 35",
         "note": "Rachel dies giving birth to Benjamin on the road to Ephrath, naming him with her dying breath before Jacob buries her there."},
    ],
}

GC_CHAPTERS = [
    {"chapter": 1, "speaker": "narrator", "reference": "Genesis 1",
     "note": "The six days of creation, culminating in mankind, male and female, made in God's image."},
    {"chapter": 2, "speaker": "adam_eve", "reference": "Genesis 2",
     "note": "The LORD God forms the man from the dust, plants the garden of Eden, and forms the woman from the man's side."},
    {"chapter": 3, "speaker": "adam_eve", "reference": "Genesis 3",
     "note": "The serpent tempts the woman and the man to eat the forbidden fruit; God pronounces judgment and they are driven from Eden."},
    {"chapter": 4, "speaker": "cain", "reference": "Genesis 4",
     "note": "Cain murders his brother Abel over their offerings and is exiled; his line and the birth of Seth follow."},
    {"chapter": 5, "speaker": "narrator", "reference": "Genesis 5",
     "note": "The genealogy from Adam to Noah, including Enoch, who “walked with God,” and Methuselah's 969 years."},
    {"chapter": 6, "speaker": "noah", "reference": "Genesis 6",
     "note": "Human wickedness fills the earth; God resolves to send a flood but instructs righteous Noah to build an ark."},
    {"chapter": 7, "speaker": "noah", "reference": "Genesis 7",
     "note": "Noah, his family, and the animals enter the ark; the flood covers the earth."},
    {"chapter": 8, "speaker": "noah", "reference": "Genesis 8",
     "note": "The floodwaters recede; Noah leaves the ark and offers a sacrifice to the LORD."},
    {"chapter": 9, "speaker": "noah", "reference": "Genesis 9",
     "note": "God's covenant with Noah, sealed by the rainbow; Noah's drunkenness and the curse on Canaan."},
    {"chapter": 10, "speaker": "narrator", "reference": "Genesis 10",
     "note": "The Table of Nations — the descendants of Noah's three sons, Shem, Ham, and Japheth, spread across the earth."},
    {"chapter": 11, "speaker": "narrator", "reference": "Genesis 11",
     "note": "Mankind builds the tower of Babel and God confuses their language; the genealogy from Shem to Terah, Abram's father."},
    {"chapter": 12, "speaker": "abraham", "reference": "Genesis 12",
     "note": "The LORD calls Abram to Canaan with a promise of blessing; famine drives him to Egypt, where he deceives Pharaoh about Sarai."},
    {"chapter": 13, "speaker": "abraham", "reference": "Genesis 13",
     "note": "Abram and his nephew Lot separate over their growing herds; Lot chooses the well-watered plain near Sodom."},
    {"chapter": 14, "speaker": "abraham", "reference": "Genesis 14",
     "note": "Abram rescues Lot from four invading kings and is blessed by Melchizedek, king of Salem and priest of God Most High."},
    {"chapter": 15, "speaker": "abraham", "reference": "Genesis 15",
     "note": "The LORD makes a covenant with Abram; his faith “was credited to him as righteousness.”"},
    {"chapter": 16, "speaker": "abraham", "reference": "Genesis 16",
     "note": "Sarai gives her servant Hagar to Abram; Hagar bears Ishmael after fleeing into the wilderness."},
    {"chapter": 17, "speaker": "abraham", "reference": "Genesis 17",
     "note": "God establishes circumcision as the covenant sign and renames Abram and Sarai as Abraham and Sarah."},
    {"chapter": 18, "speaker": "abraham", "reference": "Genesis 18",
     "note": "Three visitors promise Sarah a son within the year; Abraham intercedes with the LORD over Sodom."},
    {"chapter": 19, "speaker": "lot", "reference": "Genesis 19",
     "note": "Two angels rescue Lot from Sodom before its destruction; his wife looks back and becomes a pillar of salt."},
    {"chapter": 20, "speaker": "abraham", "reference": "Genesis 20",
     "note": "Abraham again passes Sarah off as his sister, this time to Abimelech, king of Gerar."},
    {"chapter": 21, "speaker": "abraham", "reference": "Genesis 21",
     "note": "Isaac is born; Hagar and Ishmael are sent away; Abraham makes a treaty with Abimelech at Beersheba."},
    {"chapter": 22, "speaker": "abraham", "reference": "Genesis 22",
     "note": "God tests Abraham by commanding him to sacrifice Isaac; the LORD provides a ram in his place."},
    {"chapter": 23, "speaker": "abraham", "reference": "Genesis 23",
     "note": "Sarah dies, and Abraham buys the cave of Machpelah from the Hittites as a family burial site."},
    {"chapter": 24, "speaker": "isaac", "reference": "Genesis 24",
     "note": "Abraham's servant travels to Abraham's homeland and returns with Rebekah as a bride for Isaac."},
    {"chapter": 25, "speaker": "jacob", "reference": "Genesis 25",
     "note": "Abraham dies and is buried beside Sarah (25:1-11); Rebekah bears twins, and Esau sells his birthright to Jacob for a bowl of stew."},
    {"chapter": 26, "speaker": "isaac", "reference": "Genesis 26",
     "note": "Isaac repeats his father's deception about his wife, re-digs Abraham's wells, and makes a treaty with Abimelech."},
    {"chapter": 27, "speaker": "jacob", "reference": "Genesis 27",
     "note": "With his mother Rebekah's help, Jacob deceives his aging, nearly blind father Isaac into giving him Esau's blessing."},
    {"chapter": 28, "speaker": "jacob", "reference": "Genesis 28",
     "note": "Fleeing Esau's anger, Jacob dreams of a stairway to heaven at Bethel, and the LORD renews the covenant promise to him."},
    {"chapter": 29, "speaker": "jacob", "reference": "Genesis 29",
     "note": "Jacob arrives at his uncle Laban's household, is tricked into marrying Leah, then marries Rachel as well."},
    {"chapter": 30, "speaker": "jacob", "reference": "Genesis 30",
     "note": "Jacob's sons are born to Leah, Rachel, and their servants; Jacob grows wealthy through selective breeding of Laban's flocks."},
    {"chapter": 31, "speaker": "jacob", "reference": "Genesis 31",
     "note": "Jacob flees from Laban with his family and flocks; the two make a covenant of peace at Mizpah."},
    {"chapter": 32, "speaker": "jacob", "reference": "Genesis 32",
     "note": "Jacob sends gifts ahead to appease Esau and wrestles with God at Peniel, receiving the name Israel."},
    {"chapter": 33, "speaker": "jacob", "reference": "Genesis 33",
     "note": "Jacob and Esau are reconciled; Jacob settles near Shechem."},
    {"chapter": 34, "speaker": "dinah", "reference": "Genesis 34",
     "note": "Shechem violates Jacob's daughter Dinah; her brothers Simeon and Levi avenge her by deceiving and slaughtering the men of his city."},
    {"chapter": 35, "speaker": "jacob", "reference": "Genesis 35",
     "note": "Jacob returns to Bethel; Rachel dies giving birth to Benjamin; Isaac dies at Hebron."},
    {"chapter": 36, "speaker": "narrator", "reference": "Genesis 36",
     "note": "The genealogy of Esau, ancestor of the Edomites."},
    {"chapter": 37, "speaker": "joseph", "reference": "Genesis 37",
     "note": "Joseph's dreams of ruling over his family provoke his brothers, who sell him into slavery in Egypt."},
    {"chapter": 38, "speaker": "judah", "reference": "Genesis 38",
     "note": "Judah's daughter-in-law Tamar disguises herself to secure an heir after his sons' deaths; Judah admits, “she is more righteous than I.”"},
    {"chapter": 39, "speaker": "joseph", "reference": "Genesis 39",
     "note": "Joseph rises to oversee Potiphar's house, then is falsely accused and imprisoned after refusing Potiphar's wife."},
    {"chapter": 40, "speaker": "joseph", "reference": "Genesis 40",
     "note": "In prison, Joseph correctly interprets the dreams of Pharaoh's cupbearer and baker."},
    {"chapter": 41, "speaker": "joseph", "reference": "Genesis 41",
     "note": "Joseph interprets Pharaoh's dreams of coming famine and is made ruler over all Egypt."},
    {"chapter": 42, "speaker": "joseph", "reference": "Genesis 42",
     "note": "Joseph's brothers come to Egypt for grain and do not recognize him; he accuses them of spying and keeps Simeon."},
    {"chapter": 43, "speaker": "joseph", "reference": "Genesis 43",
     "note": "The brothers return with Benjamin as Joseph required; Joseph weeps privately and hosts them at a feast."},
    {"chapter": 44, "speaker": "judah", "reference": "Genesis 44",
     "note": "Joseph's silver cup is planted in Benjamin's sack; Judah offers himself as a slave in Benjamin's place rather than let their father lose him."},
    {"chapter": 45, "speaker": "joseph", "reference": "Genesis 45",
     "note": "Joseph reveals his identity to his brothers and sends for his father Jacob to come to Egypt."},
    {"chapter": 46, "speaker": "jacob", "reference": "Genesis 46",
     "note": "God reassures Jacob (Israel) at Beersheba; his family — seventy in all — journeys to Egypt and is reunited with Joseph."},
    {"chapter": 47, "speaker": "jacob", "reference": "Genesis 47",
     "note": "Jacob is presented to Pharaoh and settles in Goshen; Joseph administers Egypt's grain through the famine."},
    {"chapter": 48, "speaker": "jacob", "reference": "Genesis 48",
     "note": "The dying Jacob blesses Joseph's two sons, Ephraim and Manasseh, giving the younger the greater blessing."},
    {"chapter": 49, "speaker": "jacob", "reference": "Genesis 49",
     "note": "Jacob blesses each of his twelve sons in turn, then dies."},
    {"chapter": 50, "speaker": "joseph", "reference": "Genesis 50",
     "note": "Joseph buries Jacob in Canaan, reassures his fearful brothers (“you meant evil... God meant it for good”), and dies in Egypt at 110."},
]


def render_genesis_chapters_svg(chapters):
    runs = jc_group_runs(chapters)
    rows = {key: [r for r in runs if r["speaker"] == key] for key in GC_ROW_ORDER if key not in GC_SECONDARY_ROWS}
    rows.update(GC_SECONDARY_SPANS)

    total_chapters = 50
    margin_left, margin_right = 16, 16
    plot_width = 1900
    bar_h = 30
    row_label_h = 34
    row_gap = 14
    axis_h = 34
    bar_font_size = 18
    tick_step = 5

    def x_of(boundary):
        return margin_left + boundary / total_chapters * plot_width

    total_h = axis_h + len(GC_ROW_ORDER) * (row_label_h + bar_h) + (len(GC_ROW_ORDER) - 1) * row_gap + 8
    total_w = margin_left + plot_width + margin_right

    parts = [
        f'<svg id="genesis-chart-svg" viewBox="0 0 {total_w} {total_h}" width="{total_w}" height="{total_h}" role="img" '
        f'aria-label="Timeline of all 50 chapters of Genesis, one row per protagonist plus Sarah, Rebekah, and Rachel rows for the chapters each shares as a major secondary worker, showing which chapters each one\'s story is told in" '
        f'xmlns="http://www.w3.org/2000/svg" class="kp-chart-svg gnc-timeline-svg">'
    ]

    y_axis_top = axis_h
    y_axis_bottom = total_h - 4
    tick_chapters = sorted(set([1] + list(range(tick_step, total_chapters, tick_step)) + [total_chapters]))
    for tick in tick_chapters:
        boundary = tick - 1 if tick < total_chapters else total_chapters
        tx = x_of(boundary)
        parts.append(f'<line x1="{tx:.1f}" y1="{y_axis_top}" x2="{tx:.1f}" y2="{y_axis_bottom}" class="kp-gridline" />')
        parts.append(f'<text x="{tx:.1f}" y="26" class="kp-axis-label" text-anchor="middle">{tick}</text>')

    y = axis_h
    for key in GC_ROW_ORDER:
        speaker = GC_SPEAKERS[key]
        parts.append(f'<text x="{margin_left}" y="{y + 26}" class="kp-row-label">{esc(speaker["label"])}</text>')
        lane_y = y + row_label_h

        for run in rows[key]:
            x1 = x_of(run["start"] - 1)
            x2 = x_of(run["end"])
            bw = max(2.0, x2 - x1)
            chapter_label = str(run["start"]) if run["start"] == run["end"] else f'{run["start"]}–{run["end"]}'
            title = f'Genesis {chapter_label} — {speaker["label"]}. {run["note"]} ({run["reference"]})'
            rect = (
                f'<rect x="{x1:.1f}" y="{lane_y:.1f}" width="{bw:.1f}" height="{bar_h}" rx="4" '
                f'fill="{speaker["color_var"]}" class="kp-bar" tabindex="0" '
                f'data-name="{esc(speaker["label"])}" data-nation="Genesis {esc(chapter_label)}" '
                f'data-span="{esc(run["note"])}" data-reference="{esc(run["reference"])}">'
                f'<title>{esc(title)}</title></rect>'
            )
            label_el = ""
            if kp_bar_label_fits(chapter_label, bw, font_size=bar_font_size):
                label_el = (
                    f'<text x="{x1 + bw / 2:.1f}" y="{lane_y + bar_h / 2 + 6.5:.1f}" '
                    f'class="kp-bar-label" text-anchor="middle">{esc(chapter_label)}</text>'
                )
            if speaker["person_id"]:
                href = f'../people/{speaker["person_id"]}.html'
                parts.append(f'<a href="{href}">{rect}{label_el}</a>')
            else:
                parts.append(rect + label_el)

        y += row_label_h + bar_h + row_gap

    parts.append("</svg>")
    return "\n".join(parts)


def render_genesis_chapters_legend():
    items = "\n    ".join(
        f'<span class="kp-legend-item"><span class="kp-legend-swatch" style="background:{s["color_var"]}"></span>{esc(s["label"])}</span>'
        for s in GC_SPEAKERS.values()
    )
    return f'<div class="kp-legend gnc-timeline-legend">{items}</div>'


def render_genesis_chapters_table(chapters):
    # Sarah/Rebekah/Rachel's spans aren't in `chapters` (see GC_SECONDARY_SPANS
    # above -- overlapping secondary rows, not any chapter's primary speaker),
    # so they're interleaved into the table by their own start chapter rather
    # than iterated alongside the primary per-chapter rows.
    secondary_by_start = {}
    for key in GC_SECONDARY_ROWS:
        for span in GC_SECONDARY_SPANS[key]:
            secondary_by_start.setdefault(span["start"], []).append((key, span))

    def row_html(entry):
        speaker = GC_SPEAKERS[entry["speaker"]]
        name_cell = (
            f'<a href="../people/{speaker["person_id"]}.html">{esc(speaker["label"])}</a>'
            if speaker["person_id"] else esc(speaker["label"])
        )
        return (
            f'<tr><td>{entry["chapter"]}</td><td>{name_cell}</td>'
            f'<td>{esc(entry["reference"])}</td><td>{esc(entry["note"])}</td></tr>'
        )

    def secondary_row_html(key, span):
        speaker = GC_SPEAKERS[key]
        chapter_label = str(span["start"]) if span["start"] == span["end"] else f'{span["start"]}–{span["end"]}'
        name_cell = f'<a href="../people/{speaker["person_id"]}.html">{esc(speaker["label"])}</a> (also)'
        return (
            f'<tr class="kp-table-secondary"><td>{chapter_label}</td><td>{name_cell}</td>'
            f'<td>{esc(span["reference"])}</td><td>{esc(span["note"])}</td></tr>'
        )

    rows = []
    for entry in chapters:
        rows.append(row_html(entry))
        for key, span in secondary_by_start.get(entry["chapter"], []):
            rows.append(secondary_row_html(key, span))

    body_rows = "\n    ".join(rows)
    return f"""<details class="kp-table-details">
    <summary>View as a table</summary>
    <div class="table-scroll">
    <table class="kp-table">
      <thead><tr><th>Chapter</th><th>Protagonist</th><th>Reference</th><th>Note</th></tr></thead>
      <tbody>
    {body_rows}
      </tbody>
    </table>
    </div>
  </details>"""


def build_genesis_chapters_chart_page(chapters):
    base = "../"
    canonical = f"{SITE_URL}/charts/genesis-chapters.html"
    title = "Genesis — Main Characters by Chapter — Lives of Scripture"
    description = "Every chapter of Genesis, colored by whose story it tells — from Adam and Eve to Noah, Abraham, Jacob, and Joseph."
    breadcrumb_ld = breadcrumb_json_ld([
        ("Home", f"{SITE_URL}/"), ("Charts", f"{SITE_URL}/charts.html"),
        (title.replace(" — Lives of Scripture", ""), None),
    ])

    svg = render_genesis_chapters_svg(chapters)
    legend = render_genesis_chapters_legend()
    table = render_genesis_chapters_table(chapters)

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
<script type="application/ld+json">
{breadcrumb_ld}
</script>
</head>
<body>
{header_html(base, "charts.html")}

<main>
  <p><a href="{base}charts.html">&larr; Charts</a></p>
  <h2>Genesis &mdash; Main Characters by Chapter</h2>
  <p class="page-intro">Genesis moves through several overlapping generations rather than one continuous
  drama. Each row below is a person; each bar is a chapter, colored by whoever the text's own narrative
  centers on in that chapter &mdash; Adam and Eve in Eden, Cain after the first murder, Noah and the flood,
  Abraham's call and covenant, his nephew Lot at Sodom, Isaac's generation, Jacob's flight and return, his
  daughter Dinah, and finally Joseph and his brother Judah in Egypt. Chapters with no single human
  protagonist &mdash; the creation week and the book's genealogical &ldquo;these are the generations of...&rdquo;
  lists &mdash; are grouped under Creation &amp; Genealogies. Sarah, Rebekah, and Rachel each get their own
  row too, overlapping the chapters they share with Abraham, Isaac, and Jacob &mdash; each is a major
  secondary worker with her own decisive scenes, not the chapter's primary storyteller, so her bars sit
  alongside those rows' colors rather than replacing them. Bars are clickable and link to that person's
  page; hover or focus a bar for a chapter summary.</p>

  <div class="kp-legend-row">
    {legend}
    <div class="kp-chart-toolbar">
    <button type="button" class="kp-chart-copy" id="genesis-chart-copy">&#128203; Copy image</button>
    <button type="button" class="kp-chart-expand" id="genesis-chart-expand">&#128269; View larger</button>
    </div>
  </div>

  <div class="kp-chart-scroll">
  {svg}
  </div>

  <p class="kp-disclaimer">A few chapters split across two people and required a judgment call rather than
  a single clean answer: ch. 25 covers both Abraham's death and the birth/birthright sale of Esau and Jacob
  (grouped under Jacob, since that event sets the course of the rest of the book); ch. 44's planted silver
  cup is grouped under Judah rather than Joseph, since the chapter's back half is Judah's own pivotal plea
  to take Benjamin's place as a slave. Jacob is renamed Israel partway through the book (32:22-32); the row
  is labeled &ldquo;Jacob&rdquo; throughout for consistency, but links to his person page under that later
  name. Sarah's row spans Genesis 16-18, 20-21, and 23; Rebekah's spans 24 and 27; Rachel's spans 30-31 and
  35 &mdash; chapter-granularity spans covering each woman's own decisive scenes (Sarah's laughter and
  death, Rebekah's part in Jacob's blessing, Rachel's stolen idols and death in childbirth), not every verse
  she's mentioned in. Esau, Leah, Hagar, and Tamar (ch. 38, folded into Judah's row) were considered for
  their own rows too but left out &mdash; a scope decision, not a claim their roles were minor.</p>

  {table}
</main>

{footer_html(base)}

<script src="{base}js/app.js"></script>
<script>initNavToggle(); initKpChartTooltips(); initChartLightbox("genesis-chart-expand", "genesis-chart-svg", "Genesis — Main Characters by Chapter, enlarged"); initChartCopyButton("genesis-chart-copy", "genesis-chart-svg");</script>
</body>
</html>
"""


# ---------------------------------------------------------------------
# "Acts — Main Characters by Chapter" chart (charts.html hub +
# charts/acts-chapters.html)
# ---------------------------------------------------------------------

# Same "whose story is the text following" framing as the Genesis chart
# above, applied to Acts -- a book that famously pivots from a
# Peter-centered first half to a Paul-centered second half. Peter, Stephen,
# and Philip's ministries are grouped by the person they're centered on;
# Acts 15's Jerusalem Council, where Peter, Paul, Barnabas, and James all
# speak with no single figure driving the chapter, reuses --gen-shared, the
# same "not a competing identity" role it plays on the Job and Genesis
# charts.
#
# One judgment call, flagged on the page itself rather than picked
# silently: ch. 9 splits between Saul's conversion (9:1-31, the majority of
# the chapter and the more significant event) and Peter's healings of
# Aeneas and Dorcas (9:32-43); the whole chapter is grouped under Paul, but
# the note says so. Saul is renamed Paul partway through the book (13:9);
# the row is labeled "Paul" throughout for a single consistent label,
# matching the site's own person_id and page title -- see paul.json's
# alt_names, which already lists "Saul"/"Saul of Tarsus".
#
# Barnabas gets his own row (added 2026-08-12) rather than folding into
# Paul's -- but as an overlapping *secondary-worker* row, not a competing
# "whose story" chapter assignment: ACC_BARNABAS_SPANS below is a second,
# independent presence list (Acts 9, 11-15) that renders alongside the
# primary per-chapter speaker assignment rather than replacing any chapter's
# color, so Barnabas's bars can legitimately span the same chapters already
# colored for Peter (11-12) or Paul/the Council (13-15). Text basis: he
# vouches for the newly converted Saul in Jerusalem (9:26-28); is sent to
# found/encourage the Antioch church, fetches Saul from Tarsus to teach
# there, and carries relief funds to Judea during the famine (11:22-30,
# 12:25); is set apart with Saul/Paul for the first missionary journey and
# named first, suggesting initial seniority (13:1-3); stands with Paul at
# the Jerusalem Council; and splits from Paul afterward over whether to
# bring John Mark again (15:36-41). His single-verse introduction in 4:36-37
# (selling a field) isn't included as its own span -- it's a backstory
# mention, not an active role in that chapter's narrative.
ACC_SPEAKERS = {
    "peter": {"label": "Peter", "person_id": "peter", "color_var": "var(--acc-peter)"},
    "stephen": {"label": "Stephen", "person_id": "stephen", "color_var": "var(--acc-stephen)"},
    "philip": {"label": "Philip", "person_id": "philip-3", "color_var": "var(--acc-philip)"},
    "paul": {"label": "Paul", "person_id": "paul", "color_var": "var(--acc-paul)"},
    "barnabas": {"label": "Barnabas", "person_id": "barnabas", "color_var": "var(--acc-barnabas)"},
    "council": {"label": "Jerusalem Council", "person_id": None, "color_var": "var(--gen-shared)"},
}

ACC_ROW_ORDER = ["peter", "stephen", "philip", "paul", "barnabas", "council"]

# Barnabas's presence spans -- independent of ACC_CHAPTERS/jc_group_runs,
# since that mechanism assigns exactly one "whose story" speaker per
# chapter and Barnabas is deliberately a second, overlapping row rather
# than a replacement for Peter's/Paul's/the Council's chapter assignment.
ACC_BARNABAS_SPANS = [
    {"start": 9, "end": 9, "reference": "Acts 9",
     "note": "Barnabas vouches for the newly converted Saul before Jerusalem's suspicious believers, describing his encounter with the Lord and his bold preaching in Damascus."},
    {"start": 11, "end": 15, "reference": "Acts 11",
     "note": "Sent to the new church at Antioch, Barnabas fetches Saul from Tarsus to teach there, carries relief funds to Judea, and is set apart with Saul (now Paul) for their first missionary journey; after the Jerusalem Council, the two part ways over whether to bring John Mark again."},
]

ACC_CHAPTERS = [
    {"chapter": 1, "speaker": "peter", "reference": "Acts 1",
     "note": "Jesus ascends to heaven after commissioning the apostles; awaiting the Spirit, Peter leads the choosing of Matthias to replace Judas."},
    {"chapter": 2, "speaker": "peter", "reference": "Acts 2",
     "note": "The Holy Spirit falls on the gathered believers at Pentecost; Peter preaches, and about three thousand are added to the church."},
    {"chapter": 3, "speaker": "peter", "reference": "Acts 3",
     "note": "Peter heals a man lame from birth at the temple gate and preaches to the crowd that gathers."},
    {"chapter": 4, "speaker": "peter", "reference": "Acts 4",
     "note": "Peter and John are arrested and testify before the Sanhedrin; the believers share their possessions in common."},
    {"chapter": 5, "speaker": "peter", "reference": "Acts 5",
     "note": "Ananias and Sapphira die after lying to the Holy Spirit; the apostles are arrested, freed by an angel, and defended by Gamaliel."},
    {"chapter": 6, "speaker": "stephen", "reference": "Acts 6",
     "note": "The Twelve appoint seven men, including Stephen and Philip, to serve the Grecian widows; Stephen, “full of grace and power,” is opposed and arrested."},
    {"chapter": 7, "speaker": "stephen", "reference": "Acts 7",
     "note": "Stephen's speech before the Sanhedrin retells Israel's history; he is stoned to death, the first Christian martyr."},
    {"chapter": 8, "speaker": "philip", "reference": "Acts 8",
     "note": "Persecution scatters the believers; Philip preaches in Samaria, confronts Simon the sorcerer, and leads an Ethiopian official to Christ."},
    {"chapter": 9, "speaker": "paul", "reference": "Acts 9",
     "note": "Saul is converted on the road to Damascus and begins preaching Christ (9:1-31); the chapter closes with Peter healing Aeneas and raising Dorcas (9:32-43)."},
    {"chapter": 10, "speaker": "peter", "reference": "Acts 10",
     "note": "Peter, guided by a vision, brings the gospel to Cornelius, a Gentile centurion, whose household receives the Holy Spirit."},
    {"chapter": 11, "speaker": "peter", "reference": "Acts 11",
     "note": "Peter defends his visit to Cornelius before the Jerusalem church; the Antioch church is founded, and Barnabas brings Saul there to teach."},
    {"chapter": 12, "speaker": "peter", "reference": "Acts 12",
     "note": "Herod kills James, the brother of John, and imprisons Peter, who is freed by an angel; Herod is struck down and dies."},
    {"chapter": 13, "speaker": "paul", "reference": "Acts 13",
     "note": "Barnabas and Saul are sent out from Antioch; on Cyprus, Saul (now called Paul) blinds the sorcerer Elymas and preaches in Pisidian Antioch."},
    {"chapter": 14, "speaker": "paul", "reference": "Acts 14",
     "note": "Paul and Barnabas preach in Iconium and Lystra, where Paul heals a lame man, is stoned and left for dead, then continues on."},
    {"chapter": 15, "speaker": "council", "reference": "Acts 15",
     "note": "The Jerusalem Council debates whether Gentile believers must be circumcised; Peter, Paul, Barnabas, and James all speak, and a decision is sent out."},
    {"chapter": 16, "speaker": "paul", "reference": "Acts 16",
     "note": "Paul recruits Timothy, is called in a vision to Macedonia, converts Lydia at Philippi, and is imprisoned with Silas before an earthquake frees them."},
    {"chapter": 17, "speaker": "paul", "reference": "Acts 17",
     "note": "Paul preaches in Thessalonica and Berea, then reasons with the philosophers at the Areopagus in Athens."},
    {"chapter": 18, "speaker": "paul", "reference": "Acts 18",
     "note": "Paul ministers in Corinth alongside Priscilla and Aquila and is brought before the proconsul Gallio."},
    {"chapter": 19, "speaker": "paul", "reference": "Acts 19",
     "note": "In Ephesus, Paul baptizes disciples of John, works miracles, and a riot breaks out among the silversmiths over Artemis worship."},
    {"chapter": 20, "speaker": "paul", "reference": "Acts 20",
     "note": "Paul raises Eutychus, who fell asleep and dropped from a window, at Troas, then gives a farewell address to the Ephesian elders at Miletus."},
    {"chapter": 21, "speaker": "paul", "reference": "Acts 21",
     "note": "Paul is warned by the prophet Agabus, arrives in Jerusalem, and is seized in the temple by an angry crowd."},
    {"chapter": 22, "speaker": "paul", "reference": "Acts 22",
     "note": "Paul addresses the crowd from the barracks steps, recounting his conversion, until he claims his Roman citizenship."},
    {"chapter": 23, "speaker": "paul", "reference": "Acts 23",
     "note": "Paul divides the Sanhedrin over the resurrection; warned of a plot to kill him, he is sent under guard to Felix in Caesarea."},
    {"chapter": 24, "speaker": "paul", "reference": "Acts 24",
     "note": "Paul is accused before governor Felix and gives his defense; Felix leaves him in custody for two years, hoping for a bribe."},
    {"chapter": 25, "speaker": "paul", "reference": "Acts 25",
     "note": "The new governor Festus hears Paul's case; Paul appeals to Caesar and is presented before King Agrippa."},
    {"chapter": 26, "speaker": "paul", "reference": "Acts 26",
     "note": "Paul gives his defense before Agrippa, again recounting his conversion; Agrippa says he is “almost persuaded” to become a Christian."},
    {"chapter": 27, "speaker": "paul", "reference": "Acts 27",
     "note": "Paul sails for Rome as a prisoner; the ship is caught in a storm and wrecked off the island of Malta."},
    {"chapter": 28, "speaker": "paul", "reference": "Acts 28",
     "note": "On Malta, Paul survives a viper's bite and heals the sick; he arrives in Rome and preaches the kingdom of God under house arrest."},
]


def render_acts_chapters_svg(chapters):
    runs = jc_group_runs(chapters)
    rows = {key: [r for r in runs if r["speaker"] == key] for key in ACC_ROW_ORDER if key != "barnabas"}
    rows["barnabas"] = ACC_BARNABAS_SPANS

    total_chapters = 28
    margin_left, margin_right = 16, 16
    plot_width = 1400
    bar_h = 34
    row_label_h = 38
    row_gap = 16
    axis_h = 34
    bar_font_size = 22
    tick_step = 5

    def x_of(boundary):
        return margin_left + boundary / total_chapters * plot_width

    total_h = axis_h + len(ACC_ROW_ORDER) * (row_label_h + bar_h) + (len(ACC_ROW_ORDER) - 1) * row_gap + 8
    total_w = margin_left + plot_width + margin_right

    parts = [
        f'<svg id="acts-chart-svg" viewBox="0 0 {total_w} {total_h}" width="{total_w}" height="{total_h}" role="img" '
        f'aria-label="Timeline of all 28 chapters of Acts, one row per protagonist plus a Barnabas row for the chapters he shares as a major secondary worker, showing which chapters each one\'s story is told in" '
        f'xmlns="http://www.w3.org/2000/svg" class="kp-chart-svg acc-timeline-svg">'
    ]

    y_axis_top = axis_h
    y_axis_bottom = total_h - 4
    tick_chapters = sorted(set([1] + list(range(tick_step, total_chapters, tick_step)) + [total_chapters]))
    for tick in tick_chapters:
        boundary = tick - 1 if tick < total_chapters else total_chapters
        tx = x_of(boundary)
        parts.append(f'<line x1="{tx:.1f}" y1="{y_axis_top}" x2="{tx:.1f}" y2="{y_axis_bottom}" class="kp-gridline" />')
        parts.append(f'<text x="{tx:.1f}" y="26" class="kp-axis-label" text-anchor="middle">{tick}</text>')

    y = axis_h
    for key in ACC_ROW_ORDER:
        speaker = ACC_SPEAKERS[key]
        parts.append(f'<text x="{margin_left}" y="{y + 30}" class="kp-row-label">{esc(speaker["label"])}</text>')
        lane_y = y + row_label_h

        for run in rows[key]:
            x1 = x_of(run["start"] - 1)
            x2 = x_of(run["end"])
            bw = max(2.0, x2 - x1)
            chapter_label = str(run["start"]) if run["start"] == run["end"] else f'{run["start"]}–{run["end"]}'
            title = f'Acts {chapter_label} — {speaker["label"]}. {run["note"]} ({run["reference"]})'
            rect = (
                f'<rect x="{x1:.1f}" y="{lane_y:.1f}" width="{bw:.1f}" height="{bar_h}" rx="4" '
                f'fill="{speaker["color_var"]}" class="kp-bar" tabindex="0" '
                f'data-name="{esc(speaker["label"])}" data-nation="Acts {esc(chapter_label)}" '
                f'data-span="{esc(run["note"])}" data-reference="{esc(run["reference"])}">'
                f'<title>{esc(title)}</title></rect>'
            )
            label_el = ""
            if kp_bar_label_fits(chapter_label, bw, font_size=bar_font_size):
                label_el = (
                    f'<text x="{x1 + bw / 2:.1f}" y="{lane_y + bar_h / 2 + 7.5:.1f}" '
                    f'class="kp-bar-label" text-anchor="middle">{esc(chapter_label)}</text>'
                )
            if speaker["person_id"]:
                href = f'../people/{speaker["person_id"]}.html'
                parts.append(f'<a href="{href}">{rect}{label_el}</a>')
            else:
                parts.append(rect + label_el)

        y += row_label_h + bar_h + row_gap

    parts.append("</svg>")
    return "\n".join(parts)


def render_acts_chapters_legend():
    items = "\n    ".join(
        f'<span class="kp-legend-item"><span class="kp-legend-swatch" style="background:{s["color_var"]}"></span>{esc(s["label"])}</span>'
        for s in ACC_SPEAKERS.values()
    )
    return f'<div class="kp-legend acc-timeline-legend">{items}</div>'


def render_acts_chapters_table(chapters):
    barnabas = ACC_SPEAKERS["barnabas"]
    # Barnabas's spans aren't in `chapters` (see ACC_BARNABAS_SPANS above --
    # an overlapping secondary row, not a chapter's primary speaker), so
    # they're interleaved into the table by their own start chapter rather
    # than iterated alongside the primary per-chapter rows.
    secondary_by_start = {}
    for span in ACC_BARNABAS_SPANS:
        secondary_by_start.setdefault(span["start"], []).append(span)

    def row_html(entry):
        speaker = ACC_SPEAKERS[entry["speaker"]]
        name_cell = (
            f'<a href="../people/{speaker["person_id"]}.html">{esc(speaker["label"])}</a>'
            if speaker["person_id"] else esc(speaker["label"])
        )
        return (
            f'<tr><td>{entry["chapter"]}</td><td>{name_cell}</td>'
            f'<td>{esc(entry["reference"])}</td><td>{esc(entry["note"])}</td></tr>'
        )

    def secondary_row_html(span):
        chapter_label = str(span["start"]) if span["start"] == span["end"] else f'{span["start"]}–{span["end"]}'
        name_cell = f'<a href="../people/{barnabas["person_id"]}.html">{esc(barnabas["label"])}</a> (also)'
        return (
            f'<tr class="kp-table-secondary"><td>{chapter_label}</td><td>{name_cell}</td>'
            f'<td>{esc(span["reference"])}</td><td>{esc(span["note"])}</td></tr>'
        )

    rows = []
    for entry in chapters:
        rows.append(row_html(entry))
        for span in secondary_by_start.get(entry["chapter"], []):
            rows.append(secondary_row_html(span))

    body_rows = "\n    ".join(rows)
    return f"""<details class="kp-table-details">
    <summary>View as a table</summary>
    <div class="table-scroll">
    <table class="kp-table">
      <thead><tr><th>Chapter</th><th>Protagonist</th><th>Reference</th><th>Note</th></tr></thead>
      <tbody>
    {body_rows}
      </tbody>
    </table>
    </div>
  </details>"""


def build_acts_chapters_chart_page(chapters):
    base = "../"
    canonical = f"{SITE_URL}/charts/acts-chapters.html"
    title = "Acts — Main Characters by Chapter — Lives of Scripture"
    description = "Every chapter of Acts, colored by whose story it tells — the book's pivot from Peter's ministry to Paul's, with Stephen and Philip between."
    breadcrumb_ld = breadcrumb_json_ld([
        ("Home", f"{SITE_URL}/"), ("Charts", f"{SITE_URL}/charts.html"),
        (title.replace(" — Lives of Scripture", ""), None),
    ])

    svg = render_acts_chapters_svg(chapters)
    legend = render_acts_chapters_legend()
    table = render_acts_chapters_table(chapters)

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
<script type="application/ld+json">
{breadcrumb_ld}
</script>
</head>
<body>
{header_html(base, "charts.html")}

<main>
  <p><a href="{base}charts.html">&larr; Charts</a></p>
  <h2>Acts &mdash; Main Characters by Chapter</h2>
  <p class="page-intro">Acts famously pivots partway through from a Peter-centered church to a
  Paul-centered mission. Each row below is a person; each bar is a chapter, colored by whoever the text's
  own narrative centers on in that chapter &mdash; Peter's early ministry in Jerusalem, Stephen's speech and
  martyrdom, Philip's mission to Samaria and the Ethiopian official, and then Paul's conversion and
  missionary journeys, which dominate the second half of the book. Acts 15's Jerusalem Council, where
  several voices speak and no single figure drives the chapter, is grouped under Jerusalem Council.
  Barnabas gets his own row too, overlapping the chapters he shares with Peter, Paul, and the Council
  &mdash; he's a major secondary worker throughout, not the chapter's primary storyteller, so his bars sit
  alongside those rows' colors rather than replacing them. Bars are clickable and link to that person's
  page; hover or focus a bar for a chapter summary.</p>

  <div class="kp-legend-row">
    {legend}
    <div class="kp-chart-toolbar">
    <button type="button" class="kp-chart-copy" id="acts-chart-copy">&#128203; Copy image</button>
    <button type="button" class="kp-chart-expand" id="acts-chart-expand">&#128269; View larger</button>
    </div>
  </div>

  <div class="kp-chart-scroll">
  {svg}
  </div>

  <p class="kp-disclaimer">Ch. 9 splits between Saul's conversion (9:1-31, the larger and more significant
  portion) and Peter's healing of Aeneas and raising of Dorcas (9:32-43); the whole chapter is grouped
  under Paul. Saul is renamed Paul partway through the book (13:9); the row is labeled &ldquo;Paul&rdquo;
  throughout for consistency. Barnabas's own row spans Acts 9 (vouching for Saul in Jerusalem) and Acts
  11-15 (the Antioch mission, the first missionary journey, and the Jerusalem Council, ending with his and
  Paul's split over John Mark) &mdash; chapter-granularity spans, so his bar doesn't imply he's foregrounded
  in every verse of that range (e.g. most of ch. 12 is Peter's escape from prison; Barnabas reappears only
  at 12:25).</p>

  {table}
</main>

{footer_html(base)}

<script src="{base}js/app.js"></script>
<script>initNavToggle(); initKpChartTooltips(); initChartLightbox("acts-chart-expand", "acts-chart-svg", "Acts — Main Characters by Chapter, enlarged"); initChartCopyButton("acts-chart-copy", "acts-chart-svg");</script>
</body>
</html>
"""


def build_charts_list_page():
    base = ""
    canonical = f"{SITE_URL}/charts.html"
    title = "Charts — Lives of Scripture"
    description = "Visual charts across the whole dataset, including the kings of Israel and Judah, the two genealogies of Jesus, the twelve tribes, who's speaking in each chapter of Job, and whose story each chapter of Genesis and Acts tells."
    breadcrumb_ld = breadcrumb_json_ld([("Home", f"{SITE_URL}/"), ("Charts", None)])

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
<script type="application/ld+json">
{breadcrumb_ld}
</script>
</head>
<body>
{header_html(base, "charts.html")}

<main>
  <h2>Charts</h2>
  <p class="page-intro">Visual charts across the whole dataset.</p>

  <div class="person-grid">
    <a class="person-card" href="{base}charts/kings-and-prophets.html">
      <div class="name"><strong>Kings &amp; Prophets of the Monarchy</strong></div>
      <p class="chart-card-desc">Every king of the United Kingdom, Israel, and Judah, and every prophet
      active in that period, laid out on one timeline.</p>
    </a>
    <a class="person-card" href="{base}charts/genealogies-of-jesus.html">
      <div class="name"><strong>The Two Genealogies of Jesus</strong></div>
      <p class="chart-card-desc">Matthew's and Luke's genealogies of Jesus, compared and joined on one
      family-tree chart.</p>
    </a>
    <a class="person-card" href="{base}charts/twelve-tribes.html">
      <div class="name"><strong>The Twelve Tribes, By Mother</strong></div>
      <p class="chart-card-desc">Every person whose tribe Scripture records, grouped by which of Jacob's
      four wives they descend from, then by tribe, in one sunburst chart.</p>
    </a>
    <a class="person-card" href="{base}charts/job-chapters.html">
      <div class="name"><strong>Job &mdash; Main Speaker by Chapter</strong></div>
      <p class="chart-card-desc">All 42 chapters of Job, colored by who is speaking in each one — Job,
      his three friends, Elihu, or the LORD.</p>
    </a>
    <a class="person-card" href="{base}charts/genesis-chapters.html">
      <div class="name"><strong>Genesis &mdash; Main Characters by Chapter</strong></div>
      <p class="chart-card-desc">All 50 chapters of Genesis, colored by whose story it tells — Adam and
      Eve, Cain, Noah, Abraham, Isaac, Jacob, or Joseph.</p>
    </a>
    <a class="person-card" href="{base}charts/acts-chapters.html">
      <div class="name"><strong>Acts &mdash; Main Characters by Chapter</strong></div>
      <p class="chart-card-desc">All 28 chapters of Acts, colored by whose story it tells — the book's
      pivot from Peter's ministry to Paul's, with Stephen and Philip between.</p>
    </a>
  </div>

  <p class="page-intro">Have an idea for another chart? Email
  <a href="mailto:andyabel+livesofscripture@gmail.com">andyabel+livesofscripture@gmail.com</a>
  with your suggestion.</p>
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
    breadcrumb_ld = breadcrumb_json_ld([
        ("Home", f"{SITE_URL}/"), ("Charts", f"{SITE_URL}/charts.html"),
        (title.replace(" — Lives of Scripture", ""), None),
    ])

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
<script type="application/ld+json">
{breadcrumb_ld}
</script>
</head>
<body>
{header_html(base, "charts.html")}

<main>
  <p><a href="{base}charts.html">&larr; Charts</a></p>
  <h2>Kings &amp; Prophets of the Monarchy</h2>
  <p class="page-intro">Every king of the United Kingdom, the Kingdom of Israel, and the Kingdom of
  Judah, alongside every prophet active in that period and the kingdom or nation each one addressed.
  Bars are clickable and link to that person's page; hover or focus a bar for exact dates.</p>

  <div class="kp-legend-row">
    {legend}
    <div class="kp-chart-toolbar">
    <button type="button" class="kp-chart-copy" id="kp-chart-copy">&#128203; Copy image</button>
    <button type="button" class="kp-chart-expand" id="kp-chart-expand">&#128269; View larger</button>
    </div>
  </div>

  <div class="kp-chart-scroll">
  {svg}
  </div>

  <p class="kp-disclaimer">Reign and ministry years follow a single widely-used evangelical regnal
  chronology (the Thiele/synchronistic framework already used elsewhere on this site &mdash; see e.g.
  <a href="{base}people/david.html">David's</a> page), marked &ldquo;c.&rdquo; throughout. Other
  evangelical chronological frameworks shift several of these dates, especially where a co-regency is
  involved (Uzziah/Jotham, Amaziah/Uzziah, Hezekiah/Manasseh). Every entry cites the verse stating its
  reign length or ministry's dating; hover, focus, or open the table below for the reference.</p>

  {table}

  {unplotted_html}
</main>

{footer_html(base)}

<script src="{base}js/app.js"></script>
<script>initNavToggle(); initKpChartTooltips(); initKpChartLightbox(); initChartCopyButton("kp-chart-copy", "kp-chart-svg");</script>
</body>
</html>
"""


# ---------------------------------------------------------------------
# sitemap.xml
# ---------------------------------------------------------------------


def build_sitemap(index, churches, places_index):
    urls = [
        (f"{SITE_URL}/", "weekly", "1.0"),
        (f"{SITE_URL}/people.html", "weekly", "0.9"),
        (f"{SITE_URL}/timeline.html", "monthly", "0.6"),
        (f"{SITE_URL}/connections.html", "monthly", "0.6"),
        (f"{SITE_URL}/churches.html", "monthly", "0.6"),
        (f"{SITE_URL}/places.html", "monthly", "0.6"),
        (f"{SITE_URL}/map.html", "monthly", "0.6"),
        (f"{SITE_URL}/place-connections.html", "monthly", "0.6"),
        (f"{SITE_URL}/charts.html", "monthly", "0.6"),
        (f"{SITE_URL}/charts/kings-and-prophets.html", "monthly", "0.6"),
        (f"{SITE_URL}/charts/genealogies-of-jesus.html", "monthly", "0.6"),
        (f"{SITE_URL}/charts/twelve-tribes.html", "monthly", "0.6"),
        (f"{SITE_URL}/charts/job-chapters.html", "monthly", "0.6"),
        (f"{SITE_URL}/charts/genesis-chapters.html", "monthly", "0.6"),
        (f"{SITE_URL}/charts/acts-chapters.html", "monthly", "0.6"),
        (f"{SITE_URL}/quiz.html", "monthly", "0.5"),
        (f"{SITE_URL}/about.html", "monthly", "0.4"),
    ]
    lines = [
        f"  <url>\n    <loc>{loc}</loc>\n"
        f"    <changefreq>{freq}</changefreq>\n    <priority>{prio}</priority>\n  </url>"
        for loc, freq, prio in urls
    ]
    for entry in index:
        # Stub person pages are noindex (see build_person_page) — thin,
        # single-reference genealogy listings, not something to ask Google
        # to crawl-and-index via the sitemap. Leaving them out of the
        # sitemap entirely follows Google's own guidance for noindexed URLs;
        # they're still reachable (and crawlable) via genealogy links.
        if entry["tier"] != "full":
            continue
        priority = "0.8"
        loc = f'{SITE_URL}/people/{entry["person_id"]}.html'
        # Image sitemap extension, restricted to the unique stained-glass
        # portrait (portraits2-web) — the shared generic/legacy icons are
        # reused across dozens of people, so listing those would just tell
        # Google many different pages share one image rather than helping
        # any single person's name rank in Image Search.
        full_file = resolve_full_portrait_file(entry)
        image_xml = ""
        if full_file:
            img_url = f'{SITE_URL}/images/portraits2-web/{full_file}'
            caption = esc(f'{entry["name"]} — stained-glass style portrait')
            image_xml = (
                f"\n    <image:image>\n      <image:loc>{esc(img_url)}</image:loc>\n"
                f"      <image:caption>{caption}</image:caption>\n    </image:image>"
            )
        lines.append(
            f"  <url>\n    <loc>{loc}</loc>\n"
            f"    <changefreq>monthly</changefreq>\n    <priority>{priority}</priority>{image_xml}\n  </url>"
        )
    for church in churches:
        loc = f'{SITE_URL}/churches/{church["church_id"]}.html'
        lines.append(
            f"  <url>\n    <loc>{loc}</loc>\n"
            f"    <changefreq>monthly</changefreq>\n    <priority>0.6</priority>\n  </url>"
        )
    for place in places_index:
        # Stub place pages are noindex, same rationale as stub person pages
        # (see build_place_detail_page) — left out of the sitemap entirely.
        if place["tier"] != "full":
            continue
        loc = f'{SITE_URL}/places/{place["place_id"]}.html'
        lines.append(
            f"  <url>\n    <loc>{loc}</loc>\n"
            f"    <changefreq>monthly</changefreq>\n    <priority>0.5</priority>\n  </url>"
        )

    entries = "\n".join(lines)
    sitemap = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
        'xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">\n'
        f"{entries}\n</urlset>\n"
    )
    (ROOT / "sitemap.xml").write_text(sitemap)


# ---------------------------------------------------------------------


def build_people_by_name(index):
    """Every person (full or stub) grouped by name match, so a person's page
    can point to other entries sharing their name (e.g. the several
    Jehoshaphats, Jehus, and Zechariahs in the underlying genealogy dataset
    -- or a full/stub pair like Mordecai/Mordecai the Ezra 2:2 returnee)
    instead of leaving the reader to guess which one is meant. Grouping uses
    name_grouping_key rather than the raw name, so a bare name (e.g.
    "Hiram") still groups with a namesake whose canonical name bakes in a
    trailing " of <Place>" epithet (e.g. "Hiram of Tyre", "Eliezer of
    Damascus", "Judas of Galilee", "Lucius of Cyrene"). Stub entries carry
    no source_summary/portrait, so their card falls back to a
    reference-based blurb and a "name only" badge (see
    disambiguation_section)."""
    by_name = {}
    for entry in index:
        pid = entry["person_id"]
        person_path = ROOT / "data" / "people" / f"{pid}.json"
        if not person_path.exists():
            continue
        fp = json.loads(person_path.read_text())
        portrait_dir, portrait_file = resolve_portrait_file(fp)
        by_name.setdefault(name_grouping_key(fp["name"]).lower(), []).append({
            "person_id": pid,
            "name": fp["name"],
            "tier": entry["tier"],
            "source_summary": fp.get("source_summary", ""),
            "first_reference": fp.get("first_reference", ""),
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
    ref_by_id = {e["person_id"]: e.get("first_reference", "") for e in index}
    gender_by_id = {e["person_id"]: e.get("gender") for e in index}
    people_by_name = build_people_by_name(index)
    church_membership_by_person = build_church_membership_index(churches, index_by_id)
    link_ctx = link_person_mentions.build_context(index, connections)

    places_index = json.loads((ROOT / "data" / "places-index.json").read_text())
    places_by_name = build_places_by_name(places_index)
    place_membership_by_person = build_place_membership_index(places_index)

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
        page = build_person_page(person, index_by_id, gender_by_id, connections, people_by_name, church_membership_by_person, link_ctx, place_membership_by_person)
        (people_dir / f"{pid}.html").write_text(page)
        generated += 1

    update_people_grid(index)

    churches_dir = ROOT / "churches"
    churches_dir.mkdir(exist_ok=True)
    for church in churches:
        page = build_church_detail_page(church, index_by_id, gender_by_id)
        (churches_dir / f'{church["church_id"]}.html').write_text(page)
    (ROOT / "churches.html").write_text(build_churches_list_page(churches))

    places_dir = ROOT / "places"
    places_dir.mkdir(exist_ok=True)
    placed_places = [e for e in places_index if e.get("lat") is not None]
    for place_entry in places_index:
        place_path = ROOT / "data" / "places" / f'{place_entry["place_id"]}.json'
        if not place_path.exists():
            print(f"warning: no data/places/{place_entry['place_id']}.json, skipping")
            continue
        place = json.loads(place_path.read_text())
        page = build_place_detail_page(place, gender_by_id, places_by_name, link_ctx, placed_places)
        (places_dir / f'{place["place_id"]}.html').write_text(page)
    (ROOT / "places.html").write_text(build_places_list_page(places_index))
    (ROOT / "map.html").write_text(build_map_explorer_page(places_index))

    charts_dir = ROOT / "charts"
    charts_dir.mkdir(exist_ok=True)
    kp_rows, kp_unplotted = collect_kings_and_prophets()
    (charts_dir / "kings-and-prophets.html").write_text(build_kings_and_prophets_chart_page(kp_rows, kp_unplotted))
    (charts_dir / "genealogies-of-jesus.html").write_text(build_genealogies_chart_page(index_by_id, ref_by_id))
    (charts_dir / "twelve-tribes.html").write_text(build_tribe_sunburst_chart_page(build_tribe_layout()))
    (charts_dir / "job-chapters.html").write_text(build_job_chapters_chart_page(JC_CHAPTERS))
    (charts_dir / "genesis-chapters.html").write_text(build_genesis_chapters_chart_page(GC_CHAPTERS))
    (charts_dir / "acts-chapters.html").write_text(build_acts_chapters_chart_page(ACC_CHAPTERS))
    (ROOT / "charts.html").write_text(build_charts_list_page())

    build_sitemap(index, churches, places_index)

    print(f"Generated {generated} person pages, {len(churches)} church pages, {len(places_index)} place pages, "
          f"sitemap.xml, and people.html/churches.html/places.html/charts.html static output.")


if __name__ == "__main__":
    main()
