#!/usr/bin/env python3
"""
analyze_architecture.py — Extract Moodle architecture metrics from source tree.

Reads:
    - Moodle source tree (lib/db/services.php, ai/provider/, ai/classes/aiactions/,
      analytics/, course/classes/analytics/target/, lib/classes/task/)

Produces:
    - data/architecture_summary.json

Cross-references:
    This output feeds into:
    - task1/ARCHITECTURE_MAP.md (architecture trace document)
    - task5/fig5_event_flow.png (event flow architecture diagram)
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path


def resolve_path(moodle_root: Path, *parts) -> Path:
    """Resolve a path, checking both traditional and public/ prefix layouts."""
    direct = moodle_root.joinpath(*parts)
    if direct.exists():
        return direct
    public = moodle_root.joinpath("public", *parts)
    if public.exists():
        return public
    return direct  # Return direct (will fail naturally if neither exists)


def count_web_service_functions(moodle_root: Path) -> dict:
    """Count web service function definitions in lib/db/services.php."""
    services_file = resolve_path(moodle_root, "lib", "db", "services.php")
    if not services_file.exists():
        return {"count": 0, "error": f"File not found: {services_file}"}

    content = services_file.read_text(encoding="utf-8", errors="replace")
    # Each web service function entry has a 'classname' key
    classname_matches = re.findall(r"'classname'", content)
    return {"count": len(classname_matches), "file": "lib/db/services.php"}


def list_ai_providers(moodle_root: Path) -> list:
    """List AI provider directories in ai/provider/."""
    provider_dir = resolve_path(moodle_root, "ai", "provider")
    if not provider_dir.is_dir():
        return []
    providers = sorted([
        d.name for d in provider_dir.iterdir()
        if d.is_dir() and not d.name.startswith(".")
    ])
    return providers


def list_ai_actions(moodle_root: Path) -> list:
    """List AI action type PHP files in ai/classes/aiactions/."""
    actions_dir = resolve_path(moodle_root, "ai", "classes", "aiactions")
    if not actions_dir.is_dir():
        actions_dir = resolve_path(moodle_root, "ai", "classes", "aiactions")
        if not actions_dir.is_dir():
            return []
    actions = sorted([
        f.stem for f in actions_dir.glob("*.php")
        if f.stem != "base" and not f.stem.startswith("_")
    ])
    return actions


def check_ai_analytics_isolation(moodle_root: Path) -> dict:
    """Check for cross-imports between core_ai and core_analytics."""
    ai_dir = resolve_path(moodle_root, "ai")
    analytics_dir = resolve_path(moodle_root, "analytics")

    ai_refs_analytics = 0
    analytics_refs_ai = 0
    ai_files_with_refs = []
    analytics_files_with_refs = []

    # Check ai/ for references to core_analytics
    if ai_dir.is_dir():
        for php_file in ai_dir.rglob("*.php"):
            try:
                content = php_file.read_text(encoding="utf-8", errors="replace")
                if "core_analytics" in content:
                    ai_refs_analytics += 1
                    ai_files_with_refs.append(
                        str(php_file.relative_to(moodle_root))
                    )
            except Exception:
                pass

    # Check analytics/ for references to core_ai
    if analytics_dir.is_dir():
        for php_file in analytics_dir.rglob("*.php"):
            try:
                content = php_file.read_text(encoding="utf-8", errors="replace")
                if "core_ai" in content:
                    analytics_refs_ai += 1
                    analytics_files_with_refs.append(
                        str(php_file.relative_to(moodle_root))
                    )
            except Exception:
                pass

    return {
        "ai_references_analytics": ai_refs_analytics,
        "analytics_references_ai": analytics_refs_ai,
        "isolated": ai_refs_analytics == 0 and analytics_refs_ai == 0,
        "ai_files_with_refs": ai_files_with_refs,
        "analytics_files_with_refs": analytics_files_with_refs,
    }


def list_analytics_targets(moodle_root: Path) -> list:
    """List analytics prediction target classes."""
    target_dir = resolve_path(moodle_root, "course", "classes", "analytics", "target")
    targets = []
    if target_dir.is_dir():
        targets = sorted([
            f.stem for f in target_dir.glob("*.php")
            if not f.stem.startswith("_")
        ])

    # Also check analytics/classes/target/ for additional targets
    alt_dir = resolve_path(moodle_root, "analytics", "classes", "target")
    if alt_dir.is_dir():
        for f in alt_dir.glob("*.php"):
            if not f.stem.startswith("_") and f.stem not in targets:
                targets.append(f.stem)
        targets.sort()

    return targets


def count_scheduled_tasks(moodle_root: Path) -> dict:
    """Count scheduled task classes in lib/classes/task/."""
    task_dir = resolve_path(moodle_root, "lib", "classes", "task")
    if not task_dir.is_dir():
        return {"count": 0, "tasks": []}

    tasks = sorted([
        f.stem for f in task_dir.glob("*.php")
        if f.stem not in ("manager", "base", "task_base", "scheduled_task",
                          "adhoc_task", "task_trait")
        and not f.stem.startswith("_")
    ])
    return {"count": len(tasks), "tasks": tasks}


def main():
    parser = argparse.ArgumentParser(
        description="Extract Moodle architecture metrics from source tree."
    )
    parser.add_argument(
        "moodle_src",
        nargs="?",
        default="../moodle_src",
        help="Path to the Moodle source directory (default: ../moodle_src)",
    )
    parser.add_argument(
        "-o", "--output",
        default=None,
        help="Output JSON path (default: data/architecture_summary.json)",
    )
    args = parser.parse_args()

    moodle_root = Path(args.moodle_src).resolve()
    if not moodle_root.is_dir():
        print(f"ERROR: Moodle source directory not found: {moodle_root}")
        print("")
        print("For reproducible results, DO NOT run a raw `git clone` of Moodle -- you will")
        print("get current HEAD, which may differ from the version analysed in the paper.")
        print("Use the pinned-commit fetch script from the repo root:")
        print("  bash scripts/fetch_moodle.sh              # macOS / Linux")
        print("  powershell -File scripts/fetch_moodle.ps1 # Windows")
        print("Or run `python reproduce.py` which calls the fetch automatically.")
        print("Pinned SHA: 213a869e7ffd48d3a5679818bcddbb22dbc31aa5 (Moodle 5.2dev+, 2026-03-20)")
        sys.exit(1)

    # Determine output path
    script_dir = Path(__file__).resolve().parent
    project_dir = script_dir.parent
    data_dir = project_dir / "data"
    data_dir.mkdir(exist_ok=True)

    output_path = Path(args.output) if args.output else data_dir / "architecture_summary.json"

    print(f"Scanning Moodle source at: {moodle_root}")
    print()

    # Gather all metrics
    ws = count_web_service_functions(moodle_root)
    print(f"Web service functions: {ws['count']}")

    providers = list_ai_providers(moodle_root)
    print(f"AI providers ({len(providers)}): {', '.join(providers) if providers else 'none found'}")

    actions = list_ai_actions(moodle_root)
    print(f"AI action types ({len(actions)}): {', '.join(actions) if actions else 'none found'}")

    isolation = check_ai_analytics_isolation(moodle_root)
    iso_status = "CONFIRMED" if isolation["isolated"] else "BROKEN"
    print(f"AI-Analytics isolation: {iso_status}")
    if not isolation["isolated"]:
        print(f"  ai/ refs analytics: {isolation['ai_references_analytics']}")
        print(f"  analytics/ refs ai: {isolation['analytics_references_ai']}")

    targets = list_analytics_targets(moodle_root)
    print(f"Analytics targets ({len(targets)}): {', '.join(targets) if targets else 'none found'}")

    tasks = count_scheduled_tasks(moodle_root)
    print(f"Scheduled task classes: {tasks['count']}")
    print()

    # Build summary
    summary = {
        "moodle_source": str(moodle_root),
        "web_services": ws,
        "ai_providers": {
            "count": len(providers),
            "providers": providers,
            "path": "ai/provider/",
        },
        "ai_actions": {
            "count": len(actions),
            "actions": actions,
            "path": "ai/classes/aiactions/",
        },
        "ai_analytics_isolation": isolation,
        "analytics_targets": {
            "count": len(targets),
            "targets": targets,
        },
        "scheduled_tasks": tasks,
    }

    # Write JSON
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    print(f"Wrote architecture summary to: {output_path}")
    print()

    # Cross-reference
    print("=== Cross-Reference ===")
    print("This output feeds into:")
    print("  - task1/ARCHITECTURE_MAP.md (architecture trace document)")
    print("  - task5/fig5_event_flow.png (event flow architecture diagram)")
    print()
    print(f"Output file: {output_path}")


if __name__ == "__main__":
    main()
