-- delete_note.applescript
-- Args: noteTitle
-- Permanently deletes a note by title from the iCloud Notes account.

on run argv
	set noteTitle to item 1 of argv

	tell application "Notes"
		set targetAccount to account "iCloud"

		try
			set matchedNote to first note of targetAccount whose name is noteTitle
		on error
			error "Note not found: " & noteTitle
		end try

		delete matchedNote
	end tell
end run
