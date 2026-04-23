#!/usr/bin/env python3
"""
score_stair.py — Compute STAIR readiness scores under multiple weighting schemes.

Reads:
    - data/moodle_scores.json (sub-dimension scores on a 0-4 ordinal scale)

Produces:
    - data/stair_scores_output.json (level-wise and overall readiness percentages
      under three weighting schemes)

Cross-references:
    This output feeds into:
    - task3/STAIR_EVALUATION.md (STAIR level-by-level evaluation)
    - task5/fig2_readiness_radar.png (readiness radar chart)
    - task5/fig4_gap_analysis.png (sub-dimension gap analysis)
"""

import argparse
import json
import sys
from pathlib import Path


# Three weighting schemes for sensitivity analysis
# Weights are per-level multipliers (L1 through L5)
WEIGHTING_SCHEMES = {
    "equal": {
        "description": "All five levels weighted equally",
        "weights": [1.0, 1.0, 1.0, 1.0, 1.0],
    },
    "theoretical_priority": {
        "description": "Higher weight to foundational levels (event sensing, student state)",
        "weights": [1.5, 1.3, 1.0, 0.8, 0.9],
    },
    "agent_priority": {
        "description": "Higher weight to agent-specific levels (reasoning, orchestration)",
        "weights": [0.8, 0.9, 1.5, 1.3, 1.0],
    },
}

MAX_SCORE = 4  # Maximum score per sub-dimension


def load_scores(scores_path: Path) -> dict:
    """Load the sub-dimension scores from JSON."""
    if not scores_path.exists():
        print(f"ERROR: Scores file not found: {scores_path}")
        print("Ensure data/moodle_scores.json exists with the sub-dimension scores.")
        sys.exit(1)

    with open(scores_path, "r", encoding="utf-8") as f:
        return json.load(f)


def compute_level_readiness(level_name: str, level_data: dict) -> dict:
    """Compute readiness percentage and stats for a single STAIR level.

    Handles both list-based and dict-based sub_dimensions formats:
      List: [{"id": "1.1", "score": 3}, ...]
      Dict: {"1.1_Name": {"score": 3, "evidence": "..."}, ...}
    """
    sub_dims_raw = level_data["sub_dimensions"]

    # Normalize to list of (id, score) tuples
    if isinstance(sub_dims_raw, dict):
        scores = [v["score"] for v in sub_dims_raw.values()]
        ids = list(sub_dims_raw.keys())
    else:
        scores = [sd["score"] for sd in sub_dims_raw]
        ids = [sd.get("id", str(i)) for i, sd in enumerate(sub_dims_raw)]

    n = len(scores)
    mean_score = sum(scores) / n if n > 0 else 0
    readiness_pct = (mean_score / MAX_SCORE) * 100

    # Minimum threshold rule: if any sub-dimension = 0, note it
    has_zero = any(s == 0 for s in scores)
    zero_dims = [ids[i] for i, s in enumerate(scores) if s == 0]

    # Extract level ID from name (e.g., "L1_Event_Sensing" → 1)
    import re as _re
    level_id_match = _re.search(r'L(\d)', level_name)
    level_id = int(level_id_match.group(1)) if level_id_match else 0

    return {
        "level_id": level_id,
        "level_name": level_name,
        "num_sub_dimensions": n,
        "scores": scores,
        "mean_score": round(mean_score, 3),
        "readiness_pct": round(readiness_pct, 1),
        "has_zero_subdim": has_zero,
        "zero_subdimensions": zero_dims,
        "verdict": _verdict(readiness_pct, has_zero),
    }


def _verdict(pct: float, has_zero: bool) -> str:
    """Determine readiness verdict, applying minimum threshold rule."""
    if has_zero:
        # Cap at Partially Ready if any sub-dimension is absent
        if pct >= 61:
            return "Partially Ready (capped: zero sub-dimension)"
        elif pct >= 31:
            return "Partially Ready"
        elif pct >= 11:
            return "Nascent"
        else:
            return "Absent"
    else:
        if pct >= 81:
            return "Ready"
        elif pct >= 61:
            return "Substantially Ready"
        elif pct >= 31:
            return "Partially Ready"
        elif pct >= 11:
            return "Nascent"
        else:
            return "Absent"


def compute_weighted_overall(level_results: list, weights: list) -> float:
    """Compute weighted overall readiness percentage."""
    total_weighted = 0.0
    total_weight = 0.0
    for result, weight in zip(level_results, weights):
        total_weighted += result["readiness_pct"] * weight
        total_weight += weight
    return round(total_weighted / total_weight, 1) if total_weight > 0 else 0.0


def main():
    parser = argparse.ArgumentParser(
        description="Compute STAIR readiness scores under multiple weighting schemes."
    )
    parser.add_argument(
        "-i", "--input",
        default=None,
        help="Path to moodle_scores.json (default: data/moodle_scores.json)",
    )
    parser.add_argument(
        "-o", "--output",
        default=None,
        help="Output JSON path (default: data/stair_scores_output.json)",
    )
    args = parser.parse_args()

    # Resolve paths
    script_dir = Path(__file__).resolve().parent
    project_dir = script_dir.parent
    data_dir = project_dir / "data"

    input_path = Path(args.input) if args.input else data_dir / "moodle_scores.json"
    output_path = Path(args.output) if args.output else data_dir / "stair_scores_output.json"

    print("STAIR Readiness Score Calculator")
    print("=" * 50)
    print(f"Input:  {input_path}")
    print(f"Output: {output_path}")
    print()

    scores_data = load_scores(input_path)

    # Compute per-level readiness
    level_results = []
    levels = scores_data["levels"]
    for level_name, level_data in levels.items():
        result = compute_level_readiness(level_name, level_data)
        level_results.append(result)

    # Print per-level results
    print("=== Per-Level Readiness ===")
    print(f"{'Level':<30} {'Score':>8} {'Readiness':>10}  {'Verdict'}")
    print("-" * 80)
    for r in level_results:
        print(
            f"  L{r['level_id']}: {r['level_name']:<23} "
            f"{r['mean_score']:>5.2f}/4  "
            f"{r['readiness_pct']:>7.1f}%   "
            f"{r['verdict']}"
        )
        if r["zero_subdimensions"]:
            print(f"      Zero sub-dimensions: {', '.join(r['zero_subdimensions'])}")
    print()

    # Compute under all weighting schemes
    print("=== Sensitivity Analysis (Weighting Schemes) ===")
    scheme_results = {}
    for scheme_name, scheme in WEIGHTING_SCHEMES.items():
        overall = compute_weighted_overall(level_results, scheme["weights"])
        scheme_results[scheme_name] = {
            "description": scheme["description"],
            "weights": dict(zip(
                [f"L{r['level_id']}" for r in level_results],
                scheme["weights"]
            )),
            "overall_readiness_pct": overall,
        }
        print(f"  {scheme_name:.<35} {overall:>6.1f}%  ({scheme['description']})")
    print()

    # Build output
    output = {
        "metadata": {
            "framework": "STAIR v1.0",
            "platform": scores_data.get("platform", "Moodle"),
            "version": scores_data.get("version", "unknown"),
            "max_score_per_subdim": MAX_SCORE,
        },
        "level_results": level_results,
        "sensitivity_analysis": scheme_results,
    }

    # Write output
    data_dir.mkdir(exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"Wrote results to: {output_path}")
    print()

    # Cross-reference
    print("=== Cross-Reference ===")
    print("This output feeds into:")
    print("  - task3/STAIR_EVALUATION.md (STAIR level-by-level evaluation)")
    print("  - task5/fig2_readiness_radar.png (readiness radar chart)")
    print("  - task5/fig4_gap_analysis.png (sub-dimension gap analysis)")
    print()
    print(f"Output file: {output_path}")


if __name__ == "__main__":
    main()
