const DATA = {
  index: null,
  connections: null,
};

function dataPath(path) {
  return `data/${path}`;
}

async function loadIndex() {
  if (!DATA.index) {
    const res = await fetch(dataPath("people-index.json"));
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

function matchesSearch(entry, query) {
  if (!query) return true;
  const q = query.trim().toLowerCase();
  if (entry.name.toLowerCase().includes(q)) return true;
  return (entry.alt_names || []).some((n) => n.toLowerCase().includes(q));
}

function personCard(entry) {
  const a = document.createElement("a");
  a.className = "person-card";
  a.href = `person.html?id=${encodeURIComponent(entry.person_id)}`;

  const name = document.createElement("div");
  name.className = "name";
  name.textContent = entry.name;
  a.appendChild(name);

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

async function renderIndexPage() {
  const grid = document.getElementById("person-grid");
  const countEl = document.getElementById("result-count");
  const emptyEl = document.getElementById("empty-state");
  const searchInput = document.getElementById("search-input");
  const testamentFilter = document.getElementById("filter-testament");
  const tierFilter = document.getElementById("filter-tier");
  const eraFilter = document.getElementById("filter-era");

  const index = await loadIndex();

  const eras = [...new Set(index.filter((e) => e.era).map((e) => e.era))].sort();
  for (const era of eras) {
    const opt = document.createElement("option");
    opt.value = era;
    opt.textContent = era;
    eraFilter.appendChild(opt);
  }

  function render() {
    const query = searchInput.value;
    const testament = testamentFilter.value;
    const tier = tierFilter.value;
    const era = eraFilter.value;

    const filtered = index.filter((entry) => {
      if (!matchesSearch(entry, query)) return false;
      if (testament && entry.testament !== testament) return false;
      if (tier && entry.tier !== tier) return false;
      if (era && entry.era !== era) return false;
      return true;
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
  tierFilter.addEventListener("change", render);
  eraFilter.addEventListener("change", render);

  render();
}

function nameForId(index, id) {
  const entry = index.find((e) => e.person_id === id);
  return entry ? entry.name : id;
}

function linkForId(index, id) {
  const a = document.createElement("a");
  a.href = `person.html?id=${encodeURIComponent(id)}`;
  a.textContent = nameForId(index, id);
  return a;
}

function genealogyBlock(title, ids, index) {
  const block = document.createElement("div");
  block.className = "genealogy-block";
  const h4 = document.createElement("h4");
  h4.textContent = title;
  block.appendChild(h4);

  if (!ids || (Array.isArray(ids) && ids.length === 0) || ids === null) {
    const span = document.createElement("span");
    span.textContent = "—";
    span.style.color = "var(--color-text-muted)";
    block.appendChild(span);
    return block;
  }

  const list = Array.isArray(ids) ? ids : [ids];
  list.forEach((id, i) => {
    block.appendChild(linkForId(index, id));
    if (i < list.length - 1) block.appendChild(document.createTextNode(", "));
  });
  return block;
}

function reviewBadge(review) {
  const span = document.createElement("span");
  if (review && review.human_reviewed) {
    span.className = "review-badge reviewed";
    span.textContent = "✅ Reviewed for accuracy";
  } else {
    span.className = "review-badge unreviewed";
    span.textContent = "⚠️ AI-generated — not yet human reviewed";
  }
  return span;
}

function referencesList(refs) {
  const p = document.createElement("p");
  p.className = "references-list";
  p.textContent = `References: ${refs.join("; ")}`;
  return p;
}

async function renderFullPerson(person, index, connections) {
  const main = document.getElementById("person-main");
  main.innerHTML = "";

  const header = document.createElement("div");
  header.className = "person-header";

  const img = document.createElement("img");
  img.src = `images/portraits/${person.image.file}`;
  img.alt = `${person.name} — ${person.image.caption}`;
  img.onerror = () => {
    const placeholder = document.createElement("div");
    placeholder.className = "image-placeholder";
    placeholder.textContent = "Illustration pending";
    img.replaceWith(placeholder);
  };
  header.appendChild(img);

  const titleBlock = document.createElement("div");
  titleBlock.className = "person-title";

  const h2 = document.createElement("h2");
  h2.textContent = person.name;
  titleBlock.appendChild(h2);

  if (person.alt_names && person.alt_names.length) {
    const alt = document.createElement("div");
    alt.className = "alt-names";
    alt.textContent = `Also called: ${person.alt_names.join(", ")}`;
    titleBlock.appendChild(alt);
  }

  const tags = document.createElement("div");
  tags.className = "tags";
  const testamentBadge = document.createElement("span");
  testamentBadge.className = `badge ${person.testament === "OT" ? "ot" : "nt"}`;
  testamentBadge.textContent = person.testament;
  tags.appendChild(testamentBadge);
  if (person.era) {
    const eraBadge = document.createElement("span");
    eraBadge.className = "badge";
    eraBadge.textContent = person.era;
    tags.appendChild(eraBadge);
  }
  titleBlock.appendChild(tags);

  const reviewP = document.createElement("p");
  reviewP.appendChild(reviewBadge(person.review));
  titleBlock.appendChild(reviewP);

  header.appendChild(titleBlock);
  main.appendChild(header);

  if (person.source_summary) {
    const summary = document.createElement("p");
    summary.textContent = person.source_summary;
    main.appendChild(summary);
  }

  if (person.family_friendly_summary) {
    const kidBox = document.createElement("div");
    kidBox.className = "family-friendly";
    const label = document.createElement("span");
    label.className = "family-friendly-label";
    label.textContent = "For younger readers";
    const text = document.createElement("p");
    text.textContent = person.family_friendly_summary;
    kidBox.appendChild(label);
    kidBox.appendChild(text);
    main.appendChild(kidBox);
  }

  if (person.interpretive_dispute && person.interpretive_note) {
    const note = document.createElement("div");
    note.className = "interpretive-note";
    note.textContent = `Interpretive note: ${person.interpretive_note}`;
    main.appendChild(note);
  }

  const storySection = document.createElement("section");
  storySection.className = "story";

  const h3adult = document.createElement("h3");
  h3adult.textContent = "Life Story";
  storySection.appendChild(h3adult);
  const pAdult = document.createElement("p");
  pAdult.textContent = person.adult_story;
  storySection.appendChild(pAdult);

  const h3family = document.createElement("h3");
  h3family.textContent = "Family";
  storySection.appendChild(h3family);
  const pFamily = document.createElement("p");
  pFamily.textContent = person.family_story;
  storySection.appendChild(pFamily);

  main.appendChild(storySection);

  if (person.references && person.references.length) {
    main.appendChild(referencesList(person.references));
  }

  const genSection = document.createElement("section");
  const h3gen = document.createElement("h3");
  h3gen.textContent = "Genealogy";
  genSection.appendChild(h3gen);
  const genGrid = document.createElement("div");
  genGrid.className = "genealogy-grid";
  genGrid.appendChild(genealogyBlock("Father", person.genealogy.father, index));
  genGrid.appendChild(genealogyBlock("Mother", person.genealogy.mother, index));
  genGrid.appendChild(genealogyBlock("Spouse(s)", person.genealogy.spouses, index));
  genGrid.appendChild(genealogyBlock("Children", person.genealogy.children, index));
  genSection.appendChild(genGrid);
  main.appendChild(genSection);

  const related = connections.edges.filter(
    (e) => e.from === person.person_id || e.to === person.person_id
  );
  if (related.length) {
    const connSection = document.createElement("section");
    const h3conn = document.createElement("h3");
    h3conn.textContent = "Connections";
    connSection.appendChild(h3conn);
    const ul = document.createElement("ul");
    ul.className = "connections-list";
    for (const edge of related) {
      const otherId = edge.from === person.person_id ? edge.to : edge.from;
      const li = document.createElement("li");
      const otherName = nameForId(index, otherId);
      const label =
        edge.from === person.person_id
          ? `${edge.type} → ${otherName}`
          : `${otherName} → ${edge.type}`;
      li.textContent = `${label}: ${edge.note}`;
      ul.appendChild(li);
    }
    connSection.appendChild(ul);
    main.appendChild(connSection);
  }
}

function renderStubPerson(person, index) {
  const main = document.getElementById("person-main");
  main.innerHTML = "";

  const h2 = document.createElement("h2");
  h2.textContent = person.name;
  main.appendChild(h2);

  if (person.alt_names && person.alt_names.length) {
    const alt = document.createElement("div");
    alt.className = "alt-names";
    alt.textContent = `Also called: ${person.alt_names.join(", ")}`;
    main.appendChild(alt);
  }

  const notice = document.createElement("div");
  notice.className = "stub-notice";
  notice.textContent =
    "This person is named in Scripture without enough narrative to support a full story. This entry exists to keep the genealogy graph complete.";
  main.appendChild(notice);

  if (person.references && person.references.length) {
    main.appendChild(referencesList(person.references));
  }

  const genSection = document.createElement("section");
  const h3gen = document.createElement("h3");
  h3gen.textContent = "Genealogy";
  genSection.appendChild(h3gen);
  const genGrid = document.createElement("div");
  genGrid.className = "genealogy-grid";
  genGrid.appendChild(genealogyBlock("Father", person.genealogy.father, index));
  genGrid.appendChild(genealogyBlock("Mother", person.genealogy.mother, index));
  genGrid.appendChild(genealogyBlock("Spouse(s)", person.genealogy.spouses, index));
  genGrid.appendChild(genealogyBlock("Children", person.genealogy.children, index));
  genSection.appendChild(genGrid);
  main.appendChild(genSection);
}

async function renderPersonPage() {
  const params = new URLSearchParams(window.location.search);
  const id = params.get("id");
  const main = document.getElementById("person-main");

  if (!id) {
    main.innerHTML = "<p>No person specified.</p>";
    return;
  }

  const [person, index, connections] = await Promise.all([
    loadPerson(id),
    loadIndex(),
    loadConnections(),
  ]);

  if (!person) {
    main.innerHTML = "<p>Person not found.</p>";
    return;
  }

  document.title = `${person.name} — Lives of Scripture`;
  const titleTag = document.getElementById("page-title");
  if (titleTag) titleTag.textContent = document.title;

  if (person.tier === "full") {
    await renderFullPerson(person, index, connections);
  } else {
    renderStubPerson(person, index);
  }
}
