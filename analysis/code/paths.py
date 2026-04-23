"""Central path resolver for the STAIR reproduction bundle.

All analysis scripts should import the paths they need from here rather than
computing their own relative paths. This makes the bundle portable — if a user
moves the repo somewhere unexpected, paths are still resolved from the known
layout of the repository root.

Repository layout assumed (with this file at REPO_ROOT/analysis/code/paths.py):

    REPO_ROOT/
    ├── analysis/
    │   ├── code/
    │   │   └── paths.py           ← this file
    │   ├── data/
    │   ├── instruments/
    │   └── outputs/               ← created on demand
    ├── moodle_src/                ← fetched by scripts/fetch_moodle.*
    └── figures/                   ← existing PNG set, NOT overwritten
"""

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
ANALYSIS_DIR = REPO_ROOT / "analysis"
CODE_DIR = ANALYSIS_DIR / "code"
DATA_DIR = ANALYSIS_DIR / "data"
INSTRUMENTS_DIR = ANALYSIS_DIR / "instruments"
OUTPUTS_DIR = ANALYSIS_DIR / "outputs"
OUTPUT_FIGURES_DIR = OUTPUTS_DIR / "figures"

MOODLE_SRC = REPO_ROOT / "moodle_src"
PAPER_FIGURES_DIR = REPO_ROOT / "figures"
PAPER_DIR = REPO_ROOT / "paper"

# Key data files
MOODLE_SCORES_JSON = DATA_DIR / "moodle_scores.json"
TABLE3_DERIVED_JSON = DATA_DIR / "table3_derived.json"
ARCHITECTURE_SUMMARY_JSON = DATA_DIR / "architecture_summary.json"
PAPER_CLAIMS_JSON = DATA_DIR / "paper_claims.json"

# Output files (regenerated each run)
STAIR_SCORES_OUTPUT = OUTPUTS_DIR / "stair_scores_output.json"


def ensure_outputs_dir() -> Path:
    """Create outputs directory if it doesn't exist."""
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    return OUTPUTS_DIR


__all__ = [
    "REPO_ROOT", "ANALYSIS_DIR", "CODE_DIR", "DATA_DIR",
    "INSTRUMENTS_DIR", "OUTPUTS_DIR", "OUTPUT_FIGURES_DIR",
    "MOODLE_SRC", "PAPER_FIGURES_DIR", "PAPER_DIR",
    "MOODLE_SCORES_JSON", "TABLE3_DERIVED_JSON",
    "ARCHITECTURE_SUMMARY_JSON", "PAPER_CLAIMS_JSON",
    "STAIR_SCORES_OUTPUT", "ensure_outputs_dir",
]
