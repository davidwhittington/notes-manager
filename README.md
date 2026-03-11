# notes-manager

A Python CLI for auditing and reorganizing Apple Notes. Export your library, scan for keywords, triage each candidate, then execute — moving notes directly into the right folders in Apple Notes.

Built for anyone with years of accumulated notes who needs to systematically sort the useful from the noise without doing it manually one note at a time.

## Current status

Phase 1 — active development. Full pipeline (export → scan → triage → execute) is working. Not yet packaged for distribution.

## Requirements

- macOS (Apple Notes via AppleScript)
- Python 3.10+
- Anthropic API key (required for `--auto` triage and `extract` verdicts)

## Installation

```bash
git clone https://github.com/davidwhittington/notes-manager.git
cd notes-manager
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Configuration

notes-manager uses a `.env` file for personal keywords. This keeps your contacts, accounts, and custom terms out of version control.

```bash
cp .env.example .env
```

Edit `.env` and fill in your keyword buckets:

```
# Extra terms beyond any default product keywords
NM_EXTRA_KEYWORDS=your,custom,terms

# People names to scan for
NM_PEOPLE=first last,first last

# Company or account names to scan for
NM_ACCOUNTS=company name,another company

# Current employer keywords (used for Active-Work routing)
NM_ISLAND_KEYWORDS=your company,product name
NM_ISLAND_PEOPLE=colleague name,colleague name
NM_ISLAND_ACCOUNTS=key account

# Date cutoff for Active-Work routing (notes must be on or after this date)
NM_ACTIVE_WORK_CUTOFF=2025-09-01

# Personal project names (used for Active-Personal routing)
NM_PERSONAL_PROJECTS=project-one,project-two
```

If you have an Anthropic API key for AI-powered triage and extract summaries:

```
ANTHROPIC_API_KEY=sk-ant-...
```

## Usage

### Step by step

```bash
# 1. Create the target folder structure in Apple Notes
./run.sh setup

# 2. Export all notes to ~/Desktop/NotesExport/
./run.sh export

# 3. Scan exported notes for your keywords
./run.sh scan

# 4. Or scan Apple Notes SQLite directly (no export needed, less content available)
./run.sh scan --direct

# 5. Triage interactively (no API key needed)
./run.sh triage

# 6. Or triage with Claude (preview first, then for real)
./run.sh triage --auto --dry-run
./run.sh triage --auto

# 7. Preview what execute will do before touching Notes
./run.sh execute --dry-run

# 8. Execute — moves notes into their target folders in Apple Notes
./run.sh execute

# 9. Check progress at any point
./run.sh status
```

### Triage verdicts

During triage, each candidate note is shown with a content preview. Press one key to assign a verdict.

| Key | Verdict | Destination |
|-----|---------|-------------|
| `w` | Promote — Work | `Active – Work` |
| `p` | Promote — Personal | `Active – Personal` |
| `f` | Archive — Fortinet | `Archive – Fortinet` + header stamped |
| `a` | Archive — Personal | `Archive – Personal` + header stamped |
| `e` | Extract | Gem → new note in `Drafts` (Claude writes clean summary), original archived |
| `r` | Review | `INBOX` — needs a manual pass |
| `d` | Discard | Deleted |
| `s` | Skip | Leave untouched for now |
| `q` | Quit | Save progress and exit |

**Active-Work routing** checks two criteria: the note must match current-employer keywords and have a creation or modification date on or after `NM_ACTIVE_WORK_CUTOFF`. If either condition isn't met, execute warns but moves the note anyway since you made the call during triage.

**Extract** uses Claude (Haiku) to distill the useful idea into a clean new note in `Drafts`, then archives the original.

### Archive header

Notes routed to any archive folder get a header stamped at the top:

```
────────────────────────────
ARCHIVED: 2025-11-04
Source: Fortinet era (2011–2024)
────────────────────────────
```

### Target folder structure

`./run.sh setup` creates these folders in Apple Notes if they don't already exist:

```
INBOX               ← review verdicts land here
Active – Work       ← current job, active accounts
Active – Personal   ← personal projects
Drafts              ← extracted gems, ideas in progress
Archive – Fortinet  ← former employer notes
Archive – Personal  ← old personal notes worth keeping
Archive – General   ← everything else
Templates
```

### Output files

All output lands on `~/Desktop/`:

| File | Contents |
|------|----------|
| `NotesExport/` | Exported notes as `.txt` files, organized by folder |
| `fortinet_candidates.csv` | Notes that matched your keywords, with triage verdict column |
| `fortinet_scan_summary.txt` | Breakdown by folder and keyword |
| `fortinet_triage_log.csv` | Triage decisions with timestamp and reason |
| `fortinet_execute_log.csv` | Execute results — what moved where, errors if any |

## Repo layout

```
notes-manager/
├── notes_manager/              — Python package
│   ├── cli.py                  — Click CLI entry point
│   ├── config.py               — paths and keyword loading (.env)
│   ├── export.py               — wraps export_notes.applescript
│   ├── scan.py                 — keyword scanner (file-based + SQLite)
│   ├── triage.py               — interactive and AI-powered triage
│   ├── execute.py              — moves notes in Apple Notes per triage verdicts
│   ├── setup_notes.py          — creates folder structure in Notes
│   └── status.py               — progress summary
├── scripts/
│   ├── export_notes.applescript
│   ├── create_folder_structure.applescript
│   ├── install_templates.applescript
│   ├── move_note.applescript
│   ├── archive_note.applescript
│   ├── create_note.applescript
│   ├── delete_note.applescript
│   └── grep_fortinet_notes.sh  — standalone bash alternative to nm scan
├── commands/                   — Claude Code command definitions
├── .env.example                — config template (copy to .env)
├── requirements.txt
└── run.sh
```

## License

MIT
