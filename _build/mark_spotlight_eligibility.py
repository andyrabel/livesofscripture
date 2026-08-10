#!/usr/bin/env python3
"""One-time pass: mark full-tier people who are real (Scripture narrates
*something* about them, so they correctly hold full tier per CLAUDE.md's
promotion rule) but too minor to put in front of every visitor as "the"
featured person — the home page spotlight (`js/app.js`'s
`renderHomeSpotlight`) and the daily Facebook/Instagram post
(`_build/fb/selector.py`).

This does NOT touch `tier` (full tier is about narrative substance existing
at all, which is real for everyone below) or `devotionals` eligibility
(already gated separately, see feedback-devotionals-eligibility memory).
It's a new, orthogonal field: can this person carry a whole public post by
themselves, not just "is there a paragraph about them."

`spotlight_eligible: false` is stored ONLY on the ~113 excluded people
(sparse-storage convention, like other bool+note pairs in this schema) --
absence of the field means eligible. A short `spotlight_note` records why,
for the next person auditing this list.

Candidates were selected in two groups:
1. NON_NARRATED -- symbolic/apocalyptic figures or a dynastic title, not
   real narrated individuals (already excluded from `devotionals` for the
   same underlying reason, see the "Not real human individuals" note in
   task-add-devotionals-field memory).
2. LIST_ONLY -- named only inside a genealogy/list/casualty-roll with zero
   independent word or action of their own (the "too thin" subset of the
   same 44 devotionals-excluded people -- deliberately excludes that list's
   other 9 people, who were skipped for a *different* reason, sensitive
   content, and are NOT minor: cozbi, hamor, heber-2, jonadab, jehozabad,
   shechem, menachem, menahem, jesus).
3. THIN_EPISODE -- full-tier people who DO have devotionals (cleared the
   "major" bar) but scored lowest on a mechanical proxy for spotlight
   weight: exactly 1 devotional phrase, <=2 references, and a sub-median
   adult_story word count. Auto-generated then hand-checked against the
   full list for well-known names wrongly caught by the metric -- `jael`
   (Judges 4, the Sisera killer praised in Deborah's Song) was the one
   removed; everyone else held up on inspection (e.g. `mishael` here is
   the Levite cousin of Moses, not Daniel's companion Meshach; `deborah`
   here is Rebekah's nurse of Genesis 35:8, not the judge).

Re-run is safe (idempotent) but there's no reason to -- this was a single
editorial pass, not a recomputed metric like era inference. Extending the
list later should edit PEOPLE below directly rather than re-deriving it.
"""
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PEOPLE_DIR = REPO_ROOT / "data" / "people"
INDEX_PATH = REPO_ROOT / "data" / "people.json"

NON_NARRATED = {
    "abaddon", "legion", "gog-2", "candace",
}
LIST_ONLY = {
    "abdon", "adriel", "ahuzzath", "amon", "amraphel", "aretas", "argob",
    "arieh", "arioch", "azrikam-4", "birsha", "blastus", "calcol", "darda",
    "elkanah-8", "erastus", "gershom", "gilead-2", "heman", "horam",
    "hur-2", "ira", "jobab-3", "jonathan-9", "malchi-shua", "mary-5",
    "osnappar", "shelumiel", "shemer", "tibni",
}
THIN_EPISODE = {
    "elon", "segub", "elon-3", "seraiah-9", "shabbethai", "sephatiah",
    "saph", "persis", "ibzan", "irijah", "rezon", "epanetus", "eliezer-6",
    "mattan", "peninnah", "sargon", "forunatus", "eunice", "ahab-2",
    "judas-5", "parmenas", "elah-2", "lois", "archippus", "mnason",
    "prochorus", "adrammelech", "eleazar-3", "ahiman", "deborah",
    "phygelus", "amasiah", "jarib", "achaicus", "dionysius", "jehucal",
    "joram", "jozacar", "lamech", "adoni-bezek", "iddo-6", "jezrahiah",
    "palti-2", "rechab", "shallum", "ishbi-benob", "jether", "jezreel-2",
    "mishael", "azariah-8", "mithredath", "seraiah-10", "shimshai",
    "jaazaniah-3", "micaiah-6", "chilion", "jucal", "nethanel-6",
    "drusilla", "medad", "michael-7", "bigthan", "jehiel-3", "antipas",
    "geshem", "hanamel", "jair-2", "jannes", "mamre", "shethar-bozenai",
    "baanah", "jehosheba", "nobah", "rehum-2", "shemeber", "chenaniah",
    "joah-2", "bidkar",
}

REASON = {
    "non-narrated": "symbolic/apocalyptic figure or dynastic title, not a narrated individual",
    "list-only": "named only in a genealogy/list/casualty-roll, with no independent word or action of their own",
    "thin-episode": "a single brief episode with minimal narrative weight",
}


def group_for(person_id: str) -> str:
    if person_id in NON_NARRATED:
        return "non-narrated"
    if person_id in LIST_ONLY:
        return "list-only"
    return "thin-episode"


def main() -> None:
    all_ids = NON_NARRATED | LIST_ONLY | THIN_EPISODE
    assert len(all_ids) == len(NON_NARRATED) + len(LIST_ONLY) + len(THIN_EPISODE), "overlap between groups"

    updated_files = 0
    for person_id in sorted(all_ids):
        path = PEOPLE_DIR / f"{person_id}.json"
        person = json.loads(path.read_text(encoding="utf-8"))
        if person.get("tier") != "full":
            raise SystemExit(f"{person_id} is not full-tier -- list is stale, check by hand")
        person["spotlight_eligible"] = False
        person["spotlight_note"] = REASON[group_for(person_id)]
        path.write_text(json.dumps(person, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        updated_files += 1

    index = json.loads(INDEX_PATH.read_text(encoding="utf-8"))
    updated_index = 0
    for entry in index:
        if entry["person_id"] in all_ids:
            entry["spotlight_eligible"] = False
            updated_index += 1
    INDEX_PATH.write_text(json.dumps(index, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"person files updated: {updated_files}")
    print(f"index entries updated: {updated_index}")
    print(f"  non-narrated: {len(NON_NARRATED)}")
    print(f"  list-only:    {len(LIST_ONLY)}")
    print(f"  thin-episode: {len(THIN_EPISODE)}")
    print(f"  total:        {len(all_ids)}")


if __name__ == "__main__":
    main()
