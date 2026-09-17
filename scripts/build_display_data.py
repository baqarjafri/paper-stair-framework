#!/usr/bin/env python3
"""Generate docs/assets/site-data.js (window.STAIR_DATA) from analysis/data/*.json.

Sources of truth: table3_derived.json (level and dimension scores), moodle_scores.json
(28 raw scores and evidence), sub_dimension_definitions.json (definitions, rubric, grounding),
paper_claims.json (headline counts). scoring_provenance.json is deliberately NOT read: two of
its per-cell "score" fields are stale (L2 INT 25, L5 EDU 0) relative to Table 3.

Regenerate after any data change, then commit the output:
    python scripts/build_display_data.py
Check that the committed output is still in sync (exit 1 on drift):
    python scripts/build_display_data.py --check

The page copy that is not in the data files (each level's verb, components, Table 1
requirement and the three Figure 2 grounding constructs, stored as `constructs`) lives
in LEVEL_COPY below, so the whole page vocabulary has one source.
"""
import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "analysis" / "data"
OUT = ROOT / "docs" / "assets" / "site-data.js"

LEVEL_KEYS = ["L1_Event_Sensing", "L2_Student_State", "L3_Agent_Reasoning",
              "L4_Orchestration", "L5_Intervention_Delivery"]
DIM_ORDER = ["COV", "ACC", "EDU", "TMP", "INT"]
DIM_NAMES = {
    "COV": "Coverage and classification",
    "ACC": "External accessibility",
    "EDU": "Educational specificity",
    "TMP": "Temporal availability",
    "INT": "Cross-subsystem integration",
}
LEVEL_COPY = {
    "L1": {"verb": "Sense",
           "components": "Event broker \u00b7 Real-time stream \u00b7 Pedagogical event schema",
           "requirement": "Platform emits structured, pedagogically classified learner events accessible to AI consumers.",
           "constructs": {"Z": "Self-observation", "T": "Event sensing layer", "H": "Contextual input"}},
    "L2": {"verb": "Remember",
           "components": "Learner model \u00b7 Analytics API \u00b7 Temporal reasoning",
           "requirement": "Platform maintains a persistent, queryable model of each learner's cumulative progress, performance, and risk status.",
           "constructs": {"Z": "Self-judgment", "T": "Knowledge representation", "H": "Memory (short and long-term)"}},
    "L3": {"verb": "Reason",
           "components": "AI subsystem \u00b7 Reasoning pipeline \u00b7 SRL detection",
           "requirement": "Platform supports autonomous AI deliberation over student state, with platform-enforced pedagogical guardrails.",
           "constructs": {"Z": "Strategic planning", "T": "Agent reasoning loop", "H": "Planning and goal decomposition"}},
    "L4": {"verb": "Coordinate",
           "components": "Agent registry \u00b7 Shared state \u00b7 Conflict resolution",
           "requirement": "Platform coordinates concurrent AI agents sharing student context, with conflict resolution and load management.",
           "constructs": {"Z": "Metacognitive monitoring", "T": "Multi-agent coordination", "H": "Multi-agent communication"}},
    "L5": {"verb": "Reach",
           "components": "Message delivery \u00b7 UI injection \u00b7 Feedback loop",
           "requirement": "Platform delivers context-aware, timely agent interventions embedded within the flow of learning activity.",
           "constructs": {"Z": "Adaptive self-reactions", "T": "Delivery mechanism", "H": "Personalisation and real-time adaptation"}},
}
RUBRIC_LABEL = {0: "Absent", 1: "Nascent", 2: "Partial", 3: "Substantial", 4: "Ready"}


def clean(text: str) -> str:
    """Page copy carries no em-dashes: an em-dash becomes a middle dot separator,
    the data files' ' -- ' becomes a colon."""
    text = re.sub(r"\s*\u2014\s*", " \u00b7 ", text)
    return re.sub(r"\s+--\s+", ": ", text)


def band(score: int) -> str:
    return "ready" if score >= 40 else ("limited" if score >= 20 else "critical")


def load(name: str) -> dict:
    return json.loads((DATA / name).read_text(encoding="utf-8"))


def build() -> dict:
    scores = load("moodle_scores.json")
    defs_file = load("sub_dimension_definitions.json")
    defs = defs_file["sub_dimensions"]
    table3 = load("table3_derived.json")["table3"]
    claims_file = load("paper_claims.json")
    claims = {c["id"]: c["expected"] for c in claims_file["claims"]}
    m = re.search(r"(Moodle \S+) \(Build:?\s*(\d+)\)", scores["_meta"]["description"])
    if not m:
        raise ValueError("moodle_scores.json _meta.description lacks 'Moodle <version> (Build: <n>)': "
                         + scores["_meta"]["description"])
    platform, build_no = m.group(1), m.group(2)

    levels, subs = [], {}
    for key in LEVEL_KEYS:
        lid = key[:2]
        lv = scores["levels"][key]
        row = table3[lid]
        if claims[f"{lid}_readiness"] != row["avg"]:
            raise ValueError(f"{lid}: paper_claims.json says {claims[f'{lid}_readiness']}, "
                             f"table3_derived.json says {row['avg']}")
        sub_ids = list(lv["sub_dimensions"].keys())
        for sid in sub_ids:
            s = lv["sub_dimensions"][sid]
            d = defs[sid]
            if d["level"] != lid:
                raise ValueError(f"{sid}: definitions file says level {d['level']}, "
                                 f"scores file places it under {lid}")
            subs[sid] = {
                "id": sid, "level": lid, "name": clean(d["name"]), "score": s["score"],
                "label": RUBRIC_LABEL[s["score"]], "pct": s["score"] * 25,
                "evidence": clean(s["evidence"]), "definition": clean(d["definition"]),
                "grounding": d["grounding"],
            }
        copy = dict(LEVEL_COPY[lid])
        levels.append({
            "id": lid, "key": key, "long": key[3:].replace("_", " "),
            **copy,
            "score": row["avg"], "band": band(row["avg"]),
            "dims": {dim: row[dim] for dim in DIM_ORDER},
            "subs": sub_ids,
        })

    orphans = sorted(set(defs) - set(subs))
    if orphans:
        raise ValueError(f"definitions without scores: {orphans}")

    return {
        "platform": platform, "build": build_no,
        "levels": levels, "subs": subs, "dims": DIM_NAMES,
        "rubric": {k: clean(v) for k, v in defs_file["_meta"]["rubric_scale"].items()},
        "grounding": {k: clean(v) for k, v in defs_file["_meta"]["grounding_codes"].items()},
        "claims": {
            "cliff": claims["L2_to_L3_cliff"],
            "ai_refs_analytics": claims["ai_refs_analytics_count"],
            "analytics_refs_ai": claims["analytics_refs_ai_count"],
            "web_services": claims["web_services_count"],
            "ai_providers": claims["ai_providers_count"],
            "ai_actions": claims["ai_actions_count"],
            "analytics_targets": claims["analytics_targets_count"],
            "claims_total": len(claims_file["claims"]),
        },
    }


def render(data: dict) -> str:
    return ("// Generated by scripts/build_display_data.py from analysis/data/*.json. Do not edit by hand.\n"
            "window.STAIR_DATA = " + json.dumps(data, indent=1, ensure_ascii=False) + ";\n")


def in_sync() -> bool:
    """True when docs/assets/site-data.js equals a fresh build from analysis/data."""
    return OUT.exists() and OUT.read_text(encoding="utf-8") == render(build())


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Generate docs/assets/site-data.js from analysis/data.")
    parser.add_argument("--check", action="store_true",
                        help="report whether the committed file is in sync (exit 1 on drift) instead of writing")
    args = parser.parse_args(argv)
    rel = OUT.relative_to(ROOT).as_posix() if ROOT in OUT.parents else str(OUT)
    if args.check:
        if not OUT.exists():
            print(f"MISSING: {rel}. Run: python scripts/build_display_data.py")
            return 1
        if not in_sync():
            print(f"DRIFT: {rel} is out of date. Run: python scripts/build_display_data.py")
            return 1
        print(f"OK: {rel} matches analysis/data")
        return 0
    text = render(build())
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(text, encoding="utf-8", newline="\n")
    print(f"wrote {rel} ({len(text)} chars)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
