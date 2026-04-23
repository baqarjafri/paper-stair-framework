# Moodle pinned commit — the exact version this paper analyses

For the paper's findings to be reproducible, the analysis must run against the exact Moodle source that was examined. This document records the pinned commit and how to verify you have the right one.

## Pinned commit

| Field | Value |
|---|---|
| **Commit SHA** | `213a869e7ffd48d3a5679818bcddbb22dbc31aa5` |
| **Committed on** | 2026-03-20 15:12:29 +1100 |
| **Commit message** | `on-demand release 5.2dev+` |
| **Branch at pin time** | `main` |
| **Build label** | Moodle 5.2dev+ |
| **Upstream repository** | https://github.com/moodle/moodle |

## How the reproduction uses this

When you run `python reproduce.py` for the first time, it calls `scripts/fetch_moodle.sh` (Linux/macOS) or `scripts/fetch_moodle.ps1` (Windows), which runs:

```bash
git clone https://github.com/moodle/moodle.git moodle_src
cd moodle_src
git checkout 213a869e7ffd48d3a5679818bcddbb22dbc31aa5
```

After that, every analysis script runs against the Moodle tree at exactly this SHA.

## How to verify you have the right commit

```bash
cd moodle_src
git rev-parse HEAD
```

Should print:
```
213a869e7ffd48d3a5679818bcddbb22dbc31aa5
```

If it prints anything else, you are not looking at the same Moodle the paper analysed, and the reproduced numbers may differ. Run `scripts/fetch_moodle.*` again to correct.

## Why this specific commit

The paper's scoring is grounded in evidence from specific file paths and line ranges in the Moodle source (recorded in `analysis/data/scoring_provenance.json`). Moodle is under active development on `master` / `main` — refactors, renames, and new features happen weekly. Pinning to an SHA makes the analysis immutable: the commit will be fetchable from `github.com/moodle/moodle` indefinitely, and its contents cannot change.

This specific build (`5.2dev+`, March 2026) was chosen because it represents the state of Moodle immediately before the AITHE-2026 paper deadline and includes all the AI subsystem features discussed in the paper (the `core_ai` module, six LLM providers, four AI action types).

## If this commit disappears

The risk is low but not zero: if Moodle ever deletes the `moodle/moodle` repository or force-pushes over history, the pinned SHA becomes unreachable. Mitigations:

1. **GitHub keeps commits fetchable** even if they are no longer on any branch, provided the repository still exists.
2. As a backup, the key filesystem facts the paper depends on are recorded in `../analysis/data/architecture_summary.json` (committed to this repo). If Moodle vanishes, the JSON preserves the counts that `analyze_architecture.py` produced against this commit.
3. If you need the raw source and GitHub no longer serves it, the full Moodle source is also mirrored on SourceForge and at the Moodle Association's own Git server (`git.moodle.org`).

## Bumping to a newer Moodle commit

Post-submission, if a journal extension prompts a re-analysis against a newer Moodle version, the update is a one-line edit in two files:

```
scripts/fetch_moodle.sh  : PINNED_SHA="<new-sha>"
scripts/fetch_moodle.ps1 : $PinnedSha = "<new-sha>"
```

Then re-run `python reproduce.py` and check that the claims still pass. If any claim drifts, update `analysis/data/moodle_scores.json` to reflect the new evidence, update the paper text, and re-run verify. Never bump the SHA without re-verifying.
