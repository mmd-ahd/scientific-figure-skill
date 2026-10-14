#!/usr/bin/env bash
# Build scientific-figure.zip: the skill folder as claude.ai expects it (a top-level
# `scientific-figure/` directory containing SKILL.md), without dev-only files.
#   bash scripts/tools/build_skill_zip.sh [outdir]
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
OUT="$(mkdir -p "${1:-$ROOT/dist}" && cd "${1:-$ROOT/dist}" && pwd)"
STAGE="$(mktemp -d)"
trap 'rm -rf "$STAGE"' EXIT
DEST="$STAGE/scientific-figure"
mkdir -p "$DEST"
cp -r "$ROOT"/SKILL.md "$ROOT"/LICENSE "$ROOT"/THIRD_PARTY.md "$ROOT"/README.md "$ROOT"/pyproject.toml \
      "$ROOT"/scripts "$ROOT"/styles "$ROOT"/references "$ROOT"/assets "$DEST"/
mkdir -p "$DEST/examples"
cp "$ROOT"/examples/*.png "$DEST/examples/"      # PNG previews only; PDFs live in the repo
find "$DEST" -name "__pycache__" -type d -prune -exec rm -rf {} +
rm -f "$OUT/scientific-figure.zip"
(cd "$STAGE" && zip -qr "$OUT/scientific-figure.zip" scientific-figure)
echo "wrote $OUT/scientific-figure.zip ($(du -h "$OUT/scientific-figure.zip" | cut -f1))"
