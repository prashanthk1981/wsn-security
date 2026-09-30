#!/bin/bash
# Compile IEEE Access Journal Paper LaTeX Document
set -e

PAPER_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "=========================================================================="
echo " Compiling IEEE Access Journal Paper: ieee_access_journal_paper.tex"
echo "=========================================================================="
cd "$PAPER_DIR"
pdflatex -interaction=nonstopmode ieee_access_journal_paper.tex >/dev/null 2>&1 || true
pdflatex -interaction=nonstopmode ieee_access_journal_paper.tex >/dev/null 2>&1 || true

if [ -f "$PAPER_DIR/IEEE_Access_journal/ieee_access_journal_paper.tex" ]; then
    cp "$PAPER_DIR/ieee_access_journal_paper.tex" "$PAPER_DIR/IEEE_Access_journal/ieee_access_journal_paper.tex"
    cp "$PAPER_DIR/ieee_access_journal_paper.pdf" "$PAPER_DIR/IEEE_Access_journal/ieee_access_journal_paper.pdf" 2>/dev/null || true
fi

PAGE_COUNT=$(pdfinfo ieee_access_journal_paper.pdf 2>/dev/null | grep "Pages:" | awk '{print $2}' || echo "N/A")
echo "[SUCCESS] IEEE Access PDF: $PAPER_DIR/ieee_access_journal_paper.pdf (Pages: $PAGE_COUNT)"
echo "=========================================================================="
echo " IEEE Access Paper Compilation Complete!"
echo "=========================================================================="
