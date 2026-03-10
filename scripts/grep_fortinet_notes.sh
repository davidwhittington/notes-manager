#!/bin/bash
# ============================================================
# grep_fortinet_notes.sh
# Run AFTER export_notes.applescript has finished
# Greps ~/Desktop/NotesExport/ for Fortinet keywords
# and builds a CSV of candidates
# ============================================================
# USAGE:
#   chmod +x grep_fortinet_notes.sh
#   ./grep_fortinet_notes.sh
#
# OUTPUT:
#   ~/Desktop/fortinet_candidates.csv
#   ~/Desktop/fortinet_scan_summary.txt
# ============================================================

set -euo pipefail

EXPORT_DIR="$HOME/Desktop/NotesExport"
OUTPUT_CSV="$HOME/Desktop/fortinet_candidates.csv"
OUTPUT_SUMMARY="$HOME/Desktop/fortinet_scan_summary.txt"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Fortinet Keyword Scanner"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

if [ ! -d "$EXPORT_DIR" ]; then
  echo "❌  Export folder not found at $EXPORT_DIR"
  echo "    Run export_notes.applescript first."
  exit 1
fi

TOTAL_FILES=$(find "$EXPORT_DIR" -name "*.txt" | wc -l | tr -d ' ')
echo "✓  Found $TOTAL_FILES exported notes"
echo "   Scanning for keywords..."
echo ""

# ── Keywords ─────────────────────────────────────────────────
KEYWORDS=(
  "fortinet"
  "fortigate"
  "fortimanager"
  "fortianalyzer"
  "fortisiem"
  "fortiedr"
  "forticlient"
  "forticloud"
  "fortiap"
  "fortiswitch"
  "fortiweb"
  "fortisoar"
  "smart ticket"
  "smartticket"
  "stxe"
  "tola"
  "alex draskovich"
  "ben cook"
  "bill morgan"
  "bryan miller"
  "chris asher"
  "chris sherry"
  "dean olson"
  "eric hastings"
  "greg schwartzkopf"
  "james herrera"
  "jason dean"
  "jim huber"
  "joel garza"
  "ken xie"
  "luis castillo"
  "marc blackwell"
  "michael ford"
  "michael lohman"
  "michael stoeger"
  "minh ly"
  "nick futter"
  "pat young"
  "randy blaylock"
  "steve huddleston"
  "wes ballinger"
  "exxon"
  "waste management"
  "chevron"
  "walmart"
)

# Build single grep pattern (case insensitive)
PATTERN=$(printf '%s\n' "${KEYWORDS[@]}" | paste -sd'|')

# ── CSV header ────────────────────────────────────────────────
echo "folder,title,created,modified,matched_keyword,file_path,triage_verdict" > "$OUTPUT_CSV"

MATCH_COUNT=0
declare -A KEYWORD_COUNTS
declare -A FOLDER_COUNTS

while IFS= read -r -d '' file; do
  # Check if file matches any keyword
  MATCHED=$(grep -ioE "$PATTERN" "$file" | head -1 || true)
  
  if [ -n "$MATCHED" ]; then
    MATCH_COUNT=$((MATCH_COUNT + 1))
    
    # Extract metadata from header lines
    TITLE=$(grep "^TITLE:" "$file" | head -1 | sed 's/^TITLE: //' || echo "untitled")
    CREATED=$(grep "^CREATED:" "$file" | head -1 | sed 's/^CREATED: //' || echo "")
    MODIFIED=$(grep "^MODIFIED:" "$file" | head -1 | sed 's/^MODIFIED: //' || echo "")
    FOLDER=$(grep "^FOLDER:" "$file" | head -1 | sed 's/^FOLDER: //' || echo "No Folder")

    # Track keyword counts
    KEY_LOWER=$(echo "$MATCHED" | tr '[:upper:]' '[:lower:]')
    KEYWORD_COUNTS["$KEY_LOWER"]=$(( ${KEYWORD_COUNTS["$KEY_LOWER"]:-0} + 1 ))

    # Track folder counts
    FOLDER_COUNTS["$FOLDER"]=$(( ${FOLDER_COUNTS["$FOLDER"]:-0} + 1 ))

    # Escape for CSV
    TITLE_ESC=$(echo "$TITLE" | sed 's/"/""/g')
    CREATED_ESC=$(echo "$CREATED" | sed 's/"/""/g')
    MODIFIED_ESC=$(echo "$MODIFIED" | sed 's/"/""/g')
    FOLDER_ESC=$(echo "$FOLDER" | sed 's/"/""/g')
    MATCHED_ESC=$(echo "$MATCHED" | sed 's/"/""/g')
    FILE_ESC=$(echo "$file" | sed 's/"/""/g')

    echo "\"$FOLDER_ESC\",\"$TITLE_ESC\",\"$CREATED_ESC\",\"$MODIFIED_ESC\",\"$MATCHED_ESC\",\"$FILE_ESC\",\"\"" >> "$OUTPUT_CSV"
  fi
done < <(find "$EXPORT_DIR" -name "*.txt" -print0)

# ── Summary ───────────────────────────────────────────────────
{
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Fortinet Scan Summary"
echo "  $(date)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Total notes scanned:   $TOTAL_FILES"
echo "Candidate notes found: $MATCH_COUNT"
echo ""
echo "── By folder ──────────────────────────────"
for folder in "${!FOLDER_COUNTS[@]}"; do
  echo "  ${FOLDER_COUNTS[$folder]}  $folder"
done | sort -rn
echo ""
echo "── By matched keyword ─────────────────────"
for kw in "${!KEYWORD_COUNTS[@]}"; do
  echo "  ${KEYWORD_COUNTS[$kw]}  $kw"
done | sort -rn
} | tee "$OUTPUT_SUMMARY"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✓  CSV:     $OUTPUT_CSV"
echo "✓  Summary: $OUTPUT_SUMMARY"
echo ""
echo "Next: open fortinet_candidates.csv in Numbers"
echo "and paste note content into the Triage tool."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
