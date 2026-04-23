# Claims Map — every number in the paper, traced to its producing script

Each quantitative claim in the paper is backed by a script and a data source. This table is the spine of reproducibility — running `python reproduce.py` loads `analysis/data/paper_claims.json` (the machine-readable version of this table) and verifies each row. Exit code 0 means every row passed.

If you see a number in the paper that is not in this table, one of two things is true:
1. It is a qualitative label (not a reproducible quantity), or
2. The claim was introduced during revision without updating the manifest — please open an issue.

## Headline claims (Table 3, Abstract, Fig 1 teaser)

| # | Paper section | Claim | Producing script | Data source | Output key |
|---|---|---|---|---|---|
| 1 | §5 Results (Table 3) | L1 Event Sensing readiness = **55%** | `analysis/code/derive_table3.py` | `analysis/data/moodle_scores.json` | `table3.L1.avg` |
| 2 | §5 Results (Table 3) | L2 Student State readiness = **53%** | `analysis/code/derive_table3.py` | `analysis/data/moodle_scores.json` | `table3.L2.avg` |
| 3 | §5 Results (Table 3) | L3 Agent Reasoning readiness = **25%** | `analysis/code/derive_table3.py` | `analysis/data/moodle_scores.json` | `table3.L3.avg` |
| 4 | §5 Results (Table 3) | L4 Orchestration readiness = **5%** | `analysis/code/derive_table3.py` | `analysis/data/moodle_scores.json` | `table3.L4.avg` |
| 5 | §5 Results (Table 3) | L5 Intervention Delivery readiness = **22%** | `analysis/code/derive_table3.py` | `analysis/data/moodle_scores.json` | `table3.L5.avg` |
| 6 | §5 Results, Abstract, Fig 1 teaser | **28-point cliff** between L2 and L3 | derived: `table3.L2.avg - table3.L3.avg` | same | computed |

## Architecture claims (central finding)

| # | Paper section | Claim | Producing script | Data source | Output key |
|---|---|---|---|---|---|
| 7 | §5 Results (central finding) | **Zero cross-imports** between `core_ai` and `core_analytics` | `analysis/code/analyze_architecture.py` | `moodle_src/ai/`, `moodle_src/analytics/` | `ai_analytics_isolation.isolated` |
| 8 | §5 Results | `core_ai` references to `core_analytics` = **0** | `analysis/code/analyze_architecture.py` | `moodle_src/ai/` | `ai_analytics_isolation.ai_references_analytics` |
| 9 | §5 Results | `core_analytics` references to `core_ai` = **0** | `analysis/code/analyze_architecture.py` | `moodle_src/analytics/` | `ai_analytics_isolation.analytics_references_ai` |

## Moodle inventory claims

| # | Paper section | Claim | Producing script | Data source | Output key |
|---|---|---|---|---|---|
| 10 | §5 Results | **402 web service functions** | `analysis/code/analyze_architecture.py` | `moodle_src/lib/db/services.php` | `web_services.count` |
| 11 | §5 Results | **6 AI providers** (OpenAI, Azure, AWS Bedrock, Gemini, DeepSeek, Ollama) | `analysis/code/analyze_architecture.py` | `moodle_src/ai/provider/` | `ai_providers.count` |
| 12 | §5 Results | **4 AI action types** (generate_text, generate_image, summarise_text, explain_text) | `analysis/code/analyze_architecture.py` | `moodle_src/ai/classes/aiactions/` | `ai_actions.count` |
| 13 | §5 Results | **8 analytics prediction targets** | `analysis/code/analyze_architecture.py` | `moodle_src/course/classes/analytics/target/` | `analytics_targets.count` |

## How this table is enforced

The machine-readable version at `analysis/data/paper_claims.json` has one entry per row above, each with an `expected` value and a `tolerance`. `verify_claims.py` reads the output JSON from the producing script, walks the `output_key` path, and compares to `expected`. Any drift beyond `tolerance` prints `FAIL` and exits nonzero. A pre-push sanity check in the [paper-repo sync workflow](REPRODUCE.md) makes claim drift visible before a commit goes public.

## Updating this manifest

If the paper's quantitative claims change (they shouldn't, but if they do — e.g., a reviewer asks for a re-analysis), update both:

1. This table (`docs/CLAIMS_MAP.md`)
2. The machine-readable version (`analysis/data/paper_claims.json`)
3. The paper text itself

...in the same commit. The reproduction pipeline will refuse to pass otherwise.
