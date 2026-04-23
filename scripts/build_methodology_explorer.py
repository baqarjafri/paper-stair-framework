#!/usr/bin/env python3
"""build_methodology_explorer.py -- generate docs/methodology_explorer.html.

Reads every data file the STAIR paper depends on, embeds them as inline JSON
in a single self-contained HTML file, and emits a zero-dependency interactive
browser of the methodology. The output works offline, from file://, with no
build step, no CDN, no fetch calls.

Inputs:
    analysis/data/sub_dimension_definitions.json   (canonical definitions + grounding)
    analysis/data/moodle_scores.json                (raw 0-4 scores + evidence)
    analysis/data/scoring_provenance.json           (consolidated Table 3 derivation)
    analysis/data/table3_derived.json               (Table 3 output + mapping)
    analysis/data/architecture_summary.json         (AI-analytics isolation finding)
    analysis/data/EVENTS_CATALOG.csv                (227 Moodle events with SRL mapping)
    analysis/data/paper_claims.json                 (paper claim manifest)

Output:
    docs/methodology_explorer.html                  (single self-contained HTML)

Run:
    python scripts/build_methodology_explorer.py

Re-run whenever any input file changes.
"""

from __future__ import annotations

import csv
import json
import sys
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_ROOT / "analysis" / "data"
OUTPUT_PATH = REPO_ROOT / "docs" / "methodology_explorer.html"


def load_json(name: str):
    path = DATA_DIR / name
    if not path.exists():
        print(f"ERROR: {path} missing", file=sys.stderr)
        sys.exit(1)
    return json.loads(path.read_text(encoding="utf-8"))


def load_events_csv() -> list[dict]:
    path = DATA_DIR / "EVENTS_CATALOG.csv"
    if not path.exists():
        return []
    with open(path, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def render_html(data: dict) -> str:
    """Render the full HTML using an f-string template.

    Data is serialized as JSON into inline <script> tags so the page works
    from file:// without fetch calls.
    """
    data_json = json.dumps(data, indent=2, ensure_ascii=False)
    generated = datetime.now().strftime("%Y-%m-%d")

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>STAIR Methodology Explorer</title>
<style>
:root {{
  --bg: #ffffff;
  --surface: #f7f8fa;
  --surface-alt: #eef1f6;
  --ink: #1a2332;
  --ink-soft: #475569;
  --ink-faint: #94a3b8;
  --border: #dde3ec;
  --accent: #1a4b8c;
  --green: #2d7a3e;
  --green-soft: #e4f1e6;
  --amber: #c98515;
  --amber-soft: #fbf0d8;
  --red: #b02a2a;
  --red-soft: #f9e0e0;
  --code-bg: #0f172a;
  --code-ink: #e2e8f0;
  --mono: 'JetBrains Mono', 'Consolas', 'Menlo', monospace;
  --sans: -apple-system, 'Segoe UI', 'Inter', Arial, sans-serif;
  --serif: Georgia, 'Times New Roman', serif;
}}
* {{ box-sizing: border-box; }}
html, body {{
  margin: 0; padding: 0;
  font-family: var(--sans);
  font-size: 15px;
  line-height: 1.5;
  color: var(--ink);
  background: var(--surface);
}}
a {{ color: var(--accent); text-decoration: none; }}
a:hover {{ text-decoration: underline; }}
code {{
  font-family: var(--mono);
  font-size: 0.88em;
  background: var(--surface-alt);
  padding: 2px 5px;
  border-radius: 3px;
}}

header {{
  background: var(--ink);
  color: white;
  padding: 28px 40px 24px;
  border-bottom: 1px solid var(--border);
}}
header h1 {{
  margin: 0 0 8px;
  font-size: 22px;
  font-weight: 600;
  letter-spacing: -0.01em;
}}
header .subtitle {{
  color: #cbd5e1;
  font-size: 14px;
  line-height: 1.5;
}}
header .meta {{
  margin-top: 12px;
  color: #94a3b8;
  font-size: 12px;
  font-family: var(--mono);
}}

nav.tabs {{
  background: var(--bg);
  border-bottom: 1px solid var(--border);
  padding: 0 40px;
  display: flex;
  gap: 0;
  position: sticky;
  top: 0;
  z-index: 10;
  overflow-x: auto;
}}
nav.tabs button {{
  background: transparent;
  border: none;
  border-bottom: 3px solid transparent;
  padding: 16px 20px;
  cursor: pointer;
  font-family: inherit;
  font-size: 14px;
  color: var(--ink-soft);
  font-weight: 500;
  white-space: nowrap;
}}
nav.tabs button:hover {{ color: var(--ink); }}
nav.tabs button.active {{
  color: var(--accent);
  border-bottom-color: var(--accent);
  font-weight: 600;
}}

main {{
  max-width: 1100px;
  margin: 0 auto;
  padding: 32px 40px 80px;
}}
.section {{ display: none; }}
.section.active {{ display: block; }}

h2.section-title {{
  font-size: 20px;
  font-weight: 600;
  margin: 0 0 8px;
  color: var(--ink);
}}
p.section-lede {{
  color: var(--ink-soft);
  margin: 0 0 24px;
  max-width: 68ch;
}}

/* OVERVIEW */
.pipeline {{
  display: flex;
  align-items: stretch;
  gap: 8px;
  margin: 24px 0 32px;
  overflow-x: auto;
  padding-bottom: 8px;
}}
.pipeline-step {{
  background: var(--bg);
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 14px 18px;
  flex: 1 1 0;
  min-width: 160px;
}}
.pipeline-step h3 {{
  margin: 0 0 4px;
  font-size: 13px;
  font-weight: 600;
  color: var(--accent);
  font-family: var(--mono);
}}
.pipeline-step p {{
  margin: 0;
  font-size: 13px;
  color: var(--ink-soft);
  line-height: 1.45;
}}
.pipeline-arrow {{
  align-self: center;
  color: var(--ink-faint);
  font-size: 20px;
  user-select: none;
}}

.score-grid {{
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 12px;
  margin: 24px 0;
}}
.score-card {{
  background: var(--bg);
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 18px;
  cursor: pointer;
  transition: border-color 0.15s, box-shadow 0.15s;
}}
.score-card:hover {{
  border-color: var(--accent);
  box-shadow: 0 2px 6px rgba(0,0,0,0.06);
}}
.score-card .level-id {{
  font-family: var(--mono);
  font-size: 12px;
  color: var(--ink-faint);
  margin-bottom: 4px;
}}
.score-card .level-name {{
  font-weight: 600;
  font-size: 14px;
  margin-bottom: 8px;
  color: var(--ink);
}}
.score-card .score-big {{
  font-size: 28px;
  font-weight: 700;
  font-family: var(--mono);
  letter-spacing: -0.02em;
}}
.score-card .verdict {{
  font-size: 12px;
  color: var(--ink-soft);
  margin-top: 4px;
}}
.score-card.green .score-big {{ color: var(--green); }}
.score-card.amber .score-big {{ color: var(--amber); }}
.score-card.red .score-big {{ color: var(--red); }}

.headline-finding {{
  background: var(--red-soft);
  border: 1px solid var(--red);
  border-radius: 6px;
  padding: 16px 20px;
  margin: 24px 0;
}}
.headline-finding strong {{ color: var(--red); }}

/* LEVEL DETAIL */
.level-header {{
  background: var(--bg);
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 20px 24px;
  margin-bottom: 20px;
}}
.level-header h3 {{
  margin: 0 0 6px;
  font-size: 18px;
  font-weight: 600;
}}
.level-header .big-score {{
  font-family: var(--mono);
  font-size: 32px;
  font-weight: 700;
  margin: 8px 0;
}}
.level-header.green .big-score {{ color: var(--green); }}
.level-header.amber .big-score {{ color: var(--amber); }}
.level-header.red .big-score {{ color: var(--red); }}
.level-header .grounding-pills {{
  display: flex;
  gap: 6px;
  margin-top: 10px;
}}

.pill {{
  display: inline-block;
  font-size: 11px;
  font-family: var(--mono);
  padding: 2px 8px;
  border-radius: 10px;
  background: var(--surface-alt);
  color: var(--ink-soft);
  letter-spacing: 0.03em;
}}
.pill-z {{ background: #e0ebf7; color: #1a4b8c; }}
.pill-t {{ background: #f3e7f3; color: #6b2c6b; }}
.pill-h {{ background: #e0f2ec; color: #256d50; }}

.subdim-list {{
  background: var(--bg);
  border: 1px solid var(--border);
  border-radius: 6px;
  margin-bottom: 20px;
  overflow: hidden;
}}
.subdim {{
  border-bottom: 1px solid var(--border);
  padding: 0;
}}
.subdim:last-child {{ border-bottom: none; }}
.subdim-head {{
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 20px;
  cursor: pointer;
  user-select: none;
  background: var(--bg);
}}
.subdim-head:hover {{ background: var(--surface); }}
.subdim-head .chev {{
  color: var(--ink-faint);
  font-family: var(--mono);
  font-size: 12px;
  width: 12px;
  transition: transform 0.15s;
}}
.subdim.open .chev {{ transform: rotate(90deg); }}
.subdim-head .sid {{
  font-family: var(--mono);
  font-size: 13px;
  color: var(--ink-soft);
  width: 56px;
}}
.subdim-head .sname {{
  font-weight: 500;
  flex: 1;
}}
.subdim-head .sgrounds {{ display: flex; gap: 4px; }}
.subdim-head .sscore {{
  font-family: var(--mono);
  font-size: 13px;
  font-weight: 600;
  width: 80px;
  text-align: right;
}}
.subdim-head .sscore.green {{ color: var(--green); }}
.subdim-head .sscore.amber {{ color: var(--amber); }}
.subdim-head .sscore.red {{ color: var(--red); }}

.subdim-body {{
  display: none;
  padding: 0 20px 20px 88px;
  background: var(--surface);
  border-top: 1px solid var(--border);
}}
.subdim.open .subdim-body {{ display: block; }}

.subdim-body h4 {{
  margin: 16px 0 4px;
  font-size: 12px;
  font-weight: 600;
  color: var(--ink-soft);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}}
.subdim-body p {{ margin: 0 0 8px; font-size: 14px; line-height: 1.5; }}
.subdim-body .evidence {{
  font-family: var(--mono);
  font-size: 12.5px;
  background: var(--code-bg);
  color: var(--code-ink);
  padding: 10px 14px;
  border-radius: 4px;
  line-height: 1.45;
  white-space: pre-wrap;
  word-break: break-word;
}}

.consolidation {{
  background: var(--bg);
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 20px;
  margin-bottom: 20px;
}}
.consolidation h3 {{
  margin: 0 0 8px;
  font-size: 14px;
  font-weight: 600;
  color: var(--ink);
}}
.consolidation .cells {{
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 8px;
  margin: 12px 0;
}}
.cons-cell {{
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 4px;
  padding: 10px;
  text-align: center;
}}
.cons-cell .label {{
  font-family: var(--mono);
  font-size: 11px;
  color: var(--ink-faint);
  letter-spacing: 0.05em;
  margin-bottom: 2px;
}}
.cons-cell .value {{
  font-family: var(--mono);
  font-size: 18px;
  font-weight: 600;
}}
.cons-cell.green .value {{ color: var(--green); }}
.cons-cell.amber .value {{ color: var(--amber); }}
.cons-cell.red .value {{ color: var(--red); }}
.consolidation .calc {{
  font-family: var(--mono);
  font-size: 13px;
  color: var(--ink-soft);
  padding: 10px 14px;
  background: var(--surface);
  border-radius: 4px;
  margin-top: 12px;
}}
.consolidation .calc strong {{
  color: var(--ink);
  font-weight: 600;
}}

/* CELL-BY-CELL DERIVATION (how each consolidated cell was computed) */
.deriv-header {{
  margin: 20px 0 10px;
  font-size: 13px;
  font-weight: 600;
  color: var(--ink-soft);
  text-transform: uppercase;
  letter-spacing: 0.04em;
}}
.deriv-grid {{
  display: grid;
  gap: 10px;
}}
.deriv-cell {{
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 4px;
  padding: 12px 16px;
}}
.deriv-head {{
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 8px;
}}
.deriv-result {{
  font-family: var(--mono);
  font-weight: 700;
  font-size: 14px;
}}
.deriv-result.green {{ color: var(--green); }}
.deriv-result.amber {{ color: var(--amber); }}
.deriv-result.red {{ color: var(--red); }}
.deriv-sources {{
  display: grid;
  gap: 2px;
  margin: 6px 0;
}}
.deriv-src {{
  display: grid;
  grid-template-columns: 44px 1fr 100px 60px;
  gap: 10px;
  font-size: 12.5px;
  padding: 3px 0;
  align-items: baseline;
}}
.deriv-src .mono {{
  font-family: var(--mono);
  color: var(--ink-soft);
}}
.deriv-src .deriv-name {{
  color: var(--ink);
}}
.deriv-src .weight {{
  font-family: var(--mono);
  color: var(--accent);
  text-align: right;
}}
.deriv-formula {{
  font-family: var(--mono);
  font-size: 12.5px;
  color: var(--ink-soft);
  padding-top: 6px;
  margin-top: 6px;
  border-top: 1px dashed var(--border);
}}
.deriv-formula strong {{
  color: var(--ink);
}}

/* ARCHITECTURE */
.arch-grid {{
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 16px;
  margin: 20px 0;
}}
.arch-card {{
  background: var(--bg);
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 16px 20px;
}}
.arch-card h4 {{
  margin: 0 0 4px;
  font-size: 13px;
  font-weight: 600;
  color: var(--ink-soft);
}}
.arch-card .count {{
  font-family: var(--mono);
  font-size: 28px;
  font-weight: 700;
  color: var(--accent);
  margin: 4px 0;
}}
.arch-card .path {{
  font-family: var(--mono);
  font-size: 11px;
  color: var(--ink-faint);
  margin-top: 4px;
}}
.arch-card ul {{ margin: 8px 0 0; padding-left: 18px; }}
.arch-card li {{ font-size: 13px; color: var(--ink-soft); font-family: var(--mono); }}

.isolation-banner {{
  background: var(--red-soft);
  border-left: 4px solid var(--red);
  padding: 16px 20px;
  border-radius: 4px;
  margin: 20px 0;
}}
.isolation-banner h4 {{
  margin: 0 0 6px;
  color: var(--red);
  font-size: 14px;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}}
.isolation-banner p {{ margin: 0; font-size: 14px; }}

/* EVENTS */
.events-summary {{
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 12px;
  margin-bottom: 20px;
}}
.events-filters {{
  background: var(--bg);
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 14px 18px;
  margin-bottom: 16px;
  display: flex;
  gap: 16px;
  align-items: center;
  flex-wrap: wrap;
}}
.events-filters label {{
  font-size: 13px;
  color: var(--ink-soft);
  display: flex;
  align-items: center;
  gap: 6px;
}}
.events-filters select, .events-filters input {{
  font-family: inherit;
  font-size: 13px;
  padding: 5px 10px;
  border: 1px solid var(--border);
  border-radius: 4px;
  background: var(--bg);
  color: var(--ink);
}}
.events-table {{
  width: 100%;
  border-collapse: collapse;
  background: var(--bg);
  border: 1px solid var(--border);
  border-radius: 6px;
  overflow: hidden;
  font-size: 13px;
}}
.events-table thead th {{
  background: var(--surface-alt);
  padding: 10px 12px;
  text-align: left;
  font-size: 12px;
  font-weight: 600;
  color: var(--ink-soft);
  border-bottom: 1px solid var(--border);
}}
.events-table td {{
  padding: 8px 12px;
  border-bottom: 1px solid var(--border);
  vertical-align: top;
}}
.events-table td.mono {{ font-family: var(--mono); font-size: 12px; }}
.events-table tr:last-child td {{ border-bottom: none; }}
.events-count {{
  font-size: 13px;
  color: var(--ink-soft);
  margin-bottom: 8px;
}}

/* FILES */
.files-list {{
  background: var(--bg);
  border: 1px solid var(--border);
  border-radius: 6px;
  overflow: hidden;
}}
.file-row {{
  padding: 12px 20px;
  border-bottom: 1px solid var(--border);
  display: grid;
  grid-template-columns: 340px 1fr;
  gap: 20px;
}}
.file-row:last-child {{ border-bottom: none; }}
.file-row .fname {{ font-family: var(--mono); font-size: 13px; color: var(--accent); }}
.file-row .fdesc {{ font-size: 14px; color: var(--ink-soft); }}
.files-section-head {{
  background: var(--surface-alt);
  padding: 10px 20px;
  font-size: 12px;
  font-weight: 600;
  color: var(--ink-soft);
  text-transform: uppercase;
  letter-spacing: 0.04em;
  border-bottom: 1px solid var(--border);
}}

footer {{
  border-top: 1px solid var(--border);
  padding: 20px 40px;
  color: var(--ink-faint);
  font-size: 12px;
  text-align: center;
}}
footer code {{ background: var(--bg); }}
</style>
</head>
<body>

<header>
  <h1>STAIR Methodology Explorer</h1>
  <div class="subtitle">
    Interactive walkthrough of how Moodle's readiness scores (55 / 53 / 25 / 5 / 22) were derived.
    Every number traces to a specific source file, class, or constant in the Moodle 5.2dev+ codebase.
  </div>
  <div class="meta">
    Generated {generated} &middot; Data sources: sub_dimension_definitions.json, moodle_scores.json, scoring_provenance.json, architecture_summary.json, EVENTS_CATALOG.csv
  </div>
</header>

<nav class="tabs">
  <button class="tab-btn active" data-tab="overview">Overview</button>
  <button class="tab-btn" data-tab="levels">The 5 Levels</button>
  <button class="tab-btn" data-tab="architecture">Architecture Finding</button>
  <button class="tab-btn" data-tab="events">Event Catalog</button>
  <button class="tab-btn" data-tab="files">Code &amp; Data Files</button>
</nav>

<main>
  <section id="sec-overview" class="section active">
    <h2 class="section-title">How the scores come together</h2>
    <p class="section-lede">
      STAIR scores a learning management system on its architectural readiness to host an autonomous teaching agent.
      The pipeline takes raw evidence from the Moodle source tree, scores 28 sub-dimensions on a 0&ndash;4 ordinal scale,
      consolidates those scores into a 5&times;5 Table 3 matrix, and averages per level. Every step is shown below.
    </p>

    <div class="pipeline">
      <div class="pipeline-step"><h3>STEP 1 · RUBRIC</h3><p>Formal instrument defines 28 sub-dimensions grounded in Zimmerman SRL, Talebirad-Nadiri multi-agent, and Chu educational LLM theory.</p></div>
      <div class="pipeline-arrow">&rarr;</div>
      <div class="pipeline-step"><h3>STEP 2 · SCORE</h3><p>Each sub-dimension scored 0&ndash;4 with evidence from Moodle source (file paths, class names, constants).</p></div>
      <div class="pipeline-arrow">&rarr;</div>
      <div class="pipeline-step"><h3>STEP 3 · CONSOLIDATE</h3><p>Raw 0&ndash;4 scores mapped to percentages and averaged into a 5&times;5 (level &times; dimension) matrix.</p></div>
      <div class="pipeline-arrow">&rarr;</div>
      <div class="pipeline-step"><h3>STEP 4 · LEVEL AVG</h3><p>Each level's five consolidated cells averaged into the headline score.</p></div>
    </div>

    <h3 style="margin-top:32px;font-size:15px;color:var(--ink-soft);">Click a level to explore its sub-dimensions</h3>
    <div class="score-grid" id="overview-grid"></div>

    <div class="headline-finding">
      <strong>Headline empirical finding:</strong> the 28-percentage-point cliff between L2 Student State (53%) and L3 Agent Reasoning (25%) is the paper's central result. Its mechanism: the AI subsystem and the analytics framework share zero code-level imports in Moodle's codebase. See the <a href="#" data-tab-jump="architecture">Architecture Finding</a> tab for the evidence.
    </div>
  </section>

  <section id="sec-levels" class="section">
    <h2 class="section-title">The 5 Levels &mdash; sub-dimensions, evidence, consolidation</h2>
    <p class="section-lede">
      Click a level tab below, then click each sub-dimension to expand its definition, theoretical grounding, evidence from Moodle source, and which consolidated dimension (COV / ACC / EDU / TMP / INT) it contributes to.
    </p>
    <div class="level-tabs" id="level-tabs"></div>
    <div id="level-detail"></div>
  </section>

  <section id="sec-architecture" class="section">
    <h2 class="section-title">The architectural finding behind the L2&rarr;L3 cliff</h2>
    <p class="section-lede">
      Moodle scores well at L1 and L2 (the data layers exist) but collapses at L3 Agent Reasoning. The mechanism is not a missing feature &mdash; it is a missing <em>connection</em>. The AI subsystem and the analytics framework live in parallel, with zero shared code.
    </p>
    <div id="architecture-body"></div>
  </section>

  <section id="sec-events" class="section">
    <h2 class="section-title">Event Catalog &mdash; Moodle's 227 learning events</h2>
    <p class="section-lede">
      STAIR L1 Event Sensing scores 55% because Moodle emits a large, well-classified event stream. This table lists every event included in the analysis, its category, the learner action that triggers it, the SRL phase it supports, and the agent use case it enables.
    </p>
    <div id="events-body"></div>
  </section>

  <section id="sec-files" class="section">
    <h2 class="section-title">Every code and data file behind the paper's numbers</h2>
    <p class="section-lede">
      All files referenced here are present in the reproduction repository and are reachable from the repo root.
      The list is partitioned by role so a reader can navigate from a claim to the exact file that produces or documents it.
    </p>
    <div id="files-body"></div>
  </section>
</main>

<footer>
  STAIR Methodology Explorer &middot; generated from <code>scripts/build_methodology_explorer.py</code>.
  Re-run the generator whenever <code>analysis/data/*.json</code> or the scoring instrument changes.
</footer>

<script id="data-json" type="application/json">
{data_json}
</script>

<script>
'use strict';

const DATA = JSON.parse(document.getElementById('data-json').textContent);

function band(pct) {{
  if (pct >= 40) return 'green';
  if (pct >= 20) return 'amber';
  return 'red';
}}
function verdict(pct) {{
  if (pct >= 81) return 'Ready';
  if (pct >= 61) return 'Substantially Ready';
  if (pct >= 31) return 'Partially Ready';
  if (pct >= 11) return 'Nascent';
  return 'Absent';
}}

// --- TAB SWITCHING ---
document.querySelectorAll('.tab-btn').forEach(btn => {{
  btn.addEventListener('click', () => activateTab(btn.dataset.tab));
}});
document.querySelectorAll('[data-tab-jump]').forEach(el => {{
  el.addEventListener('click', e => {{ e.preventDefault(); activateTab(el.dataset.tabJump); }});
}});
function activateTab(name) {{
  document.querySelectorAll('.tab-btn').forEach(b => b.classList.toggle('active', b.dataset.tab === name));
  document.querySelectorAll('.section').forEach(s => s.classList.toggle('active', s.id === 'sec-' + name));
  window.scrollTo(0, 0);
}}

// --- OVERVIEW GRID ---
(function renderOverview() {{
  const grid = document.getElementById('overview-grid');
  DATA.levels.forEach(lv => {{
    const pct = lv.avg;
    const b = band(pct);
    const card = document.createElement('div');
    card.className = 'score-card ' + b;
    card.innerHTML = `
      <div class="level-id">${{lv.short}}</div>
      <div class="level-name">${{lv.display_name}}</div>
      <div class="score-big">${{pct}}%</div>
      <div class="verdict">${{verdict(pct)}}</div>
    `;
    card.addEventListener('click', () => {{
      activateTab('levels');
      selectLevel(lv.short);
    }});
    grid.appendChild(card);
  }});
}})();

// --- LEVEL TABS + DETAIL ---
const levelTabsEl = document.getElementById('level-tabs');
const levelDetailEl = document.getElementById('level-detail');
let currentLevel = DATA.levels[0].short;

(function renderLevelTabs() {{
  levelTabsEl.className = 'pipeline';
  DATA.levels.forEach(lv => {{
    const btn = document.createElement('div');
    btn.className = 'score-card ' + band(lv.avg);
    btn.style.cursor = 'pointer';
    btn.innerHTML = `
      <div class="level-id">${{lv.short}}</div>
      <div class="level-name">${{lv.display_name}}</div>
      <div class="score-big">${{lv.avg}}%</div>
    `;
    btn.addEventListener('click', () => selectLevel(lv.short));
    btn.dataset.lv = lv.short;
    levelTabsEl.appendChild(btn);
  }});
}})();

function selectLevel(short) {{
  currentLevel = short;
  document.querySelectorAll('#level-tabs .score-card').forEach(c => {{
    c.style.outline = c.dataset.lv === short ? '3px solid var(--accent)' : 'none';
  }});
  renderLevelDetail(short);
}}

function renderLevelDetail(short) {{
  const lv = DATA.levels.find(l => l.short === short);
  if (!lv) return;
  const b = band(lv.avg);
  const groundingSet = new Set();
  lv.sub_dimensions.forEach(sd => sd.grounding.forEach(g => groundingSet.add(g)));
  const gPills = Array.from(groundingSet).map(g =>
    `<span class="pill pill-${{g.toLowerCase()}}">${{g}} &middot; ${{DATA.grounding_codes[g]}}</span>`
  ).join('');

  const subdimRows = lv.sub_dimensions.map(sd => {{
    const sb = band(sd.pct);
    const gp = sd.grounding.map(g => `<span class="pill pill-${{g.toLowerCase()}}">${{g}}</span>`).join('');
    const rubricRows = Object.entries(DATA.rubric_scale).map(([k, v]) => {{
      const mark = parseInt(k) === sd.score ? '&#9679;' : '&#9675;';
      const em = parseInt(k) === sd.score ? 'style="font-weight:700;color:var(--accent);"' : '';
      return `<div ${{em}}>${{mark}} <strong>${{k}}</strong> &mdash; ${{v}}</div>`;
    }}).join('');

    return `
      <div class="subdim" data-sid="${{sd.id}}">
        <div class="subdim-head">
          <span class="chev">&#9656;</span>
          <span class="sid">${{sd.id.split('_')[0]}}</span>
          <span class="sname">${{sd.name}}</span>
          <span class="sgrounds">${{gp}}</span>
          <span class="sscore ${{sb}}">${{sd.score}}/4 &middot; ${{sd.pct}}%</span>
        </div>
        <div class="subdim-body">
          <h4>Definition</h4>
          <p>${{sd.definition}}</p>
          <h4>Rubric scale (highlighted = Moodle's score)</h4>
          <div style="font-size:13.5px;line-height:1.7;">${{rubricRows}}</div>
          <h4>Evidence from Moodle source</h4>
          <div class="evidence">${{sd.evidence || '(no evidence string recorded)'}}</div>
          <h4>Contributes to consolidated dimension</h4>
          <p><span class="pill">${{sd.contributes_to || '(mapping not found)'}}</span> within ${{short}}</p>
        </div>
      </div>`;
  }}).join('');

  // Consolidation cells for this level
  const cons = DATA.consolidation[short] || {{}};
  const consOrder = ['COV', 'ACC', 'EDU', 'TMP', 'INT'];
  const getVal = d => (cons[d] && cons[d].value != null) ? cons[d].value : 0;
  const consCells = consOrder.map(dim => {{
    const v = getVal(dim);
    const cb = band(v);
    return `<div class="cons-cell ${{cb}}"><div class="label">${{dim}}</div><div class="value">${{v}}</div></div>`;
  }}).join('');
  const consSum = consOrder.reduce((a, d) => a + getVal(d), 0);
  const consAvg = Math.round(consSum / consOrder.length);

  // Cell-by-cell derivation: how each of the 5 consolidated cells was computed
  // from its contributing sub-dimensions and their weights.
  const derivRows = consOrder.map(dim => {{
    const c = cons[dim] || {{ value: 0, sources: [] }};
    const cb = band(c.value);
    const srcRows = (c.sources || []).map(s => `
      <div class="deriv-src">
        <span class="mono">${{s.short_id}}</span>
        <span class="deriv-name">${{s.name}}</span>
        <span class="mono">${{s.raw}}/4 = ${{s.pct}}%</span>
        <span class="weight">\u00d7 ${{s.weight.toFixed(1)}}</span>
      </div>`).join('');
    let formula;
    if (c.sources && c.sources.length > 0) {{
      const numerTerms = c.sources.map(s => `${{s.pct}}\u00d7${{s.weight.toFixed(1)}}`).join(' + ');
      const denom = c.sources.reduce((a, s) => a + s.weight, 0);
      formula = `= (${{numerTerms}}) / ${{denom.toFixed(1)}} = <strong>${{c.value}}%</strong>`;
    }} else {{
      formula = '<em>(no sources mapped)</em>';
    }}
    return `
      <div class="deriv-cell">
        <div class="deriv-head">
          <span class="pill">${{dim}}</span>
          <span class="deriv-result ${{cb}}">= ${{c.value}}%</span>
        </div>
        <div class="deriv-sources">${{srcRows}}</div>
        <div class="deriv-formula">${{formula}}</div>
      </div>`;
  }}).join('');

  levelDetailEl.innerHTML = `
    <div class="level-header ${{b}}">
      <h3>${{lv.short}}: ${{lv.display_name}}</h3>
      <p style="margin:0;color:var(--ink-soft);">${{lv.question}}</p>
      <div class="big-score">${{lv.avg}}% &mdash; ${{verdict(lv.avg)}}</div>
      <div class="grounding-pills">${{gPills}}</div>
    </div>
    <div class="subdim-list">${{subdimRows}}</div>
    <div class="consolidation">
      <h3>Consolidation of ${{lv.short}} sub-dimensions into Table 3 row</h3>
      <p style="margin:0 0 10px;color:var(--ink-soft);font-size:13.5px;">
        Each raw 0&ndash;4 score converts to the percentage rubric (0 / 25 / 50 / 75 / 100) and maps into one or two consolidated dimensions. The per-dimension cells below are the weighted mean of the mapped sub-dimensions, which then average into the level score.
      </p>
      <div class="cells">${{consCells}}</div>
      <div class="calc">
        <strong>${{lv.short}} average</strong> = (${{consOrder.map(d => getVal(d)).join(' + ')}}) / 5
        = ${{consSum}} / 5 = <strong>${{consAvg}}%</strong>
      </div>

      <div class="deriv-header">Cell-by-cell derivation</div>
      <div class="deriv-grid">${{derivRows}}</div>
    </div>
  `;

  levelDetailEl.querySelectorAll('.subdim-head').forEach(h => {{
    h.addEventListener('click', () => h.parentElement.classList.toggle('open'));
  }});
}}

selectLevel(DATA.levels[0].short);

// --- ARCHITECTURE FINDING ---
(function renderArchitecture() {{
  const a = DATA.architecture;
  const iso = a.ai_analytics_isolation || {{}};
  document.getElementById('architecture-body').innerHTML = `
    <div class="isolation-banner">
      <h4>Zero cross-imports: the L2 &rarr; L3 cliff mechanism</h4>
      <p>
        A code-level scan of Moodle's <code>ai/</code> and <code>analytics/</code> subsystems produced
        <strong>${{iso.ai_references_analytics}}</strong> references from <code>ai/</code> to <code>core_analytics</code>
        and <strong>${{iso.analytics_references_ai}}</strong> references from <code>analytics/</code> to <code>core_ai</code>.
        Both directories exist, both contain substantial infrastructure, and neither imports from the other. That is the architectural reason the L3 cliff shows up in Moodle.
      </p>
    </div>

    <div class="arch-grid">
      <div class="arch-card">
        <h4>Web Service Functions</h4>
        <div class="count">${{a.web_services.count}}</div>
        <div class="path">${{a.web_services.file}}</div>
      </div>
      <div class="arch-card">
        <h4>AI Providers</h4>
        <div class="count">${{a.ai_providers.count}}</div>
        <ul>${{(a.ai_providers.providers || []).map(p => `<li>${{p}}</li>`).join('')}}</ul>
        <div class="path">${{a.ai_providers.path}}</div>
      </div>
      <div class="arch-card">
        <h4>AI Action Types</h4>
        <div class="count">${{a.ai_actions.count}}</div>
        <ul>${{(a.ai_actions.actions || []).map(p => `<li>${{p}}</li>`).join('')}}</ul>
        <div class="path">${{a.ai_actions.path}}</div>
      </div>
      <div class="arch-card">
        <h4>Analytics Prediction Targets</h4>
        <div class="count">${{a.analytics_targets.count}}</div>
        <ul>${{((a.analytics_targets.targets) || []).slice(0,8).map(p => `<li>${{p}}</li>`).join('')}}</ul>
      </div>
      <div class="arch-card">
        <h4>Scheduled Tasks</h4>
        <div class="count">${{a.scheduled_tasks.count}}</div>
      </div>
      <div class="arch-card" style="background:var(--red-soft);border-color:var(--red);">
        <h4>AI &harr; Analytics Imports</h4>
        <div class="count" style="color:var(--red);">0</div>
        <div class="path">The finding this paper is built on</div>
      </div>
    </div>
  `;
}})();

// --- EVENT CATALOG ---
(function renderEvents() {{
  const events = DATA.events;
  const body = document.getElementById('events-body');
  if (!events || events.length === 0) {{
    body.innerHTML = '<p style="color:var(--ink-soft);">Event catalog is empty.</p>';
    return;
  }}

  // Summary counts
  const byCat = {{}};
  const bySRL = {{}};
  const byLevel = {{}};
  events.forEach(e => {{
    byCat[e.Category] = (byCat[e.Category] || 0) + 1;
    bySRL[e['SRL Phase']] = (bySRL[e['SRL Phase']] || 0) + 1;
    byLevel[e['STAIR Level']] = (byLevel[e['STAIR Level']] || 0) + 1;
  }});

  const summaryCards = [
    {{h: 'Total events', c: events.length, path: '227 rows in EVENTS_CATALOG.csv'}},
    {{h: 'Categories', c: Object.keys(byCat).length, path: 'Course, User, Assignment, Quiz, ...'}},
    {{h: 'SRL phases covered', c: Object.keys(bySRL).length, path: 'Forethought, Performance, Reflection'}},
    {{h: 'STAIR levels involved', c: Object.keys(byLevel).length, path: 'L1 primary; L2-L5 downstream'}},
  ];

  const cats = Object.keys(byCat).sort();
  const srls = Object.keys(bySRL).sort();

  body.innerHTML = `
    <div class="events-summary">
      ${{summaryCards.map(s => `
        <div class="arch-card">
          <h4>${{s.h}}</h4>
          <div class="count">${{s.c}}</div>
          <div class="path">${{s.path}}</div>
        </div>`).join('')}}
    </div>
    <div class="events-filters">
      <label>Category:
        <select id="evt-cat">
          <option value="">all (${{events.length}})</option>
          ${{cats.map(c => `<option value="${{c}}">${{c}} (${{byCat[c]}})</option>`).join('')}}
        </select>
      </label>
      <label>SRL phase:
        <select id="evt-srl">
          <option value="">all</option>
          ${{srls.map(s => `<option value="${{s}}">${{s}} (${{bySRL[s]}})</option>`).join('')}}
        </select>
      </label>
      <label>Search: <input type="text" id="evt-search" placeholder="event name or trigger..."></label>
    </div>
    <div class="events-count" id="evt-count"></div>
    <table class="events-table"><thead><tr>
      <th>Event</th><th>Category</th><th>Trigger</th><th>SRL Phase</th><th>Agent Use Case</th><th>STAIR Level</th>
    </tr></thead><tbody id="evt-tbody"></tbody></table>
  `;

  function applyFilters() {{
    const cat = document.getElementById('evt-cat').value;
    const srl = document.getElementById('evt-srl').value;
    const q = document.getElementById('evt-search').value.toLowerCase();
    const rows = events.filter(e =>
      (!cat || e.Category === cat) &&
      (!srl || e['SRL Phase'] === srl) &&
      (!q || (e.Event + ' ' + e.Trigger + ' ' + e['Agent Use Case']).toLowerCase().includes(q))
    );
    document.getElementById('evt-count').textContent = rows.length + ' event(s) match';
    document.getElementById('evt-tbody').innerHTML = rows.slice(0, 200).map(r => `
      <tr>
        <td class="mono">${{r.Event}}</td>
        <td>${{r.Category}}</td>
        <td>${{r.Trigger}}</td>
        <td>${{r['SRL Phase']}}</td>
        <td>${{r['Agent Use Case']}}</td>
        <td>${{r['STAIR Level']}}</td>
      </tr>`).join('') + (rows.length > 200 ? '<tr><td colspan="6" style="text-align:center;color:var(--ink-faint);font-style:italic;">+ ' + (rows.length-200) + ' more (filter to narrow)</td></tr>' : '');
  }}
  ['evt-cat', 'evt-srl', 'evt-search'].forEach(id => {{
    document.getElementById(id).addEventListener('input', applyFilters);
  }});
  applyFilters();
}})();

// --- FILES ---
(function renderFiles() {{
  const groups = DATA.files;
  document.getElementById('files-body').innerHTML = `
    <div class="files-list">
      ${{Object.entries(groups).map(([group, items]) => `
        <div class="files-section-head">${{group}}</div>
        ${{items.map(f => `
          <div class="file-row">
            <div class="fname">${{f.path}}</div>
            <div class="fdesc">${{f.desc}}</div>
          </div>`).join('')}}
      `).join('')}}
    </div>
  `;
}})();
</script>
</body>
</html>
"""


# ---------------------------------------------------------------------------
# DATA PREP
# ---------------------------------------------------------------------------

LEVEL_NAMES = {
    "L1": "Event Sensing",
    "L2": "Student State",
    "L3": "Agent Reasoning",
    "L4": "Orchestration",
    "L5": "Intervention Delivery",
}
LEVEL_QUESTIONS = {
    "L1": "Can the platform detect what a student is doing?",
    "L2": "Can it maintain the student's accumulated learning trajectory?",
    "L3": "Can an agent reason over that state within pedagogical constraints?",
    "L4": "Can multiple agents coordinate without conflict?",
    "L5": "Can agents deliver interventions back into the learning flow?",
}
RAW_TO_PCT = {0: 0, 1: 25, 2: 50, 3: 75, 4: 100}


def prep_data():
    defs = load_json("sub_dimension_definitions.json")
    scores = load_json("moodle_scores.json")
    prov = load_json("scoring_provenance.json")
    table3 = load_json("table3_derived.json")
    arch = load_json("architecture_summary.json")
    paper_claims = load_json("paper_claims.json")
    events = load_events_csv()

    sd_defs = defs["sub_dimensions"]
    grounding_codes = defs["_meta"]["grounding_codes"]
    rubric_scale = defs["_meta"]["rubric_scale"]
    mapping = prov.get("mapping", {})

    # Build sub-dim -> consolidated dimension reverse lookup
    sd_to_cons = {}  # sd_id -> list of (level_short, dim)
    for level_long, cells in mapping.items():
        level_short = level_long.split("_")[0]
        for dim, celldata in cells.items():
            if dim in ("level_avg", "paper_reports", "discrepancy_note"):
                continue
            for src in celldata.get("sources", []):
                sid = src.get("raw_id")
                if sid:
                    sd_to_cons.setdefault(sid, []).append((level_short, dim))

    levels = []
    for level_long, level_data in scores["levels"].items():
        short = level_long.split("_")[0]
        sub_dims = []
        for sid, svals in level_data["sub_dimensions"].items():
            defn = sd_defs.get(sid, {})
            score_val = svals["score"]
            contributes = sorted({d for (_, d) in sd_to_cons.get(sid, [])})
            sub_dims.append({
                "id": sid,
                "name": defn.get("name", sid.replace("_", " ")),
                "grounding": defn.get("grounding", []),
                "definition": defn.get("definition", ""),
                "score": score_val,
                "pct": RAW_TO_PCT.get(score_val, 0),
                "evidence": svals.get("evidence", ""),
                "contributes_to": ", ".join(contributes) if contributes else "",
            })

        avg_consolidated = level_data.get("level_score_pct_consolidated", 0)
        levels.append({
            "short": short,
            "long": level_long,
            "display_name": LEVEL_NAMES.get(short, short),
            "question": LEVEL_QUESTIONS.get(short, ""),
            "avg": avg_consolidated,
            "sub_dimensions": sub_dims,
        })

    # Consolidation: each cell carries its computed value AND the sources that
    # produced it (with weights and percentages). The provenance file already
    # holds this in mapping[<level>].<DIM>.sources; we enrich each source with
    # its sub-dimension name for display and emit the derivation arithmetic.
    consolidation = {}
    for t3_level, t3_vals in table3.get("table3", {}).items():
        # t3_level like 'L1', mapping key is 'L1_Event_Sensing'
        prov_level_key = next(
            (k for k in mapping.keys() if k.startswith(t3_level + "_")),
            None,
        )
        prov_cells = mapping.get(prov_level_key, {}) if prov_level_key else {}

        cell_map = {}
        for dim in ("COV", "ACC", "EDU", "TMP", "INT"):
            cell = prov_cells.get(dim, {})
            sources = []
            for src in cell.get("sources", []):
                sid = src.get("raw_id", "")
                name = sd_defs.get(sid, {}).get("name", sid.split("_", 1)[-1].replace("_", " "))
                sources.append({
                    "id": sid,
                    "short_id": sid.split("_")[0] if sid else "",
                    "name": name,
                    "raw": src.get("raw_score", 0),
                    "pct": src.get("pct", 0),
                    "weight": src.get("weight", 0),
                })
            cell_map[dim] = {
                "value": t3_vals.get(dim, 0),
                "sources": sources,
            }
        consolidation[t3_level] = cell_map

    # Files list, grouped
    files = {
        "Analysis code (reproduces the paper's numbers)": [
            {"path": "analysis/code/derive_table3.py", "desc": "Canonical script. Maps 28 raw sub-dim scores into Table 3 (5×5 consolidated matrix) and averages each row. This is what produces 55/53/25/5/22."},
            {"path": "analysis/code/score_stair.py", "desc": "Secondary: raw arithmetic mean of sub-dim scores, plus 3-way weighting sensitivity analysis. Not the paper's reported numbers."},
            {"path": "analysis/code/analyze_architecture.py", "desc": "Scans Moodle source for web services, AI providers, analytics targets, and the AI↔analytics cross-import count (the paper's headline finding)."},
            {"path": "analysis/code/analyze_events.py", "desc": "Enumerates Moodle's 227+ event classes and categorises them by module, CRUD type, and education level."},
            {"path": "analysis/code/verify_claims.py", "desc": "Trust anchor: walks paper_claims.json and prints a PASS/FAIL table of every paper claim against reproduced values."},
            {"path": "analysis/code/paths.py", "desc": "Central path resolver used by all analysis scripts."},
        ],
        "Data (authoritative inputs)": [
            {"path": "analysis/data/sub_dimension_definitions.json", "desc": "Canonical definitions for the 28 sub-dimensions, with Z/T/H theoretical grounding codes and rubric scale."},
            {"path": "analysis/data/moodle_scores.json", "desc": "Per-sub-dimension raw 0-4 scores with one-line evidence strings (file paths, class names, constants)."},
            {"path": "analysis/data/scoring_provenance.json", "desc": "Maps each Table 3 cell to its source sub-dimensions, shows derivation and evidence for all 25 consolidated cells."},
            {"path": "analysis/data/table3_derived.json", "desc": "Computed output of derive_table3.py. Contains the 5×5 matrix and per-level averages."},
            {"path": "analysis/data/architecture_summary.json", "desc": "Computed output of analyze_architecture.py. Web service count (402), AI providers, AI actions, analytics targets, AI↔analytics isolation finding (0)."},
            {"path": "analysis/data/EVENTS_CATALOG.csv", "desc": "227 Moodle events with category, trigger, key payload fields, SRL phase, agent use case, and STAIR level mapping."},
            {"path": "analysis/data/paper_claims.json", "desc": "Machine-readable manifest of every quantitative claim in the paper with expected value, tolerance, source script, and data source."},
        ],
        "Instruments and documentation": [
            {"path": "analysis/instruments/STAIR_SCORING_INSTRUMENT.md", "desc": "Formal scoring rubric. Establishes the 0-4 ordinal scale, evidence criteria, minimum-threshold rule, and theoretical grounding framework."},
            {"path": "docs/CLAIMS_MAP.md", "desc": "Per-claim provenance map: every number in the paper → the producing script and data file."},
            {"path": "docs/REPRODUCE.md", "desc": "Plain-prose reproduction guide for non-technical readers."},
            {"path": "docs/SCORING_METHODOLOGY.md", "desc": "Reader-friendly explainer of the rubric, the consolidation mapping, and the raw vs consolidated distinction."},
            {"path": "docs/MOODLE_PINNED_COMMIT.md", "desc": "Pinned Moodle commit SHA and verify commands."},
        ],
        "Reproduction harness": [
            {"path": "reproduce.py", "desc": "One-command entry point. Verifies environment, fetches pinned Moodle commit, runs analysis, verifies claims. Exit 0 iff every claim reproduces."},
            {"path": "scripts/fetch_moodle.sh", "desc": "Bash script to clone Moodle at the pinned SHA."},
            {"path": "scripts/fetch_moodle.ps1", "desc": "PowerShell equivalent for Windows."},
            {"path": "scripts/verify_environment.py", "desc": "Checks Python version, required packages, and git availability."},
            {"path": "scripts/build_methodology_explorer.py", "desc": "Regenerates this explorer from the data files. Re-run whenever data changes."},
        ],
    }

    return {
        "levels": levels,
        "consolidation": consolidation,
        "architecture": arch,
        "events": events,
        "grounding_codes": grounding_codes,
        "rubric_scale": rubric_scale,
        "paper_claims": paper_claims.get("claims", []),
        "files": files,
    }


def main():
    data = prep_data()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    html = render_html(data)
    OUTPUT_PATH.write_text(html, encoding="utf-8")
    size_kb = OUTPUT_PATH.stat().st_size / 1024
    print(f"OK: {OUTPUT_PATH.relative_to(REPO_ROOT)} ({size_kb:.1f} KB)")
    print(f"Open: file:///{OUTPUT_PATH.as_posix()}")


if __name__ == "__main__":
    main()
