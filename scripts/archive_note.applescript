-- archive_note.applescript
-- Args: noteTitle, targetFolderName, archiveDate, sourceLabel
-- Stamps an archive header onto a note and moves it to the target folder.

on run argv
	set noteTitle to item 1 of argv
	set targetFolderName to item 2 of argv
	set archiveDate to item 3 of argv
	set sourceLabel to item 4 of argv

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

		-- Prepend archive header as HTML, preserving the existing body
		set headerHTML to "<div>\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500</div><div><b>ARCHIVED: " & archiveDate & "</b></div><div>Source: " & sourceLabel & "</div><div>\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500</div><br>"
		set currentBody to body of matchedNote
		set body of matchedNote to headerHTML & currentBody

		move matchedNote to dest
	end tell
end run
