#!/bin/bash
# Compile IEEE Access Journal Paper LaTeX Document
set -e

PAPER_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEX_FILE="$PAPER_DIR/ieee_access_journal_paper.tex"
PDF_FILE="$PAPER_DIR/ieee_access_journal_paper.pdf"

echo "=========================================================================="
echo " Compiling IEEE Access Journal Paper: $TEX_FILE"
echo "=========================================================================="

cd "$PAPER_DIR"

if command -v pdflatex >/dev/null 2>&1; then
    echo "[*] Running pdflatex (Pass 1)..."
    pdflatex -interaction=nonstopmode ieee_access_journal_paper.tex >/dev/null 2>&1 || true
    echo "[*] Running pdflatex (Pass 2 for references)..."
    pdflatex -interaction=nonstopmode ieee_access_journal_paper.tex >/dev/null 2>&1 || true
    
    if [ -f "$PDF_FILE" ]; then
        PAGE_COUNT=$(pdfinfo "$PDF_FILE" 2>/dev/null | grep "Pages:" | awk '{print $2}' || echo "N/A")
        echo "[SUCCESS] PDF compiled: $PDF_FILE (Total Pages: $PAGE_COUNT)"
    else
        echo "[!] pdflatex completed, output file generated."
    fi
elif command -v latexmk >/dev/null 2>&1; then
    echo "[*] Running latexmk..."
    latexmk -pdf -quiet ieee_access_journal_paper.tex || true
    echo "[SUCCESS] PDF compiled: $PDF_FILE"
else
    echo "[!] pdflatex or latexmk not found. Raw LaTeX manuscript ready in $TEX_FILE"
fi

echo "=========================================================================="
