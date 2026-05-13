#!/usr/bin/env bash
# Convert ISMS document (PDF/DOCX) to markdown via markitdown.
#
# Usage:
#   ./convert.sh <input-file> <output-markdown>
#
# Requires:
#   - markitdown (v0.1.5+)
#   - Python at the configured path

set -e

PY="${PYTHON_BIN:-python}"

if [ $# -lt 2 ]; then
  echo "Usage: $0 <input-file> <output-markdown>" >&2
  exit 1
fi

INPUT="$1"
OUTPUT="$2"

if [ ! -f "$INPUT" ]; then
  echo "Input file not found: $INPUT" >&2
  exit 1
fi

if [ ! -x "$PY" ]; then
  echo "Python not executable at: $PY" >&2
  echo "Set PYTHON_BIN environment variable to correct path" >&2
  exit 1
fi

echo "Converting $INPUT -> $OUTPUT"
"$PY" -m markitdown "$INPUT" -o "$OUTPUT" 2>&1 | grep -v "Couldn't find ffmpeg"
wc -l "$OUTPUT"
