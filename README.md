# notes-manager

A Python CLI for auditing and reorganizing Apple Notes. Built for people with years of accumulated notes who need to systematically find, triage, and graduate the ones worth keeping.

## Current status

Phase 1 — active development. Core CLI pipeline (export, scan, triage, status) is working. Not yet packaged for distribution.

## Requirements

- macOS (Apple Notes via AppleScript)
- Python 3.10+
- Anthropic API key (only required for `--auto` triage)

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

Edit `.env` and fill in:

```
NM_EXTRA_KEYWORDS=your,custom,terms
NM_PEOPLE=first last,first last
NM_ACCOUNTS=company name,another company
```

If you have an Anthropic API key for AI-powered triage, either export it in your shell or add it to `.env`:

```
ANTHROPIC_API_KEY=sk-ant-...
```

## Usage

### Full pipeline (recommended first run)

```bash
./run.sh pipeline
```

Runs: export → scan → triage (auto) → status in sequence.

### Step by step

```bash
# 1. Create target folder structure in Apple Notes
./run.sh setup

# 2. Export all notes to ~/Desktop/NotesExport/
./run.sh export

# 3. Scan exported notes for your keywords
./run.sh scan

# 4. Preview AI triage verdicts without writing
./run.sh triage --auto --dry-run

# 5. Run triage for real
./run.sh triage --auto

# 6. Or triage interactively (no API key needed)
./run.sh triage

# 7. Check progress
./run.sh status
```

### Triage verdicts

| Verdict | Meaning |
|---|---|
| `archive` | No enduring value. Move to archive folder. |
| `promote` | Transferable idea worth keeping as a real doc. |
| `extract` | One good idea buried in noise. Pull it out. |
| `review` | Mixed — needs a human pass. |

### Direct SQLite scan (no export needed)

```bash
./run.sh scan --direct
```

Reads Apple Notes database directly. Faster, but no note body content available for triage.

## Repo layout

```
notes-manager/
├── notes_manager/          — Python package
│   ├── cli.py              — Click CLI entry point
│   ├── config.py           — paths and keyword loading (.env)
│   ├── export.py           — wraps export_notes.applescript
│   ├── scan.py             — keyword scanner (file-based + SQLite)
│   ├── triage.py           — interactive and AI-powered triage
│   ├── setup_notes.py      — creates folder structure in Notes
│   └── status.py           — progress summary
├── scripts/
│   ├── export_notes.applescript
│   ├── grep_fortinet_notes.sh
│   ├── create_folder_structure.applescript
│   └── install_templates.applescript
├── commands/               — Claude Code command definitions
├── .env.example            — config template (copy to .env)
├── requirements.txt
└── run.sh
```

## License

MIT
