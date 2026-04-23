# How to reproduce the STAIR paper's findings — step by step

This document walks you through reproducing every quantitative claim in the paper, assuming you have used a command line before but are not a professional programmer. Total time from a clean machine: about 10 minutes, most of which is one-time setup (Python, Git, Moodle download).

## What you need before you start

1. **A computer** running Windows, macOS, or Linux.
2. **Python 3.10 or newer** — download from [python.org](https://www.python.org/downloads/). On Windows, during install, tick "Add Python to PATH".
3. **Git** — download from [git-scm.com](https://git-scm.com/downloads).
4. **About 2 GB of free disk space** for the Moodle source code.
5. **An internet connection** — needed once, to fetch Moodle.

You do not need to install PHP, Node.js, Docker, Jupyter, or any database. The reproduction is pure Python.

## Step 1 — Open a terminal

- **Windows**: press Start, type "PowerShell", press Enter.
- **macOS**: press Cmd-Space, type "Terminal", press Enter.
- **Linux**: use your distribution's terminal application.

You should see a prompt ending in `>` (Windows) or `$` (macOS/Linux).

## Step 2 — Confirm Python and Git are installed

Type:

```
python --version
git --version
```

You should see something like `Python 3.12.0` and `git version 2.40.1`. If either says "command not found" or similar, re-install from the links in the prerequisites.

## Step 3 — Clone this repository

```
git clone https://github.com/baqarjafri/paper-stair-framework.git
cd paper-stair-framework
```

This creates a new folder `paper-stair-framework` in your current directory and moves into it. The download is small (~5 MB) because the Moodle source is fetched separately.

## Step 4 — Install the Python packages

```
python -m pip install -r requirements.txt
```

This installs three packages: `matplotlib`, `seaborn`, `numpy`. Install takes under a minute.

## Step 5 — Run the reproduction

```
python reproduce.py
```

You will see seven steps print one after another:

1. **Verifying Python environment** — checks your Python and packages.
2. **Fetching Moodle source** — downloads Moodle at the exact commit analysed in the paper. This takes 2–5 minutes on first run depending on your connection. If you re-run later, it skips this step.
3. **Analyzing Moodle architecture** — counts events, web service functions, AI providers, and checks the zero-cross-import claim.
4. **Deriving Table 3 consolidated scores** — applies the paper's scoring rubric to produce L1–L5 readiness percentages.
5. **Computing raw STAIR readiness** — secondary sensitivity analysis (not the paper's headline numbers).
6. **Verifying every paper claim** — this is the important step. You will see a table like:

   ```
   PAPER CLAIM                                             REPRODUCED  MATCH
   L1 Event Sensing readiness = 55%                        55          PASS
   L2 Student State readiness = 53%                        53          PASS
   ...
   13 matched, 0 drifted, 13 total.
   ```

7. **Summary** — a banner telling you whether reproduction succeeded.

If every row says `PASS` and the script exits without an error, the paper is fully reproduced.

## What the output means

Each row in the verification table has three parts:

- **PAPER CLAIM** — what the paper reports.
- **REPRODUCED** — what the code just computed from the Moodle source.
- **MATCH** — `PASS` if the two agree, `FAIL` otherwise.

A `FAIL` means the code and the paper disagree. This could be because:

- Moodle has been updated and the pinned commit is no longer fetchable (very unlikely — commits are immutable).
- Someone edited `analysis/data/moodle_scores.json` and forgot to update the paper.
- The paper was revised but the manifest `analysis/data/paper_claims.json` was not.

## If something goes wrong

### "Python command not found"

Make sure Python is on your PATH. On Windows, re-run the installer and tick the "Add Python to PATH" checkbox. On macOS/Linux, try `python3` instead of `python`.

### "Permission denied" when running scripts

On macOS/Linux, the fetch script may need execute permission:

```
chmod +x scripts/fetch_moodle.sh
```

### Moodle fetch fails

Check your internet connection and that you can reach GitHub. If your institution blocks git over HTTPS, try fetching over SSH:

```
cd moodle_src 2>/dev/null || git clone git@github.com:moodle/moodle.git moodle_src
cd moodle_src && git checkout 213a869e7ffd48d3a5679818bcddbb22dbc31aa5
cd ..
python reproduce.py
```

### Numbers almost match but are slightly different

Some claims have a small tolerance (e.g., web service count ±5) to absorb harmless drift from Moodle's ongoing development on `master`. The reproduction pins a specific commit so this should not happen, but if you re-run after someone bumped the SHA in `scripts/fetch_moodle.*`, a small drift is expected.

## Next steps

- Read [`CLAIMS_MAP.md`](CLAIMS_MAP.md) to see which paper section each number comes from.
- Read [`SCORING_METHODOLOGY.md`](SCORING_METHODOLOGY.md) to understand the 28-sub-dimension rubric.
- Open `paper/Paper_1_STAIR_AITHE2026.pdf` to read the paper itself.
- Open `analysis/outputs/` to inspect the JSON that `reproduce.py` generated.

## Contact

Questions, problems, or corrections: `baqar@nexgenclass.com`.
