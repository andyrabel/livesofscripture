const DATA = {
  index: null,
  connections: null,
  whatsNew: null,
  quiz: null,
};

// ---------------------------------------------------------------------
// Cookie consent (Google Analytics)
//
// UK/EU/EEA visitors (detected via the browser's own timezone, never sent
// anywhere) see a banner and analytics only loads after they accept.
// Everywhere else analytics loads automatically, since prior consent isn't
// legally required there. A stored "declined" choice is honored everywhere,
// regardless of region, so "Manage cookie preferences" always works.
// ---------------------------------------------------------------------

const GA_MEASUREMENT_ID = "G-ZF8K07D6WG";
const COOKIE_CONSENT_KEY = "los_cookie_consent";

function regionRequiresCookieConsent() {
  try {
    const tz = Intl.DateTimeFormat().resolvedOptions().timeZone || "";
    return tz.startsWith("Europe/");
  } catch (e) {
    return false;
  }
}

function getCookieConsent() {
  try {
    return localStorage.getItem(COOKIE_CONSENT_KEY);
  } catch (e) {
    return null;
  }
}

function setCookieConsent(value) {
  try {
    localStorage.setItem(COOKIE_CONSENT_KEY, value);
  } catch (e) {
    /* ignore */
  }
}

function loadGoogleAnalytics() {
  if (window.__losGaLoaded) return;
  window.__losGaLoaded = true;
  window.dataLayer = window.dataLayer || [];
  function gtag() {
    window.dataLayer.push(arguments);
  }
  window.gtag = gtag;
  gtag("js", new Date());
  gtag("config", GA_MEASUREMENT_ID);
  const script = document.createElement("script");
  script.async = true;
  script.src = `https://www.googletagmanager.com/gtag/js?id=${GA_MEASUREMENT_ID}`;
  document.head.appendChild(script);
}

function hideCookieBanner() {
  const banner = document.getElementById("cookie-consent-banner");
  if (banner) banner.remove();
}

function showCookieBanner() {
  if (document.getElementById("cookie-consent-banner")) return;
  const banner = document.createElement("div");
  banner.id = "cookie-consent-banner";
  banner.className = "cookie-consent-banner";
  banner.setAttribute("role", "dialog");
  banner.setAttribute("aria-label", "Cookie preferences");
  banner.innerHTML = `
    <p>We use Google Analytics to see how many people visit and which pages
    help worship leaders and families most. This sets analytics cookies. No
    personal information is collected, sold, or used for advertising. See
    <a href="https://livesofscripture.org/about.html#cookies-analytics">Cookies &amp; Analytics</a>
    for details.</p>
    <div class="cookie-consent-actions">
      <button type="button" class="cookie-consent-decline">Decline</button>
      <button type="button" class="cookie-consent-accept">Accept</button>
    </div>`;
  document.body.appendChild(banner);

  banner.querySelector(".cookie-consent-accept").addEventListener("click", () => {
    setCookieConsent("accepted");
    hideCookieBanner();
    loadGoogleAnalytics();
  });
  banner.querySelector(".cookie-consent-decline").addEventListener("click", () => {
    setCookieConsent("declined");
    hideCookieBanner();
  });
}

function openCookiePreferences() {
  showCookieBanner();
}

function initCookieConsent() {
  const consent = getCookieConsent();
  if (consent === "accepted") {
    loadGoogleAnalytics();
  } else if (consent === "declined") {
    // Honor an explicit opt-out everywhere, not just in consent-required regions.
  } else if (regionRequiresCookieConsent()) {
    showCookieBanner();
  } else {
    loadGoogleAnalytics();
  }

  const manageLink = document.getElementById("manage-cookie-preferences");
  if (manageLink) {
    manageLink.addEventListener("click", (evt) => {
      evt.preventDefault();
      openCookiePreferences();
    });
  }
}

initCookieConsent();

function dataPath(path) {
  return `data/${path}`;
}

async function loadIndex() {
  if (!DATA.index) {
    const res = await fetch(dataPath("people.json"));
    DATA.index = await res.json();
  }
  return DATA.index;
}

async function loadConnections() {
  if (!DATA.connections) {
    const res = await fetch(dataPath("connections.json"));
    DATA.connections = await res.json();
  }
  return DATA.connections;
}

async function loadPlacesIndex() {
  if (!DATA.placesIndex) {
    const res = await fetch(dataPath("places-index.json"));
    DATA.placesIndex = await res.json();
  }
  return DATA.placesIndex;
}

async function loadPlaceConnections() {
  if (!DATA.placeConnections) {
    const res = await fetch(dataPath("place-connections.json"));
    DATA.placeConnections = await res.json();
  }
  return DATA.placeConnections;
}

async function loadPlace(id) {
  const res = await fetch(dataPath(`places/${id}.json`));
  if (!res.ok) return null;
  return res.json();
}

// A place node in the connections graph is given the id "place:<place_id>"
// so it can share the same person_id-keyed adjacency/index machinery as a
// person node (see renderConnectionsPage). This turns a places-index.json
// entry into that shape.
function placeToGraphEntry(place) {
  return {
    person_id: `place:${place.place_id}`,
    name: place.name,
    alt_names: place.alt_names || [],
    kind: "place",
    place_type: place.type,
    era: place.eras && place.eras[0],
    eras: place.eras || [],
    tier: place.tier,
  };
}

function isPlaceNodeId(id) {
  return typeof id === "string" && id.startsWith("place:");
}

function graphNodeHref(entry, id) {
  if (isPlaceNodeId(id)) {
    return `places/${encodeURIComponent(id.slice("place:".length))}.html`;
  }
  return `people/${encodeURIComponent(id)}.html`;
}

async function loadPerson(id) {
  const res = await fetch(dataPath(`people/${id}.json`));
  if (!res.ok) return null;
  return res.json();
}

async function loadWhatsNew() {
  if (!DATA.whatsNew) {
    const res = await fetch(dataPath("whats-new.json"));
    DATA.whatsNew = (await res.json()).entries;
  }
  return DATA.whatsNew;
}

async function loadQuiz() {
  if (!DATA.quiz) {
    const res = await fetch(dataPath("quiz.json"));
    DATA.quiz = (await res.json()).questions;
  }
  return DATA.quiz;
}

function initNavToggle() {
  const toggle = document.getElementById("nav-toggle");
  const nav = document.getElementById("site-nav");
  if (!toggle || !nav) return;

  toggle.addEventListener("click", () => {
    const open = nav.classList.toggle("nav-open");
    toggle.setAttribute("aria-expanded", open ? "true" : "false");
  });

  nav.addEventListener("click", (evt) => {
    if (evt.target.tagName === "A") {
      nav.classList.remove("nav-open");
      toggle.setAttribute("aria-expanded", "false");
    }
  });
}

// Places list page (places.html): the grid is server-rendered with every
// place in it, but the name-only (stub) cards are hidden by CSS until the
// visitor ticks "Include name-only places", which toggles .show-stub-places
// on the grid. Purely presentational -- no data fetch, works with JS off
// (the box just does nothing and the default full-place list stays shown).
function initPlacesToggle() {
  const checkbox = document.getElementById("places-include-stubs");
  const grid = document.getElementById("place-grid");
  if (!checkbox || !grid) return;
  const apply = () => grid.classList.toggle("show-stub-places", checkbox.checked);
  checkbox.addEventListener("change", apply);
  apply();
}

// Hover/focus tooltip layer for the server-rendered Kings & Prophets SVG
// chart (charts/kings-and-prophets.html) -- the chart itself is fully
// legible without this (native <title> tooltips + the table view below it
// both work with JS off), this only adds the nicer positioned HTML tooltip.
function initKpChartTooltips() {
  const bars = document.querySelectorAll(".kp-bar");
  if (!bars.length) return;

  const tooltip = document.createElement("div");
  tooltip.className = "kp-tooltip";
  tooltip.hidden = true;
  document.body.appendChild(tooltip);

  function show(bar, x, y) {
    tooltip.textContent = "";
    const strong = document.createElement("strong");
    strong.textContent = `${bar.dataset.name} — ${bar.dataset.nation}`;
    tooltip.appendChild(strong);
    tooltip.appendChild(document.createTextNode(`${bar.dataset.span} (${bar.dataset.reference})`));
    tooltip.hidden = false;
    const pad = 12;
    tooltip.style.left = `${Math.min(x + pad, window.innerWidth - tooltip.offsetWidth - pad)}px`;
    tooltip.style.top = `${Math.max(y - tooltip.offsetHeight - pad, pad)}px`;
  }

  function hide() {
    tooltip.hidden = true;
  }

  bars.forEach((bar) => {
    bar.addEventListener("pointermove", (evt) => show(bar, evt.clientX, evt.clientY));
    bar.addEventListener("pointerenter", (evt) => show(bar, evt.clientX, evt.clientY));
    bar.addEventListener("pointerleave", hide);
    bar.addEventListener("focus", () => {
      const rect = bar.getBoundingClientRect();
      show(bar, rect.left, rect.top);
    });
    bar.addEventListener("blur", hide);
  });
}

// Same pattern as initKpChartTooltips() above, for the server-rendered "Two
// Genealogies of Jesus" SVG chart (charts/genealogies-of-jesus.html) --
// native <title> tooltips + the two full-list tables below the chart both
// work with JS off, this only adds the nicer positioned HTML tooltip.
function initGenChartTooltips() {
  const nodes = document.querySelectorAll(".gen-node, .gen-node-terminus");
  if (!nodes.length) return;

  const tooltip = document.createElement("div");
  tooltip.className = "kp-tooltip";
  tooltip.hidden = true;
  document.body.appendChild(tooltip);

  function show(node, x, y) {
    tooltip.textContent = "";
    const strong = document.createElement("strong");
    strong.textContent = node.dataset.name;
    tooltip.appendChild(strong);
    const detail = node.dataset.reference
      ? `${node.dataset.note} (${node.dataset.reference})`
      : node.dataset.note;
    tooltip.appendChild(document.createTextNode(detail));
    tooltip.hidden = false;
    const pad = 12;
    tooltip.style.left = `${Math.min(x + pad, window.innerWidth - tooltip.offsetWidth - pad)}px`;
    tooltip.style.top = `${Math.max(y - tooltip.offsetHeight - pad, pad)}px`;
  }

  function hide() {
    tooltip.hidden = true;
  }

  nodes.forEach((node) => {
    node.addEventListener("pointermove", (evt) => show(node, evt.clientX, evt.clientY));
    node.addEventListener("pointerenter", (evt) => show(node, evt.clientX, evt.clientY));
    node.addEventListener("pointerleave", hide);
    node.addEventListener("focus", () => {
      const rect = node.getBoundingClientRect();
      show(node, rect.left, rect.top);
    });
    node.addEventListener("blur", hide);
  });
}

// Same pattern as initKpChartTooltips()/initGenChartTooltips() above, for
// the server-rendered "Twelve Tribes, By Mother" sunburst
// (charts/twelve-tribes.html) -- native <title> tooltips + the full-list
// table below the chart both work with JS off, this only adds the nicer
// positioned HTML tooltip. Only .tsun-leaf (the minor-tribe individual
// spokes) and .tsun-mega-arc (the Judah/Levi/Benjamin mass bands) carry
// tooltip data -- the mother/tribe band labels are already always visible
// as text, so don't need one.
function initTribeChartTooltips() {
  const nodes = document.querySelectorAll(".tsun-leaf, .tsun-mega-arc");
  if (!nodes.length) return;

  const tooltip = document.createElement("div");
  tooltip.className = "kp-tooltip";
  tooltip.hidden = true;
  document.body.appendChild(tooltip);

  function show(node, x, y) {
    tooltip.textContent = "";
    const strong = document.createElement("strong");
    const isMega = node.classList.contains("tsun-mega-arc");
    strong.textContent = isMega ? `Tribe of ${node.dataset.tribe}` : node.dataset.name;
    tooltip.appendChild(strong);
    const detail = isMega
      ? `${node.dataset.n} people — see the full list below the chart`
      : `Tribe of ${node.dataset.tribe} — ${node.dataset.testament === "OT" ? "Old Testament" : "New Testament"} — ${node.dataset.ref}`;
    tooltip.appendChild(document.createTextNode(detail));
    tooltip.hidden = false;
    const pad = 12;
    tooltip.style.left = `${Math.min(x + pad, window.innerWidth - tooltip.offsetWidth - pad)}px`;
    tooltip.style.top = `${Math.max(y - tooltip.offsetHeight - pad, pad)}px`;
  }

  function hide() {
    tooltip.hidden = true;
  }

  nodes.forEach((node) => {
    node.addEventListener("pointermove", (evt) => show(node, evt.clientX, evt.clientY));
    node.addEventListener("pointerenter", (evt) => show(node, evt.clientX, evt.clientY));
    node.addEventListener("pointerleave", hide);
    node.addEventListener("focus", () => {
      const rect = node.getBoundingClientRect();
      show(node, rect.left, rect.top);
    });
    node.addEventListener("blur", hide);
  });
}

// Full-screen zoomable view of a server-rendered SVG chart, for readers who
// find the inline chart's native size too small -- it's real vector content
// (not a raster image), so scaling it up via width/height keeps text crisp
// at any zoom level rather than pixelating like an <img> zoom would.
// Originally written just for the Kings & Prophets chart (hence the
// "kp-chart-lightbox-*" CSS class names, kept as-is rather than renamed to
// avoid a pure-rename diff); initKpChartLightbox() below is a thin wrapper
// kept for that one call site, and charts/twelve-tribes.html calls this
// directly with its own element ids.
function initChartLightbox(triggerId, sourceId, dialogLabel) {
  const trigger = document.getElementById(triggerId);
  const source = document.getElementById(sourceId);
  if (!trigger || !source) return;

  const viewBox = source.viewBox.baseVal;
  // Floor used to be 100% (the lightbox was built to zoom in only), but
  // wide charts like job-chapters.html's 42-chapter timeline can be wider
  // than the viewport even at 100%, so readers need to zoom *out* past
  // that to see the whole thing without scrolling.
  const ZOOM_MIN = 0.25;
  const ZOOM_MAX = 4;
  const ZOOM_STEP = 0.25;
  let scale = 1.75;

  trigger.addEventListener("click", () => {
    const overlay = document.createElement("div");
    overlay.className = "kp-chart-lightbox-overlay";
    overlay.setAttribute("role", "dialog");
    overlay.setAttribute("aria-modal", "true");
    overlay.setAttribute("aria-label", dialogLabel);

    const toolbar = document.createElement("div");
    toolbar.className = "kp-chart-lightbox-toolbar";

    const zoomOut = document.createElement("button");
    zoomOut.type = "button";
    zoomOut.textContent = "−";
    zoomOut.setAttribute("aria-label", "Zoom out");

    const zoomLabel = document.createElement("span");
    zoomLabel.className = "kp-chart-lightbox-zoom-label";

    const zoomIn = document.createElement("button");
    zoomIn.type = "button";
    zoomIn.textContent = "+";
    zoomIn.setAttribute("aria-label", "Zoom in");

    const closeBtn = document.createElement("button");
    closeBtn.type = "button";
    closeBtn.className = "kp-chart-lightbox-close";
    closeBtn.textContent = "✕ Close";

    toolbar.append(zoomOut, zoomLabel, zoomIn, closeBtn);

    const scroll = document.createElement("div");
    scroll.className = "kp-chart-lightbox-scroll";
    const clone = source.cloneNode(true);
    clone.removeAttribute("id");
    scroll.appendChild(clone);

    overlay.append(toolbar, scroll);

    function applyScale() {
      clone.setAttribute("width", Math.round(viewBox.width * scale));
      clone.setAttribute("height", Math.round(viewBox.height * scale));
      zoomLabel.textContent = `${Math.round(scale * 100)}%`;
      zoomOut.disabled = scale <= ZOOM_MIN;
      zoomIn.disabled = scale >= ZOOM_MAX;
    }

    function close() {
      overlay.remove();
      document.removeEventListener("keydown", onKeyDown);
      trigger.focus();
    }
    function onKeyDown(evt) {
      if (evt.key === "Escape") close();
    }

    zoomOut.addEventListener("click", () => {
      scale = Math.max(ZOOM_MIN, scale - ZOOM_STEP);
      applyScale();
    });
    zoomIn.addEventListener("click", () => {
      scale = Math.min(ZOOM_MAX, scale + ZOOM_STEP);
      applyScale();
    });
    closeBtn.addEventListener("click", close);
    overlay.addEventListener("click", (evt) => {
      if (evt.target === overlay) close();
    });
    document.addEventListener("keydown", onKeyDown);

    document.body.appendChild(overlay);
    applyScale();
    closeBtn.focus();
  });
}

function initKpChartLightbox() {
  initChartLightbox("kp-chart-expand", "kp-chart-svg", "Kings and Prophets chart, enlarged");
}

// "Copy image" button for the server-rendered chart SVGs. Rasterizes the
// live SVG (at a higher pixel density than its native size, so pasted
// copies stay crisp) onto an offscreen canvas and writes the PNG to the
// clipboard. The SVG's own colors/fonts come from CSS custom properties
// and classes defined in css/style.css, which aren't available inside the
// standalone SVG document a clipboard/canvas render uses, so the chart's
// external stylesheet is fetched once and embedded directly in the cloned
// SVG, with every custom property it declares then re-resolved against the
// live page and appended last -- this guarantees the export matches
// whatever theme (system or an explicit light/dark toggle) the visitor is
// actually looking at, rather than only following prefers-color-scheme.
const CHART_COPY_RENDER_SCALE = 3;
let chartStylesheetTextPromise = null;

function fetchChartStylesheetText() {
  if (!chartStylesheetTextPromise) {
    const link = document.querySelector('link[rel="stylesheet"]');
    chartStylesheetTextPromise = fetch(link.href).then((res) => res.text());
  }
  return chartStylesheetTextPromise;
}

async function buildChartExportSvgText(source) {
  const stylesheetText = await fetchChartStylesheetText();
  const customPropNames = new Set();
  for (const m of stylesheetText.matchAll(/--[a-zA-Z0-9-]+(?=\s*:)/g)) {
    customPropNames.add(m[0]);
  }
  const rootStyle = getComputedStyle(document.documentElement);
  let overrideRule = ":root{";
  customPropNames.forEach((name) => {
    overrideRule += `${name}:${rootStyle.getPropertyValue(name).trim()};`;
  });
  overrideRule += "}";

  const viewBox = source.viewBox.baseVal;
  const clone = source.cloneNode(true);
  clone.removeAttribute("id");
  clone.setAttribute("width", Math.round(viewBox.width * CHART_COPY_RENDER_SCALE));
  clone.setAttribute("height", Math.round(viewBox.height * CHART_COPY_RENDER_SCALE));

  const bg = document.createElementNS("http://www.w3.org/2000/svg", "rect");
  bg.setAttribute("x", viewBox.x);
  bg.setAttribute("y", viewBox.y);
  bg.setAttribute("width", viewBox.width);
  bg.setAttribute("height", viewBox.height);
  bg.setAttribute("fill", rootStyle.getPropertyValue("--color-surface").trim() || "#ffffff");
  clone.insertBefore(bg, clone.firstChild);

  const styleEl = document.createElementNS("http://www.w3.org/2000/svg", "style");
  styleEl.textContent = `${stylesheetText}\n${overrideRule}`;
  clone.insertBefore(styleEl, clone.firstChild);

  return new XMLSerializer().serializeToString(clone);
}

function chartExportFilename(source) {
  const label = source.getAttribute("aria-label") || source.id || "chart";
  const slug = label
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "")
    .slice(0, 60);
  return `${slug || "chart"}.png`;
}

function downloadBlob(blob, filename) {
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
}

function initChartCopyButton(triggerId, sourceId) {
  const trigger = document.getElementById(triggerId);
  const source = document.getElementById(sourceId);
  if (!trigger || !source) return;

  const originalLabel = trigger.textContent;

  trigger.addEventListener("click", async () => {
    trigger.disabled = true;
    trigger.classList.remove("copied", "copy-failed");
    trigger.textContent = "Copying…";
    try {
      const svgText = await buildChartExportSvgText(source);
      const svgBlob = new Blob([svgText], { type: "image/svg+xml;charset=utf-8" });
      const svgUrl = URL.createObjectURL(svgBlob);
      const img = new Image();
      await new Promise((resolve, reject) => {
        img.onload = resolve;
        img.onerror = reject;
        img.src = svgUrl;
      });

      const canvas = document.createElement("canvas");
      canvas.width = img.naturalWidth;
      canvas.height = img.naturalHeight;
      canvas.getContext("2d").drawImage(img, 0, 0);
      URL.revokeObjectURL(svgUrl);

      const pngBlob = await new Promise((resolve) => canvas.toBlob(resolve, "image/png"));
      if (!pngBlob) throw new Error("canvas.toBlob returned no data");

      if (navigator.clipboard && window.ClipboardItem) {
        await navigator.clipboard.write([new ClipboardItem({ "image/png": pngBlob })]);
        trigger.textContent = "✓ Copied!";
        trigger.classList.add("copied");
      } else {
        downloadBlob(pngBlob, chartExportFilename(source));
        trigger.textContent = "Downloaded";
        trigger.classList.add("copied");
      }
    } catch (err) {
      trigger.textContent = "Copy failed";
      trigger.classList.add("copy-failed");
    }
    setTimeout(() => {
      trigger.disabled = false;
      trigger.textContent = originalLabel;
      trigger.classList.remove("copied", "copy-failed");
    }, 2000);
  });
}

function initPortraitLightbox() {
  const trigger = document.querySelector(".portrait-lightbox");
  if (!trigger) return;

  function openLightbox(href, alt) {
    const overlay = document.createElement("div");
    overlay.className = "portrait-lightbox-overlay";
    overlay.setAttribute("role", "dialog");
    overlay.setAttribute("aria-modal", "true");

    const img = document.createElement("img");
    img.src = href;
    img.alt = alt;
    overlay.appendChild(img);

    function close() {
      overlay.remove();
      document.removeEventListener("keydown", onKeyDown);
    }
    function onKeyDown(evt) {
      if (evt.key === "Escape") close();
    }

    overlay.addEventListener("click", close);
    document.addEventListener("keydown", onKeyDown);
    document.body.appendChild(overlay);
  }

  trigger.addEventListener("click", (evt) => {
    evt.preventDefault();
    const img = trigger.querySelector("img");
    openLightbox(trigger.href, img ? img.alt : "");
  });
}

const STORY_PREF_KEY = "preferred-story-version";

function getStoryVersion() {
  return localStorage.getItem(STORY_PREF_KEY) || "adult";
}

function setStoryVersion(v) {
  localStorage.setItem(STORY_PREF_KEY, v);
}

function initPersonStory() {
  const wrapper = document.querySelector(".story-tabs-wrapper");
  if (!wrapper) return;

  function applyVersion(v) {
    wrapper.querySelectorAll(".story-tab").forEach((b) => {
      const active = b.dataset.version === v;
      b.classList.toggle("active", active);
      b.setAttribute("aria-selected", String(active));
    });
    wrapper.querySelectorAll(".story-panel").forEach((p) => {
      p.classList.toggle("hidden", p.dataset.version !== v);
    });
  }

  applyVersion(getStoryVersion());

  wrapper.querySelectorAll(".story-tab").forEach((btn) => {
    btn.addEventListener("click", () => {
      const v = btn.dataset.version;
      setStoryVersion(v);
      applyVersion(v);
    });
  });

  wrapper.querySelectorAll("[data-copy-version]").forEach((btn) => {
    btn.addEventListener("click", async () => {
      const panel = wrapper.querySelector(`.story-panel[data-version="${btn.dataset.copyVersion}"]`);
      const storyText = panel ? panel.querySelector(".story-text").innerText : "";
      const personName = wrapper.dataset.personName || "";
      const text = personName ? `${personName}\n\n${storyText}` : storyText;
      const original = btn.textContent;
      try {
        await navigator.clipboard.writeText(text);
        btn.textContent = "Copied!";
        btn.classList.add("copied");
      } catch (err) {
        btn.textContent = "Copy failed";
      }
      setTimeout(() => {
        btn.textContent = original;
        btn.classList.remove("copied");
      }, 2000);
    });
  });

  wrapper.querySelectorAll("[data-read-version]").forEach((btn) => {
    btn.disabled = false;
    btn.addEventListener("click", () => {
      const panel = wrapper.querySelector(`.story-panel[data-version="${btn.dataset.readVersion}"]`);
      const storyText = panel ? panel.querySelector(".story-text").innerText : "";
      const personName = wrapper.dataset.personName || "";
      readAloud(storyText, personName, btn);
    });
  });
}

// The site stores story text as plain, already-escaped prose (no markdown or
// wiki-style links), but this guards against any inline markup that sneaks
// into future content before it reaches the speech synthesizer.
function stripLinks(text) {
  return text
    .replace(/\[\[([^\]|]+)\|[^\]]+\]\]/g, "$1")
    .replace(/\[([^\]]+)\]\([^)]+\)/g, "$1");
}

function flashButton(button, message, isError) {
  const original = button.dataset.originalLabel || button.textContent;
  button.dataset.originalLabel = original;
  button.textContent = message;
  setTimeout(() => {
    button.textContent = original;
  }, 2000);
}

let currentReadButton = null;

function resetReadButton(button) {
  button.textContent = button.dataset.originalLabel || button.textContent;
  button.classList.remove("reading");
  if (currentReadButton === button) currentReadButton = null;
}

function readAloud(text, label, button) {
  if (!("speechSynthesis" in window)) {
    flashButton(button, "Not supported in this browser", true);
    return;
  }

  const wasReadingThis = currentReadButton === button;

  if (currentReadButton) resetReadButton(currentReadButton);

  window.speechSynthesis.cancel();

  if (wasReadingThis) return; // second click stops playback

  const spoken = label ? `${label}. ${stripLinks(text)}` : stripLinks(text);
  const utterance = new SpeechSynthesisUtterance(spoken);
  utterance.rate = 0.95;

  utterance.onend = () => resetReadButton(button);
  utterance.onerror = () => resetReadButton(button);

  button.dataset.originalLabel = button.dataset.originalLabel || button.textContent;

  button.textContent = "⏹ Stop Reading";
  button.classList.add("reading");
  currentReadButton = button;

  window.speechSynthesis.speak(utterance);
}

function matchesSearch(entry, query) {
  if (!query) return true;
  const q = query.trim().toLowerCase();
  if (entry.name.toLowerCase().includes(q)) return true;
  return (entry.alt_names || []).some((n) => n.toLowerCase().includes(q));
}

function personCard(entry) {
  const a = document.createElement("a");
  a.className = "person-card";
  a.href = `people/${encodeURIComponent(entry.person_id)}.html`;

  const name = document.createElement("div");
  name.className = "name";
  const nameText = document.createElement(entry.tier === "stub" ? "span" : "strong");
  nameText.className = "name-text";
  nameText.textContent = entry.name;
  name.appendChild(nameText);
  const tag = genderTag(entry.gender);
  if (tag) {
    name.appendChild(document.createTextNode(" "));
    name.appendChild(tag);
  }
  a.appendChild(name);

  if (entry.disambiguation) {
    const disamb = document.createElement("div");
    disamb.className = "disambiguation";
    disamb.textContent = entry.disambiguation;
    a.appendChild(disamb);
  }

  const meta = document.createElement("div");
  meta.className = "meta";

  const testamentBadge = document.createElement("span");
  testamentBadge.className = `badge ${entry.testament === "OT" ? "ot" : "nt"}`;
  testamentBadge.textContent = entry.testament;
  meta.appendChild(testamentBadge);

  if (entry.tier === "stub") {
    const stubBadge = document.createElement("span");
    stubBadge.className = "badge stub";
    stubBadge.textContent = "name only";
    meta.appendChild(stubBadge);
  } else if (entry.era) {
    const eraBadge = document.createElement("span");
    eraBadge.className = "badge";
    eraBadge.textContent = entry.era;
    meta.appendChild(eraBadge);
  }

  a.appendChild(meta);
  return a;
}

async function renderWhatsNew() {
  const box = document.getElementById("whats-new");
  if (!box) return;
  const entries = await loadWhatsNew();
  const recent = entries
    .slice()
    .sort((a, b) => b.date.localeCompare(a.date))
    .slice(0, 4);

  if (!recent.length) {
    box.hidden = true;
    return;
  }

  const list = document.createElement("ul");
  list.className = "whats-new__list";
  for (const entry of recent) {
    const li = document.createElement("li");
    const a = document.createElement("a");
    a.href = entry.page;
    a.textContent = entry.title;
    li.appendChild(a);
    li.appendChild(document.createTextNode(` — ${entry.description}`));
    const date = document.createElement("span");
    date.className = "whats-new__date";
    date.textContent = entry.date;
    li.appendChild(date);
    list.appendChild(li);
  }
  box.querySelector(".whats-new__list")?.remove();
  box.appendChild(list);
}

async function renderIndexPage() {
  const grid = document.getElementById("person-grid");
  const countEl = document.getElementById("result-count");
  const emptyEl = document.getElementById("empty-state");
  const searchInput = document.getElementById("search-input");
  const testamentFilter = document.getElementById("filter-testament");
  const includeStubsCheckbox = document.getElementById("filter-include-stubs");
  const eraFilter = document.getElementById("filter-era");
  const genderFilter = document.getElementById("filter-gender");
  const kingdomFilter = document.getElementById("filter-kingdom");
  const regionFilter = document.getElementById("filter-region");
  const sortOrder = document.getElementById("sort-order");

  const index = await loadIndex();

  const initialQuery = new URLSearchParams(window.location.search).get("q");
  if (initialQuery) searchInput.value = initialQuery;

  const eras = [...new Set(index.filter((e) => e.era).map((e) => e.era))].sort((a, b) => {
    const ai = ERA_ORDER.indexOf(a);
    const bi = ERA_ORDER.indexOf(b);
    if (ai === -1 && bi === -1) return a.localeCompare(b);
    if (ai === -1) return 1;
    if (bi === -1) return -1;
    return ai - bi;
  });
  for (const era of eras) {
    const opt = document.createElement("option");
    opt.value = era;
    opt.textContent = era;
    eraFilter.appendChild(opt);
  }

  const presentRegions = new Set(index.filter((e) => e.region).map((e) => e.region));
  for (const region of TIMELINE_REGIONS) {
    if (!presentRegions.has(region.key)) continue;
    const opt = document.createElement("option");
    opt.value = region.key;
    opt.textContent = region.label;
    regionFilter.appendChild(opt);
  }

  function render() {
    const query = searchInput.value;
    const testament = testamentFilter.value;
    const includeStubs = includeStubsCheckbox.checked;
    const era = eraFilter.value;
    const gender = genderFilter.value;
    const kingdom = kingdomFilter.value;
    const region = regionFilter.value;

    const filtered = index.filter((entry) => {
      if (!includeStubs && entry.tier === "stub") return false;
      if (!matchesSearch(entry, query)) return false;
      if (testament && entry.testament !== testament) return false;
      if (era && entry.era !== era) return false;
      if (gender && entry.gender !== gender) return false;
      if (kingdom && entry.kingdom !== kingdom) return false;
      if (region && entry.region !== region) return false;
      return true;
    });

    filtered.sort((a, b) => {
      switch (sortOrder.value) {
        case "name-desc":
          return b.name.localeCompare(a.name);
        case "era-asc":
        case "era-desc": {
          const ai = a.era ? ERA_ORDER.indexOf(a.era) : -1;
          const bi = b.era ? ERA_ORDER.indexOf(b.era) : -1;
          // People with no era (stubs) always sort last, in either direction.
          if (ai === -1 && bi === -1) return a.name.localeCompare(b.name);
          if (ai === -1) return 1;
          if (bi === -1) return -1;
          if (ai !== bi) return sortOrder.value === "era-asc" ? ai - bi : bi - ai;
          return a.name.localeCompare(b.name);
        }
        case "name-asc":
        default:
          return a.name.localeCompare(b.name);
      }
    });

    grid.innerHTML = "";
    for (const entry of filtered) {
      grid.appendChild(personCard(entry));
    }

    countEl.textContent = `${filtered.length} of ${index.length} people`;
    emptyEl.style.display = filtered.length === 0 ? "block" : "none";
  }

  searchInput.addEventListener("input", render);
  testamentFilter.addEventListener("change", render);
  includeStubsCheckbox.addEventListener("change", render);
  eraFilter.addEventListener("change", render);
  genderFilter.addEventListener("change", render);
  kingdomFilter.addEventListener("change", render);
  regionFilter.addEventListener("change", render);
  sortOrder.addEventListener("change", render);

  render();
}

function nameForId(index, id) {
  const entry = index.find((e) => e.person_id === id);
  return entry ? entry.name : id;
}

// ---------------------------------------------------------------------
// Home page: daily digest
// ---------------------------------------------------------------------

function todayKey() {
  const d = new Date();
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, "0");
  const day = String(d.getDate()).padStart(2, "0");
  return `${y}-${m}-${day}`;
}

function seededHash(str) {
  let h = 2166136261;
  for (let i = 0; i < str.length; i++) {
    h ^= str.charCodeAt(i);
    h = Math.imul(h, 16777619);
  }
  return h >>> 0;
}

function dailyPick(seedPrefix, list) {
  if (!list || !list.length) return null;
  const idx = seededHash(`${seedPrefix}:${todayKey()}`) % list.length;
  return list[idx];
}

function mulberry32(seed) {
  let a = seed;
  return function () {
    a |= 0;
    a = (a + 0x6d2b79f5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

function dailySeededShuffle(seedPrefix, list) {
  const rand = mulberry32(seededHash(`${seedPrefix}:${todayKey()}`));
  const arr = list.slice();
  for (let i = arr.length - 1; i > 0; i--) {
    const j = Math.floor(rand() * (i + 1));
    [arr[i], arr[j]] = [arr[j], arr[i]];
  }
  return arr;
}

function initials(name) {
  return name
    .split(/\s+/)
    .map((w) => w[0])
    .filter(Boolean)
    .slice(0, 2)
    .join("")
    .toUpperCase();
}

function genderTag(gender) {
  if (gender !== "male" && gender !== "female") return null;
  const span = document.createElement("span");
  span.className = `gender-tag gender-tag--${gender}`;
  span.textContent = gender === "male" ? "(M)" : "(F)";
  return span;
}

function portraitImg(personId, name, className, imageFile, gender, image2File) {
  const img = document.createElement("img");
  img.src = image2File
    ? `images/portraits2-web/${personId}.jpg`
    : `images/portraits/${imageFile || `${personId}.png`}`;
  img.alt = name;
  img.className = className;
  img.onerror = () => {
    const placeholder = document.createElement("div");
    if (gender === "male" || gender === "female") {
      placeholder.className = `${className} avatar-placeholder avatar-placeholder--icon avatar-placeholder--${gender}`;
    } else {
      placeholder.className = `${className} avatar-placeholder`;
      placeholder.textContent = initials(name);
    }
    img.replaceWith(placeholder);
  };
  return img;
}

function truncateExcerpt(text, max) {
  if (!text || text.length <= max) return text || "";
  const cut = text.slice(0, max);
  const lastSpace = cut.lastIndexOf(" ");
  return `${cut.slice(0, lastSpace)}…`;
}

const QUIZ_DIFFICULTY_KEY = "preferred-quiz-difficulty";

function getPreferredQuizDifficulty() {
  const stored = Number(localStorage.getItem(QUIZ_DIFFICULTY_KEY));
  return stored === 1 || stored === 2 || stored === 3 ? stored : 1;
}

function setPreferredQuizDifficulty(difficulty) {
  localStorage.setItem(QUIZ_DIFFICULTY_KEY, String(difficulty));
}

// Builds a sorted (longest-first) list of [name, topic_id] pairs so that a
// full name matches before a shorter substring of it (e.g. a two-word name
// before either word alone).
function quizNameEntries(index) {
  const byName = new Map();
  for (const p of index) {
    byName.set(p.name, p.person_id);
    for (const alt of p.alt_names || []) byName.set(alt, p.person_id);
  }
  return [...byName.entries()].sort((a, b) => b[0].length - a[0].length);
}

function escapeRegExp(str) {
  return str.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

// Wraps any name from nameEntries that already appears as plain text in
// `text` with a link to that person's page. Never introduces a name that
// wasn't already visible, so it can't leak the answer to a different
// question whose hidden answer is that name.
function renderTextWithNameLinks(el, text, nameEntries) {
  el.textContent = "";
  if (!nameEntries.length) {
    el.appendChild(document.createTextNode(text));
    return;
  }
  const idByName = new Map(nameEntries);
  const pattern = nameEntries.map(([name]) => escapeRegExp(name)).join("|");
  const regex = new RegExp(`\\b(?:${pattern})\\b`, "g");
  let lastIndex = 0;
  let match;
  while ((match = regex.exec(text))) {
    if (match.index > lastIndex) {
      el.appendChild(document.createTextNode(text.slice(lastIndex, match.index)));
    }
    const a = document.createElement("a");
    a.href = `people/${encodeURIComponent(idByName.get(match[0]))}.html`;
    a.textContent = match[0];
    el.appendChild(a);
    lastIndex = regex.lastIndex;
  }
  el.appendChild(document.createTextNode(text.slice(lastIndex)));
}

function renderQuizAnswerBlock(container, q, index) {
  container.innerHTML = "";

  const strong = document.createElement("strong");
  strong.textContent = q.answer;
  container.appendChild(strong);

  if (q.reference) {
    container.appendChild(document.createTextNode(" "));
    const ref = document.createElement("span");
    ref.className = "home-quiz-box__answer-ref";
    ref.textContent = `(${q.reference})`;
    container.appendChild(ref);
  }

  // Attribution only makes sense for a sub-entity question (e.g. a hymn
  // under a person) where the topic is distinct from what's being asked
  // about; for a plain person-topic question it would just repeat the
  // "Learn more" link's own name.
  if (q.subtopic_id) {
    container.appendChild(document.createTextNode(" "));
    const attribution = document.createElement("span");
    attribution.className = "home-quiz-box__answer-attribution";
    attribution.textContent = `(by ${nameForId(index, q.topic_id)})`;
    container.appendChild(attribution);
  }

  const learnMore = document.createElement("a");
  learnMore.className = "home-quiz-box__answer-link";
  learnMore.href = `people/${encodeURIComponent(q.topic_id)}.html`;
  learnMore.textContent = "Learn more →";
  container.appendChild(learnMore);

  container.tabIndex = -1;
  container.focus();
}

function renderQuizPick(quiz, index) {
  const maxDifficulty = getPreferredQuizDifficulty();
  const pool = quiz.filter((q) => q.difficulty <= maxDifficulty);
  const pick = dailyPick("question-of-the-day", pool);
  const nameEntries = quizNameEntries(index);

  const box = document.getElementById("home-quiz");
  box.innerHTML = "";

  if (!pick) {
    box.hidden = true;
    return;
  }
  box.hidden = false;

  const label = document.createElement("span");
  label.className = "home-quiz-box__label";
  label.textContent = "Quiz Question:";
  box.appendChild(label);

  const q = document.createElement("span");
  q.className = "home-quiz-box__question";
  renderTextWithNameLinks(q, pick.question, nameEntries);
  box.appendChild(q);

  const btn = document.createElement("button");
  btn.type = "button";
  btn.className = "home-quiz-box__reveal-btn";
  btn.textContent = "Reveal Answer";
  box.appendChild(btn);

  const cta = document.createElement("a");
  cta.className = "home-quiz-box__cta";
  cta.href = `quiz.html?max=${maxDifficulty}`;
  cta.textContent = "Take the quiz →";

  btn.addEventListener("click", () => {
    btn.remove();
    const answer = document.createElement("span");
    answer.className = "home-quiz-box__answer";
    box.insertBefore(answer, cta);
    renderQuizAnswerBlock(answer, pick, index);
  });

  box.appendChild(cta);
}

function initHomeQuiz(quiz, index) {
  renderQuizPick(quiz, index);
}

async function renderHomeSpotlight(fullTier) {
  const box = document.getElementById("home-spotlight");
  const pick = dailyPick("spotlight", fullTier);
  if (!pick) {
    box.hidden = true;
    return;
  }
  const person = await loadPerson(pick.person_id);
  box.innerHTML = "";
  const thumb = portraitImg(pick.person_id, pick.name, "home-spotlight__thumb", pick.image, undefined, pick.image2);
  const personHref = `people/${encodeURIComponent(pick.person_id)}.html`;

  const media = document.createElement("div");
  media.className = "home-spotlight__media";
  if (pick.image2) {
    const thumbLink = document.createElement("a");
    thumbLink.className = "home-spotlight__thumb-link portrait-lightbox";
    thumbLink.href = `images/portraits2-web/${pick.person_id}-full.jpg`;
    thumbLink.target = "_blank";
    thumbLink.rel = "noopener";
    thumbLink.setAttribute("aria-label", `View full-size image of ${pick.name}`);
    thumbLink.appendChild(thumb);
    media.appendChild(thumbLink);
  } else {
    media.appendChild(thumb);
  }

  const excerptText = truncateExcerpt(person?.source_summary, 280);

  const actions = document.createElement("div");
  actions.className = "home-spotlight__actions";

  const readBtn = document.createElement("button");
  readBtn.type = "button";
  readBtn.className = "btn-story home-spotlight__action";
  readBtn.textContent = "\u{1F50A} Read Aloud";
  readBtn.addEventListener("click", () => readAloud(excerptText, pick.name, readBtn));
  actions.appendChild(readBtn);

  const copyBtn = document.createElement("button");
  copyBtn.type = "button";
  copyBtn.className = "btn-story home-spotlight__action";
  copyBtn.textContent = "Copy";
  copyBtn.addEventListener("click", async () => {
    const text = `${pick.name}\n\n${excerptText}`;
    try {
      await navigator.clipboard.writeText(text);
      copyBtn.textContent = "Copied!";
      copyBtn.classList.add("copied");
    } catch (err) {
      copyBtn.textContent = "Copy failed";
    }
    setTimeout(() => {
      copyBtn.textContent = "Copy";
      copyBtn.classList.remove("copied");
    }, 2000);
  });
  actions.appendChild(copyBtn);

  media.appendChild(actions);
  box.appendChild(media);

  const text = document.createElement("div");
  const label = document.createElement("div");
  label.className = "home-spotlight__label";
  label.textContent = "Today's Featured Person";
  text.appendChild(label);

  const name = document.createElement("h2");
  name.className = "home-spotlight__name";
  const nameLink = document.createElement("a");
  nameLink.className = "home-spotlight__name-link";
  nameLink.href = personHref;
  nameLink.textContent = pick.name;
  name.appendChild(nameLink);
  text.appendChild(name);

  const meta = document.createElement("div");
  meta.className = "home-spotlight__meta";
  meta.textContent = [pick.testament === "OT" ? "Old Testament" : "New Testament", pick.era]
    .filter(Boolean)
    .join(" · ");
  text.appendChild(meta);

  const excerpt = document.createElement("p");
  excerpt.className = "home-spotlight__excerpt";
  excerpt.textContent = excerptText;
  text.appendChild(excerpt);

  const a = document.createElement("a");
  a.href = personHref;
  a.textContent = "Read full story →";
  text.appendChild(a);

  box.appendChild(text);
}

// A slow, continuously-scrolling strip of stained-glass portraits above the
// home quiz box. Capped at CAROUSEL_SIZE and daily-reshuffled (rather than
// showing all spotlight-eligible portraits, currently 268 and growing per
// STAINED_GLASS_QUEUE.md) so the loop stays a reasonable length and the page
// isn't fetching hundreds of images. The item list is duplicated once and
// the track is animated from translateX(0) to translateX(-50%) so the loop
// is seamless.
const HOME_CAROUSEL_SIZE = 40;
const HOME_CAROUSEL_SECONDS_PER_ITEM = 3.5;

function homeCarouselItem(entry) {
  const a = document.createElement("a");
  a.className = "home-carousel__item";
  a.href = `people/${encodeURIComponent(entry.person_id)}.html`;
  a.title = entry.name;

  const img = document.createElement("img");
  img.src = `images/portraits2-web/${entry.person_id}.jpg`;
  img.alt = entry.name;
  img.loading = "lazy";
  a.appendChild(img);

  return a;
}

function renderHomeCarousel(spotlightEligible) {
  const section = document.getElementById("home-carousel");
  const track = document.getElementById("home-carousel-track");
  const picks = dailySeededShuffle("carousel", spotlightEligible).slice(0, HOME_CAROUSEL_SIZE);

  if (!picks.length) {
    section.hidden = true;
    return;
  }
  section.hidden = false;

  track.innerHTML = "";
  track.style.animationDuration = `${picks.length * HOME_CAROUSEL_SECONDS_PER_ITEM * 2}s`;
  // Duplicated so the strip can loop from -50% back to 0% with no visible seam.
  for (const entry of [...picks, ...picks]) {
    track.appendChild(homeCarouselItem(entry));
  }
}

function exploreCard(entry) {
  const a = document.createElement("a");
  a.className = "explore-card";
  a.href = `people/${encodeURIComponent(entry.person_id)}.html`;
  a.appendChild(
    portraitImg(entry.person_id, entry.name, "explore-card__thumb", entry.image, undefined, entry.image2)
  );
  const name = document.createElement("span");
  name.className = "explore-card__name";
  name.textContent = entry.name;
  a.appendChild(name);
  return a;
}

function fitExploreRow(candidates) {
  const track = document.getElementById("explore-row-track");
  track.innerHTML = "";
  const cards = candidates.map(exploreCard);
  cards.forEach((c) => track.appendChild(c));

  if (!cards.length) return;
  const firstTop = cards[0].offsetTop;
  for (const card of cards) {
    if (card.offsetTop > firstTop) card.remove();
  }
}

function debounce(fn, wait) {
  let t;
  return (...args) => {
    clearTimeout(t);
    t = setTimeout(() => fn(...args), wait);
  };
}

function renderExploreRow(fullTier, totalCount) {
  const shuffled = dailySeededShuffle("explore", fullTier);
  fitExploreRow(shuffled);

  const viewAll = document.getElementById("explore-row-viewall");
  viewAll.textContent = `View all ${totalCount} people →`;

  window.addEventListener(
    "resize",
    debounce(() => fitExploreRow(shuffled), 150)
  );
}

function renderCollectionSummary(index, fullTier, quiz) {
  const el = document.getElementById("collection-summary");
  if (!el) return;
  el.textContent = `${index.length} people · ${fullTier.length} full ${
    fullTier.length === 1 ? "story" : "stories"
  } · ${quiz.length} quiz questions`;
}

async function renderHomePage() {
  const [index, quiz] = await Promise.all([loadIndex(), loadQuiz()]);
  const fullTier = index.filter((p) => p.tier === "full");
  const spotlightEligible = fullTier.filter((p) => p.image2 && p.spotlight_eligible !== false);

  await renderHomeSpotlight(spotlightEligible);
  initPortraitLightbox();
  renderHomeCarousel(spotlightEligible);
  initHomeQuiz(quiz, index);
  renderExploreRow(fullTier.filter((p) => p.image2), index.length);
  renderCollectionSummary(index, fullTier, quiz);
}

// ---------------------------------------------------------------------
// Quiz builder page
// ---------------------------------------------------------------------

let quizBuilderState = null;

function topicKey(q) {
  return q.subtopic_id ? `${q.topic_id}::${q.subtopic_id}` : `${q.topic_id}`;
}

function quizLearnMoreHref(q) {
  return `people/${encodeURIComponent(q.topic_id)}.html`;
}

function buildDefaultQuizSheet(maxDifficulty) {
  const pool = DATA.quiz.filter((q) => q.difficulty <= maxDifficulty);
  const shuffled = dailySeededShuffle(`quiz-sheet-${maxDifficulty}`, pool);

  const sheet = [];
  const usedTopics = new Set();
  const usedQids = new Set();
  for (const q of shuffled) {
    if (sheet.length >= 10) break;
    const key = topicKey(q);
    if (usedTopics.has(key)) continue;
    usedTopics.add(key);
    usedQids.add(q._qid);
    sheet.push(q);
  }
  if (sheet.length < 10) {
    for (const q of shuffled) {
      if (sheet.length >= 10) break;
      if (usedQids.has(q._qid)) continue;
      usedQids.add(q._qid);
      sheet.push(q);
    }
  }
  if (sheet.length < 10) {
    // Not enough questions at or below the preferred difficulty — top up
    // from the full question bank so a quiz always has 10 questions.
    const overflow = dailySeededShuffle(`quiz-sheet-${maxDifficulty}-overflow`, DATA.quiz);
    for (const q of overflow) {
      if (sheet.length >= 10) break;
      if (usedQids.has(q._qid)) continue;
      usedQids.add(q._qid);
      sheet.push(q);
    }
  }
  return sheet;
}

function setQuizStatus(text) {
  const status = document.getElementById("quiz-status");
  if (status) status.textContent = text;
}

function updateQuizStatusLine() {
  const n = quizBuilderState.sheet.length;
  setQuizStatus(
    n < 10 ? `${n} question${n === 1 ? "" : "s"} on this quiz — add more or lower the difficulty.` : ""
  );
}

function updateQuizAddButtonState() {
  const btn = document.getElementById("quiz-add-btn");
  const pool = DATA.quiz.filter((q) => q.difficulty <= quizBuilderState.maxDifficulty);
  const usedQids = new Set(quizBuilderState.sheet.map((q) => q._qid));
  const available = pool.filter((q) => !usedQids.has(q._qid));
  btn.classList.toggle("is-disabled", quizBuilderState.sheet.length >= 10 || !available.length);
}

function addQuizQuestion() {
  if (quizBuilderState.sheet.length >= 10) {
    setQuizStatus("Your quiz already has 10 questions — remove one first, or print as-is.");
    return;
  }
  const pool = DATA.quiz.filter((q) => q.difficulty <= quizBuilderState.maxDifficulty);
  const usedQids = new Set(quizBuilderState.sheet.map((q) => q._qid));
  const available = pool.filter((q) => !usedQids.has(q._qid));
  if (!available.length) {
    setQuizStatus("No more questions available at this difficulty — try raising the maximum difficulty.");
    return;
  }
  const usedTopics = new Set(quizBuilderState.sheet.map(topicKey));
  const preferred = available.filter((q) => !usedTopics.has(topicKey(q)));
  const source = preferred.length ? preferred : available;
  const pick = source[Math.floor(Math.random() * source.length)];
  quizBuilderState.sheet.push(pick);
  renderQuizSheet({ animate: true });
}

function moveQuizQuestion(qid, dir) {
  const sheet = quizBuilderState.sheet;
  const i = sheet.findIndex((q) => q._qid === qid);
  const j = i + dir;
  if (i < 0 || j < 0 || j >= sheet.length) return;
  [sheet[i], sheet[j]] = [sheet[j], sheet[i]];
  renderQuizSheet({ animate: true });
}

function removeQuizQuestion(qid) {
  quizBuilderState.sheet = quizBuilderState.sheet.filter((q) => q._qid !== qid);
  renderQuizSheet({ animate: true });
}

// Reordering uses Pointer Events (not native HTML5 drag-and-drop) so it
// works with mouse, touch, and pen alike. The move/up listeners are on
// `document`, not the row, because browsers can silently release
// setPointerCapture mid-drag — tracking on document avoids depending on it.
let quizDrag = null;

function startQuizDrag(evt, qid) {
  evt.preventDefault();
  const list = document.getElementById("quiz-sheet-list");
  const row = list.querySelector(`[data-qid="${qid}"]`);
  if (!row) return;
  quizDrag = { qid, startY: evt.clientY };
  row.classList.add("dragging");
  document.addEventListener("pointermove", onQuizDragMove);
  document.addEventListener("pointerup", onQuizDragEnd);
  document.addEventListener("pointercancel", onQuizDragEnd);
}

function onQuizDragMove(evt) {
  if (!quizDrag) return;
  const list = document.getElementById("quiz-sheet-list");
  const row = list.querySelector(`[data-qid="${quizDrag.qid}"]`);
  if (!row) return;
  row.style.transform = `translateY(${evt.clientY - quizDrag.startY}px)`;
}

function onQuizDragEnd() {
  if (!quizDrag) return;
  const list = document.getElementById("quiz-sheet-list");
  const row = list.querySelector(`[data-qid="${quizDrag.qid}"]`);
  document.removeEventListener("pointermove", onQuizDragMove);
  document.removeEventListener("pointerup", onQuizDragEnd);
  document.removeEventListener("pointercancel", onQuizDragEnd);

  if (row) {
    const draggedRect = row.getBoundingClientRect();
    const draggedCenter = draggedRect.top + draggedRect.height / 2;
    const order = [...list.children]
      .map((r) => {
        if (r === row) return { qid: r.dataset.qid, center: draggedCenter };
        const rect = r.getBoundingClientRect();
        return { qid: r.dataset.qid, center: rect.top + rect.height / 2 };
      })
      .sort((a, b) => a.center - b.center)
      .map((item) => item.qid);

    row.classList.remove("dragging");
    row.style.transform = "";

    const byQid = new Map(quizBuilderState.sheet.map((q) => [String(q._qid), q]));
    quizBuilderState.sheet = order.map((qid) => byQid.get(qid)).filter(Boolean);
  }

  quizDrag = null;
  renderQuizSheet({ animate: true });
}

function quizSheetRow(q, index, nameEntries) {
  const li = document.createElement("li");
  li.className = "quiz-sheet-row";
  li.dataset.qid = q._qid;

  const handle = document.createElement("button");
  handle.type = "button";
  handle.className = "quiz-drag-handle no-print";
  handle.setAttribute("aria-label", "Drag to reorder");
  handle.textContent = "⠿";
  li.appendChild(handle);

  const textEl = document.createElement("div");
  textEl.className = "quiz-sheet-row__text";
  renderTextWithNameLinks(textEl, q.question, nameEntries);
  li.appendChild(textEl);

  const controls = document.createElement("div");
  controls.className = "quiz-sheet-row__controls no-print";

  const upBtn = document.createElement("button");
  upBtn.type = "button";
  upBtn.className = "quiz-move-up";
  upBtn.setAttribute("aria-label", "Move question up");
  upBtn.textContent = "↑";
  upBtn.disabled = index === 0;
  controls.appendChild(upBtn);

  const downBtn = document.createElement("button");
  downBtn.type = "button";
  downBtn.className = "quiz-move-down";
  downBtn.setAttribute("aria-label", "Move question down");
  downBtn.textContent = "↓";
  downBtn.disabled = index === quizBuilderState.sheet.length - 1;
  controls.appendChild(downBtn);

  const removeBtn = document.createElement("button");
  removeBtn.type = "button";
  removeBtn.className = "quiz-remove";
  removeBtn.setAttribute("aria-label", "Remove question");
  removeBtn.textContent = "✕";
  controls.appendChild(removeBtn);

  li.appendChild(controls);

  upBtn.addEventListener("click", () => moveQuizQuestion(q._qid, -1));
  downBtn.addEventListener("click", () => moveQuizQuestion(q._qid, 1));
  removeBtn.addEventListener("click", () => removeQuizQuestion(q._qid));
  handle.addEventListener("pointerdown", (evt) => startQuizDrag(evt, q._qid));

  return li;
}

function renderQuizAnswerKey() {
  const list = document.getElementById("quiz-answer-key-list");
  list.innerHTML = "";
  quizBuilderState.sheet.forEach((q) => {
    const li = document.createElement("li");

    const a = document.createElement("a");
    a.href = quizLearnMoreHref(q);
    a.textContent = q.answer;
    li.appendChild(a);

    if (q.reference) {
      const ref = document.createElement("span");
      ref.className = "quiz-answer-key__ref";
      ref.textContent = ` (${q.reference})`;
      li.appendChild(ref);
    }
    list.appendChild(li);
  });
}

function captureRowRects(list) {
  const map = new Map();
  for (const row of list.children) map.set(row.dataset.qid, row.getBoundingClientRect());
  return map;
}

function playFlipAnimation(list, prevRects) {
  for (const row of list.children) {
    const prev = prevRects.get(row.dataset.qid);
    if (!prev) continue;
    const next = row.getBoundingClientRect();
    const dy = prev.top - next.top;
    if (!dy) continue;
    row.style.transition = "none";
    row.style.transform = `translateY(${dy}px)`;
    requestAnimationFrame(() => {
      row.style.transition = "transform 160ms ease";
      row.style.transform = "";
    });
  }
}

function renderQuizSheet(opts = {}) {
  const list = document.getElementById("quiz-sheet-list");
  const prevRects = opts.animate ? captureRowRects(list) : null;

  const nameEntries = quizNameEntries(quizBuilderState.index);
  list.innerHTML = "";
  quizBuilderState.sheet.forEach((q, i) => {
    list.appendChild(quizSheetRow(q, i, nameEntries));
  });

  if (prevRects) playFlipAnimation(list, prevRects);

  renderQuizAnswerKey();
  updateQuizStatusLine();
  updateQuizAddButtonState();
}

function setQuizMaxDifficulty(value, { persist, updateUrl } = {}) {
  quizBuilderState.maxDifficulty = value;
  if (persist) setPreferredQuizDifficulty(value);
  if (updateUrl) {
    const params = new URLSearchParams(window.location.search);
    params.set("max", String(value));
    history.replaceState(null, "", `${window.location.pathname}?${params}`);
  }
}

async function renderQuizBuilderPage() {
  const [index, quiz] = await Promise.all([loadIndex(), loadQuiz()]);
  quiz.forEach((q, i) => {
    q._qid = String(i);
  });

  quizBuilderState = { index, maxDifficulty: null, sheet: [] };

  const params = new URLSearchParams(window.location.search);
  const urlMax = Number(params.get("max"));
  const initialMax = urlMax === 1 || urlMax === 2 || urlMax === 3 ? urlMax : getPreferredQuizDifficulty();
  setQuizMaxDifficulty(initialMax, { persist: true, updateUrl: true });

  const select = document.getElementById("quiz-difficulty-select");
  select.value = String(initialMax);
  quizBuilderState.sheet = buildDefaultQuizSheet(initialMax);
  renderQuizSheet();

  select.addEventListener("change", () => {
    const value = Number(select.value);
    setQuizMaxDifficulty(value, { persist: true, updateUrl: true });
    quizBuilderState.sheet = buildDefaultQuizSheet(value);
    renderQuizSheet({ animate: true });
  });

  document.getElementById("quiz-reset-btn").addEventListener("click", () => {
    quizBuilderState.sheet = buildDefaultQuizSheet(quizBuilderState.maxDifficulty);
    renderQuizSheet({ animate: true });
  });

  document.getElementById("quiz-print-btn").addEventListener("click", () => window.print());
  document.getElementById("quiz-add-btn").addEventListener("click", () => addQuizQuestion());
}

// ---------------------------------------------------------------------
// Connections graph
// ---------------------------------------------------------------------

const SVG_NS = "http://www.w3.org/2000/svg";

function svgEl(tag, attrs) {
  const el = document.createElementNS(SVG_NS, tag);
  for (const key in attrs) el.setAttribute(key, attrs[key]);
  return el;
}

const CONN_DEFAULT_DEPTH = 2;
const CONN_MIN_DEPTH = 1;
const CONN_MAX_DEPTH = 5;
const CONN_RADII = [24, 18, 15, 13, 11];
const CONN_ROW_HEIGHT = 118;
const CONN_SLOT_GAP = 26;
const CONN_CHAR_WIDTH = 6.6;
const CONN_LABEL_MAX_CHARS = 12;
const CONN_MARGIN = 60;
const CONN_ARROW_CLEARANCE = 9;
const CONN_MIN_ZOOM = 25;
const CONN_MAX_ZOOM = 300;

// Categorical era palette (see css/style.css --era-* custom properties),
// validated with the dataviz skill's six-checks script against this site's
// surfaces. Exile and Post-Exile/Intertestamental share a swatch since both
// are minor transitional eras in the finalized taxonomy; the exact era is
// still shown as text in the tooltip and sidebar.
const ERA_BUCKETS = [
  { key: "patriarchal", eras: ["Patriarchal"], label: "Patriarchal" },
  { key: "exodus", eras: ["Exodus/Wilderness"], label: "Exodus / Wilderness" },
  { key: "judges", eras: ["Judges"], label: "Judges" },
  { key: "united-monarchy", eras: ["United Monarchy"], label: "United Monarchy" },
  { key: "divided-monarchy", eras: ["Divided Monarchy"], label: "Divided Monarchy" },
  { key: "exile", eras: ["Exile", "Post-Exile/Intertestamental"], label: "Exile & Post-Exile" },
  { key: "gospels", eras: ["Gospels"], label: "Gospels" },
  { key: "apostolic", eras: ["Apostolic"], label: "Apostolic" },
];

const PLACE_TYPE_LABELS = {
  nation: "Nation", region: "Region", city: "City", town: "Town",
  village: "Village", mountain: "Mountain", wilderness: "Wilderness",
  valley: "Valley", "body-of-water": "Body of Water", site: "Site",
};

function eraBucketKey(entry) {
  if (entry && entry.kind === "place") return "place";
  if (entry && entry.era) {
    const bucket = ERA_BUCKETS.find((b) => b.eras.includes(entry.era));
    if (bucket) return bucket.key;
  }
  return "other";
}

function renderConnectionsLegend(container, showPlace = true) {
  container.innerHTML = "";
  const items = [...ERA_BUCKETS.map((b) => [b.key, b.label]), ["other", "Era not placed"]];
  if (showPlace) items.push(["place", "Place"]);
  for (const [key, label] of items) {
    const span = document.createElement("span");
    span.className = "connections-legend__item";
    const swatch = document.createElement("span");
    swatch.className = `connections-legend__swatch connections-legend__swatch--${key}`;
    span.appendChild(swatch);
    span.appendChild(document.createTextNode(label));
    container.appendChild(span);
  }
}

// ---- data helpers ----

function comboboxLabel(entry) {
  const base = entry.alt_names && entry.alt_names.length
    ? `${entry.name} (${entry.alt_names.join(", ")})`
    : entry.name;
  return entry.kind === "place" ? `${base} — place` : base;
}

function resolveBestMatch(query, index) {
  const q = query.trim().toLowerCase();
  if (!q) return null;
  let match = index.find((e) => comboboxLabel(e).toLowerCase() === q);
  if (match) return match;
  match = index.find((e) => e.name.toLowerCase() === q);
  if (match) return match;
  return index.find((e) => matchesSearch(e, q)) || null;
}

function buildAdjacency(index, edges) {
  const nameById = new Map(index.map((e) => [e.person_id, e.name]));
  const adjacency = new Map();
  for (const entry of index) adjacency.set(entry.person_id, []);
  for (const edge of edges) {
    if (!adjacency.has(edge.from)) adjacency.set(edge.from, []);
    if (!adjacency.has(edge.to)) adjacency.set(edge.to, []);
    adjacency.get(edge.from).push({ edge, otherId: edge.to });
    adjacency.get(edge.to).push({ edge, otherId: edge.from });
  }
  for (const items of adjacency.values()) {
    items.sort((a, b) =>
      (nameById.get(a.otherId) || a.otherId).localeCompare(nameById.get(b.otherId) || b.otherId)
    );
  }
  return adjacency;
}

function neighborIds(adjacency, id) {
  const seen = new Set();
  const order = [];
  for (const item of adjacency.get(id) || []) {
    if (!seen.has(item.otherId)) {
      seen.add(item.otherId);
      order.push(item.otherId);
    }
  }
  return order;
}

function computeNetworkSizes(index, adjacency, maxDepth) {
  const sizes = new Map();
  for (const entry of index) {
    const centerId = entry.person_id;
    const visited = new Set([centerId]);
    let frontier = [centerId];
    let depth = 0;
    while (frontier.length && depth < maxDepth) {
      const next = [];
      for (const id of frontier) {
        for (const otherId of neighborIds(adjacency, id)) {
          if (!visited.has(otherId)) {
            visited.add(otherId);
            next.push(otherId);
          }
        }
      }
      frontier = next;
      depth++;
    }
    visited.delete(centerId);
    sizes.set(centerId, visited.size);
  }
  return sizes;
}

function bfsTree(centerId, adjacency, maxDepth) {
  const depthOf = new Map([[centerId, 0]]);
  const childrenOf = new Map();
  let frontier = [centerId];
  let depth = 0;
  while (frontier.length && depth < maxDepth) {
    const next = [];
    for (const id of frontier) {
      for (const otherId of neighborIds(adjacency, id)) {
        if (!depthOf.has(otherId)) {
          depthOf.set(otherId, depth + 1);
          if (!childrenOf.has(id)) childrenOf.set(id, []);
          childrenOf.get(id).push(otherId);
          next.push(otherId);
        }
      }
    }
    frontier = next;
    depth++;
  }
  return { depthOf, childrenOf };
}

function collectDisplayEdges(edges, reachable) {
  return edges.filter((e) => reachable.has(e.from) && reachable.has(e.to));
}

// ---- layout (top-down tidy tree) ----

function labelWidthPx(name) {
  return Math.max(name.length * CONN_CHAR_WIDTH, 30);
}

function computeLayout(centerId, depthOf, childrenOf, index) {
  const entryById = new Map(index.map((e) => [e.person_id, e]));
  const positions = new Map();
  let nextX = 0;

  function slotWidth(id) {
    const radius = CONN_RADII[Math.min(depthOf.get(id), CONN_RADII.length - 1)];
    const name = (entryById.get(id) || {}).name || id;
    return Math.max(labelWidthPx(name), radius * 2 + 8);
  }

  function place(id) {
    const children = childrenOf.get(id) || [];
    if (!children.length) {
      const w = slotWidth(id);
      const x = nextX + w / 2;
      nextX += w + CONN_SLOT_GAP;
      positions.set(id, x);
      return x;
    }
    const childXs = children.map(place);
    const x = (childXs[0] + childXs[childXs.length - 1]) / 2;
    positions.set(id, x);
    return x;
  }
  place(centerId);

  const nodes = [];
  let minX = Infinity;
  let maxX = -Infinity;
  let maxDepth = 0;
  for (const [id, x] of positions) {
    const depth = depthOf.get(id);
    const w = slotWidth(id);
    nodes.push({ id, x, y: depth * CONN_ROW_HEIGHT, depth });
    minX = Math.min(minX, x - w / 2);
    maxX = Math.max(maxX, x + w / 2);
    maxDepth = Math.max(maxDepth, depth);
  }
  return { nodes, minX, maxX, maxDepth };
}

// ---- edge geometry ----

function edgePairKey(edge) {
  return [edge.from, edge.to].sort().join("|");
}

function trimEndpoints(x1, y1, x2, y2, r1, r2) {
  const dx = x2 - x1;
  const dy = y2 - y1;
  const dist = Math.sqrt(dx * dx + dy * dy) || 1;
  const ux = dx / dist;
  const uy = dy / dist;
  return { x1: x1 + ux * r1, y1: y1 + uy * r1, x2: x2 - ux * r2, y2: y2 - uy * r2 };
}

function buildEdgeGeometry(displayEdges, posById, depthOf) {
  const groups = new Map();
  for (const edge of displayEdges) {
    const key = edgePairKey(edge);
    if (!groups.has(key)) groups.set(key, []);
    groups.get(key).push(edge);
  }

  const lines = [];
  for (const group of groups.values()) {
    group.forEach((edge, i) => {
      const from = posById.get(edge.from);
      const to = posById.get(edge.to);
      if (!from || !to) return;
      let x1 = from.x;
      let y1 = from.y;
      let x2 = to.x;
      let y2 = to.y;
      const dupMid = (group.length - 1) / 2;
      if (group.length > 1) {
        const dx = x2 - x1;
        const dy = y2 - y1;
        const dist = Math.sqrt(dx * dx + dy * dy) || 1;
        const px = -dy / dist;
        const py = dx / dist;
        const offset = (i - dupMid) * 18;
        x1 += px * offset;
        y1 += py * offset;
        x2 += px * offset;
        y2 += py * offset;
      }
      const r1 = CONN_RADII[Math.min(depthOf.get(edge.from), CONN_RADII.length - 1)];
      const r2 = CONN_RADII[Math.min(depthOf.get(edge.to), CONN_RADII.length - 1)];
      const trimmed = trimEndpoints(x1, y1, x2, y2, r1, r2);

      // Same-depth (sibling) cross-links sit on one horizontal row; a straight
      // line between two non-adjacent siblings would cut through whichever
      // node sits between them. Bow those above the row instead.
      const sameDepth = depthOf.get(edge.from) === depthOf.get(edge.to);
      let control = null;
      if (sameDepth) {
        const midX = (trimmed.x1 + trimmed.x2) / 2;
        const bow = Math.min(50, Math.abs(trimmed.x2 - trimmed.x1) * 0.28 + 16) + i * 14;
        control = { x: midX, y: trimmed.y1 - bow };
      }
      // When two documented relationships link the same pair (e.g. Paul both
      // clashed with and collaborated with Peter), stagger their labels along
      // the line so they don't print on top of each other.
      const labelBias = group.length > 1 ? (i - dupMid) * 0.14 : 0;
      lines.push({ edge, ...trimmed, control, labelBias });
    });
  }
  return lines;
}

function edgeLabelPoint(line, depthOf) {
  if (line.control) {
    const t = Math.max(0.12, Math.min(0.88, 0.5 + (line.labelBias || 0)));
    const mt = 1 - t;
    return {
      x: mt * mt * line.x1 + 2 * mt * t * line.control.x + t * t * line.x2,
      y: mt * mt * line.y1 + 2 * mt * t * line.control.y + t * t * line.y2,
    };
  }

  const depthFrom = depthOf.get(line.edge.from);
  const depthTo = depthOf.get(line.edge.to);
  let t = 0.5;
  if (depthFrom !== depthTo) t = depthTo > depthFrom ? 0.68 : 0.32;
  t += line.labelBias || 0;

  const dx = line.x2 - line.x1;
  const dy = line.y2 - line.y1;
  const dist = Math.sqrt(dx * dx + dy * dy) || 1;
  if (!line.edge.mutual) {
    const minT = 1 - CONN_ARROW_CLEARANCE / dist;
    t = Math.min(t, minT);
  }
  t = Math.max(0.12, Math.min(0.88, t));
  return { x: line.x1 + dx * t, y: line.y1 + dy * t };
}

function wrapLabel(text, maxChars) {
  const words = text.split(" ");
  const lines = [];
  let cur = "";
  for (const w of words) {
    if (!cur) cur = w;
    else if ((cur + " " + w).length <= maxChars) cur += ` ${w}`;
    else {
      lines.push(cur);
      cur = w;
    }
  }
  if (cur) lines.push(cur);
  if (lines.length > 3) {
    const kept = lines.slice(0, 3);
    kept[2] = `${kept[2].slice(0, Math.max(0, maxChars - 1))}…`;
    return kept;
  }
  return lines;
}

// ---- tooltip ----

function connectionsTooltipEl() {
  return document.getElementById("connections-tooltip");
}

function positionConnectionsTooltip(evt) {
  const el = connectionsTooltipEl();
  if (!el) return;
  el.style.left = `${evt.clientX + 14}px`;
  el.style.top = `${evt.clientY + 14}px`;
}

function showNodeTooltip(evt, entry) {
  const el = connectionsTooltipEl();
  if (!el || !entry) return;
  let bits;
  if (entry.kind === "place") {
    bits = [PLACE_TYPE_LABELS[entry.place_type] || entry.place_type];
    if (entry.eras && entry.eras.length) bits.push(entry.eras.join(", "));
  } else {
    bits = [entry.testament === "OT" ? "Old Testament" : "New Testament"];
    if (entry.era) bits.push(entry.era);
  }
  el.textContent = `${entry.name} — ${bits.join(" · ")}`;
  el.hidden = false;
  positionConnectionsTooltip(evt);
}

function showEdgeTooltip(evt, edge, entryById) {
  const el = connectionsTooltipEl();
  if (!el) return;
  const fromName = (entryById.get(edge.from) || {}).name || edge.from;
  const toName = (entryById.get(edge.to) || {}).name || edge.to;
  const arrow = edge.mutual ? "↔" : "→";
  el.textContent = `${fromName} ${arrow} ${toName}: ${edge.label}`;
  el.hidden = false;
  positionConnectionsTooltip(evt);
}

function hideConnectionsTooltip() {
  const el = connectionsTooltipEl();
  if (el) el.hidden = true;
}

// ---- SVG render ----

function renderConnectionsSvg(canvas, state) {
  const { index, adjacency, edgesRaw, centerId } = state;
  const entryById = new Map(index.map((e) => [e.person_id, e]));
  const centerEntry = entryById.get(centerId);

  if (!neighborIds(adjacency, centerId).length) {
    canvas.innerHTML = "";
    const p = document.createElement("p");
    p.className = "connections-empty";
    p.textContent = `No documented connections yet for ${centerEntry ? centerEntry.name : centerId}.`;
    canvas.appendChild(p);
    return null;
  }

  const { depthOf, childrenOf } = bfsTree(centerId, adjacency, state.depth);
  const reachable = new Set(depthOf.keys());
  const displayEdges = collectDisplayEdges(edgesRaw, reachable);
  const { nodes, minX, maxX, maxDepth } = computeLayout(centerId, depthOf, childrenOf, index);

  const posById = new Map(nodes.map((n) => [n.id, n]));
  const lines = buildEdgeGeometry(displayEdges, posById, depthOf);

  const vbX = minX - CONN_MARGIN;
  const vbY = -CONN_MARGIN;
  const vbW = maxX - minX + CONN_MARGIN * 2;
  const vbH = maxDepth * CONN_ROW_HEIGHT + CONN_MARGIN * 2 + 30;

  const svg = svgEl("svg", {
    viewBox: `${vbX} ${vbY} ${vbW} ${vbH}`,
    width: String(vbW),
    height: String(vbH),
    class: `connections-svg${state.labelsOn ? "" : " labels-hidden"}`,
    role: "img",
    "aria-label": `Connections graph centered on ${centerEntry ? centerEntry.name : centerId}`,
  });

  const defs = svgEl("defs", {});
  const marker = svgEl("marker", {
    id: "conn-arrow",
    viewBox: "0 0 10 10",
    refX: "9",
    refY: "5",
    markerWidth: "8",
    markerHeight: "8",
    markerUnits: "userSpaceOnUse",
    orient: "auto-start-reverse",
  });
  marker.appendChild(svgEl("path", { d: "M 0 0 L 10 5 L 0 10 z", class: "connections-arrowhead" }));
  defs.appendChild(marker);
  svg.appendChild(defs);

  const guides = svgEl("g", { class: "connections-guides" });
  for (let d = 0; d <= maxDepth; d++) {
    guides.appendChild(
      svgEl("line", {
        x1: vbX,
        x2: vbX + vbW,
        y1: d * CONN_ROW_HEIGHT,
        y2: d * CONN_ROW_HEIGHT,
        class: "connections-guide",
      })
    );
  }
  svg.appendChild(guides);

  const edgesGroup = svgEl("g", { class: "connections-lines" });
  for (const line of lines) {
    const cls = `connections-edge${line.edge.mutual ? " connections-edge--mutual" : ""}`;
    let lineEl;
    if (line.control) {
      const d = `M ${line.x1} ${line.y1} Q ${line.control.x} ${line.control.y} ${line.x2} ${line.y2}`;
      const attrs = { d, class: cls };
      if (!line.edge.mutual) attrs["marker-end"] = "url(#conn-arrow)";
      lineEl = svgEl("path", attrs);
    } else {
      const attrs = {
        x1: line.x1,
        y1: line.y1,
        x2: line.x2,
        y2: line.y2,
        class: cls,
      };
      if (!line.edge.mutual) attrs["marker-end"] = "url(#conn-arrow)";
      lineEl = svgEl("line", attrs);
    }
    lineEl.addEventListener("mousemove", (evt) => showEdgeTooltip(evt, line.edge, entryById));
    lineEl.addEventListener("mouseenter", (evt) => showEdgeTooltip(evt, line.edge, entryById));
    lineEl.addEventListener("mouseleave", hideConnectionsTooltip);
    edgesGroup.appendChild(lineEl);

    const pt = edgeLabelPoint(line, depthOf);
    const text = svgEl("text", {
      x: pt.x,
      y: pt.y,
      "text-anchor": "middle",
      class: "connections-edge-label",
    });
    wrapLabel(line.edge.label, CONN_LABEL_MAX_CHARS).forEach((ln, i) => {
      const tspan = svgEl("tspan", { x: pt.x, dy: i === 0 ? "0" : "1.1em" });
      tspan.textContent = ln;
      text.appendChild(tspan);
    });
    edgesGroup.appendChild(text);
  }
  svg.appendChild(edgesGroup);

  const nodesGroup = svgEl("g", { class: "connections-nodes" });
  for (const node of nodes) {
    const entry = entryById.get(node.id);
    const radius = CONN_RADII[Math.min(node.depth, CONN_RADII.length - 1)];
    const bucket = eraBucketKey(entry);
    const g = svgEl("g", {
      class: `connections-node connections-node--depth${node.depth}${
        node.depth === 0 ? " connections-node--center" : ""
      }`,
      tabindex: node.depth === 0 ? "-1" : "0",
      role: "button",
      "aria-label": `Center graph on ${entry ? entry.name : node.id}`,
    });
    if (entry && entry.kind === "place") {
      // Places render as a rotated square ("diamond") rather than a
      // circle, so they read as a different kind of node at a glance
      // rather than just another era color.
      const side = radius * 1.5;
      g.appendChild(
        svgEl("rect", {
          x: node.x - side / 2,
          y: node.y - side / 2,
          width: side,
          height: side,
          transform: `rotate(45 ${node.x} ${node.y})`,
          class: `connections-node__circle connections-node__circle--${bucket}`,
        })
      );
    } else {
      g.appendChild(
        svgEl("circle", {
          cx: node.x,
          cy: node.y,
          r: radius,
          class: `connections-node__circle connections-node__circle--${bucket}`,
        })
      );
    }

    const labelLink = svgEl("a", {
      href: graphNodeHref(entry, node.id),
      class: "connections-node__label-link",
    });
    labelLink.addEventListener("click", (evt) => evt.stopPropagation());
    const genderLabelClass =
      entry && (entry.gender === "male" || entry.gender === "female")
        ? ` connections-node__label--${entry.gender}`
        : "";
    const label = svgEl("text", {
      x: node.x,
      y: node.y + radius + 14,
      "text-anchor": "middle",
      class: `connections-node__label${genderLabelClass}`,
    });
    label.textContent = entry ? entry.name : node.id;
    labelLink.appendChild(label);
    g.appendChild(labelLink);

    g.addEventListener("mousemove", (evt) => showNodeTooltip(evt, entry));
    g.addEventListener("mouseenter", (evt) => showNodeTooltip(evt, entry));
    g.addEventListener("mouseleave", hideConnectionsTooltip);

    if (node.depth !== 0) {
      const activate = () => setConnectionsCenter(node.id);
      g.addEventListener("click", activate);
      g.addEventListener("keydown", (evt) => {
        if (evt.key === "Enter" || evt.key === " ") {
          evt.preventDefault();
          activate();
        }
      });
    }
    nodesGroup.appendChild(g);
  }
  svg.appendChild(nodesGroup);

  canvas.innerHTML = "";
  canvas.appendChild(svg);
  return { width: vbW, height: vbH };
}

// ---- zoom ----

function applyConnectionsZoom(state) {
  if (!state.svgEl || !state.svgNatural) return;
  const scale = state.zoomPct / 100;
  state.svgEl.setAttribute("width", String(state.svgNatural.width * scale));
  state.svgEl.setAttribute("height", String(state.svgNatural.height * scale));
  const resetBtn = document.getElementById("conn-zoom-reset");
  if (resetBtn) resetBtn.textContent = `${Math.round(state.zoomPct)}%`;
}

function setConnectionsZoom(state, pct) {
  state.zoomPct = Math.max(CONN_MIN_ZOOM, Math.min(CONN_MAX_ZOOM, pct));
  applyConnectionsZoom(state);
}

function touchDistance(touches) {
  const dx = touches[0].clientX - touches[1].clientX;
  const dy = touches[0].clientY - touches[1].clientY;
  return Math.sqrt(dx * dx + dy * dy);
}

function initConnectionsZoom(state) {
  document
    .getElementById("conn-zoom-out")
    .addEventListener("click", () => setConnectionsZoom(state, state.zoomPct - 20));
  document
    .getElementById("conn-zoom-in")
    .addEventListener("click", () => setConnectionsZoom(state, state.zoomPct + 20));
  document
    .getElementById("conn-zoom-reset")
    .addEventListener("click", () => setConnectionsZoom(state, 100));

  const canvas = document.getElementById("connections-canvas");
  canvas.addEventListener(
    "wheel",
    (evt) => {
      if (!(evt.ctrlKey || evt.metaKey)) return;
      evt.preventDefault();
      setConnectionsZoom(state, state.zoomPct - evt.deltaY * 0.5);
    },
    { passive: false }
  );

  let pinchStartDist = null;
  let pinchStartZoom = 100;
  canvas.addEventListener(
    "touchstart",
    (evt) => {
      if (evt.touches.length === 2) {
        pinchStartDist = touchDistance(evt.touches);
        pinchStartZoom = state.zoomPct;
      }
    },
    { passive: true }
  );
  canvas.addEventListener(
    "touchmove",
    (evt) => {
      if (evt.touches.length === 2 && pinchStartDist) {
        evt.preventDefault();
        setConnectionsZoom(state, pinchStartZoom * (touchDistance(evt.touches) / pinchStartDist));
      }
    },
    { passive: false }
  );
  canvas.addEventListener("touchend", () => {
    pinchStartDist = null;
  });
}

// ---- sidebar ----

function renderConnectionsSidebar(state) {
  const container = document.getElementById("connections-sidebar");
  container.innerHTML = "";
  const entry = state.index.find((e) => e.person_id === state.centerId);
  if (!entry) return;

  const isPlace = entry.kind === "place";

  if (isPlace) {
    const placeholder = document.createElement("div");
    placeholder.className = "connections-sidebar__avatar connections-sidebar__avatar--place";
    placeholder.textContent = "📍";
    container.appendChild(placeholder);
  } else {
    container.appendChild(
      portraitImg(
        entry.person_id,
        entry.name,
        "connections-sidebar__avatar",
        entry.image,
        entry.gender,
        entry.image2
      )
    );
  }

  const name = document.createElement("h3");
  name.textContent = entry.name;
  if (!isPlace) {
    const tag = genderTag(entry.gender);
    if (tag) {
      name.appendChild(document.createTextNode(" "));
      name.appendChild(tag);
    }
  }
  container.appendChild(name);

  const meta = document.createElement("p");
  meta.className = "connections-sidebar__meta";
  if (isPlace) {
    const bits = [PLACE_TYPE_LABELS[entry.place_type] || entry.place_type];
    if (entry.eras && entry.eras.length) bits.push(entry.eras.join(", "));
    meta.textContent = bits.join(" · ");
  } else {
    const bits = [entry.testament === "OT" ? "Old Testament" : "New Testament"];
    if (entry.era) bits.push(entry.era);
    meta.textContent = bits.join(" · ");
  }
  container.appendChild(meta);

  // Total edges touching this node, not unique neighbors — two people can
  // be linked by more than one documented relationship (e.g. Paul and Peter
  // both clashed and collaborated), and each counts separately here.
  const degree = (state.adjacency.get(state.centerId) || []).length;
  const count = document.createElement("p");
  count.className = "connections-stats";
  count.textContent = isPlace
    ? `${degree} named ${degree === 1 ? "person" : "people"}`
    : `${degree} documented connection${degree === 1 ? "" : "s"}`;
  container.appendChild(count);

  const link = document.createElement("a");
  link.href = graphNodeHref(entry, state.centerId);
  link.className = "connections-sidebar__profile-link";
  link.textContent = isPlace ? "View place page →" : "View full profile →";
  container.appendChild(link);
}

// ---- picker (combobox) ----

function initConnectionsPicker(state) {
  const input = document.getElementById("conn-person-input");
  const list = document.getElementById("conn-person-listbox");
  const status = document.getElementById("conn-person-status");

  function currentCenterLabel() {
    const entry = state.index.find((e) => e.person_id === state.centerId);
    return entry ? comboboxLabel(entry) : "";
  }

  function renderList(query) {
    const q = query.trim().toLowerCase();
    const items = state.index
      .slice()
      .sort((a, b) => a.name.localeCompare(b.name))
      .filter((e) => !q || matchesSearch(e, q));
    list.innerHTML = "";
    for (const entry of items.slice(0, 200)) {
      const li = document.createElement("li");
      li.setAttribute("role", "option");
      li.tabIndex = -1;
      li.dataset.id = entry.person_id;

      const label = document.createElement("span");
      label.textContent = comboboxLabel(entry);
      const count = document.createElement("span");
      count.className = "connections-picker__count";
      count.textContent = `${state.networkSizes.get(entry.person_id) || 0} in network`;
      li.appendChild(label);
      li.appendChild(count);

      li.addEventListener("mousedown", (evt) => {
        evt.preventDefault();
        commit(entry);
      });
      list.appendChild(li);
    }
    list.hidden = items.length === 0;
    input.setAttribute("aria-expanded", items.length ? "true" : "false");
  }

  function openList() {
    renderList(input.value);
  }

  function closeList() {
    list.hidden = true;
    input.setAttribute("aria-expanded", "false");
  }

  function commit(entry) {
    input.value = comboboxLabel(entry);
    input.dataset.committed = "true";
    status.textContent = "";
    closeList();
    setConnectionsCenter(entry.person_id);
  }

  input.addEventListener("focus", () => {
    if (input.dataset.committed === "true") {
      input.dataset.committed = "false";
      input.value = "";
    }
    openList();
  });

  input.addEventListener("click", () => {
    if (input.dataset.committed === "true") {
      input.dataset.committed = "false";
      input.value = "";
      openList();
    }
  });

  input.addEventListener("input", () => {
    input.dataset.committed = "false";
    status.textContent = "";
    renderList(input.value);
  });

  input.addEventListener("keydown", (evt) => {
    if (evt.key === "Escape") {
      closeList();
    } else if (evt.key === "Enter") {
      evt.preventDefault();
      const match = resolveBestMatch(input.value, state.index);
      if (match) commit(match);
      else status.textContent = `No person named "${input.value}" found.`;
    }
  });

  input.addEventListener("blur", () => {
    setTimeout(() => {
      if (input.dataset.committed !== "true") {
        input.value = currentCenterLabel();
        input.dataset.committed = "true";
      }
      closeList();
    }, 120);
  });

  state.pickerSetValue = (id) => {
    const entry = state.index.find((e) => e.person_id === id);
    if (entry) {
      input.value = comboboxLabel(entry);
      input.dataset.committed = "true";
    }
  };
}

// ---- toolbar controls ----

function enterConnectionsFullPage(state) {
  state.fullPage = true;
  document.getElementById("connections-graph-frame").classList.add("is-fullpage");
  document.body.classList.add("connections-fullpage-active");
  document.getElementById("conn-fullpage-toggle").setAttribute("aria-pressed", "true");
}

function exitConnectionsFullPage(state) {
  state.fullPage = false;
  document.getElementById("connections-graph-frame").classList.remove("is-fullpage");
  document.body.classList.remove("connections-fullpage-active");
  document.getElementById("conn-fullpage-toggle").setAttribute("aria-pressed", "false");
}

function initConnectionsControls(state) {
  const depthSelect = document.getElementById("conn-depth-select");
  depthSelect.value = String(state.depth);
  depthSelect.addEventListener("change", () => {
    state.depth = Number(depthSelect.value);
    state.networkSizes = computeNetworkSizes(state.index, state.adjacency, state.depth);
    setConnectionsCenter(state.centerId);
  });

  document.getElementById("conn-random-btn").addEventListener("click", () => {
    const candidates = state.index.filter((e) => neighborIds(state.adjacency, e.person_id).length > 0);
    if (!candidates.length) return;
    setConnectionsCenter(candidates[Math.floor(Math.random() * candidates.length)].person_id);
  });

  document.getElementById("conn-labels-toggle").addEventListener("click", (evt) => {
    state.labelsOn = !state.labelsOn;
    evt.currentTarget.setAttribute("aria-pressed", String(state.labelsOn));
    const svg = document.querySelector("#connections-canvas svg");
    if (svg) svg.classList.toggle("labels-hidden", !state.labelsOn);
  });

  document.getElementById("conn-fullpage-toggle").addEventListener("click", () => {
    if (state.fullPage) exitConnectionsFullPage(state);
    else enterConnectionsFullPage(state);
  });

  document.addEventListener("keydown", (evt) => {
    if (evt.key === "Escape" && state.fullPage) exitConnectionsFullPage(state);
  });
}

// ---- render pipeline / state ----

let connectionsState = null;

function renderConnectionsGraph(state) {
  const canvas = document.getElementById("connections-canvas");
  const natural = renderConnectionsSvg(canvas, state);
  state.svgEl = canvas.querySelector("svg");
  state.svgNatural = natural;
  state.zoomPct = 100;
  applyConnectionsZoom(state);
  renderConnectionsSidebar(state);
}

function setConnectionsCenter(id) {
  const state = connectionsState;
  if (!state) return;
  state.centerId = id;
  const params = new URLSearchParams(window.location.search);
  params.set("id", id);
  params.set("depth", String(state.depth));
  history.replaceState(null, "", `${window.location.pathname}?${params}`);
  if (state.pickerSetValue) state.pickerSetValue(id);
  const status = document.getElementById("conn-person-status");
  if (status) status.textContent = "";
  renderConnectionsGraph(state);
}

// mode: "people" (connections.html) — genealogy + narrative edges between
// people only. "places" (place-connections.html) — a bipartite people<->place
// graph built from place-connections.json alone; person-to-person edges are
// deliberately left to the people graph so the two views stay distinct.
async function renderConnectionsPage(mode = "people") {
  const placesMode = mode === "places";
  const [peopleIndex, peopleEdges] = await Promise.all([
    loadIndex(),
    loadConnections(),
  ]);

  let index, edges;
  if (placesMode) {
    const [placesIndex, placeEdges] = await Promise.all([
      loadPlacesIndex(),
      loadPlaceConnections(),
    ]);
    // Only the people Scripture actually ties to a place appear here, plus
    // every place. Place nodes reuse the same person_id-keyed index/edge
    // machinery via placeToGraphEntry, so every traversal/render function
    // works unchanged. loadIndex()'s cached DATA.index is never mutated.
    const linkedPeople = new Set();
    for (const e of placeEdges) {
      if (!isPlaceNodeId(e.from)) linkedPeople.add(e.from);
      if (!isPlaceNodeId(e.to)) linkedPeople.add(e.to);
    }
    index = [
      ...peopleIndex.filter((e) => linkedPeople.has(e.person_id)),
      ...placesIndex.map(placeToGraphEntry),
    ];
    edges = placeEdges;
  } else {
    index = [...peopleIndex];
    edges = peopleEdges;
  }
  const adjacency = buildAdjacency(index, edges);

  const params = new URLSearchParams(window.location.search);
  let depth = Number(params.get("depth"));
  if (!Number.isInteger(depth) || depth < CONN_MIN_DEPTH || depth > CONN_MAX_DEPTH) {
    depth = CONN_DEFAULT_DEPTH;
  }

  connectionsState = {
    index,
    edgesRaw: edges,
    adjacency,
    depth,
    networkSizes: computeNetworkSizes(index, adjacency, depth),
    labelsOn: true,
    fullPage: false,
    zoomPct: 100,
    centerId: null,
  };

  renderConnectionsLegend(document.getElementById("connections-legend"), placesMode);
  initConnectionsPicker(connectionsState);
  initConnectionsControls(connectionsState);
  initConnectionsZoom(connectionsState);

  const requestedId = params.get("id");
  const requestedEntry = requestedId && index.find((e) => e.person_id === requestedId);
  let startId;
  if (requestedEntry) {
    startId = requestedEntry.person_id;
  } else {
    const withEdges = index.filter((e) => neighborIds(adjacency, e.person_id).length > 0);
    startId = withEdges.length
      ? withEdges[Math.floor(Math.random() * withEdges.length)].person_id
      : index[0] && index[0].person_id;
  }

  if (startId) setConnectionsCenter(startId);
}

// ---------------------------------------------------------------------
// Timeline
// ---------------------------------------------------------------------

const ERA_ORDER = [
  "Primeval History",
  "Patriarchal",
  "Exodus/Wilderness",
  "Judges",
  "United Monarchy",
  "Divided Monarchy",
  "Exile",
  "Post-Exile/Intertestamental",
  "Gospels",
  "Apostolic",
];

// Broad approximate year-range for each era, used ONLY as a stand-in span for
// figures whose individual birth/death years are not placed on the timeline
// (most of the OT — see CLAUDE.md's Timeline section). These are deliberately
// wide brackets reflecting one commonly-cited evangelical framework among
// several competing ones, not a claim of precision — every bar built from
// them renders with the dashed/textured "era estimate" style and says so in
// its tooltip, never as a specific date. Astronomical-style signed years
// (negative = BC).
const ERA_BANDS = {
  // Genesis 1-11 (creation through the Table of Nations and Babel) has no
  // scholarly consensus chronology at all -- not just disputed dates, like
  // the Exodus, but disputed whether the genealogies even represent an
  // unbroken chronological sequence (young-earth, old-earth, and framework
  // readings differ far more sharply here than anywhere else in the era
  // taxonomy). This band exists only to give these figures *some* left-right
  // ordinal position ahead of Patriarchal; its width is not a claim about
  // how long this period actually was.
  "Primeval History": [-6000, -2166],
  "Patriarchal": [-2166, -1805],
  "Exodus/Wilderness": [-1446, -1200],
  "Judges": [-1200, -1050],
  "United Monarchy": [-1050, -930],
  "Divided Monarchy": [-930, -586],
  "Exile": [-586, -538],
  "Post-Exile/Intertestamental": [-538, -5],
  "Gospels": [-5, 33],
  "Apostolic": [30, 100],
};

const TIMELINE_REGIONS = [
  { key: "mesopotamia", label: "Mesopotamia" },
  { key: "egypt", label: "Egypt" },
  { key: "sinai-wilderness", label: "Sinai & Wilderness" },
  { key: "canaan-israel", label: "Canaan & Israel" },
  { key: "moab-transjordan", label: "Moab & Transjordan" },
  { key: "asia-minor-greece", label: "Asia Minor & Greece" },
  { key: "rome-italy", label: "Rome & Italy" },
];
// The twelve tribes of Israel (Ephraim/Manasseh standing in for Joseph),
// used for the timeline's checkbox legend and bar color-coding -- see the
// data's `tribe` field (CLAUDE.md's Tribal Affiliation section), curated
// for a minority of full-tier people (explicit text or genealogy-chain
// inference only) and never present on stubs. Fixed order matches the hue
// order the palette was validated against (see --tribe-* in css/style.css).
const TIMELINE_TRIBES = [
  { key: "reuben", label: "Reuben" },
  { key: "simeon", label: "Simeon" },
  { key: "levi", label: "Levi" },
  { key: "judah", label: "Judah" },
  { key: "dan", label: "Dan" },
  { key: "naphtali", label: "Naphtali" },
  { key: "gad", label: "Gad" },
  { key: "asher", label: "Asher" },
  { key: "issachar", label: "Issachar" },
  { key: "zebulun", label: "Zebulun" },
  { key: "ephraim", label: "Ephraim" },
  { key: "manasseh", label: "Manasseh" },
  { key: "benjamin", label: "Benjamin" },
];
const TIMELINE_TRIBES_WITH_OTHER = [
  ...TIMELINE_TRIBES,
  { key: "other", label: "No tribe recorded" },
];

// Compositional order of the biblical books, used only to give era-precision
// (year-less) OT figures a relative left-to-right position within their era
// band -- e.g. Abraham (Genesis 12) plots left of Joseph (Genesis 37) inside
// the same Patriarchal band -- instead of every person in an era rendering
// as one identical block. This is an ordinal ranking by narrative sequence,
// never a claim about a specific calendar year.
const BOOK_ORDER = [
  "Genesis", "Exodus", "Leviticus", "Numbers", "Deuteronomy",
  "Joshua", "Judges", "Ruth",
  "1 Samuel", "2 Samuel", "1 Kings", "2 Kings",
  "1 Chronicles", "2 Chronicles", "Ezra", "Nehemiah", "Esther",
  "Job", "Psalms", "Proverbs", "Ecclesiastes", "Song of Solomon",
  "Isaiah", "Jeremiah", "Lamentations", "Ezekiel", "Daniel",
  "Hosea", "Joel", "Amos", "Obadiah", "Jonah", "Micah", "Nahum",
  "Habakkuk", "Zephaniah", "Haggai", "Zechariah", "Malachi",
  "Matthew", "Mark", "Luke", "John", "Acts",
  "Romans", "1 Corinthians", "2 Corinthians", "Galatians", "Ephesians",
  "Philippians", "Colossians", "1 Thessalonians", "2 Thessalonians",
  "1 Timothy", "2 Timothy", "Titus", "Philemon", "Hebrews",
  "James", "1 Peter", "2 Peter", "1 John", "2 John", "3 John", "Jude",
  "Revelation",
];

// Generic "lifetime" bar length for era-precision figures, in the same
// notional years used by ERA_BANDS -- a fixed, human-scale span (roughly
// what the date-precision figures elsewhere on the timeline actually live)
// rather than a fraction of the era band's own width. Era bands vary hugely
// in width (Primeval History alone spans ~3800 notional years vs. Exile's
// 48), and scaling bar length off that width made bars in the widest bands
// balloon to hundreds of "years" long -- implying a duration the ordinal
// placement never claimed. Capped at half of a narrow band's width so a bar
// still fits inside its own era's segment.
const TIMELINE_ERA_ORDINAL_LIFESPAN_YEARS = 50;

// Space kept clear at each end of an era band before the first/last
// person's bar, in the same notional years as ERA_BANDS -- also a fixed
// amount rather than a fraction of the band's width, for the same reason.
// A fractional margin compounds badly right at the seam between two very
// differently-sized eras: 8% of Primeval History's ~3800-year band alone
// was ~300 notional years of dead space on each side, which read as a
// large empty gap before Patriarchal's own bars even started, even though
// the two bands themselves are contiguous with no gap between them.
// Capped at a fraction of a narrow band's own width so it never eats the
// whole band.
const TIMELINE_ERA_ORDINAL_MARGIN_YEARS = 20;

// Where, within a parent's own bar, a child's bar begins -- expressed as a
// fraction of the parent's span. A child is a known contemporary of their
// parent (born partway through the parent's life, often outliving them),
// so anchoring here guarantees the two bars overlap instead of just sitting
// in sequence. Multiple children of the same parent are staggered by
// TIMELINE_PARENT_OVERLAP_STEP_FRACTION each so they don't all render as one
// identical bar, capped at TIMELINE_PARENT_OVERLAP_MAX_FRACTION so a large
// family doesn't get pushed past the parent's own lifespan.
const TIMELINE_PARENT_OVERLAP_START_FRACTION = 0.2;
const TIMELINE_PARENT_OVERLAP_STEP_FRACTION = 0.12;
const TIMELINE_PARENT_OVERLAP_MAX_FRACTION = 0.75;

function timelineParseReference(ref) {
  if (!ref) return null;
  let bestBook = null;
  for (const book of BOOK_ORDER) {
    if ((ref === book || ref.startsWith(`${book} `)) && (!bestBook || book.length > bestBook.length)) {
      bestBook = book;
    }
  }
  if (!bestBook) return null;
  const chapterMatch = ref.slice(bestBook.length).trim().match(/^(\d+)/);
  return {
    bookIndex: BOOK_ORDER.indexOf(bestBook),
    chapter: chapterMatch ? Number(chapterMatch[1]) : 0,
  };
}

// Ordinal rank of a person's earliest listed reference: which book it's in,
// then which chapter -- used purely to order era-precision people left to
// right, not to place them at a specific year.
function timelineNarrativeRank(person) {
  const ref = person.first_reference || (person.references || [])[0];
  const parsed = timelineParseReference(ref);
  return parsed ? parsed.bookIndex * 1000 + parsed.chapter : null;
}

// Spreads era-precision people out across their shared era band using the
// genealogy edges already in the data wherever they exist, falling back to
// narrative (book/chapter) order otherwise:
//   - spouses are known contemporaries, so they're placed in the exact same
//     slot (their bars fully overlap in x, stacked in separate lanes by the
//     existing lane packer) rather than wherever their own first reference
//     happens to fall in the text -- this is what fixes Abraham/Sarah/Hagar
//     rendering as if they lived decades apart.
//   - a child is never placed before their own parent's slot, even if the
//     child's first reference happens to appear earlier in the text.
// Mutates each person's start/end in place.
function assignEraOrdinalSpans(people) {
  const byEra = new Map();
  for (const p of people) {
    if (p.precision !== "era") continue;
    if (!byEra.has(p.era)) byEra.set(p.era, []);
    byEra.get(p.era).push(p);
  }
  for (const [era, group] of byEra) {
    const band = ERA_BANDS[era];
    if (!band) continue;
    const bandWidth = band[1] - band[0];
    const groupIds = new Set(group.map((p) => p.person_id));
    const byId = new Map(group.map((p) => [p.person_id, p]));
    const baseRank = new Map(group.map((p) => [p.person_id, timelineNarrativeRank(p)]));

    // Union-find over spouse edges within this era, so married couples
    // (and, transitively, co-wives of the same husband) collapse to one slot.
    const parentOf = new Map(group.map((p) => [p.person_id, p.person_id]));
    const find = (id) => {
      while (parentOf.get(id) !== id) {
        parentOf.set(id, parentOf.get(parentOf.get(id)));
        id = parentOf.get(id);
      }
      return id;
    };
    const union = (a, b) => {
      const ra = find(a), rb = find(b);
      if (ra !== rb) parentOf.set(ra, rb);
    };
    for (const p of group) {
      for (const spouseId of (p.genealogy && p.genealogy.spouses) || []) {
        if (groupIds.has(spouseId)) union(p.person_id, spouseId);
      }
    }

    // Cluster rank = the best (earliest) narrative rank among its members.
    const clusterRank = new Map();
    for (const p of group) {
      const root = find(p.person_id);
      const r = baseRank.get(p.person_id);
      if (r == null) continue;
      if (!clusterRank.has(root) || r < clusterRank.get(root)) clusterRank.set(root, r);
    }

    // A few relaxation passes so a child's cluster never ranks before their
    // parent's cluster, even across spouse-merged clusters.
    for (let pass = 0; pass < 4; pass++) {
      for (const p of group) {
        const parentIds = [p.genealogy && p.genealogy.father, p.genealogy && p.genealogy.mother];
        for (const parentId of parentIds) {
          if (!parentId || !byId.has(parentId)) continue;
          const childRoot = find(p.person_id);
          const parentRoot = find(parentId);
          if (childRoot === parentRoot) continue;
          const parentR = clusterRank.get(parentRoot);
          const childR = clusterRank.get(childRoot);
          if (parentR != null && (childR == null || childR <= parentR)) {
            clusterRank.set(childRoot, parentR + 0.5);
          }
        }
      }
    }

    // Order distinct clusters (not individual people) evenly across the band.
    // A cluster with no resolved rank -- no first_reference of its own, and no
    // ranked parent or spouse to inherit a position from after the relaxation
    // passes above -- has no textual or genealogical basis for a left-to-right
    // position, so it's left off the timeline entirely rather than dumped at
    // an arbitrary spot (the previous Infinity/Infinity fallback here produced
    // NaN from the sort comparator, which is exactly that arbitrary dumping).
    const clusters = new Map();
    for (const p of group) {
      const root = find(p.person_id);
      if (!clusterRank.has(root)) {
        p.start = null;
        p.end = null;
        continue;
      }
      if (!clusters.has(root)) clusters.set(root, []);
      clusters.get(root).push(p);
    }
    const ordered = Array.from(clusters.entries()).sort(
      (a, b) => clusterRank.get(a[0]) - clusterRank.get(b[0])
    );

    const margin = Math.min(TIMELINE_ERA_ORDINAL_MARGIN_YEARS, bandWidth * 0.2);
    const usableStart = band[0] + margin;
    const usableWidth = bandWidth - 2 * margin;
    const defaultLifespan = Math.min(TIMELINE_ERA_ORDINAL_LIFESPAN_YEARS, Math.max(bandWidth * 0.5, 15));

    // Only full-tier clusters get an evenly-spaced ordinal slot -- they're
    // the "spine" that stays visible with stub (name-only) entries hidden,
    // the default view. Stub-only clusters interpolate between their
    // nearest full-tier neighbors by rank instead of claiming an even share
    // of the same slots, so hiding them (the default) doesn't leave the
    // remaining full-tier bars looking artificially far apart -- e.g.
    // without this, ~100 hidden Genesis 10-11 stub entries left Nimrod
    // stranded far from Abraham even though the two eras are contiguous.
    const fullIndexes = [];
    ordered.forEach(([, members], i) => {
      if (members.some((p) => p.tier === "full")) fullIndexes.push(i);
    });
    const fullFraction = (orderedIndex) => {
      const rank = fullIndexes.indexOf(orderedIndex);
      return fullIndexes.length > 1 ? rank / (fullIndexes.length - 1) : 0.5;
    };
    const slotFraction = (i) => {
      if (fullIndexes.length === 0) {
        return ordered.length > 1 ? i / (ordered.length - 1) : 0.5;
      }
      if (fullIndexes.includes(i)) return fullFraction(i);
      let lo = null, hi = null;
      for (const fi of fullIndexes) {
        if (fi < i) lo = fi;
        if (fi > i && hi === null) hi = fi;
      }
      if (lo == null) return fullFraction(hi);
      if (hi == null) return fullFraction(lo);
      const loT = fullFraction(lo), hiT = fullFraction(hi);
      return loT + ((i - lo) / (hi - lo)) * (hiT - loT);
    };

    // A person's own Scripture-stated `timeline.lifespan_years` (see the
    // Timeline section of CLAUDE.md) sets their bar's length directly
    // instead of the generic estimate -- unlike their left-right position,
    // that number is a stated fact ("all his days were 969 years, and he
    // died," Genesis 5:27), not an ordinal guess.
    const lifespanFor = (p) => {
      const stated = p.timeline && typeof p.timeline.lifespan_years === "number"
        ? p.timeline.lifespan_years
        : null;
      return stated != null ? stated : defaultLifespan;
    };

    ordered.forEach(([, members], i) => {
      const t = slotFraction(i);
      const center = usableStart + t * usableWidth;
      for (const p of members) {
        p.start = center;
        p.end = center + lifespanFor(p);
      }
    });

    // Re-anchor children to overlap their same-era parent's bar (see
    // TIMELINE_PARENT_OVERLAP_START_FRACTION above) instead of leaving them
    // at the purely ordinal position assigned just above. Processed in
    // `ordered`'s rank order, which the relaxation passes already guarantee
    // is parent-before-child, so a parent's span is final (whether from the
    // ordinal pass or from this same pass acting on a grandparent) by the
    // time each of its children is reached -- this also lets multi-generation
    // chains (e.g. Abraham -> Isaac -> Jacob) resolve correctly in one pass.
    const orderedIndexByRoot = new Map(ordered.map(([root], i) => [root, i]));
    const isSpineRoot = (root) => fullIndexes.includes(orderedIndexByRoot.get(root));

    const childCountByParentRoot = new Map();
    for (const [root, members] of ordered) {
      let parent = null;
      for (const p of members) {
        const fatherId = p.genealogy && p.genealogy.father;
        const motherId = p.genealogy && p.genealogy.mother;
        const candidateId = fatherId && byId.has(fatherId)
          ? fatherId
          : (motherId && byId.has(motherId) ? motherId : null);
        if (!candidateId || find(candidateId) === root) continue;
        parent = byId.get(candidateId);
        break;
      }
      if (!parent || parent.start == null) continue;
      const parentRoot = find(parent.person_id);
      // A spine (full-tier) cluster keeps its own evenly-spaced slot unless
      // its nearest parent is ALSO on the spine -- otherwise a full-tier
      // person whose immediate parent happens to be a stub (extremely
      // common; most genealogy links are to stub entries) would get dragged
      // off the spine entirely, undoing the fix above: e.g. Nimrod
      // (full-tier) re-anchoring onto his stub father Cush instead of
      // keeping his own last-in-era spine slot next to Abraham.
      if (isSpineRoot(root) && !isSpineRoot(parentRoot)) continue;
      const idx = childCountByParentRoot.get(parentRoot) || 0;
      childCountByParentRoot.set(parentRoot, idx + 1);
      const parentWidth = parent.end - parent.start;
      const startFraction = Math.min(
        TIMELINE_PARENT_OVERLAP_START_FRACTION + idx * TIMELINE_PARENT_OVERLAP_STEP_FRACTION,
        TIMELINE_PARENT_OVERLAP_MAX_FRACTION
      );
      const newStart = parent.start + parentWidth * startFraction;
      for (const p of members) {
        p.start = newStart;
        p.end = newStart + lifespanFor(p);
      }
    }

    // The re-anchor pass above only guarantees overlap with whichever parent
    // (father preferred -- see the `candidateId` lookup above) was actually
    // used to place the child. If a father was used, the mother's own bar
    // was never touched, and a mother whose lifespan track differs from the
    // father's (e.g. she has no Scripture-stated lifespan and gets the
    // generic default, or simply died earlier) can end up not covering her
    // child's birth position at all -- a mother's bar must always overlap
    // the birth of every child she's recorded as bearing, so stretch her
    // span to cover it here rather than leaving that to chance.
    for (const p of group) {
      const motherId = p.genealogy && p.genealogy.mother;
      if (!motherId || !byId.has(motherId) || p.start == null) continue;
      const mother = byId.get(motherId);
      if (mother.start == null) continue;
      if (p.start < mother.start) mother.start = p.start;
      if (p.start > mother.end) mother.end = p.start;
    }
  }
}

// Minimum overlap (in the same notional years used elsewhere on the
// Timeline) forced onto a documented narrative pair -- enough to read as a
// real overlap once rendered, not a one-pixel sliver.
const TIMELINE_NARRATIVE_OVERLAP_YEARS = 15;

// The passes above guarantee a child's bar overlaps its *parent's* bar, and
// spouses already collapse to one identical slot -- but nothing makes two
// siblings, or any other documented pair, overlap *each other*. That's a
// real gap: Cain and Abel are both anchored to Adam's span but staggered
// apart (so they don't render as one identical bar), which left their bars
// not overlapping at all even though Genesis 4 requires them to have been
// alive at the same moment for Cain to kill Abel. Any `connections.json`
// edge that isn't `parent-child`/`married` (both already guaranteed above)
// describes a documented interaction -- mentorship, collaboration, rivalry,
// or a future type -- that by definition required both people to be alive
// together, so force it here: whichever era-precision bar starts later gets
// pulled back to overlap the earlier one's bar, keeping its own length.
// Only applied within the same era band; cross-era or date-precision pairs
// are left alone; already-overlapping pairs are untouched.
function assignNarrativeOverlaps(people, edges) {
  const byId = new Map(people.map((p) => [p.person_id, p]));
  for (const edge of edges || []) {
    if (edge.type === "parent-child" || edge.type === "married") continue;
    const a = byId.get(edge.from);
    const b = byId.get(edge.to);
    if (!a || !b) continue;
    if (a.precision !== "era" || b.precision !== "era") continue;
    if (a.start == null || b.start == null) continue;
    if (a.era !== b.era) continue;
    const [earlier, later] = a.start <= b.start ? [a, b] : [b, a];
    if (later.start < earlier.end) continue;
    const band = ERA_BANDS[earlier.era];
    const lifespan = later.end - later.start;
    const newStart = Math.max(
      band ? band[0] : -Infinity,
      earlier.end - TIMELINE_NARRATIVE_OVERLAP_YEARS
    );
    later.start = newStart;
    later.end = newStart + lifespan;
  }
}

const TIMELINE_PX_PER_YEAR = 4;
const TIMELINE_LANE_HEIGHT = 28;
const TIMELINE_LANE_GAP = 8;
const TIMELINE_MIN_BAR_WIDTH = 16;
const TIMELINE_LABEL_MIN_WIDTH = 46;
const TIMELINE_YEAR_PAD = 5;

let timelineDeepLinkApplied = false;
let timelineRenderState = null;

// The index stores `tribe` as a display string ("Judah", "Levi", ...) --
// normalize to the lowercase key the legend/palette use, falling back to
// "other" for anyone with no recorded tribe or a value that isn't one of
// the twelve.
function timelineTribeKey(tribe) {
  const key = (tribe || "").toLowerCase();
  return TIMELINE_TRIBES.some((t) => t.key === key) ? key : "other";
}

function timelineTribeLabel(key) {
  const found = TIMELINE_TRIBES_WITH_OTHER.find((t) => t.key === key);
  return found ? found.label : "No tribe recorded";
}

function timelineFormatYear(year) {
  const y = Math.round(year);
  return y < 0 ? `${-y} BC` : `AD ${y}`;
}

// Splits a visible [minYear, maxYear] range into the era segments it spans,
// clipped to that range -- used to label the axis by era name instead of by
// specific BC/AD year, since only the era boundaries themselves (not any one
// person's position within them) rest on a cited chronology.
function timelineEraSegments(minYear, maxYear) {
  const segments = [];
  for (const era of ERA_ORDER) {
    const band = ERA_BANDS[era];
    if (!band) continue;
    const start = Math.max(band[0], minYear);
    const end = Math.min(band[1], maxYear);
    if (end > start) segments.push({ era, start, end });
  }
  return segments;
}

// Resolves a full-tier person record into a {start, end, precision, alive}
// span the lane packer and renderer can treat uniformly, whether the person
// has a specific estimated date or only an era-band placement.
function timelinePersonSpan(person) {
  const tl = person.timeline;
  if (!tl) return null;
  if (tl.precision === "era") {
    const band = ERA_BANDS[person.era];
    if (!band) return null;
    return { start: band[0], end: band[1], precision: "era", alive: false };
  }
  if (tl.precision === "date" && typeof tl.born === "number") {
    const alive = tl.died == null;
    const end = typeof tl.died === "number" ? tl.died : new Date().getFullYear();
    return { start: tl.born, end, precision: "date", alive };
  }
  return null;
}

function timelineStatedLifespan(p) {
  return p.timeline && typeof p.timeline.lifespan_years === "number" ? p.timeline.lifespan_years : null;
}

function timelineLifespanLabel(p) {
  if (p.precision === "era") {
    const stated = timelineStatedLifespan(p);
    const positionNote = "position reflects narrative order across Scripture's books and chapters, not a calendar date";
    return stated != null
      ? `${p.era} era — lived ${stated} years (Scripture-stated); ${positionNote}`
      : `${p.era} era — ${positionNote}`;
  }
  const endLabel = p.alive ? "present" : `c. ${timelineFormatYear(p.end)}`;
  return `c. ${timelineFormatYear(p.start)} – ${endLabel}`;
}

function timelineTooltipNote(p) {
  if (p.timeline && p.timeline.note) return p.timeline.note;
  if (p.precision === "era") {
    const stated = timelineStatedLifespan(p);
    if (stated != null) {
      return `Scripture states this person lived ${stated} years, so that figure sets this bar's length directly. Its left-right position is still only an estimate: this period's chronology is genuinely disputed among evangelical scholars, and reflects where this person falls across Scripture's books and chapters, not a calendar year.`;
    }
    return "Era estimate — this period's chronology is genuinely disputed among evangelical scholars. This bar's left-right position reflects where this person falls across Scripture's books and chapters, not a calendar year, and its faded edges are a reminder that neither the date nor the exact span is known.";
  }
  return "";
}

// Greedy interval-scheduling lane packer: sorts by start year, then places
// each span in the first lane whose current occupant has already ended by
// that start year, opening a new lane only when none is free. Deterministic
// and collision-free, and naturally reuses lanes across non-overlapping
// clusters of time (e.g. Patriarchal-era and Apostolic-era bars can share a
// lane even though dozens of centuries apart).
function timelinePackLanes(spans) {
  const sorted = spans.slice().sort((a, b) => a.start - b.start);
  const laneEnds = [];
  for (const s of sorted) {
    let lane = laneEnds.findIndex((end) => end <= s.start);
    if (lane === -1) {
      lane = laneEnds.length;
      laneEnds.push(s.end);
    } else {
      laneEnds[lane] = s.end;
    }
    s.lane = lane;
  }
  return { spans: sorted, laneCount: laneEnds.length };
}

function timelineTooltipEl() {
  return document.getElementById("timeline-tooltip");
}

function positionTimelineTooltip(evt, mode) {
  const el = timelineTooltipEl();
  if (!el) return;
  if (mode === "focus") {
    const rect = evt.target.getBoundingClientRect();
    el.style.left = `${Math.round(rect.left)}px`;
    el.style.top = `${Math.round(rect.bottom + 8)}px`;
  } else {
    el.style.left = `${evt.clientX + 14}px`;
    el.style.top = `${evt.clientY + 14}px`;
  }
}

function showTimelinePersonTooltip(evt, p, mode) {
  const el = timelineTooltipEl();
  if (!el) return;
  el.innerHTML = "";
  const strong = document.createElement("strong");
  strong.textContent = p.name;
  el.appendChild(strong);
  if (p.disambiguation) {
    const disamb = document.createElement("span");
    disamb.className = "timeline-tooltip__disambig";
    disamb.textContent = p.disambiguation;
    el.appendChild(disamb);
  }
  el.appendChild(document.createTextNode(timelineLifespanLabel(p)));
  const meta = document.createElement("div");
  meta.textContent = [timelineTribeLabel(timelineTribeKey(p.tribe)), p.era]
    .filter(Boolean)
    .join(" · ");
  el.appendChild(meta);
  const note = timelineTooltipNote(p);
  if (note) {
    const em = document.createElement("em");
    em.textContent = note;
    el.appendChild(em);
  }
  el.hidden = false;
  positionTimelineTooltip(evt, mode);
}

function hideTimelineTooltip() {
  const el = timelineTooltipEl();
  if (el) el.hidden = true;
}

function timelineBuildLegend(container, presentKeys, onChange) {
  container.innerHTML = "";

  const allLabel = document.createElement("label");
  allLabel.className = "timeline-legend__item timeline-legend__item--all";
  const allCb = document.createElement("input");
  allCb.type = "checkbox";
  allCb.checked = true;
  allLabel.appendChild(allCb);
  allLabel.appendChild(document.createTextNode("All"));
  container.appendChild(allLabel);

  const tribeCheckboxes = [];
  function updateAllCheckboxState() {
    const checkedCount = tribeCheckboxes.filter((cb) => cb.checked).length;
    allCb.checked = checkedCount === tribeCheckboxes.length;
    allCb.indeterminate = checkedCount > 0 && checkedCount < tribeCheckboxes.length;
  }

  for (const tribe of TIMELINE_TRIBES_WITH_OTHER) {
    if (!presentKeys.has(tribe.key)) continue;
    const label = document.createElement("label");
    label.className = "timeline-legend__item";
    const cb = document.createElement("input");
    cb.type = "checkbox";
    cb.checked = true;
    cb.value = tribe.key;
    cb.addEventListener("change", () => {
      updateAllCheckboxState();
      onChange();
    });
    tribeCheckboxes.push(cb);
    const swatch = document.createElement("span");
    swatch.className = `timeline-legend__swatch timeline-legend__swatch--${tribe.key}`;
    label.appendChild(cb);
    label.appendChild(swatch);
    label.appendChild(document.createTextNode(tribe.label));
    container.appendChild(label);
  }

  allCb.addEventListener("change", () => {
    for (const cb of tribeCheckboxes) cb.checked = allCb.checked;
    allCb.indeterminate = false;
    onChange();
  });
}

function timelinePopulateJumpSelect(select) {
  select.innerHTML = "";
  const placeholder = document.createElement("option");
  placeholder.value = "";
  placeholder.textContent = "Jump to era…";
  select.appendChild(placeholder);
  for (const era of ERA_ORDER) {
    const band = ERA_BANDS[era];
    if (!band) continue;
    const opt = document.createElement("option");
    opt.value = String(Math.round((band[0] + band[1]) / 2));
    opt.textContent = era;
    select.appendChild(opt);
  }
}

function timelineScrollToYear(year) {
  if (!timelineRenderState) return;
  const wrapper = document.getElementById("timeline-canvas-wrapper");
  if (!wrapper) return;
  const x = (year - timelineRenderState.minYear) * TIMELINE_PX_PER_YEAR;
  wrapper.scrollTo({ left: Math.max(0, x - wrapper.clientWidth / 2), behavior: "smooth" });
}

function timelineScrollToPerson(personId) {
  const bar = document.querySelector(`.timeline-bar[data-person-id="${CSS.escape(personId)}"]`);
  if (!bar) return false;
  const wrapper = document.getElementById("timeline-canvas-wrapper");
  wrapper.scrollTo({
    left: Math.max(0, bar.offsetLeft - wrapper.clientWidth / 2),
    top: Math.max(0, bar.offsetTop - wrapper.clientHeight / 2),
    behavior: "smooth",
  });
  bar.classList.remove("timeline-bar--pulse");
  void bar.offsetWidth; // restart the animation if it already ran once
  bar.classList.add("timeline-bar--pulse");
  return true;
}

function applyTimelineDeepLink() {
  if (timelineDeepLinkApplied) return;
  timelineDeepLinkApplied = true;
  const params = new URLSearchParams(window.location.search);
  const highlight = params.get("highlight");
  if (highlight && timelineScrollToPerson(highlight)) return;
  const year = params.get("year");
  if (year && !Number.isNaN(Number(year))) {
    timelineScrollToYear(Number(year));
  }
}

async function renderTimelinePage() {
  const stateEl = document.getElementById("timeline-state");
  const wrapper = document.getElementById("timeline-canvas-wrapper");
  const canvas = document.getElementById("timeline-canvas");
  const countEl = document.getElementById("timeline-results-count");
  const legendEl = document.getElementById("timeline-legend");
  const stubToggle = document.getElementById("timeline-stub-toggle");
  const jumpSelect = document.getElementById("timeline-jump-era");

  function setState(msg) {
    if (msg) {
      stateEl.textContent = msg;
      stateEl.style.display = "block";
      wrapper.style.display = "none";
    } else {
      stateEl.style.display = "none";
      wrapper.style.display = "block";
    }
  }

  setState("Loading…");

  // Everyone in a genealogical ("x begat y") chain gets a timeline bar, not
  // just full-tier entries -- era/region/genealogy for stub entries is
  // pre-computed into the index by _build/infer_stub_eras.py, so no
  // per-person fetch is needed for any of the ~3,000 people here.
  const [index, edges] = await Promise.all([loadIndex(), loadConnections()]);

  const spanned = index
    .map((p) => {
      const span = timelinePersonSpan(p);
      return span ? Object.assign({}, p, span) : null;
    })
    .filter(Boolean);
  assignEraOrdinalSpans(spanned);
  assignNarrativeOverlaps(spanned, edges);
  // Era-precision people with no first_reference and no ranked parent/spouse
  // to inherit a position from are left unplaced (start/end nulled out) by
  // assignEraOrdinalSpans above -- drop them here rather than showing them
  // at a meaningless position.
  const people = spanned.filter((p) => p.start != null);

  if (!people.length) {
    countEl.textContent = "Showing 0 people";
    legendEl.innerHTML = "";
    setState("No full-tier entries have timeline data yet.");
    return;
  }

  const presentKeys = new Set(people.map((p) => timelineTribeKey(p.tribe)));

  function render() {
    const activeTribes = new Set(
      Array.from(legendEl.querySelectorAll('input[type="checkbox"]:checked')).map((cb) => cb.value)
    );
    const showStubs = stubToggle.checked;
    const visible = people.filter((p) => {
      if (!activeTribes.has(timelineTribeKey(p.tribe))) return false;
      if (!showStubs && p.tier === "stub") return false;
      return true;
    });

    countEl.textContent = `Showing ${visible.length} ${visible.length === 1 ? "person" : "people"}`;

    if (!visible.length) {
      canvas.innerHTML = "";
      setState("No one matches the current tribe filters.");
      return;
    }
    setState(null);

    const { spans, laneCount } = timelinePackLanes(visible.map((p) => Object.assign({}, p)));
    const minYear = Math.min(...spans.map((s) => s.start)) - TIMELINE_YEAR_PAD;
    const maxYear = Math.max(...spans.map((s) => s.end)) + TIMELINE_YEAR_PAD;
    const totalWidth = Math.round((maxYear - minYear) * TIMELINE_PX_PER_YEAR);
    const lanesHeight = laneCount * (TIMELINE_LANE_HEIGHT + TIMELINE_LANE_GAP) + TIMELINE_LANE_GAP;

    canvas.innerHTML = "";
    canvas.style.width = `${totalWidth}px`;

    const axis = document.createElement("div");
    axis.className = "timeline-axis";
    const segments = timelineEraSegments(minYear, maxYear);
    segments.forEach((seg, i) => {
      if (i > 0) {
        const divider = document.createElement("div");
        divider.className = "timeline-axis__tick";
        divider.style.left = `${Math.round((seg.start - minYear) * TIMELINE_PX_PER_YEAR)}px`;
        axis.appendChild(divider);
      }
      const label = document.createElement("span");
      label.className = "timeline-axis__era-label";
      label.style.left = `${Math.round((seg.start - minYear) * TIMELINE_PX_PER_YEAR)}px`;
      label.style.width = `${Math.round((seg.end - seg.start) * TIMELINE_PX_PER_YEAR)}px`;
      label.textContent = seg.era;
      axis.appendChild(label);
    });
    canvas.appendChild(axis);

    const lanesEl = document.createElement("div");
    lanesEl.className = "timeline-lanes";
    lanesEl.style.height = `${lanesHeight}px`;

    for (const p of spans) {
      const bar = document.createElement("a");
      bar.href = `people/${encodeURIComponent(p.person_id)}.html`;
      bar.className = `timeline-bar${p.alive ? " timeline-bar--alive" : ""}`;
      bar.dataset.personId = p.person_id;
      const x = Math.round((p.start - minYear) * TIMELINE_PX_PER_YEAR);
      const w = Math.max(TIMELINE_MIN_BAR_WIDTH, Math.round((p.end - p.start) * TIMELINE_PX_PER_YEAR));
      bar.style.left = `${x}px`;
      bar.style.top = `${TIMELINE_LANE_GAP + p.lane * (TIMELINE_LANE_HEIGHT + TIMELINE_LANE_GAP)}px`;
      bar.style.width = `${w}px`;

      const fill = document.createElement("span");
      fill.className = `timeline-bar__fill timeline-bar__fill--${p.precision}`;
      fill.style.backgroundColor = `var(--tribe-${timelineTribeKey(p.tribe)})`;
      bar.appendChild(fill);

      if (w >= TIMELINE_LABEL_MIN_WIDTH) {
        const label = document.createElement("span");
        label.className = "timeline-bar__label";
        const stated = timelineStatedLifespan(p);
        label.textContent = stated != null ? `${p.name} (${stated} yrs)` : p.name;
        bar.appendChild(label);
      }
      bar.addEventListener("mousemove", (evt) => showTimelinePersonTooltip(evt, p, "mouse"));
      bar.addEventListener("mouseenter", (evt) => showTimelinePersonTooltip(evt, p, "mouse"));
      bar.addEventListener("mouseleave", hideTimelineTooltip);
      bar.addEventListener("focus", (evt) => showTimelinePersonTooltip(evt, p, "focus"));
      bar.addEventListener("blur", hideTimelineTooltip);
      lanesEl.appendChild(bar);
    }

    canvas.appendChild(lanesEl);
    timelineRenderState = { minYear, maxYear };
    applyTimelineDeepLink();
  }

  timelineBuildLegend(legendEl, presentKeys, render);
  timelinePopulateJumpSelect(jumpSelect);
  jumpSelect.addEventListener("change", () => {
    if (jumpSelect.value) timelineScrollToYear(Number(jumpSelect.value));
    jumpSelect.value = "";
  });
  stubToggle.addEventListener("change", render);

  render();
}

function escapeHtml(s) {
  return String(s == null ? "" : s).replace(/[&<>"']/g, (c) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
  }[c]));
}

// ============================================================
// Map explorer (map.html) — our own base maps + place markers,
// preset groups from data/map-groups.json, shareable via ?places=.
// Base geometry + projection params come from data/maps.json
// (built by _build/generate_maps.py). See CLAUDE.md "Places / Map".
// ============================================================
async function renderMapExplorer() {
  const root = document.getElementById("map-explorer");
  if (!root) return;

  const [maps, placesIndex, groupsDoc] = await Promise.all([
    fetch(dataPath("maps.json")).then((r) => r.json()),
    loadPlacesIndex(),
    fetch(dataPath("map-groups.json")).then((r) => r.json()),
  ]);
  const GROUPS = groupsDoc.groups || [];
  const placed = placesIndex.filter((p) => typeof p.lat === "number");
  const byId = new Map(placed.map((p) => [p.place_id, p]));

  const geoById = new Map();
  await Promise.all(
    placed.map((p) =>
      loadPlace(p.place_id).then((d) => {
        if (d && d.geo) geoById.set(p.place_id, d.geo);
        if (d && d.first_reference) p.first_reference = d.first_reference;
      }),
    ),
  );

  const params = new URLSearchParams(location.search);
  const state = {
    extent: maps.extents[params.get("ext")] ? params.get("ext") : "holy-land",
    style: ["plain", "topo"].includes(params.get("style")) ? params.get("style") : "parchment",
    ids: new Set(),
    groupId: null,
    allLabels: false,
    zoom: 1,
    sel: null,
  };

  const els = {
    viewport: document.getElementById("mapx-viewport"),
    title: document.getElementById("mapx-title"),
    count: document.getElementById("mapx-count"),
    groups: document.getElementById("mapx-groups"),
    list: document.getElementById("mapx-list"),
    url: document.getElementById("mapx-url"),
  };

  // --- Inspect card: name / references / identification confidence, shown
  // while hovering (or keyboard-focusing) a place marker.
  const stage = els.viewport.parentNode;
  const inspectCard = document.createElement("div");
  inspectCard.className = "mapx-inspect";
  inspectCard.hidden = true;
  stage.appendChild(inspectCard);
  // When the card is "pinned" (opened by a click/tap rather than a passing
  // hover) it stays put until the reader dismisses it with the × button,
  // presses Escape, or opens another place's card.
  let inspectPinned = false;
  inspectCard.addEventListener("click", (e) => {
    if (e.target.closest(".mapx-inspect-close")) hideInspect();
  });
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && inspectPinned) hideInspect();
  });

  function hideInspect() {
    inspectCard.hidden = true;
    inspectPinned = false;
    inspectCard.classList.remove("is-pinned");
  }
  function confDescriptor(id) {
    const g = geoById.get(id) || {};
    const conf = g.confidence || 0;
    if (g.kind === "representative" && conf === 0)
      return ["Approximate regional anchor", "mk-approx"];
    if (conf === 0) return ["Approximate — location uncertain", "mk-approx"];
    if (conf >= 500) return [`Well identified · confidence ${conf}/1000`, "mk-secure"];
    return [`Disputed identification · confidence ${conf}/1000`, "mk-disputed"];
  }
  function showInspect(id, clientX, clientY, pin) {
    if (els.viewport.classList.contains("is-panning")) return;
    const p = byId.get(id);
    if (!p) return;
    inspectPinned = !!pin;
    inspectCard.classList.toggle("is-pinned", inspectPinned);
    const [ctext, ccls] = confDescriptor(id);
    const firstRef = p.first_reference || (p.references || [])[0] || "";
    inspectCard.innerHTML =
      `<button type="button" class="mapx-inspect-close" aria-label="Close">&times;</button>` +
      `<strong>${escapeHtml(p.name)}</strong>` +
      `<span class="mapx-inspect-row">${firstRef ? "First reference — " + escapeHtml(firstRef) : "Named in Scripture"}</span>` +
      `<span class="mapx-inspect-conf ${ccls}">${escapeHtml(ctext)}</span>`;
    inspectCard.hidden = false;
    const r = stage.getBoundingClientRect();
    const iw = inspectCard.offsetWidth;
    const ih = inspectCard.offsetHeight;
    let x = clientX - r.left + 14;
    let y = clientY - r.top + 14;
    if (x + iw > r.width) x = clientX - r.left - iw - 14;
    if (y + ih > r.height) y = r.height - ih - 6;
    inspectCard.style.left = `${Math.max(4, x)}px`;
    inspectCard.style.top = `${Math.max(4, y)}px`;
  }

  // --- Drag-to-pan: dragging the map body scrolls the viewport. A small
  // movement threshold keeps single-click marker toggling intact.
  (function initPan() {
    const vp = els.viewport;
    let active = false;
    let moved = false;
    let sx = 0;
    let sy = 0;
    let sl = 0;
    let st = 0;
    vp.addEventListener("pointerdown", (e) => {
      if (e.button !== 0) return;
      // Touch devices already drag-scroll the overflow container natively.
      if (e.pointerType && e.pointerType !== "mouse") return;
      active = true;
      moved = false;
      sx = e.clientX;
      sy = e.clientY;
      sl = vp.scrollLeft;
      st = vp.scrollTop;
    });
    vp.addEventListener("pointermove", (e) => {
      if (!active) return;
      const dx = e.clientX - sx;
      const dy = e.clientY - sy;
      if (!moved && Math.hypot(dx, dy) < 4) return;
      moved = true;
      vp.classList.add("is-panning");
      hideInspect();
      if (vp.setPointerCapture) {
        try {
          vp.setPointerCapture(e.pointerId);
        } catch (_) {}
      }
      vp.scrollLeft = sl - dx;
      vp.scrollTop = st - dy;
    });
    function end() {
      if (moved) {
        vp._suppressClick = true;
        setTimeout(() => {
          vp._suppressClick = false;
        }, 0);
      }
      active = false;
      vp.classList.remove("is-panning");
    }
    vp.addEventListener("pointerup", end);
    vp.addEventListener("pointercancel", end);
  })();

  // Pinch-to-zoom on touch devices (mirrors the +/- buttons; re-render is
  // throttled to one frame). One-finger drag still pans natively.
  (function initPinchZoom() {
    const vp = els.viewport;
    let startDist = null;
    let startZoom = 1;
    let raf = 0;
    vp.addEventListener(
      "touchstart",
      (e) => {
        if (e.touches.length === 2) {
          startDist = touchDistance(e.touches);
          startZoom = state.zoom;
          hideInspect();
        }
      },
      { passive: true },
    );
    vp.addEventListener(
      "touchmove",
      (e) => {
        if (e.touches.length !== 2 || !startDist) return;
        e.preventDefault();
        state.zoom = Math.max(0.6, Math.min(4, startZoom * (touchDistance(e.touches) / startDist)));
        if (!raf) raf = requestAnimationFrame(() => { raf = 0; render(); });
      },
      { passive: false },
    );
    function endPinch() {
      startDist = null;
    }
    vp.addEventListener("touchend", endPinch);
    vp.addEventListener("touchcancel", endPinch);
  })();

  function markerClass(id) {
    const g = geoById.get(id) || {};
    const conf = g.confidence || 0;
    if (g.kind === "representative" && conf === 0) return "mk-approx";
    if (conf >= 500) return "mk-secure";
    if (conf > 0) return "mk-disputed";
    return "mk-approx";
  }
  function isRegion(id) {
    return (geoById.get(id) || {}).kind === "representative";
  }
  function project(ext, lat, lng) {
    return [
      (lng - ext.lon_min) * ext.lon_scale,
      (ext.lat_max - lat) * ext.lat_scale,
    ];
  }

  function applyGroup(id) {
    const g = GROUPS.find((x) => x.id === id);
    if (!g) return;
    state.groupId = id;
    state.ids = new Set(g.places.filter((pid) => byId.has(pid)));
    if (maps.extents[g.extent]) state.extent = g.extent;
    state.sel = null;
  }

  const pParam = (params.get("places") || "")
    .split(",")
    .map((s) => s.trim())
    .filter((s) => byId.has(s));
  if (pParam.length) {
    pParam.forEach((id) => state.ids.add(id));
  } else if (params.get("group")) {
    applyGroup(params.get("group"));
  }

  function syncUrl() {
    const q = new URLSearchParams();
    q.set("ext", state.extent);
    if (state.style !== "parchment") q.set("style", state.style);
    if (state.ids.size) q.set("places", [...state.ids].join(","));
    if (els.url) els.url.value = `${location.origin}${location.pathname}?${q.toString()}`;
    history.replaceState(null, "", `?${q.toString()}`);
  }

  function render() {
    root.setAttribute("data-mapstyle", state.style);
    const ext = maps.extents[state.extent];
    const W = ext.width;
    const H = ext.height;
    // Zoom scales the geometry only; markers and labels are drawn at a
    // constant screen size (positioned in the zoomed coordinate space).
    const Z = state.zoom;
    const lakes = ext.lakes.map((d) => `<path class="map-lake" d="${d}"/>`).join("");
    const rivers = ext.rivers.map((d) => `<path class="map-river" d="${d}"/>`).join("");
    // "Topographic" style: a shaded-relief raster over the themed land. It's
    // pre-flattened to mid-grey off the land, so soft-light only bites on real
    // terrain — no land clip needed. Drawn in the scaled space, so it zooms
    // with the geometry.
    const relief =
      state.style === "topo" && ext.relief
        ? `<image class="map-relief" href="images/maps/${ext.relief}" x="0" y="0" ` +
          `width="${W}" height="${H}" preserveAspectRatio="none"/>`
        : "";

    const regionGeom = ext.regions || {};
    let regionOverlays = "";
    for (const id of state.ids) {
      const rg = regionGeom[id];
      if (rg) {
        regionOverlays += `<path class="${rg.t === "poly" ? "map-region-fill" : "map-region-line"}" d="${rg.d}"/>`;
      }
    }
    const geomLayer =
      `<g transform="scale(${Z})">` +
      `<path class="map-land" d="${ext.land}"/>${relief}${lakes}${rivers}${regionOverlays}</g>`;

    const ordered = placed.slice().sort((a, b) => {
      return (isRegion(a.place_id) ? 0 : 1) - (isRegion(b.place_id) ? 0 : 1);
    });

    let markers = "";
    for (const p of ordered) {
      const [px, py] = project(ext, p.lat, p.lng);
      if (px < -60 || px > W + 60 || py < -60 || py > H + 60) continue;
      const x = px * Z;
      const y = py * Z;
      const on = state.ids.has(p.place_id);
      const region = isRegion(p.place_id);
      const showLabel = state.allLabels || on || state.sel === p.place_id;
      const cls =
        "map-mk" +
        (region ? " mk-region" : "") +
        (on ? " is-on" : " is-dim") +
        (state.sel === p.place_id ? " is-sel" : "");
      const r = region ? 3 : on ? 5 : 3.4;
      const dotCls = region && !on ? "mk-region-dot" : markerClass(p.place_id);
      const anchorEnd = px > W * 0.72;
      const tx = anchorEnd ? -(r + 4) : r + 4;
      const ta = anchorEnd ? ' text-anchor="end"' : "";
      const label = `<text x="${tx}" y="4" font-size="12" class="${showLabel ? "" : "mk-hover-only"}"${ta}>${escapeHtml(p.name)}</text>`;
      markers +=
        `<g class="${cls}" data-id="${p.place_id}" tabindex="0" role="button" ` +
        `aria-label="${escapeHtml(p.name)}" transform="translate(${x.toFixed(1)},${y.toFixed(1)})">` +
        `<circle r="${r}" class="${dotCls}"/>${label}</g>`;
    }

    els.viewport.innerHTML =
      `<svg viewBox="0 0 ${(W * Z).toFixed(0)} ${(H * Z).toFixed(0)}" ` +
      `width="${(W * Z).toFixed(0)}" height="${(H * Z).toFixed(0)}" ` +
      `role="img" aria-label="Map: ${escapeHtml(ext.title)}">` +
      `<rect class="map-water-rect" x="0" y="0" width="${(W * Z).toFixed(0)}" height="${(H * Z).toFixed(0)}"/>` +
      `${geomLayer}${markers}</svg>`;

    els.viewport.querySelectorAll(".map-mk").forEach((g) => {
      const id = g.getAttribute("data-id");
      g.addEventListener("click", (e) => {
        if (els.viewport._suppressClick) return;
        if (state.ids.has(id)) state.ids.delete(id);
        else state.ids.add(id);
        state.groupId = null;
        state.sel = id;
        refresh();
        showInspect(id, e.clientX, e.clientY, true);
      });
      g.addEventListener("mouseenter", (e) => {
        g.parentNode.appendChild(g);
        if (!inspectPinned) showInspect(id, e.clientX, e.clientY);
      });
      g.addEventListener("mousemove", (e) => {
        if (!inspectCard.hidden && !inspectPinned) showInspect(id, e.clientX, e.clientY);
      });
      g.addEventListener("mouseleave", () => {
        if (!inspectPinned) hideInspect();
      });
      g.addEventListener("focus", () => {
        if (inspectPinned) return;
        const b = g.getBoundingClientRect();
        showInspect(id, b.left + b.width / 2, b.top + b.height / 2);
      });
      g.addEventListener("blur", () => {
        if (!inspectPinned) hideInspect();
      });
      g.addEventListener("keydown", (e) => {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault();
          g.dispatchEvent(new Event("click"));
        }
      });
    });

    requestAnimationFrame(() => {
      const vp = els.viewport;
      vp.classList.toggle(
        "is-pannable",
        vp.scrollWidth > vp.clientWidth + 1 || vp.scrollHeight > vp.clientHeight + 1,
      );
    });

    const grp = GROUPS.find((x) => x.id === state.groupId);
    els.title.textContent = grp ? grp.name : state.ids.size ? "Custom selection" : "All places";
    els.count.textContent = `${state.ids.size} place${state.ids.size === 1 ? "" : "s"} selected`;

    els.groups.querySelectorAll("button").forEach((b) =>
      b.setAttribute("aria-pressed", b.dataset.id === state.groupId),
    );
    els.list.querySelectorAll("input").forEach((cb) => {
      cb.checked = state.ids.has(cb.value);
    });
    document.querySelectorAll("#mapx-extent button").forEach((b) =>
      b.setAttribute("aria-pressed", b.dataset.v === state.extent),
    );
    document.querySelectorAll("#mapx-style button").forEach((b) =>
      b.setAttribute("aria-pressed", b.dataset.v === state.style),
    );
  }

  function refresh() {
    render();
    syncUrl();
  }

  els.groups.innerHTML = GROUPS.map(
    (g) =>
      `<button type="button" data-id="${g.id}"><span>${escapeHtml(g.name)}</span><small>${escapeHtml(g.blurb)}</small></button>`,
  ).join("");
  els.groups.querySelectorAll("button").forEach((b) => {
    b.addEventListener("click", () => {
      applyGroup(b.dataset.id);
      refresh();
    });
  });

  els.list.innerHTML = placed
    .slice()
    .sort((a, b) => a.name.localeCompare(b.name))
    .map(
      (p) =>
        `<label><input type="checkbox" value="${p.place_id}"> ${escapeHtml(p.name)}</label>`,
    )
    .join("");
  els.list.addEventListener("change", (e) => {
    const cb = e.target.closest("input");
    if (!cb) return;
    if (cb.checked) state.ids.add(cb.value);
    else state.ids.delete(cb.value);
    state.groupId = null;
    refresh();
  });

  document.getElementById("mapx-extent").addEventListener("click", (e) => {
    const b = e.target.closest("button");
    if (!b) return;
    state.extent = b.dataset.v;
    refresh();
  });
  document.getElementById("mapx-style").addEventListener("click", (e) => {
    const b = e.target.closest("button");
    if (!b) return;
    state.style = b.dataset.v;
    refresh();
  });
  document.getElementById("mapx-all-labels").addEventListener("change", (e) => {
    state.allLabels = e.target.checked;
    render();
  });
  document.getElementById("mapx-zoom-in").addEventListener("click", () => {
    state.zoom = Math.min(4, state.zoom * 1.3);
    render();
  });
  document.getElementById("mapx-zoom-out").addEventListener("click", () => {
    state.zoom = Math.max(0.6, state.zoom / 1.3);
    render();
  });
  const copyBtn = document.getElementById("mapx-copy");
  if (copyBtn) {
    copyBtn.addEventListener("click", () => {
      els.url.select();
      navigator.clipboard?.writeText(els.url.value).then(() => {
        copyBtn.textContent = "Copied";
        setTimeout(() => (copyBtn.textContent = "Copy"), 1500);
      });
    });
  }

  refresh();
}
