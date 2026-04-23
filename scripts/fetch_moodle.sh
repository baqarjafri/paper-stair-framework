#!/usr/bin/env bash
# fetch_moodle.sh — clone Moodle at the exact commit analysed by the paper.
#
# Pinned to commit: 213a869e7ffd48d3a5679818bcddbb22dbc31aa5
# Date:             2026-03-20
# Branch at pin:    main
# Build label:      Moodle 5.2dev+ (on-demand release)
#
# Running this script is idempotent. Safe to re-run.
#
# Usage:
#   bash scripts/fetch_moodle.sh
#
set -euo pipefail

PINNED_SHA="213a869e7ffd48d3a5679818bcddbb22dbc31aa5"
REPO_URL="https://github.com/moodle/moodle.git"
TARGET="moodle_src"

# Resolve repo root = parent of this script's directory
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &> /dev/null && pwd)"
REPO_ROOT="$(cd -- "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_ROOT"

echo "Fetching Moodle source at pinned commit $PINNED_SHA"
echo "Target directory: $REPO_ROOT/$TARGET"
echo

if [ -d "$TARGET/.git" ]; then
  echo "Existing clone found. Fetching and checking out pinned commit..."
  cd "$TARGET"
  git fetch --depth 1 origin "$PINNED_SHA"
  git checkout "$PINNED_SHA"
else
  echo "No existing clone. Cloning Moodle..."
  git clone "$REPO_URL" "$TARGET"
  cd "$TARGET"
  git checkout "$PINNED_SHA"
fi

echo
echo "Moodle is now at commit:"
git log -1 --format='  %H%n  %ci%n  %s'
echo
echo "Done. Moodle source ready at: $REPO_ROOT/$TARGET"
