# Command: build-structure

## What it does
Creates the target folder structure in Apple Notes via AppleScript and installs note templates.

## Instructions for Claude Code
1. Confirm David is ready to restructure Notes (this creates new folders, doesn't delete anything).

2. Run the folder creation script:
   ```bash
   osascript notes-manager/scripts/create_folder_structure.applescript
   ```

3. Confirm folders created:
   - INBOX
   - Active – Work
   - Active – Personal
   - Drafts
   - Archive – Fortinet
   - Archive – General
   - Templates

4. Install templates by running:
   ```bash
   osascript notes-manager/scripts/install_templates.applescript
   ```

5. Show David the templates installed:
   - Account Note template
   - Idea Capture template
   - Meeting Note template
   - Project Note template

6. Walk David through the new workflow:
   - Everything new goes to INBOX first
   - Daily: move INBOX items to the right folder
   - Fortinet audit items go to Archive – Fortinet
   - Graduating items get promoted to Google Docs or iCloud Drive
