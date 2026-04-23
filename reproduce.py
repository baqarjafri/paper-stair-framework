#!/usr/bin/env python3
"""reproduce.py — one-command reproduction of the STAIR paper's findings.

Run this from the repository root:

    python reproduce.py

What it does, top to bottom:
    1. Verifies your Python environment (version + required packages).
    2. Fetches the pinned Moodle source if you don't already have it.
    3. Re-runs every analysis script that produced a number in the paper.
    4. Re-renders the paper's figures.
    5. Prints a side-by-side table of paper claim vs reproduced value,
       and exits 0 if everything matches, nonzero otherwise.

No network, no write access beyond this directory. Safe to re-run any time.
"""

from __future__ import annotations

import os
import platform
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
SCRIPTS_DIR = REPO_ROOT / "scripts"
ANALYSIS_CODE = REPO_ROOT / "analysis" / "code"
OUTPUTS_DIR = REPO_ROOT / "analysis" / "outputs"
MOODLE_SRC = REPO_ROOT / "moodle_src"


# ---------------------------------------------------------------------------
# Pretty-print helpers (ASCII-only so Windows cp1252 terminals render cleanly).
# ---------------------------------------------------------------------------

def banner(title: str) -> None:
    bar = "=" * 72
    print(f"\n{bar}\n  {title}\n{bar}")


def step(n: int, total: int, title: str) -> None:
    print(f"\n[{n}/{total}] {title}")
    print("-" * 72)


# ---------------------------------------------------------------------------
# Shell-out helpers.
# ---------------------------------------------------------------------------

def run_python(script: Path, *args: str) -> int:
    cmd = [sys.executable, str(script), *args]
    print(f"  $ python {script.relative_to(REPO_ROOT)} " + " ".join(args))
    return subprocess.call(cmd, cwd=str(REPO_ROOT))


def run_fetch_moodle() -> int:
    if platform.system() == "Windows":
        script = SCRIPTS_DIR / "fetch_moodle.ps1"
        cmd = ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass",
               "-File", str(script)]
    else:
        script = SCRIPTS_DIR / "fetch_moodle.sh"
        cmd = ["bash", str(script)]
    print(f"  $ {' '.join(cmd)}")
    return subprocess.call(cmd, cwd=str(REPO_ROOT))


# ---------------------------------------------------------------------------
# Orchestration.
# ---------------------------------------------------------------------------

def main() -> int:
    banner("STAIR Paper Reproduction — one-command run")
    print(f"  Repo root: {REPO_ROOT}")
    print(f"  Python:    {sys.version.split()[0]} ({sys.executable})")
    print(f"  Platform:  {platform.system()} {platform.release()}")

    total_steps = 7

    step(1, total_steps, "Verifying Python environment")
    if run_python(SCRIPTS_DIR / "verify_environment.py") != 0:
        print("\nEnvironment verification failed. Install the missing packages above and re-run.")
        return 1

    step(2, total_steps, "Fetching Moodle source (pinned commit)")
    if not MOODLE_SRC.exists():
        if run_fetch_moodle() != 0:
            print("\nMoodle fetch failed. Check your internet connection and git install.")
            return 1
    else:
        print(f"  moodle_src/ already present at {MOODLE_SRC}")
        print(f"  Skipping fetch. Run scripts/fetch_moodle.* manually to force re-fetch.")

    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

    step(3, total_steps, "Analyzing Moodle architecture (events, AI, analytics isolation)")
    if run_python(
        ANALYSIS_CODE / "analyze_architecture.py",
        str(MOODLE_SRC),
        "-o", str(OUTPUTS_DIR / "architecture_summary.json"),
    ) != 0:
        return 1

    step(4, total_steps, "Deriving Table 3 consolidated scores (paper values)")
    if run_python(
        ANALYSIS_CODE / "derive_table3.py",
        "--output", str(OUTPUTS_DIR / "table3_derived.json"),
    ) != 0:
        return 1

    step(5, total_steps, "Computing raw STAIR readiness (sensitivity analysis, secondary)")
    if run_python(
        ANALYSIS_CODE / "score_stair.py",
        "-o", str(OUTPUTS_DIR / "stair_scores_output.json"),
    ) != 0:
        print("  NOTE: score_stair.py is secondary; paper headline numbers come from Table 3 above.")

    step(6, total_steps, "Verifying every paper claim against reproduced values")
    verify_rc = run_python(ANALYSIS_CODE / "verify_claims.py")

    step(7, total_steps, "Summary")
    if verify_rc == 0:
        banner("ALL CLAIMS REPRODUCED -- paper values match the code's output")
        print("  Outputs written to analysis/outputs/ (JSON) — inspect to dig deeper.")
        print("  The paper PDF lives at paper/Paper_1_STAIR_AITHE2026.pdf.")
        return 0
    else:
        banner("REPRODUCTION FAILED -- at least one claim did not match")
        print("  See the PAPER CLAIM vs REPRODUCED table above.")
        print("  Common causes: Moodle source drifted, data files edited, script changed.")
        return verify_rc


if __name__ == "__main__":
    sys.exit(main())
