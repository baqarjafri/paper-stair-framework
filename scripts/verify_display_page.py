#!/usr/bin/env python3
"""Guard for the project page: every data-check-marked number on docs/index.html must equal the analysis data.

Three checks, in the style of analysis/code/verify_claims.py:
1. docs/assets/site-data.js equals a fresh build from analysis/data (build_display_data.in_sync).
2. docs/index.html carries the static numbers (the no-JS fallback) in elements marked
   data-check="<key>": five level scores in the chart, five in the ladder, five in the level
   banners, 25 Table 3 cells and five means, 28 sub-dimension scores, and eight headline
   claims. Marked elements hold text only, once each; violations fail the run.
3. docs/index.html carries each level's requirement, components and grounding constructs
   verbatim (copy_gaps).

Exit 0 when everything matches, 1 on any drift. Output is ASCII only (Windows console).
"""
import html as html_lib
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_display_data import ROOT, build, in_sync  # noqa: E402

INDEX = ROOT / "docs" / "index.html"


def expected(data: dict) -> dict[str, str]:
    """Map data-check key -> expected text. 81 keys."""
    exp: dict[str, str] = {}
    for lv in data["levels"]:
        exp[f'{lv["id"]}.score'] = str(lv["score"])
        exp[f'{lv["id"]}.score.ladder'] = str(lv["score"])
        exp[f'{lv["id"]}.score.banner'] = str(lv["score"])
        exp[f'{lv["id"]}.mean'] = str(lv["score"])
        for dim, v in lv["dims"].items():
            exp[f'{lv["id"]}.{dim}'] = str(v)
    for sid, s in data["subs"].items():
        exp[sid] = str(s["score"])
    c = data["claims"]
    exp["claims.cliff"] = str(c["cliff"])
    # One page element states "0 imports in either direction"; the sum is 0 only when both directional counts are 0.
    exp["claims.imports"] = str(c["ai_refs_analytics"] + c["analytics_refs_ai"])
    exp["claims.web_services"] = str(c["web_services"])
    exp["claims.ai_providers"] = str(c["ai_providers"])
    exp["claims.ai_actions"] = str(c["ai_actions"])
    exp["claims.analytics_targets"] = str(c["analytics_targets"])
    exp["claims.subs"] = str(len(data["subs"]))
    exp["claims.total"] = str(c["claims_total"])
    return exp


def copy_gaps(page_html: str, data: dict) -> list[str]:
    """Level copy that the page must carry verbatim: Table 1 requirement, the three
    Figure 2 components and the three grounding constructs of every level. Compared
    against the entity-decoded page text so `&middot;` matches the data's middle dot."""
    text = html_lib.unescape(page_html)
    gaps: list[str] = []
    for lv in data["levels"]:
        wanted = [("requirement", lv["requirement"]), ("components", lv["components"])]
        wanted += [(f"construct {code}", value) for code, value in lv["constructs"].items()]
        for label, value in wanted:
            if not re.search(r"(?<!\w)" + re.escape(value) + r"(?!\w)", text):
                gaps.append(f'{lv["id"]} {label}: "{value}"')
    return gaps


class _Checks(HTMLParser):
    """Collect the text of every element that carries a data-check attribute.
    Rule for index.html: a marked element contains text only, no child elements,
    and each key appears once. Violations are recorded, not silently tolerated."""

    def __init__(self) -> None:
        super().__init__()
        self.found: dict[str, str] = {}
        self.violations: list[str] = []
        self._key: str | None = None
        self._buf = ""

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr_map = dict(attrs)
        if "data-check" not in attr_map:
            if self._key is not None:
                self.violations.append(f"CHILD ELEMENT <{tag}> inside data-check={self._key}")
            return
        key = attr_map["data-check"] or ""
        if not key:
            self.violations.append(f"EMPTY data-check on <{tag}>")
        if self._key is not None:
            self.violations.append(f"NESTED data-check={key} inside data-check={self._key}")
        if key in self.found:
            self.violations.append(f"DUPLICATE data-check={key}")
        self._key = key
        self._buf = ""

    def handle_data(self, data: str) -> None:
        if self._key is not None:
            self._buf += data

    def handle_endtag(self, tag: str) -> None:
        if self._key is not None:
            self.found[self._key] = self._buf.strip()
            self._key = None


def parse_checks(html: str) -> dict[str, str]:
    """Key -> text for every marked element. Raises ValueError when the marking rule is broken."""
    p = _Checks()
    p.feed(html)
    p.close()
    if p.violations:
        raise ValueError("data-check rule broken (marked elements hold text only, once each):\n  "
                         + "\n  ".join(p.violations))
    return p.found


def compare(exp: dict[str, str], found: dict[str, str]) -> list[tuple[str, str, str, str]]:
    """Rows of (key, expected, found, status) with status PASS, FAIL, MISSING or UNKNOWN
    (marked on the page but not expected)."""
    rows = []
    for key, want in exp.items():
        got = found.get(key)
        status = "MISSING" if got is None else ("PASS" if got == want else "FAIL")
        rows.append((key, want, "" if got is None else got, status))
    for key in sorted(found.keys() - exp.keys()):
        rows.append((key, "", found[key], "UNKNOWN"))
    return rows


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(errors="backslashreplace")
    data = build()
    problems = 0

    synced = in_sync()
    print(f"{'site-data.js':<38}{'':>8}{'':>8}  "
          + ("PASS" if synced else "DRIFT   run: python scripts/build_display_data.py"))
    if not synced:
        problems += 1

    rel = INDEX.relative_to(ROOT).as_posix() if ROOT in INDEX.parents else str(INDEX)
    if not INDEX.exists():
        print(f"{rel} not found")
        return 1
    page = INDEX.read_text(encoding="utf-8")
    try:
        found = parse_checks(page)
    except ValueError as err:
        print(err)
        return 1
    rows = compare(expected(data), found)
    gaps = copy_gaps(page, data)
    print(f"{'PAGE ELEMENT (data-check)':<38}{'DATA':>8}{'PAGE':>8}  STATUS")
    print("-" * 64)
    for key, want, got, status in rows:
        if status != "PASS":
            problems += 1
        print(f"{key:<38}{want:>8}{got:>8}  {status}")
    print("-" * 64)
    for gap in gaps:
        print(f"COPY MISSING  {gap}")
        problems += 1
    passed = sum(1 for r in rows if r[3] == "PASS")
    print(f"{passed} matched, {len(rows) - passed} drifted, missing or unknown, {len(rows)} total; {len(gaps)} copy gaps.")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
