#!/bin/bash
# Rebuild documents/aziz-bibitow-resume.pdf from the .docx, no Word or
# LibreOffice needed. See README.md for how it works.
#
#   tools/resume/build.sh              # rebuild from the default .docx
#   tools/resume/build.sh other.docx   # rebuild from a different one
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../.." && pwd)"
DOCX="${1:-$ROOT/documents/aziz-bibitow-resume.docx}"
PDF="$ROOT/documents/aziz-bibitow-resume.pdf"
WORK="$(mktemp -d)"
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

trap 'rm -rf "$WORK"' EXIT

[ -f "$DOCX" ] || { echo "no such file: $DOCX" >&2; exit 1; }
[ -x "$CHROME" ] || { echo "Google Chrome not found at $CHROME" >&2; exit 1; }

echo "==> building HTML from $(basename "$DOCX")"
python3 "$HERE/build_pdf_html.py" "$DOCX" "$WORK/resume.html"

echo "==> printing to PDF with headless Chrome"
"$CHROME" --headless --disable-gpu --no-pdf-header-footer \
          --print-to-pdf="$WORK/resume.pdf" "file://$WORK/resume.html" 2>/dev/null

if [ -f "$PDF" ]; then
    if command -v pdftotext >/dev/null; then
        echo "==> geometry diff against the current PDF"
        python3 "$HERE/compare.py" "$PDF" "$WORK/resume.pdf" || true
    else
        echo "==> skipping geometry diff (no pdftotext; brew install poppler)"
    fi
    cp "$PDF" "$PDF.bak"
    echo "==> previous PDF saved as $(basename "$PDF").bak"
fi

cp "$WORK/resume.pdf" "$PDF"
echo "==> wrote $PDF"
