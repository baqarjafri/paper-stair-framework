#!/usr/bin/env python3
"""
compute_scores.py — Validate and compute STAIR scores from a filled scoring worksheet.

Reads:
    - data/stair_scoring_worksheet.csv (filled by an assessor, 32 rows with scores 0-4)

Produces:
    - data/scoring_results.json (per-level averages, overall score, sensitivity analysis)
    - Summary statistics printed to stdout

Cross-references:
    Input fed by:
    - data/stair_scoring_template.csv (blank template for assessors)
    - STAIR_SCORING_INSTRUMENT.md (rubric definitions)

    This output feeds into:
    - task3/STAIR_EVALUATION.md (STAIR level-by-level evaluation)
    - task5/fig2_readiness_radar.png (readiness radar chart)
    - task5/fig4_gap_analysis.png (sub-dimension gap analysis)
"""

import argparse
import csv
import json
import sys
from collections import defaultdict
from pathlib import Path


MAX_SCORE = 4
EXPECTED_SUB_DIMENSIONS = 32

# Weighting schemes for sensitivity analysis
WEIGHTING_SCHEMES = {
    "equal": {
        "description": "All five levels weighted equally",
        "weights": {"1": 1.0, "2": 1.0, "3": 1.0, "4": 1.0, "5": 1.0},
    },
    "theoretical_priority": {
        "description": "Higher weight to foundational levels",
        "weights": {"1": 1.5, "2": 1.3, "3": 1.0, "4": 0.8, "5": 0.9},
    },
    "agent_priority": {
        "description": "Higher weight to agent-specific levels",
        "weights": {"1": 0.8, "2": 0.9, "3": 1.5, "4": 1.3, "5": 1.0},
    },
}


def load_worksheet(worksheet_path: Path) -> list:
    """Load and parse the scoring worksheet CSV."""
    if not worksheet_path.exists():
        print(f"ERROR: Scoring worksheet not found: {worksheet_path}")
        print("Create it from data/stair_scoring_template.csv by filling in the 'score' column.")
        sys.exit(1)

    rows = []
    with open(worksheet_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        required_cols = {"level", "sub_dimension_id", "sub_dimension_name", "score"}
        if not required_cols.issubset(set(reader.fieldnames or [])):
            missing = required_cols - set(reader.fieldnames or [])
            print(f"ERROR: Missing required columns: {missing}")
            sys.exit(1)

        for i, row in enumerate(reader, start=2):  # start=2 for header offset
            rows.append(row)

    return rows


def validate_scores(rows: list) -> list:
    """Validate that all scores are integers 0-4. Return list of errors."""
    errors = []
    for i, row in enumerate(rows):
        score_str = row.get("score", "").strip()
        if score_str == "":
            errors.append(
                f"Row {i+1} ({row.get('sub_dimension_id', '?')}): score is empty"
            )
            continue
        try:
            score = int(score_str)
            if score < 0 or score > MAX_SCORE:
                errors.append(
                    f"Row {i+1} ({row['sub_dimension_id']}): "
                    f"score {score} out of range 0-{MAX_SCORE}"
                )
        except ValueError:
            errors.append(
                f"Row {i+1} ({row.get('sub_dimension_id', '?')}): "
                f"score '{score_str}' is not a valid integer"
            )
    return errors


def compute_results(rows: list) -> dict:
    """Compute per-level and overall readiness from validated scores."""
    # Group by level
    levels = defaultdict(list)
    for row in rows:
        level = row["level"].strip()
        score = int(row["score"].strip())
        levels[level].append({
            "id": row["sub_dimension_id"].strip(),
            "name": row["sub_dimension_name"].strip(),
            "score": score,
        })

    level_results = {}
    for level_num in sorted(levels.keys()):
        sub_dims = levels[level_num]
        scores = [sd["score"] for sd in sub_dims]
        n = len(scores)
        mean_score = sum(scores) / n if n > 0 else 0
        readiness_pct = (mean_score / MAX_SCORE) * 100
        has_zero = any(s == 0 for s in scores)
        zero_dims = [sd["id"] for sd in sub_dims if sd["score"] == 0]

        # Minimum threshold rule
        if has_zero and readiness_pct > 60:
            verdict = "Partially Ready (capped: zero sub-dimension present)"
        elif readiness_pct >= 81:
            verdict = "Ready"
        elif readiness_pct >= 61:
            verdict = "Substantially Ready"
        elif readiness_pct >= 31:
            verdict = "Partially Ready"
        elif readiness_pct >= 11:
            verdict = "Nascent"
        else:
            verdict = "Absent"

        level_results[level_num] = {
            "num_sub_dimensions": n,
            "scores": scores,
            "mean_score": round(mean_score, 3),
            "readiness_pct": round(readiness_pct, 1),
            "has_zero": has_zero,
            "zero_dimensions": zero_dims,
            "verdict": verdict,
            "sub_dimensions": sub_dims,
        }

    # Sensitivity analysis
    sensitivity = {}
    for scheme_name, scheme in WEIGHTING_SCHEMES.items():
        total_weighted = 0.0
        total_weight = 0.0
        for level_num, result in level_results.items():
            w = scheme["weights"].get(level_num, 1.0)
            total_weighted += result["readiness_pct"] * w
            total_weight += w
        overall = round(total_weighted / total_weight, 1) if total_weight > 0 else 0.0
        sensitivity[scheme_name] = {
            "description": scheme["description"],
            "overall_readiness_pct": overall,
        }

    return {
        "total_sub_dimensions": len(rows),
        "level_results": level_results,
        "sensitivity_analysis": sensitivity,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Validate and compute STAIR scores from a filled scoring worksheet."
    )
    parser.add_argument(
        "-i", "--input",
        default=None,
        help="Path to filled scoring worksheet CSV (default: data/stair_scoring_worksheet.csv)",
    )
    parser.add_argument(
        "-o", "--output",
        default=None,
        help="Output JSON path (default: data/scoring_results.json)",
    )
    args = parser.parse_args()

    # Resolve paths
    script_dir = Path(__file__).resolve().parent
    project_dir = script_dir.parent
    data_dir = project_dir / "data"

    input_path = Path(args.input) if args.input else data_dir / "stair_scoring_worksheet.csv"
    output_path = Path(args.output) if args.output else data_dir / "scoring_results.json"

    print("STAIR Scoring Worksheet Processor")
    print("=" * 50)
    print(f"Input:  {input_path}")
    print(f"Output: {output_path}")
    print()

    # Load and validate
    rows = load_worksheet(input_path)
    print(f"Loaded {len(rows)} sub-dimension rows")

    if len(rows) != EXPECTED_SUB_DIMENSIONS:
        print(
            f"WARNING: Expected {EXPECTED_SUB_DIMENSIONS} sub-dimensions, "
            f"found {len(rows)}"
        )

    errors = validate_scores(rows)
    if errors:
        print(f"\nERROR: {len(errors)} validation error(s):")
        for err in errors:
            print(f"  - {err}")
        sys.exit(1)

    print("All scores validated (0-4 range).")
    print()

    # Compute
    results = compute_results(rows)

    # Print summary
    print("=== Per-Level Readiness ===")
    print(f"{'Level':<10} {'SubDims':>8} {'Mean':>6} {'Readiness':>10}  {'Verdict'}")
    print("-" * 70)
    for level_num in sorted(results["level_results"].keys()):
        r = results["level_results"][level_num]
        print(
            f"  L{level_num:<7} {r['num_sub_dimensions']:>8} "
            f"{r['mean_score']:>6.2f} "
            f"{r['readiness_pct']:>9.1f}%  "
            f"{r['verdict']}"
        )
        if r["zero_dimensions"]:
            print(f"           Zero: {', '.join(r['zero_dimensions'])}")
    print()

    print("=== Sensitivity Analysis ===")
    for scheme_name, scheme in results["sensitivity_analysis"].items():
        print(f"  {scheme_name:.<35} {scheme['overall_readiness_pct']:>6.1f}%")
    print()

    # Write output
    data_dir.mkdir(exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"Wrote results to: {output_path}")
    print()

    # Cross-reference
    print("=== Cross-Reference ===")
    print("Input fed by:")
    print("  - data/stair_scoring_template.csv (blank template)")
    print("  - STAIR_SCORING_INSTRUMENT.md (rubric definitions)")
    print()
    print("This output feeds into:")
    print("  - task3/STAIR_EVALUATION.md (STAIR level-by-level evaluation)")
    print("  - task5/fig2_readiness_radar.png (readiness radar chart)")
    print("  - task5/fig4_gap_analysis.png (sub-dimension gap analysis)")
    print()
    print(f"Output file: {output_path}")


if __name__ == "__main__":
    main()
