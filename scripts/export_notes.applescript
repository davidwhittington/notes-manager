-- ============================================================
-- export_notes.applescript
-- Exports all Apple Notes to individual .txt files
-- organized by folder
-- ============================================================
-- HOW TO RUN:
--   1. Open Script Editor (Applications > Utilities > Script Editor)
--   2. Paste this script in
--   3. Click Run (▶)
--   4. Wait — this will take a few minutes for thousands of notes
--   Output: ~/Desktop/NotesExport/
-- ============================================================

set exportFolder to (path to desktop as text) & "NotesExport:"

-- Create root export folder
tell application "Finder"
	if not (exists folder exportFolder) then
		make new folder at desktop with properties {name:"NotesExport"}
	end if
end tell

tell application "Notes"
	repeat with eachAccount in accounts
		set accountName to name of eachAccount
		
		repeat with eachFolder in folders of eachAccount
			set folderName to name of eachFolder
			
			-- Sanitize folder name for filesystem
			set safeFolderName to my sanitize(accountName & "_" & folderName)
			set folderPath to exportFolder & safeFolderName & ":"
			
			tell application "Finder"
				if not (exists folder folderPath) then
					make new folder at folder exportFolder with properties {name:safeFolderName}
				end if
			end tell
			
			set noteList to notes of eachFolder
			set noteCount to count of noteList
			
			repeat with i from 1 to noteCount
				set eachNote to item i of noteList
				
				try
					set noteTitle to name of eachNote
					set noteBody to plaintext of eachNote
					set noteCreated to creation date of eachNote
					set noteModified to modification date of eachNote
					
					-- Sanitize title for filename
					set safeTitle to my sanitize(noteTitle)
					if length of safeTitle > 60 then
						set safeTitle to text 1 thru 60 of safeTitle
					end if
					if safeTitle is "" then set safeTitle to "untitled_" & i
					
					-- Build file content with metadata header
					set fileContent to "TITLE: " & noteTitle & "
CREATED: " & (noteCreated as string) & "
MODIFIED: " & (noteModified as string) & "
FOLDER: " & folderName & "
ACCOUNT: " & accountName & "
----------------------------------------
" & noteBody
					
					-- Write file
					set filePath to folderPath & safeTitle & ".txt"
					set fileRef to open for access file filePath with write permission
					set eof of fileRef to 0
					write fileContent to fileRef
					close access fileRef
					
				on error errMsg
					-- Skip notes that error, log and continue
					try
						close access file filePath
					end try
				end try
			end repeat
		end repeat
	end repeat
end tell

display dialog "Export complete! Notes saved to ~/Desktop/NotesExport/" buttons {"OK"} default button "OK"

-- ── Helper: sanitize string for use as filename ──────────────
on sanitize(str)
	set illegal to {"/", ":", "\\", "*", "?", "\"", "<", ">", "|", "\n", "\r", "\t"}
	set result to str
	repeat with c in illegal
		set result to my replaceText(result, c, "_")
	end repeat
	return result
end sanitize

on replaceText(str, find, replace)
	set AppleScript's text item delimiters to find
	set parts to text items of str
	set AppleScript's text item delimiters to replace
	set result to parts as string
	set AppleScript's text item delimiters to ""
	return result
end replaceText
