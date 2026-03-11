-- create_note.applescript
-- Args: targetFolderName, noteTitle, contentFilePath
-- Creates a new note in the named folder, reading body content from a temp file.

on run argv
	set targetFolderName to item 1 of argv
	set noteTitle to item 2 of argv
	set contentFilePath to item 3 of argv

	-- Read body from temp file (avoids arg length limits)
	set contentFile to open for access POSIX file contentFilePath
	set noteBody to read contentFile as «class utf8»
	close access contentFile

	tell application "Notes"
		set targetAccount to account "iCloud"

		try
			set dest to folder targetFolderName of targetAccount
		on error
			error "Folder not found: " & targetFolderName
		end try

		make new note at dest with properties {name:noteTitle, body:noteBody}
	end tell
end run
