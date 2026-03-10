# Command: find-fortinet

## What it does
Greps ~/Desktop/NotesExport/ for all Fortinet-era keywords and builds a candidate CSV.

## Instructions for Claude Code
1. Verify export exists:
   ```bash
   [ -d ~/Desktop/NotesExport ] && echo "exists" || echo "missing"
   ```
   If missing, tell David to run export-notes first.

2. Run the grep script:
   ```bash
   bash notes-manager/scripts/grep_fortinet_notes.sh
   ```

3. Report results:
   - Total candidates found
   - Breakdown by keyword
   - Breakdown by folder
   - Confirm CSV written to ~/Desktop/fortinet_candidates.csv

4. Ask David: "Ready to start triaging? I can walk through them one by one, or you can paste batches."

## Expected output
- ~/Desktop/fortinet_candidates.csv
- ~/Desktop/fortinet_scan_summary.txt
