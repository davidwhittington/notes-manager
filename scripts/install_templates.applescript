-- ============================================================
-- install_templates.applescript
-- Creates template notes inside the Templates folder
-- ============================================================

tell application "Notes"
	set targetAccount to account "iCloud"
	
	-- Find or create Templates folder
	set templateFolder to missing value
	repeat with f in folders of targetAccount
		if name of f is "Templates" then
			set templateFolder to f
			exit repeat
		end if
	end repeat
	
	if templateFolder is missing value then
		set templateFolder to make new folder at targetAccount with properties {name:"Templates"}
	end if
	
	-- ── Template 1: Account Note ─────────────────────────────
	make new note at templateFolder with properties {name:"[TEMPLATE] Account Note", body:"ACCOUNT NOTE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Account: 
Stage: [ ] POV  [ ] Deployment  [ ] Other
Owner: 
Last Updated: 

── Overview ──────────────────────
[What is this account? What do they do? Why do they matter?]

── Current Status ────────────────
[Where are we in the engagement?]

── Key Contacts ──────────────────
Name | Role | Notes

── Open Items ────────────────────
[ ] 
[ ] 
[ ] 

── Next Steps ────────────────────
[ ] 
[ ] 

── Notes / History ───────────────
[Date] — 
"}
	
	-- ── Template 2: Idea Capture ─────────────────────────────
	make new note at templateFolder with properties {name:"[TEMPLATE] Idea Capture", body:"IDEA
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Title: 
Date: 
Context: [ ] Work  [ ] Personal
Status: [ ] Raw  [ ] Developing  [ ] Ready to graduate

── The Idea ──────────────────────
[One sentence. What is this?]

── Why it matters ────────────────
[Why does this idea have value?]

── How it could work ─────────────
[First thoughts on execution]

── Open questions ────────────────
[ ] 
[ ] 

── Graduate to ───────────────────
[ ] Google Docs  [ ] iCloud Drive  [ ] GitHub  [ ] Other: 
"}
	
	-- ── Template 3: Meeting Note ──────────────────────────────
	make new note at templateFolder with properties {name:"[TEMPLATE] Meeting Note", body:"MEETING NOTE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Date: 
With: 
Re: 
Tool: [ ] Zoom  [ ] In-person  [ ] Slack  [ ] Other

── Agenda ────────────────────────
1. 
2. 
3. 

── Notes ─────────────────────────
[Raw capture during the call]

── Decisions made ────────────────
- 

── Action items ──────────────────
[ ]  (owner) by (date)
[ ]  (owner) by (date)

── Follow-up ─────────────────────
[ ] Send recap
[ ] Update account note
[ ] 
"}
	
	-- ── Template 4: Project Note ──────────────────────────────
	make new note at templateFolder with properties {name:"[TEMPLATE] Project Note", body:"PROJECT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Project: 
Type: [ ] Work  [ ] Personal
Started: 
Target: 
Status: [ ] Planning  [ ] Active  [ ] Blocked  [ ] Done

── Goal ──────────────────────────
[What does done look like?]

── Background ────────────────────
[Context, why this exists]

── Milestones ────────────────────
[ ] 
[ ] 
[ ] 

── Open questions ────────────────
[ ] 
[ ] 

── Log ───────────────────────────
[Date] — 
"}
	
end tell

display dialog "Templates installed in your Templates folder." & return & return & "Templates created:" & return & "  ✓ Account Note" & return & "  ✓ Idea Capture" & return & "  ✓ Meeting Note" & return & "  ✓ Project Note" buttons {"OK"} default button "OK"
