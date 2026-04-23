#!/usr/bin/env python3
"""
analyze_events.py — Extract and classify Moodle event classes from source tree.

Reads:
    - Moodle source tree (lib/classes/event/*.php for core events)
    - All */classes/event/*.php paths for plugin events

Produces:
    - data/events_extracted.csv (columns: filepath, class_name, category,
      crud_type, edulevel, target, action)

Cross-references:
    This output feeds into:
    - task2/EVENTS_CATALOG.csv (event catalog for the paper)
    - task5/fig3_event_heatmap.png (event coverage heatmap)
    - task5/fig8_event_taxonomy.png (event distribution charts)
"""

import argparse
import csv
import os
import re
import sys
from collections import Counter
from pathlib import Path


# Base classes and abstract files to exclude from event counts
EXCLUDED_BASENAMES = {
    "base.php",
    "manager.php",
    "observer.php",
    "observers.php",
}


def find_event_files(moodle_root: Path):
    """Find all PHP event class files, split into core and plugin."""
    # Handle both traditional layout and public/ prefix (Moodle 5.x dev)
    core_dir = moodle_root / "lib" / "classes" / "event"
    if not core_dir.is_dir():
        core_dir = moodle_root / "public" / "lib" / "classes" / "event"
    core_files = []
    plugin_files = []

    if core_dir.is_dir():
        for f in sorted(core_dir.glob("*.php")):
            if f.name.lower() not in EXCLUDED_BASENAMES:
                core_files.append(f)

    # Scan entire tree for */classes/event/*.php
    for f in sorted(moodle_root.rglob("classes/event/*.php")):
        if f.name.lower() in EXCLUDED_BASENAMES:
            continue
        # Check if this is a core file we already captured
        try:
            rel = f.relative_to(core_dir)
            # This is a core file — skip to avoid double counting
            continue
        except ValueError:
            pass
        plugin_files.append(f)

    return core_files, plugin_files


def extract_class_name(content: str, filepath: Path) -> str:
    """Extract the PHP class name from file content."""
    match = re.search(r"class\s+(\w+)\s+extends", content)
    if match:
        return match.group(1)
    # Fallback: derive from filename
    return filepath.stem


def extract_crud_type(content: str) -> str:
    """Extract CRUD type from get_crud() or init() method."""
    # Look for explicit CRUD constant in init() or get_crud()
    crud_map = {
        "self::CRUD_CREATE": "c",
        "'c'": "c",
        "self::CRUD_READ": "r",
        "'r'": "r",
        "self::CRUD_UPDATE": "u",
        "'u'": "u",
        "self::CRUD_DELETE": "d",
        "'d'": "d",
    }
    # Check init() body for $this->data['crud']
    init_match = re.search(
        r"function\s+init\s*\(\s*\)(.*?)(?:function\s|\Z)",
        content,
        re.DOTALL,
    )
    if init_match:
        init_body = init_match.group(1)
        # Look for crud assignment
        crud_assign = re.search(r"\[.crud.\]\s*=\s*(.+?);", init_body)
        if crud_assign:
            val = crud_assign.group(1).strip()
            for pattern, letter in crud_map.items():
                if pattern in val:
                    return letter

    # Also check for a standalone get_crud() override
    crud_func = re.search(
        r"function\s+get_crud\s*\(\s*\).*?return\s+(.+?);",
        content,
        re.DOTALL,
    )
    if crud_func:
        val = crud_func.group(1).strip()
        for pattern, letter in crud_map.items():
            if pattern in val:
                return letter

    return "unknown"


def extract_edulevel(content: str) -> str:
    """Extract education level from init() method."""
    level_map = {
        "LEVEL_TEACHING": "LEVEL_TEACHING",
        "LEVEL_PARTICIPATING": "LEVEL_PARTICIPATING",
        "LEVEL_OTHER": "LEVEL_OTHER",
    }
    init_match = re.search(
        r"function\s+init\s*\(\s*\)(.*?)(?:function\s|\Z)",
        content,
        re.DOTALL,
    )
    if init_match:
        init_body = init_match.group(1)
        for pattern, label in level_map.items():
            if pattern in init_body:
                return label
    # Also check class-level constant or property
    for pattern, label in level_map.items():
        if pattern in content:
            return label
    return "unknown"


def extract_target_action(content: str, filepath: Path):
    """Extract target and action from init() or get_name()."""
    target = "unknown"
    action = "unknown"

    init_match = re.search(
        r"function\s+init\s*\(\s*\)(.*?)(?:function\s|\Z)",
        content,
        re.DOTALL,
    )
    if init_match:
        init_body = init_match.group(1)

        # target
        t_match = re.search(r"\[.target.\]\s*=\s*['\"](\w+)['\"]", init_body)
        if t_match:
            target = t_match.group(1)

        # action
        a_match = re.search(r"\[.action.\]\s*=\s*['\"](\w+)['\"]", init_body)
        if a_match:
            action = a_match.group(1)

    # Fallback: infer from filename pattern  e.g. course_viewed.php
    if target == "unknown" or action == "unknown":
        stem = filepath.stem
        # Common patterns: <target>_<action> or <action>_<target>
        parts = stem.rsplit("_", 1)
        if len(parts) == 2:
            if action == "unknown":
                action = parts[-1]
            if target == "unknown":
                target = parts[0]

    return target, action


def categorize_file(filepath: Path, moodle_root: Path) -> str:
    """Determine the category (subsystem/plugin) from the file path."""
    rel = filepath.relative_to(moodle_root)
    parts = rel.parts

    if parts[0] == "lib":
        return "core"
    elif parts[0] == "mod":
        return f"mod_{parts[1]}" if len(parts) > 1 else "mod"
    elif parts[0] in ("admin", "course", "user", "auth", "enrol",
                       "grade", "report", "block", "message",
                       "calendar", "group", "badges", "competency",
                       "contentbank", "customfield", "tool",
                       "question", "repository", "portfolio"):
        return parts[0]
    else:
        return parts[0]


def process_event_file(filepath: Path, moodle_root: Path) -> dict:
    """Parse a single event PHP file and extract metadata."""
    try:
        content = filepath.read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        return {
            "filepath": str(filepath.relative_to(moodle_root)),
            "class_name": filepath.stem,
            "category": categorize_file(filepath, moodle_root),
            "crud_type": "error",
            "edulevel": "error",
            "target": "error",
            "action": "error",
        }

    class_name = extract_class_name(content, filepath)
    crud_type = extract_crud_type(content)
    edulevel = extract_edulevel(content)
    target, action = extract_target_action(content, filepath)
    category = categorize_file(filepath, moodle_root)

    return {
        "filepath": str(filepath.relative_to(moodle_root)),
        "class_name": class_name,
        "category": category,
        "crud_type": crud_type,
        "edulevel": edulevel,
        "target": target,
        "action": action,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Extract and classify Moodle event classes from source tree."
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
        help="Output CSV path (default: data/events_extracted.csv)",
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

    # Handle both traditional layout and public/ prefix (Moodle 5.x dev)
    event_dir = moodle_root / "lib" / "classes" / "event"
    if not event_dir.is_dir():
        event_dir = moodle_root / "public" / "lib" / "classes" / "event"
    if not event_dir.is_dir():
        print(f"ERROR: Expected event directory not found in lib/classes/event/ or public/lib/classes/event/")
        sys.exit(1)

    # Determine output path
    script_dir = Path(__file__).resolve().parent
    project_dir = script_dir.parent
    data_dir = project_dir / "data"
    data_dir.mkdir(exist_ok=True)

    output_path = Path(args.output) if args.output else data_dir / "events_extracted.csv"

    print(f"Scanning Moodle source at: {moodle_root}")
    print()

    core_files, plugin_files = find_event_files(moodle_root)
    print(f"Found {len(core_files)} core event files in lib/classes/event/")
    print(f"Found {len(plugin_files)} plugin event files across the source tree")
    print(f"Total: {len(core_files) + len(plugin_files)} event classes")
    print()

    # Process all events
    rows = []
    for f in core_files:
        rows.append(process_event_file(f, moodle_root))
    for f in plugin_files:
        rows.append(process_event_file(f, moodle_root))

    # Write CSV
    fieldnames = ["filepath", "class_name", "category", "crud_type",
                  "edulevel", "target", "action"]
    with open(output_path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {len(rows)} events to: {output_path}")
    print()

    # Summary statistics
    edulevel_counts = Counter(r["edulevel"] for r in rows)
    crud_counts = Counter(r["crud_type"] for r in rows)
    category_counts = Counter(r["category"] for r in rows)

    print("=== Summary Statistics ===")
    print(f"  Core events:   {len(core_files)}")
    print(f"  Plugin events: {len(plugin_files)}")
    print(f"  Total:         {len(rows)}")
    print()

    print("  By education level:")
    for level, count in sorted(edulevel_counts.items(), key=lambda x: -x[1]):
        print(f"    {level}: {count}")
    print()

    print("  By CRUD type:")
    for crud, count in sorted(crud_counts.items(), key=lambda x: -x[1]):
        print(f"    {crud}: {count}")
    print()

    print("  Top 10 categories:")
    for cat, count in category_counts.most_common(10):
        print(f"    {cat}: {count}")
    print()

    # Cross-reference
    print("=== Cross-Reference ===")
    print("This output feeds into:")
    print("  - task2/EVENTS_CATALOG.csv (event catalog for the paper)")
    print("  - task5/fig3_event_heatmap.png (event coverage heatmap)")
    print("  - task5/fig8_event_taxonomy.png (event distribution charts)")
    print()
    print(f"Output file: {output_path}")


if __name__ == "__main__":
    main()
