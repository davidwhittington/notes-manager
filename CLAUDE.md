# Notes Manager — Claude Code Project

## Who I am
David. I use Apple Notes as a capture layer across business and personal life. This project exists to audit, organize, and systematically improve that system.

## Current Mission: Phase 1 — Fortinet Audit
I spent 2011–2024 at Fortinet. I have thousands of notes from that era mixed in with everything else, no dedicated folder. The goal is to:
1. Export all notes to flat files (AppleScript)
2. Find Fortinet-era candidates (grep)
3. Triage each candidate: archive, promote, extract, or review
4. Move keepers to the right destination, archive the rest

## My Setup
- **Mac** — Apple ecosystem, iCloud, Notes
- **Business tools**: Google Workspace (Gmail, Calendar), Slack, Zoom, Granola, GitHub (business)
- **Personal tools**: Apple Notes, iCloud Drive, GitHub (personal), Claude (personal), ChatGPT
- **Note graduation targets**:
  - Business ideas → Google Docs or GitHub Wiki
  - Personal ideas → iCloud Drive doc or GitHub personal repo

## Fortinet Context
**People to detect:**
Bryan Miller, Chris Asher, Michael Stoeger, Joel Garza, Greg Schwartzkopf, Bill Morgan, Eric Hastings, James Herrera, Ben Cook, Nick Futter, Jim Huber, Ken Xie

**Accounts to detect:**
Exxon, Waste Management, Chevron, BP, Walmart

**Products/terms to detect:**
Fortinet, FortiGate, FortiManager, FortiAnalyzer, FortiSIEM, FortiEDR, FortiClient, FortiCloud, FortiAP, FortiSwitch, FortiWeb, FortiSOAR, SMART TICKET

## Folder Structure (Target State for Apple Notes)
```
📁 INBOX           ← everything lands here first
📁 Active – Work   ← current accounts (POV or Deployment state)
📁 Active – Personal
📁 Drafts          ← ideas worth developing, not yet graduated
📁 Archive – Fortinet
📁 Archive – General
📁 Templates
```

## Triage Verdicts
- **archive** — Fortinet-specific, no enduring value. Move to Archive – Fortinet.
- **promote** — Transferable idea/framework. Graduate to Google Docs or iCloud Drive.
- **extract** — One good idea buried in noise. Pull it out into a new Draft, discard the rest.
- **review** — Mixed content. Needs a human pass.

## Key File Paths (after running export)
- Exported notes: `~/Desktop/NotesExport/`
- Candidates CSV: `~/Desktop/fortinet_candidates.csv`
- Summary: `~/Desktop/fortinet_scan_summary.txt`
- Triage log: `~/Desktop/fortinet_triage_log.csv`

## Commands Available
See `/commands/` folder. Run them by telling Claude Code what you want:
- "find my fortinet notes" → runs `find-fortinet`
- "triage this note: [paste]" → runs `triage-note`
- "show me my triage progress" → runs `triage-status`
- "build my notes folder structure" → runs `build-structure`
- "graduate this note to [destination]" → runs `graduate-note`

## Current Progress
- [ ] Phase 1: Export all notes
- [ ] Phase 1: Find Fortinet candidates
- [ ] Phase 1: Triage all candidates
- [ ] Phase 1: Archive confirmed Fortinet notes
- [ ] Phase 2: Build new folder structure in Notes
- [ ] Phase 2: Apply templates to active notes
- [ ] Phase 3: Set up graduation pipeline

## Notes on Tone
Be direct. I'm technical. Skip the hand-holding. If something needs a decision, give me the options and a recommendation — don't ask 5 questions.

## Upcoming: GitHub Project Page

A project page for the GitHub repo is planned but **must not be started until the private sub-repo separation is verified complete and no personal data (people, accounts, keywords) exists in the main repo commit history**.

Checklist before starting:
- [ ] Main repo has been pushed to GitHub
- [ ] `git log` confirms no personal data ever committed to main repo
- [ ] `private/` sub-repo is confirmed on a separate private GitHub repo
- [ ] `.env` is confirmed gitignored and not in any commit
