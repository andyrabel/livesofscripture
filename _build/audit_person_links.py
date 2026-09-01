#!/usr/bin/env python3
"""Audit what _build/link_person_mentions.py links inside person stories.

Writes two TSVs into _build/ (gitignored working files):

  link_audit_linked.tsv    -- every mention that becomes a link
  link_audit_ambiguous.tsv -- collision mentions left as plain text
                              (candidates for _build/link_overrides.json)

Inspect with grep/sort/awk rather than reading whole, e.g.:
  cut -f4,5 _build/link_audit_linked.tsv | sort | uniq -c | sort -rn | head
  sort _build/link_audit_ambiguous.tsv | uniq -c -f2 | sort -rn | head
"""
import json
from collections import Counter
from pathlib import Path

import link_person_mentions as lpm

ROOT = Path(__file__).resolve().parent.parent


def main():
    index = json.loads((ROOT / "data" / "people.json").read_text())
    connections = json.loads((ROOT / "data" / "connections.json").read_text())
    ctx = lpm.build_context(index, connections)
    name_by_id = {e["person_id"]: e["name"] for e in index}
    tier_by_id = ctx["tier_by_id"]

    linked_rows = []
    ambiguous_rows = []
    reason_counts = Counter()
    per_story_links = Counter()

    for entry in index:
        if entry.get("tier") != "full":
            continue
        pid = entry["person_id"]
        fp_path = ROOT / "data" / "people" / f"{pid}.json"
        if not fp_path.exists():
            continue
        fp = json.loads(fp_path.read_text())
        for field in ("adult_story", "family_friendly_summary"):
            text = fp.get(field) or ""
            protected = [
                (m.start(), m.end())
                for m in lpm._CITATION_RE.finditer(text)
            ]

            def is_protected(pos):
                return any(a <= pos < b for a, b in protected)

            seen_targets = set()
            for m in lpm._CANDIDATE_RE.finditer(text):
                if is_protected(m.start()):
                    continue
                word = m.group(0)
                tgt, reason = lpm.classify(word.lower(), pid, ctx)
                if reason in ("stopword", "no-match", "stub-target", "self"):
                    continue
                if tgt and tgt not in seen_targets:
                    seen_targets.add(tgt)
                    reason_counts[reason] += 1
                    per_story_links[f"{pid}:{field}"] += 1
                    linked_rows.append(
                        f"{pid}\t{name_by_id[pid]}\t{field}\t{word}\t{tgt}\t"
                        f"{name_by_id.get(tgt, tgt)}\t{tier_by_id.get(tgt)}\t{reason}"
                    )
                elif reason == "ambiguous":
                    cands = sorted(
                        ctx["name_index"].get(word.lower(), set()) - {pid}
                    )
                    ambiguous_rows.append(
                        f"{pid}\t{name_by_id[pid]}\t{field}\t{word}\t"
                        + ",".join(f"{c}({tier_by_id.get(c)})" for c in cands)
                    )

    (ROOT / "_build" / "link_audit_linked.tsv").write_text(
        "person_id\tperson\tfield\tword\ttarget_id\ttarget\ttarget_tier\treason\n"
        + "\n".join(linked_rows) + "\n"
    )
    (ROOT / "_build" / "link_audit_ambiguous.tsv").write_text(
        "person_id\tperson\tfield\tword\tcandidates\n"
        + "\n".join(ambiguous_rows) + "\n"
    )

    print("linked mentions:", len(linked_rows))
    for reason, n in reason_counts.most_common():
        print(f"  {reason:12} {n}")
    print("distinct target people linked:",
          len({r.split(chr(9))[4] for r in linked_rows}))
    print("links to stub pages:",
          sum(1 for r in linked_rows if r.split(chr(9))[6] == "stub"))
    print("ambiguous mentions left plain:", len(ambiguous_rows))
    print("stories with >8 links:",
          sum(1 for v in per_story_links.values() if v > 8))
    top = per_story_links.most_common(5)
    print("most-linked story panels:", top)


if __name__ == "__main__":
    main()
