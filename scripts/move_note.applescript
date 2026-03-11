-- move_note.applescript
-- Args: noteTitle, targetFolderName
-- Moves a note by title to the named folder in the iCloud Notes account.

on run argv
	set noteTitle to item 1 of argv
	set targetFolderName to item 2 of argv

	tell application "Notes"
		set targetAccount to account "iCloud"

		try
			set matchedNote to first note of targetAccount whose name is noteTitle
		on error
			error "Note not found: " & noteTitle
		end try

		try
			set dest to folder targetFolderName of targetAccount
		on error
			error "Folder not found: " & targetFolderName
		end try

		move matchedNote to dest
	end tell
end run
