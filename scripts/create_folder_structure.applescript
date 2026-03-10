-- ============================================================
-- create_folder_structure.applescript
-- Creates the target folder structure in Apple Notes
-- Safe to run — only creates folders that don't exist
-- ============================================================

set targetFolders to {"INBOX", "Active – Work", "Active – Personal", "Drafts", "Archive – Fortinet", "Archive – General", "Templates"}

tell application "Notes"
	-- Use the default iCloud account
	set targetAccount to account "iCloud"
	
	set existingFolderNames to {}
	repeat with f in folders of targetAccount
		set end of existingFolderNames to name of f
	end repeat
	
	set created to {}
	set skipped to {}
	
	repeat with folderName in targetFolders
		if existingFolderNames contains folderName then
			set end of skipped to folderName
		else
			make new folder at targetAccount with properties {name:folderName}
			set end of created to folderName
		end if
	end repeat
	
	-- Build result message
	set msg to "Folder structure complete." & return & return
	
	if length of created > 0 then
		set msg to msg & "Created:" & return
		repeat with f in created
			set msg to msg & "  ✓ " & f & return
		end repeat
	end if
	
	if length of skipped > 0 then
		set msg to msg & return & "Already existed (skipped):" & return
		repeat with f in skipped
			set msg to msg & "  – " & f & return
		end repeat
	end if
	
end tell

display dialog msg buttons {"OK"} default button "OK"
