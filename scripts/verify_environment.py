#!/usr/bin/env python3
"""verify_environment.py — check Python version + required packages.

Exits 0 if the environment can run the reproduction pipeline, nonzero otherwise.
Prints actionable install instructions on failure.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

MIN_PY = (3, 10)

REPO_ROOT = Path(__file__).resolve().parent.parent
REQUIREMENTS_FILE = REPO_ROOT / "requirements.txt"


def check_python() -> bool:
    cur = sys.version_info[:2]
    if cur < MIN_PY:
        print(f"FAIL: Python {MIN_PY[0]}.{MIN_PY[1]}+ required, found {cur[0]}.{cur[1]}.")
        print(f"      Install a newer Python from https://python.org and re-run.")
        return False
    print(f"PASS: Python {cur[0]}.{cur[1]} (>= {MIN_PY[0]}.{MIN_PY[1]})")
    return True


def parse_requirements() -> list[str]:
    if not REQUIREMENTS_FILE.exists():
        return []
    pkgs = []
    for line in REQUIREMENTS_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        # Take just the package name (strip version spec)
        for sep in (">=", "<=", "==", "~=", ">", "<"):
            if sep in line:
                line = line.split(sep, 1)[0]
                break
        pkgs.append(line.strip())
    return pkgs


def check_imports(pkgs: list[str]) -> list[str]:
    # Package-name → import-name override (where they differ)
    import_name = {
        "pyyaml": "yaml",
        "pillow": "PIL",
    }
    missing = []
    for pkg in pkgs:
        name = import_name.get(pkg.lower(), pkg)
        if importlib.util.find_spec(name) is None:
            missing.append(pkg)
            print(f"FAIL: missing package '{pkg}'")
        else:
            print(f"PASS: {pkg}")
    return missing


def check_git() -> bool:
    import shutil
    if shutil.which("git") is None:
        print("FAIL: 'git' not found on PATH. Install from https://git-scm.com.")
        return False
    print("PASS: git")
    return True


def main() -> int:
    print("Environment check:")
    ok = True

    if not check_python():
        ok = False

    if not check_git():
        ok = False

    missing = check_imports(parse_requirements())
    if missing:
        ok = False
        print()
        print("To install missing packages, run:")
        print(f"    {sys.executable} -m pip install -r {REQUIREMENTS_FILE}")

    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
