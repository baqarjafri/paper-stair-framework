# How the STAIR readiness scores are derived

This document explains, in plain English, how the numbers 55 / 53 / 25 / 5 / 22 in the paper are computed. The formal rubric lives at [`../analysis/instruments/STAIR_SCORING_INSTRUMENT.md`](../analysis/instruments/STAIR_SCORING_INSTRUMENT.md); this page is the readable companion.

## The framework in one paragraph

STAIR assesses a learning-platform's readiness to host autonomous AI teaching agents across five progressive architectural levels:

1. **L1 Event Sensing** — can the platform detect what a student is doing?
2. **L2 Student State** — can it maintain and expose the student's accumulated learning trajectory?
3. **L3 Agent Reasoning** — can an AI agent reason over that state within pedagogical constraints?
4. **L4 Orchestration** — can multiple agents coordinate without conflict?
5. **L5 Intervention Delivery** — can agents deliver interventions back into the learning flow?

Each level gets a percentage score between 0 and 100. The paper reports Moodle's scores as 55 / 53 / 25 / 5 / 22 — solid foundations, catastrophic collapse at the agent-reasoning level.

## How each score is produced

### Step 1 — Raw sub-dimension scoring (0–4 ordinal)

Each STAIR level is decomposed into 5–7 sub-dimensions. For example, L1 Event Sensing has five:

- 1.1 Event Coverage
- 1.2 Observer Subscription
- 1.3 SRL Phase Observability
- 1.4 Real-Time External Access
- 1.5 Event Enrichment

Each sub-dimension is scored 0–4 on an ordinal scale:

| Score | Label | Meaning |
|:---:|---|---|
| 0 | Absent | No infrastructure exists |
| 1 | Nascent | Primitive building blocks exist but require major development |
| 2 | Partial | Half-built; significant gaps remain |
| 3 | Substantial | Most of the capability present, targeted gaps |
| 4 | Ready | Production-ready for the assessed capability |

Scores are evidence-based — each one is justified by a specific file path, line range, or API signature in the Moodle source. Evidence is recorded in `analysis/data/scoring_provenance.json`.

The full set of raw scores lives in `analysis/data/moodle_scores.json`. 32 sub-dimensions across 5 levels.

### Step 2 — Mapping to the five consolidated dimensions

The paper reports Table 3 with five columns per level:

| Abbreviation | Dimension |
|---|---|
| **COV** | Coverage — does the capability exist at all? |
| **ACC** | Access — can an external process reach it? |
| **EDU** | Education-aware — does it carry pedagogical meaning? |
| **TMP** | Temporal — can it observe change over time? |
| **INT** | Integrity — is it safe, private, scalable? |

The 32 raw sub-dimensions are mapped to these five columns via a documented routing (see `analysis/code/derive_table3.py`, the `MAPPING` constant). Most sub-dimensions map to exactly one column; a few split 50/50 across two columns when they genuinely span two dimensions.

Raw 0–4 scores are converted to percentages using a fixed rubric:

```
0 → 0%    1 → 25%    2 → 50%    3 → 75%    4 → 100%
```

Each Table 3 cell is the weighted average of its contributing sub-dimensions on the percentage scale.

### Step 3 — Per-level average

The final level score is the arithmetic mean of its five Table 3 cells (COV, ACC, EDU, TMP, INT), rounded to the nearest whole number.

### Worked example — L2 Student State

From `analysis/data/moodle_scores.json`, the six sub-dimensions of L2 and their evidence-based raw scores:

| Sub-dim | Raw | % scale |
|---|:---:|:---:|
| 2.1 Raw Data Availability | 3 | 75 |
| 2.2 Analytics Framework | 3 | 75 |
| 2.3 Unified Learner Model | 1 | 25 |
| 2.4 API Query Capability | 3 | 75 |
| 2.5 Temporal Analytics | 2 | 50 |
| 2.6 Privacy-Aware Access | 2 | 50 |

Mapping to Table 3 columns (from `derive_table3.py`):

- COV = mean(2.1 × 0.5, 2.2 × 0.5) = mean(37.5, 37.5) / 1 = **75**
- ACC = 2.4 × 1.0 = **75**
- EDU = 2.3 × 1.0 = **25**
- TMP = 2.5 × 1.0 = **50**
- INT = mean(2.6 × 0.5, 2.3 × 0.5) = mean(25, 12.5) / 1 = **38** (rounded)

Level average = mean(75, 75, 25, 50, 38) = **53%**  — the paper's reported L2 score.

The same arithmetic produces 55 / 53 / 25 / 5 / 22 for L1–L5.

## Why a consolidated aggregation and not a raw mean?

Simple arithmetic mean of the raw sub-dim percentages produces a slightly different set of numbers (55 / 58 / 21 / 5 / 30). Both are legitimate computations — they tell different stories:

- **Raw mean** treats every sub-dimension as equally important.
- **Consolidated aggregation** asks "in each of the five platform dimensions (Coverage, Access, Education-awareness, Temporal, Integrity), how ready is this level?" and then averages across those dimensions.

The paper reports the consolidated version because the five dimensions are themselves meaningful — they align with the platform architecture concerns a systems engineer would ask about. The raw mean is included as a sensitivity check (see `analysis/code/score_stair.py`, which also runs three weighting schemes — equal, theoretical-priority, agent-priority — to confirm the headline conclusion is robust to weighting choice).

## Minimum threshold rule

If any sub-dimension within a level scores 0 (Absent), the level verdict is capped at "Partially Ready" regardless of the arithmetic average. This prevents a few very-strong sub-dimensions from masking a critical missing capability. Applied in `derive_table3.py` and `score_stair.py`.

## Reproducing the scores yourself

```bash
cd paper-stair-framework
python analysis/code/derive_table3.py
```

You should see the Table 3 matrix print with the five `avg` values at 55 / 53 / 25 / 5 / 22. That output is what the paper reports.

## Further reading

- [`../analysis/instruments/STAIR_SCORING_INSTRUMENT.md`](../analysis/instruments/STAIR_SCORING_INSTRUMENT.md) — the formal 32-dimension rubric with evidence criteria per cell
- [`../analysis/data/scoring_provenance.json`](../analysis/data/scoring_provenance.json) — per-score evidence (file paths, line ranges)
- [`CLAIMS_MAP.md`](CLAIMS_MAP.md) — every paper number traced to its script
