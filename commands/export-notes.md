# Command: export-notes

## What it does
Runs the AppleScript to export all Apple Notes to ~/Desktop/NotesExport/ as plain text files, organized by folder. This is the prerequisite for all other commands.

## Instructions for Claude Code
1. Check if ~/Desktop/NotesExport/ already exists
   - If yes, ask David if he wants to re-export or use the existing export
   - If no, proceed

2. Tell David to run the AppleScript:
   - Open Script Editor (Spotlight → "Script Editor")
   - Open the file: notes-manager/scripts/export_notes.applescript
   - Click Run ▶
   - Allow Notes access when prompted
   - Wait for "Export complete!" dialog (5–15 min for large libraries)

3. Once David confirms it's done, verify:
   ```bash
   find ~/Desktop/NotesExport -name "*.txt" | wc -l
   ```

4. Report the count and confirm ready for `find-fortinet`

## Expected output
- ~/Desktop/NotesExport/ with subfolders per Notes folder
- Each note as a .txt file with metadata header (TITLE, CREATED, MODIFIED, FOLDER)
