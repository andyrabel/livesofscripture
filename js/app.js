const DATA = {
  index: null,
  connections: null,
  places: null,
  whatsNew: null,
  quiz: null,
  timelineEvents: null,
};

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

async function loadTimelineEvents() {
  if (!DATA.timelineEvents) {
    const res = await fetch(dataPath("timeline-events.json"));
    DATA.timelineEvents = (await res.json()).events;
  }
  return DATA.timelineEvents;
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

function portraitImg(personId, name, className, imageFile, gender) {
  const img = document.createElement("img");
  img.src = `images/portraits/${imageFile || `${personId}.png`}`;
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

function renderHomeTopic(fullTier) {
  const box = document.getElementById("home-topic");
  const withTopics = fullTier.filter((p) => p.topics && p.topics.length);
  const pick = dailyPick("topic", withTopics);
  if (!pick) {
    box.hidden = true;
    return;
  }
  const topicIdx = seededHash(`topic-index:${todayKey()}`) % pick.topics.length;
  const topic = pick.topics[topicIdx];

  box.innerHTML = "";
  const label = document.createElement("span");
  label.className = "home-topic-box__label";
  label.textContent = "Today's theme";
  box.appendChild(label);

  const a = document.createElement("a");
  a.href = `people/${encodeURIComponent(pick.person_id)}.html`;
  a.className = "home-topic-box__value";
  a.textContent = `${topic} — as seen in ${pick.name}'s story`;
  box.appendChild(a);
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

  const answerText = document.createElement("p");
  answerText.className = "quiz-answer__text";
  answerText.textContent = q.answer;
  container.appendChild(answerText);

  if (q.reference) {
    const ref = document.createElement("p");
    ref.className = "quiz-answer__ref";
    ref.textContent = q.reference;
    container.appendChild(ref);
  }

  // Attribution only makes sense for a sub-entity question (e.g. a hymn
  // under a person) where the topic is distinct from what's being asked
  // about; for a plain person-topic question it would just repeat the
  // "Learn more" link's own name.
  if (q.subtopic_id) {
    const attribution = document.createElement("p");
    attribution.className = "quiz-answer__attribution";
    attribution.textContent = `(by ${nameForId(index, q.topic_id)})`;
    container.appendChild(attribution);
  }

  const learnMore = document.createElement("a");
  learnMore.className = "quiz-answer__learn-more";
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

  const body = document.getElementById("quiz-body");
  body.innerHTML = "";

  if (!pick) {
    const p = document.createElement("p");
    p.textContent = "No quiz questions available yet.";
    body.appendChild(p);
    return;
  }

  const q = document.createElement("p");
  q.className = "quiz-question";
  renderTextWithNameLinks(q, pick.question, nameEntries);
  body.appendChild(q);

  const btn = document.createElement("button");
  btn.type = "button";
  btn.className = "quiz-reveal-btn";
  btn.textContent = "Reveal Answer";
  body.appendChild(btn);

  btn.addEventListener("click", () => {
    btn.remove();
    const answer = document.createElement("div");
    answer.className = "quiz-answer";
    body.appendChild(answer);
    renderQuizAnswerBlock(answer, pick, index);
  });

  const takeQuizLink = document.getElementById("quiz-take-link");
  if (takeQuizLink) takeQuizLink.href = `quiz.html?max=${maxDifficulty}`;
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
  box.appendChild(portraitImg(pick.person_id, pick.name, "home-spotlight__thumb", pick.image));

  const text = document.createElement("div");
  const label = document.createElement("div");
  label.className = "home-spotlight__label";
  label.textContent = "Featured Entry";
  text.appendChild(label);

  const name = document.createElement("h2");
  name.className = "home-spotlight__name";
  name.textContent = pick.name;
  text.appendChild(name);

  const meta = document.createElement("div");
  meta.className = "home-spotlight__meta";
  meta.textContent = [pick.testament === "OT" ? "Old Testament" : "New Testament", pick.era]
    .filter(Boolean)
    .join(" · ");
  text.appendChild(meta);

  const excerpt = document.createElement("p");
  excerpt.className = "home-spotlight__excerpt";
  excerpt.textContent = truncateExcerpt(person?.source_summary, 280);
  text.appendChild(excerpt);

  const a = document.createElement("a");
  a.href = `people/${encodeURIComponent(pick.person_id)}.html`;
  a.textContent = "Read full story →";
  text.appendChild(a);

  box.appendChild(text);
}

function exploreCard(entry) {
  const a = document.createElement("a");
  a.className = "explore-card";
  a.href = `people/${encodeURIComponent(entry.person_id)}.html`;
  a.appendChild(portraitImg(entry.person_id, entry.name, "explore-card__thumb", entry.image));
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

  await renderHomeSpotlight(fullTier);
  renderHomeTopic(fullTier);
  initHomeQuiz(quiz, index);
  renderExploreRow(fullTier, index.length);
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

function eraBucketKey(entry) {
  if (entry && entry.era) {
    const bucket = ERA_BUCKETS.find((b) => b.eras.includes(entry.era));
    if (bucket) return bucket.key;
  }
  return "other";
}

function renderConnectionsLegend(container) {
  container.innerHTML = "";
  const items = [...ERA_BUCKETS.map((b) => [b.key, b.label]), ["other", "Era not placed"]];
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
  return entry.alt_names && entry.alt_names.length
    ? `${entry.name} (${entry.alt_names.join(", ")})`
    : entry.name;
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
  const bits = [entry.testament === "OT" ? "Old Testament" : "New Testament"];
  if (entry.era) bits.push(entry.era);
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
    g.appendChild(
      svgEl("circle", {
        cx: node.x,
        cy: node.y,
        r: radius,
        class: `connections-node__circle connections-node__circle--${bucket}`,
      })
    );

    const labelLink = svgEl("a", {
      href: `people/${encodeURIComponent(node.id)}.html`,
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

  container.appendChild(
    portraitImg(entry.person_id, entry.name, "connections-sidebar__avatar", entry.image, entry.gender)
  );

  const name = document.createElement("h3");
  name.textContent = entry.name;
  const tag = genderTag(entry.gender);
  if (tag) {
    name.appendChild(document.createTextNode(" "));
    name.appendChild(tag);
  }
  container.appendChild(name);

  const meta = document.createElement("p");
  meta.className = "connections-sidebar__meta";
  const bits = [entry.testament === "OT" ? "Old Testament" : "New Testament"];
  if (entry.era) bits.push(entry.era);
  meta.textContent = bits.join(" · ");
  container.appendChild(meta);

  // Total edges touching this person, not unique neighbors — two people can
  // be linked by more than one documented relationship (e.g. Paul and Peter
  // both clashed and collaborated), and each counts separately here.
  const degree = (state.adjacency.get(state.centerId) || []).length;
  const count = document.createElement("p");
  count.className = "connections-stats";
  count.textContent = `${degree} documented connection${degree === 1 ? "" : "s"}`;
  container.appendChild(count);

  const link = document.createElement("a");
  link.href = `people/${encodeURIComponent(entry.person_id)}.html`;
  link.className = "connections-sidebar__profile-link";
  link.textContent = "View full profile →";
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

async function renderConnectionsPage() {
  const [index, edges] = await Promise.all([loadIndex(), loadConnections()]);
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

  renderConnectionsLegend(document.getElementById("connections-legend"));
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
const TIMELINE_REGIONS_WITH_OTHER = [
  ...TIMELINE_REGIONS,
  { key: "other", label: "Other / unspecified" },
];

// Only meaningful during the Divided Monarchy era (930-586 BC), when the
// united kingdom split into the Northern Kingdom (Israel) and Southern
// Kingdom (Judah) -- see data's `kingdom` field, hand-curated for full-tier
// figures and propagated to stub genealogy relatives by
// _build/infer_stub_eras.py. People from other eras never carry this field.
const TIMELINE_KINGDOMS = [
  { key: "israel", label: "Israel (Northern Kingdom)" },
  { key: "judah", label: "Judah (Southern Kingdom)" },
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

// Fraction of an era band's width used as a generic "lifetime" bar length
// for era-precision figures, and the margin kept clear at each end of the
// band so the earliest/latest-ranked person's bar isn't flush with the
// hard edge of the era itself.
const TIMELINE_ERA_ORDINAL_SPAN_FRACTION = 0.16;
const TIMELINE_ERA_ORDINAL_MARGIN_FRACTION = 0.08;

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

    const usableStart = band[0] + bandWidth * TIMELINE_ERA_ORDINAL_MARGIN_FRACTION;
    const usableWidth = bandWidth * (1 - 2 * TIMELINE_ERA_ORDINAL_MARGIN_FRACTION);
    const lifespan = Math.max(bandWidth * TIMELINE_ERA_ORDINAL_SPAN_FRACTION, 15);
    ordered.forEach(([, members], i) => {
      const t = ordered.length > 1 ? i / (ordered.length - 1) : 0.5;
      const center = usableStart + t * usableWidth;
      for (const p of members) {
        p.start = center - lifespan / 2;
        p.end = center + lifespan / 2;
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
        p.end = newStart + lifespan;
      }
    }
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

function timelineRegionKey(region) {
  return TIMELINE_REGIONS.some((r) => r.key === region) ? region : "other";
}

function timelineRegionLabel(key) {
  const found = TIMELINE_REGIONS_WITH_OTHER.find((r) => r.key === key);
  return found ? found.label : "Region unspecified";
}

function timelineKingdomLabel(kingdom) {
  const found = TIMELINE_KINGDOMS.find((k) => k.key === kingdom);
  return found ? found.label : "";
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

function timelineLifespanLabel(p) {
  if (p.precision === "era") {
    return `${p.era} era — position reflects narrative order across Scripture's books and chapters, not a calendar date`;
  }
  const endLabel = p.alive ? "present" : `c. ${timelineFormatYear(p.end)}`;
  return `c. ${timelineFormatYear(p.start)} – ${endLabel}`;
}

function timelineTooltipNote(p) {
  if (p.timeline && p.timeline.note) return p.timeline.note;
  if (p.precision === "era") {
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
  el.appendChild(document.createTextNode(timelineLifespanLabel(p)));
  const meta = document.createElement("div");
  const kingdomLabel = timelineKingdomLabel(p.kingdom);
  meta.textContent = [timelineRegionLabel(timelineRegionKey(p.region)), p.era, kingdomLabel]
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

function showTimelineEventTooltip(evt, ev, mode) {
  const el = timelineTooltipEl();
  if (!el) return;
  el.innerHTML = "";
  const strong = document.createElement("strong");
  strong.textContent = `${ev.label} — ${ev.date}`;
  el.appendChild(strong);
  el.appendChild(document.createTextNode(ev.description));
  el.hidden = false;
  positionTimelineTooltip(evt, mode);
}

function hideTimelineTooltip() {
  const el = timelineTooltipEl();
  if (el) el.hidden = true;
}

function timelineBuildLegend(container, presentKeys, onChange) {
  container.innerHTML = "";
  for (const region of TIMELINE_REGIONS_WITH_OTHER) {
    if (!presentKeys.has(region.key)) continue;
    const label = document.createElement("label");
    label.className = "timeline-legend__item";
    const cb = document.createElement("input");
    cb.type = "checkbox";
    cb.checked = true;
    cb.value = region.key;
    cb.addEventListener("change", onChange);
    const swatch = document.createElement("span");
    swatch.className = `timeline-legend__swatch timeline-legend__swatch--${region.key}`;
    label.appendChild(cb);
    label.appendChild(swatch);
    label.appendChild(document.createTextNode(region.label));
    container.appendChild(label);
  }
  const eventItem = document.createElement("span");
  eventItem.className = "timeline-legend__item";
  const eventSwatch = document.createElement("span");
  eventSwatch.className = "timeline-legend__swatch timeline-legend__swatch--event";
  eventItem.appendChild(eventSwatch);
  eventItem.appendChild(document.createTextNode("Historical event"));
  container.appendChild(eventItem);
}

// Separate legend for the Israel/Judah split, shown only when at least one
// visible person carries a `kingdom` value (i.e. only ever during the
// Divided Monarchy era -- see TIMELINE_KINGDOMS above). Kept as its own
// row, distinct from the geographic region legend, since kingdom is a
// political rather than geographic distinction and both kingdoms share the
// same "Canaan & Israel" region.
function timelineBuildKingdomLegend(container, presentKingdoms, onChange) {
  container.innerHTML = "";
  if (!presentKingdoms.size) {
    container.style.display = "none";
    return;
  }
  container.style.display = "flex";
  const intro = document.createElement("span");
  intro.className = "timeline-legend__intro";
  intro.textContent = "Divided Monarchy:";
  container.appendChild(intro);
  for (const kingdom of TIMELINE_KINGDOMS) {
    if (!presentKingdoms.has(kingdom.key)) continue;
    const label = document.createElement("label");
    label.className = "timeline-legend__item";
    const cb = document.createElement("input");
    cb.type = "checkbox";
    cb.checked = true;
    cb.value = kingdom.key;
    cb.addEventListener("change", onChange);
    const swatch = document.createElement("span");
    swatch.className = `timeline-legend__swatch timeline-legend__swatch--kingdom-${kingdom.key}`;
    label.appendChild(cb);
    label.appendChild(swatch);
    label.appendChild(document.createTextNode(kingdom.label));
    container.appendChild(label);
  }
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
  const kingdomLegendEl = document.getElementById("timeline-kingdom-legend");
  const eventsToggle = document.getElementById("timeline-events-toggle");
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
  const [index, events] = await Promise.all([loadIndex(), loadTimelineEvents()]);

  const spanned = index
    .map((p) => {
      const span = timelinePersonSpan(p);
      return span ? Object.assign({}, p, span) : null;
    })
    .filter(Boolean);
  assignEraOrdinalSpans(spanned);
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

  const presentKeys = new Set(people.map((p) => timelineRegionKey(p.region)));
  const presentKingdoms = new Set(people.filter((p) => p.kingdom).map((p) => p.kingdom));

  function render() {
    const activeRegions = new Set(
      Array.from(legendEl.querySelectorAll('input[type="checkbox"]:checked')).map((cb) => cb.value)
    );
    const activeKingdoms = new Set(
      Array.from(kingdomLegendEl.querySelectorAll('input[type="checkbox"]:checked')).map((cb) => cb.value)
    );
    const showStubs = stubToggle.checked;
    const visible = people.filter((p) => {
      if (!activeRegions.has(timelineRegionKey(p.region))) return false;
      if (p.kingdom && !activeKingdoms.has(p.kingdom)) return false;
      if (!showStubs && p.tier === "stub") return false;
      return true;
    });

    countEl.textContent = `Showing ${visible.length} ${visible.length === 1 ? "person" : "people"}`;

    if (!visible.length) {
      canvas.innerHTML = "";
      setState("No one matches the current region filters.");
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
      fill.style.backgroundColor = p.kingdom
        ? `var(--kingdom-${p.kingdom})`
        : `var(--region-${timelineRegionKey(p.region)})`;
      bar.appendChild(fill);

      if (w >= TIMELINE_LABEL_MIN_WIDTH) {
        const label = document.createElement("span");
        label.className = "timeline-bar__label";
        label.textContent = p.name;
        bar.appendChild(label);
      }
      bar.addEventListener("mousemove", (evt) => showTimelinePersonTooltip(evt, p, "mouse"));
      bar.addEventListener("mouseenter", (evt) => showTimelinePersonTooltip(evt, p, "mouse"));
      bar.addEventListener("mouseleave", hideTimelineTooltip);
      bar.addEventListener("focus", (evt) => showTimelinePersonTooltip(evt, p, "focus"));
      bar.addEventListener("blur", hideTimelineTooltip);
      lanesEl.appendChild(bar);
    }

    if (eventsToggle.checked) {
      for (const ev of events) {
        if (ev.year < minYear || ev.year > maxYear) continue;
        const btn = document.createElement("button");
        btn.type = "button";
        btn.className = "timeline-event";
        btn.style.left = `${Math.round((ev.year - minYear) * TIMELINE_PX_PER_YEAR)}px`;
        btn.style.height = `${lanesHeight}px`;
        btn.setAttribute("aria-label", `${ev.label}, ${ev.date}`);
        const line = document.createElement("span");
        line.className = "timeline-event__line";
        btn.appendChild(line);
        const evLabel = document.createElement("span");
        evLabel.className = "timeline-event__label";
        evLabel.textContent = ev.label;
        btn.appendChild(evLabel);
        btn.addEventListener("mousemove", (evt) => showTimelineEventTooltip(evt, ev, "mouse"));
        btn.addEventListener("mouseenter", (evt) => showTimelineEventTooltip(evt, ev, "mouse"));
        btn.addEventListener("mouseleave", hideTimelineTooltip);
        btn.addEventListener("focus", (evt) => showTimelineEventTooltip(evt, ev, "focus"));
        btn.addEventListener("blur", hideTimelineTooltip);
        lanesEl.appendChild(btn);
      }
    }

    canvas.appendChild(lanesEl);
    timelineRenderState = { minYear, maxYear };
    applyTimelineDeepLink();
  }

  timelineBuildLegend(legendEl, presentKeys, render);
  timelineBuildKingdomLegend(kingdomLegendEl, presentKingdoms, render);
  timelinePopulateJumpSelect(jumpSelect);
  jumpSelect.addEventListener("change", () => {
    if (jumpSelect.value) timelineScrollToYear(Number(jumpSelect.value));
    jumpSelect.value = "";
  });
  eventsToggle.addEventListener("change", render);
  stubToggle.addEventListener("change", render);

  render();
}
