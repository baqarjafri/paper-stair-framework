# STAIR — Reproducibility Repository

*Scaffold for Teaching Agent Reasoning Readiness — Evaluating Moodle's Architecture for AI Teaching Agent Reasoning*

**Paper:** AITHE 2026, Swansea, UK (July 1–3, 2026) — AHEAD stream
**Author:** Baqar Jafri, University of Stirling
**Contact:** baqar@nexgenclass.com
**License:** MIT (code) · CC-BY-4.0 (paper and figures)

---

## What this is

This repository contains everything needed to reproduce the quantitative findings of the STAIR paper from scratch. The paper evaluates the open-source Moodle 5.2dev+ learning management system against five progressive levels of AI teaching-agent readiness (Event Sensing, Student State, Agent Reasoning, Orchestration, Intervention Delivery) and reports that Moodle is ready at the lower data-sensing levels (L1=55%, L2=53%) but collapses 28 percentage points at the agent-reasoning level (L3=25%) because Moodle's AI subsystem and analytics framework share zero code-level imports.

Running **one command** (`python reproduce.py`) re-derives every number in the paper from source: it fetches the exact Moodle commit that was analysed, runs the scoring scripts, regenerates the figures, and prints a side-by-side table comparing each paper claim to its reproduced value.

---

## Quick reproduction (one command)

```bash
git clone https://github.com/baqarjafri/paper-stair-framework.git
cd paper-stair-framework
python reproduce.py
```

You should see output ending like this:

```
PAPER CLAIM                                             REPRODUCED  MATCH
-----------------------------------------------------------------------
L1 Event Sensing readiness = 55%                        55          PASS
L2 Student State readiness = 53%                        53          PASS
L3 Agent Reasoning readiness = 25%                      25          PASS
L4 Orchestration readiness = 5%                         5           PASS
L5 Intervention Delivery readiness = 22%                22          PASS
28-point cliff between L2 (53%) and L3 (25%)            28          PASS
Zero cross-imports between core_ai and core_analytics   True        PASS
core_ai references to core_analytics = 0                0           PASS
core_analytics references to core_ai = 0                0           PASS
402 web service functions                               402         PASS
6 AI providers                                          6           PASS
4 AI action types                                       4           PASS
8 analytics prediction targets                          8           PASS
-----------------------------------------------------------------------
13 matched, 0 drifted, 13 total.
```

Exit code `0` means every claim in the paper matches the code's output. Exit code nonzero means at least one number drifted — the PAPER CLAIM vs REPRODUCED table tells you which.

---

## Prerequisites

| Tool | Version | Why |
|---|---|---|
| Python | 3.10 or newer | All analysis scripts are pure Python |
| Git | any recent | Used to fetch the pinned Moodle commit |
| Disk | ~2 GB free | Moodle source tree is ~1.8 GB |
| Internet | one-time | Only needed the first time you run `reproduce.py` |

No PHP, no Node.js, no Docker, no Jupyter. The paper build chain (Word / docx / PDF export) is separate and **not required** for reproduction — you only need it if you want to rebuild the paper PDF itself.

The reproduction script installs no packages automatically. If `verify_environment.py` reports missing packages, run:

```bash
python -m pip install -r requirements.txt
```

---

## What gets reproduced

Every quantitative claim the paper makes is backed by a producing script and a data file. The manifest lives at `analysis/data/paper_claims.json`. See [`docs/CLAIMS_MAP.md`](docs/CLAIMS_MAP.md) for the section-by-section map.

| Claim | Producing script | Data source |
|---|---|---|
| L1–L5 readiness scores (55/53/25/5/22) | `analysis/code/derive_table3.py` | `analysis/data/moodle_scores.json` |
| L2→L3 28-point cliff | derived from Table 3 | same |
| Zero cross-imports AI ↔ analytics | `analysis/code/analyze_architecture.py` | `moodle_src/ai/`, `moodle_src/analytics/` |
| 402 web service functions | `analysis/code/analyze_architecture.py` | `moodle_src/lib/db/services.php` |
| 6 AI providers, 4 AI action types | `analysis/code/analyze_architecture.py` | `moodle_src/ai/` tree |
| 8 analytics prediction targets | `analysis/code/analyze_architecture.py` | `moodle_src/course/classes/analytics/target/` |
| Paper figures (5 PNGs) | `analysis/code/generate_figures.py` | all of the above |

---

## Interactive methodology explorer

A self-contained HTML walkthrough of the full scoring methodology lives at [`docs/methodology_explorer.html`](docs/methodology_explorer.html). Open it in any browser to navigate the five STAIR levels, click into each sub-dimension to see its definition, theoretical grounding, raw 0-4 score, the source-code evidence behind that score, and how every cell of Table 3 was derived. It also carries the architecture finding (zero AI-analytics cross-imports) and a searchable browser of Moodle's 227 learning events. Works offline, no dependencies, no build step. Regenerated from the data files by `scripts/build_methodology_explorer.py`.

---

## Paper PDF

Open [`paper/Paper_1_STAIR_AITHE2026.pdf`](paper/Paper_1_STAIR_AITHE2026.pdf) to read the paper without running anything. GitHub renders PDFs inline in the browser.

---

## Repository layout

```
paper-stair-framework/
├── README.md                    ← you are here
├── LICENSE                      ← MIT (covers all code)
├── LICENSE-CC-BY-4.0            ← CC-BY-4.0 (covers paper and figures)
├── CITATION.cff                 ← machine-readable citation
├── requirements.txt             ← Python dependencies
├── reproduce.py                 ← ONE-COMMAND entry point
│
├── paper/                       ← compiled PDF (for GitHub's inline viewer)
│   └── Paper_1_STAIR_AITHE2026.pdf
│
├── figures/                     ← rendered paper figures (5 PNGs)
│
├── analysis/                    ← the reproduction bundle
│   ├── code/                    ← scoring + analysis scripts
│   ├── data/                    ← raw sub-dim scores, provenance, manifests
│   ├── instruments/             ← formal STAIR scoring rubric
│   └── outputs/                 ← regenerated each run (gitignored)
│
├── scripts/                     ← reproduction helpers
│   ├── fetch_moodle.sh          ← git clone pinned commit (Bash)
│   ├── fetch_moodle.ps1         ← same for Windows PowerShell
│   └── verify_environment.py    ← Python + package check
│
└── docs/                        ← user-facing reproduction docs
    ├── REPRODUCE.md             ← plain-prose step-by-step
    ├── CLAIMS_MAP.md            ← every paper number → producing script
    ├── SCORING_METHODOLOGY.md   ← rubric explainer
    └── MOODLE_PINNED_COMMIT.md  ← exact commit SHA, date, how to verify
```

The paper's canonical form is the compiled PDF under `paper/`. This repository's job is to let you reproduce the paper's quantitative findings from the Moodle source — not to show how the document itself was typeset.

---

## For readers who don't code

If command lines are not your world, [`docs/REPRODUCE.md`](docs/REPRODUCE.md) walks through the entire reproduction in full prose — how to install Python, how to install Git, how to run one command, and what each output means.

---

## Citation

```bibtex
@inproceedings{jafri2026stair,
  title     = {{STAIR}: {S}caffold for {T}eaching {A}gent {R}easoning {R}eadiness --
               Evaluating {M}oodle's {A}rchitecture for {AI} {T}eaching {A}gent {R}easoning},
  author    = {Jafri, Baqar},
  booktitle = {Proceedings of AITHE 2026 --- Artificial Intelligence and the
               Transformation of Higher Education Symposium},
  address   = {Swansea, United Kingdom},
  year      = {2026},
  month     = jul,
  url       = {https://github.com/baqarjafri/paper-stair-framework}
}
```

Machine-readable citation metadata: [`CITATION.cff`](CITATION.cff)

---

## License

- **Code** (`analysis/`, `scripts/`, `reproduce.py`) — MIT. See [`LICENSE`](LICENSE).
- **Paper and figures** (`paper/`, `figures/`) — CC-BY-4.0. See [`LICENSE-CC-BY-4.0`](LICENSE-CC-BY-4.0).

The Moodle source code (fetched by `scripts/fetch_moodle.*`) is the work of the Moodle community and is licensed under GNU GPL v3+. This repository includes no Moodle source directly; it clones it on demand.

---

## Contact

Baqar Jafri — `baqar@nexgenclass.com`
University of Stirling, Computing Science and Mathematics (MSc in Artificial Intelligence)
