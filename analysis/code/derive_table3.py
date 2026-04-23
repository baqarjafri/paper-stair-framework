#!/usr/bin/env python3
"""
derive_table3.py — Derives Table 3 (consolidated 5x5 scoring matrix) from
the 32 raw sub-dimension scores in moodle_scores.json.

This script implements the documented mapping from raw sub-dimensions to the
five consolidated dimensions (COV, ACC, EDU, TMP, INT) used in the paper.

Mapping logic:
    Each raw sub-dimension is assigned to one or two consolidated dimensions
    based on which aspect of platform readiness it primarily measures.
    When a sub-dimension spans two consolidated dimensions, it contributes
    to both with equal weight (0.5 each).

    Raw scores (0-4) are converted to the rubric percentage scale:
        0 = Absent    =>   0%
        1 = Nascent   =>  25%
        2 = Partial   =>  50%
        3 = Substantial => 75%
        4 = Ready     => 100%

    Each consolidated cell is the weighted average of its contributing
    raw sub-dimensions on this percentage scale.

Usage:
    python derive_table3.py
    python derive_table3.py --output data/table3_derived.json

Cross-references:
    Input:  data/moodle_scores.json (32 raw sub-dimension scores)
    Map:    data/scoring_provenance.json (full evidence mapping)
    Output: data/table3_derived.json (derived Table 3 scores)
    Paper:  Table 3 in create_draft_v11.js
"""

import json
import sys
from pathlib import Path

RUBRIC = {0: 0, 1: 25, 2: 50, 3: 75, 4: 100}

# Mapping: consolidated_dim -> list of (raw_sub_id, weight)
# Each raw sub-dimension is assigned to the consolidated dimension(s) it measures
MAPPING = {
    "L1_Event_Sensing": {
        "COV": [("1.1_Event_Coverage", 1.0)],
        "ACC": [("1.2_Observer_Subscription", 1.0)],
        "EDU": [("1.3_SRL_Phase_Observability", 1.0)],
        "TMP": [("1.4_Real_Time_External_Access", 1.0)],
        "INT": [("1.5_Event_Enrichment", 1.0)],
    },
    "L2_Student_State": {
        "COV": [("2.1_Raw_Data_Availability", 0.5), ("2.2_Analytics_Framework", 0.5)],
        "ACC": [("2.4_API_Query_Capability", 1.0)],
        "EDU": [("2.3_Unified_Learner_Model", 1.0)],
        "TMP": [("2.5_Temporal_Analytics", 1.0)],
        "INT": [("2.6_Privacy_Aware_Access", 0.5), ("2.3_Unified_Learner_Model", 0.5)],
    },
    "L3_Agent_Reasoning": {
        "COV": [("3.1_AI_Subsystem_Infrastructure", 1.0)],
        "ACC": [("3.5_Write_Back_Capability", 1.0)],
        "EDU": [("3.2_Agent_Identity_Model", 0.5), ("3.3_Reasoning_Pipeline", 0.5)],
        "TMP": [("3.6_SRL_Detection_Logic", 0.5), ("3.7_Contextual_Adaptation", 0.5)],
        "INT": [("3.4_AI_Analytics_Bridge", 1.0)],
    },
    "L4_Orchestration": {
        "COV": [("4.1_Agent_Registry", 1.0)],
        "ACC": [("4.2_Shared_State_Store", 1.0)],
        "EDU": [("4.3_Coordination_Protocol", 0.5), ("4.4_Conflict_Resolution", 0.5)],
        "TMP": [("4.3_Coordination_Protocol", 0.5), ("4.4_Conflict_Resolution", 0.5)],
        "INT": [("4.5_Scalability_Architecture", 1.0)],
    },
    "L5_Intervention_Delivery": {
        "COV": [("5.1_Message_Delivery", 0.5), ("5.3_Content_Generation", 0.5)],
        "ACC": [("5.2_UI_Injection", 1.0)],
        "EDU": [("5.4_Feedback_Loop", 0.5), ("5.5_Timing_Intelligence", 0.5)],
        "TMP": [("5.5_Timing_Intelligence", 1.0)],
        "INT": [("5.4_Feedback_Loop", 1.0)],
    },
}

DIMS = ["COV", "ACC", "EDU", "TMP", "INT"]
LEVELS = ["L1_Event_Sensing", "L2_Student_State", "L3_Agent_Reasoning",
          "L4_Orchestration", "L5_Intervention_Delivery"]
LEVEL_SHORT = {"L1_Event_Sensing": "L1", "L2_Student_State": "L2",
               "L3_Agent_Reasoning": "L3", "L4_Orchestration": "L4",
               "L5_Intervention_Delivery": "L5"}


def load_raw_scores(path: Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    scores = {}
    for level_key, level_data in data["levels"].items():
        for sub_id, sub_data in level_data["sub_dimensions"].items():
            scores[sub_id] = sub_data["score"]
    return scores


def derive_table3(raw_scores: dict) -> dict:
    """Derive the 5x5 Table 3 from raw sub-dimension scores."""
    table = {}
    for level in LEVELS:
        row = {}
        for dim in DIMS:
            sources = MAPPING[level][dim]
            weighted_sum = 0.0
            weight_sum = 0.0
            for sub_id, weight in sources:
                raw = raw_scores[sub_id]
                pct = RUBRIC[raw]
                weighted_sum += pct * weight
                weight_sum += weight
            cell_score = round(weighted_sum / weight_sum) if weight_sum > 0 else 0
            row[dim] = cell_score
        row["avg"] = round(sum(row[d] for d in DIMS) / len(DIMS))
        table[LEVEL_SHORT[level]] = row
    return table


def print_table(table: dict):
    header = f"{'Level':<5} {'COV':>5} {'ACC':>5} {'EDU':>5} {'TMP':>5} {'INT':>5} {'Avg':>5}"
    print(header)
    print("-" * len(header))
    for level in ["L1", "L2", "L3", "L4", "L5"]:
        row = table[level]
        print(f"{level:<5} {row['COV']:>5} {row['ACC']:>5} {row['EDU']:>5} "
              f"{row['TMP']:>5} {row['INT']:>5} {row['avg']:>4}%")


def main():
    base = Path(__file__).resolve().parent.parent / "data"
    scores_path = base / "moodle_scores.json"

    if not scores_path.exists():
        print(f"ERROR: {scores_path} not found")
        sys.exit(1)

    raw_scores = load_raw_scores(scores_path)
    table = derive_table3(raw_scores)

    print("=" * 50)
    print("STAIR Table 3: Derived from Raw Sub-Dimensions")
    print("=" * 50)
    print()
    print_table(table)
    print()

    # Show mapping detail
    print("MAPPING DETAIL:")
    print("-" * 70)
    for level in LEVELS:
        short = LEVEL_SHORT[level]
        print(f"\n{short} ({level}):")
        for dim in DIMS:
            sources = MAPPING[level][dim]
            parts = []
            for sub_id, weight in sources:
                raw = raw_scores[sub_id]
                pct = RUBRIC[raw]
                parts.append(f"{sub_id}(raw={raw}=>{pct}%,w={weight})")
            cell = table[short][dim]
            print(f"  {dim} = {cell:>3}  <- {' + '.join(parts)}")

    # Save output
    output_path = base / "table3_derived.json"
    if "--output" in sys.argv:
        idx = sys.argv.index("--output")
        if idx + 1 < len(sys.argv):
            output_path = Path(sys.argv[idx + 1])

    output = {
        "_meta": {
            "description": "Table 3 scores derived from raw sub-dimensions via documented mapping",
            "source": "moodle_scores.json",
            "script": "code/derive_table3.py",
            "rubric": "0=0%, 1=25%, 2=50%, 3=75%, 4=100%",
        },
        "table3": table,
        "mapping": {LEVEL_SHORT[lv]: {d: MAPPING[lv][d] for d in DIMS} for lv in LEVELS},
    }
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)
    print(f"\nSaved: {output_path}")


if __name__ == "__main__":
    main()
