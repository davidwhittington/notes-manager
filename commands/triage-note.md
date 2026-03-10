# Command: triage-note

## What it does
Evaluates a single note and returns a verdict with reasoning and destination.

## Instructions for Claude Code
When David pastes note content, evaluate it using this framework:

### Triage criteria
- **archive**: Old Fortinet org context (AMs, SEs, account maps), meeting logistics, names without transferable ideas, product-specific ops that don't apply elsewhere. Default lean for anything that's just a record of a thing that happened.
- **promote**: Contains a framework, strategy, or insight that transfers to current work. Worth turning into a real doc. Should be immediately useful or instructive today.
- **extract**: Has 1–2 specific ideas buried in noise. The container is junk but there's a gem. Pull the gem, trash the container.
- **review**: Genuinely unclear — mixed signal, could go either way. Flag for David to decide.

### Response format
Return a structured verdict:

```
VERDICT: [archive|promote|extract|review]
SUMMARY: [1 sentence — what this note actually is]
REASON: [2–3 sentences on the verdict]
KEEP: [bullet list of specific ideas worth preserving, or "none"]
DESTINATION: [where it goes — e.g. "Archive – Fortinet", "Drafts", "iCloud Drive", "GitHub wiki"]
TITLE: [suggested title if it graduates]
```

### After verdict
Ask: "Log this verdict? (y/n)" — if yes, append to ~/Desktop/fortinet_triage_log.csv:
```
"[timestamp]","[note title or first 50 chars]","[verdict]","[destination]","[suggested title]"
```

## Triage log format
CSV columns: timestamp, note_snippet, verdict, destination, suggested_title
