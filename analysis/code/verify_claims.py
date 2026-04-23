#!/usr/bin/env python3
"""verify_claims.py — the trust anchor of the STAIR reproduction bundle.

Reads the paper-claims manifest (paper_claims.json) and the freshly-reproduced
analysis outputs (table3_derived.json, architecture_summary.json), then prints
a side-by-side comparison table:

    PAPER CLAIM                                    | REPRODUCED | MATCH?
    L1 Event Sensing readiness = 55%               | 55         | ✓
    L2 Student State readiness = 53%               | 53         | ✓
    ...
    Cross-imports core_ai → core_analytics = 0     | 0          | ✓

Exit code 0 if every row matches (within the claim's tolerance);
nonzero if any claim drifted. This is what makes the reproduction
script meaningful — without this, a reviewer has no way to know
whether the code they just ran actually validates the paper.
"""

import argparse
import json
import sys
from pathlib import Path

# Allow running as a standalone script OR as `python -m analysis.code.verify_claims`
try:
    from .paths import (
        PAPER_CLAIMS_JSON, TABLE3_DERIVED_JSON, ARCHITECTURE_SUMMARY_JSON,
        DATA_DIR, OUTPUTS_DIR,
    )
except ImportError:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from paths import (  # type: ignore[import-not-found]
        PAPER_CLAIMS_JSON, TABLE3_DERIVED_JSON, ARCHITECTURE_SUMMARY_JSON,
        DATA_DIR, OUTPUTS_DIR,
    )


# ASCII-only markers — Windows terminals default to cp1252 and cannot render ✓/✗.
# Keep these plain so the verification table renders identically across all shells.
CHECK = "PASS"
CROSS = "FAIL"


def load_json(path: Path) -> dict:
    if not path.exists():
        print(f"ERROR: required file not found: {path}", file=sys.stderr)
        sys.exit(2)
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def resolve_output_key(key: str, sources: dict):
    """Resolve a dotted key path against one of several source dicts.

    Special case: 'table3.L2.avg - table3.L3.avg' → computed diff.
    """
    key = key.strip()
    if " - " in key:
        a, b = [s.strip() for s in key.split(" - ", 1)]
        return resolve_output_key(a, sources) - resolve_output_key(b, sources)

    parts = key.split(".")
    for src in sources.values():
        try:
            cur = src
            for p in parts:
                cur = cur[p]
            return cur
        except (KeyError, TypeError):
            continue
    raise KeyError(f"cannot resolve {key!r} in any source")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--strict", action="store_true",
                        help="Treat missing source files as fatal errors (default).")
    parser.add_argument("--no-strict", dest="strict", action="store_false",
                        help="Skip claims whose source file is missing (warn only).")
    parser.set_defaults(strict=True)
    args = parser.parse_args()

    manifest = load_json(PAPER_CLAIMS_JSON)

    sources = {}
    # Load in both canonical locations (data/ as committed, outputs/ as regenerated)
    for name, data_path, out_path in [
        ("table3", TABLE3_DERIVED_JSON, OUTPUTS_DIR / "table3_derived.json"),
        ("arch", ARCHITECTURE_SUMMARY_JSON, OUTPUTS_DIR / "architecture_summary.json"),
    ]:
        path = out_path if out_path.exists() else data_path
        if not path.exists():
            msg = f"source file not found for {name}: tried {out_path} and {data_path}"
            if args.strict:
                print(f"ERROR: {msg}", file=sys.stderr)
                sys.exit(2)
            else:
                print(f"WARNING: {msg}", file=sys.stderr)
                continue
        sources[name] = load_json(path)

    claims = manifest["claims"]
    rows = []
    n_pass = 0
    n_fail = 0

    for claim in claims:
        try:
            reproduced = resolve_output_key(claim["output_key"], sources)
        except KeyError as e:
            rows.append((claim["claim"], "MISSING", CROSS, str(e)))
            n_fail += 1
            continue

        expected = claim["expected"]
        tolerance = claim.get("tolerance", 0)

        if isinstance(expected, bool):
            match = (reproduced == expected)
        elif isinstance(expected, (int, float)) and isinstance(reproduced, (int, float)):
            match = abs(reproduced - expected) <= tolerance
        else:
            match = (reproduced == expected)

        marker = CHECK if match else CROSS
        if match:
            n_pass += 1
        else:
            n_fail += 1
        rows.append((claim["claim"], str(reproduced), marker, ""))

    # Print table
    claim_w = max(len(r[0]) for r in rows) + 2
    repro_w = max(10, max(len(r[1]) for r in rows) + 2)
    header = f"{'PAPER CLAIM':<{claim_w}} {'REPRODUCED':<{repro_w}} MATCH"
    print(header)
    print("-" * len(header))
    for claim_text, reproduced, marker, note in rows:
        print(f"{claim_text:<{claim_w}} {reproduced:<{repro_w}} {marker}"
              + (f"   [{note}]" if note else ""))
    print("-" * len(header))
    print(f"{n_pass} matched, {n_fail} drifted, {len(rows)} total.")

    sys.exit(0 if n_fail == 0 else 1)


if __name__ == "__main__":
    main()
