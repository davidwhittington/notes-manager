import csv
import os
import subprocess
import sys
import tempfile
import time
from datetime import datetime
from pathlib import Path

from .config import (
    ACTIVE_WORK_CUTOFF,
    ALL_ISLAND,
    EXECUTE_LOG,
    SCRIPTS_DIR,
    TRIAGE_LOG,
)

EXECUTE_LOG_HEADER = ["timestamp", "title", "verdict", "destination", "status", "error"]

ARCHIVE_VERDICTS = {"archive-fortinet", "archive-personal"}

EXTRACT_SYSTEM_PROMPT = """\
You are distilling a useful idea from a messy old note written during a corporate career.
Write a clean, concise note capturing only the core insight or enduring value.

Rules:
- First line: a clear, descriptive title (no "Note:" prefix, no quotes)
- Blank line
- The content: keep only what is useful today. Strip company-specific context \
(people names, org details, account names, product versions).
- Plain text only
- Be brief. If the insight fits in 2-4 sentences, do that.

Output only the note content. No preamble, no meta-commentary.
"""


def run_execute(dry_run: bool = False) -> None:
    log_rows = _load_triage_log()
    if not log_rows:
        print("No triage log found. Run 'nm triage' first.")
        return

    executed = _load_executed_set()
    pending = [r for r in log_rows if r.get("title", "") not in executed]

    if not pending:
        print("All triaged notes have already been executed.")
        return

    mode = "DRY RUN — " if dry_run else ""
    print(f"{mode}Executing {len(pending)} notes...\n")

    ok = errors = 0

    for row in pending:
        verdict = row.get("verdict", "").strip()
        title = row.get("title", "(untitled)")

        print(f"  [{verdict}] {title[:60]}", end="", flush=True)

        try:
            dest = _route(row, dry_run)
            print(f"  → {dest}")
            if not dry_run:
                _log_execute(title, verdict, dest, "ok", "")
                executed.add(title)
            ok += 1
        except Exception as e:
            print(f"  ERROR: {e}")
            if not dry_run:
                _log_execute(title, verdict, "", "error", str(e))
            errors += 1

    print(f"\nDone. {ok} succeeded, {errors} errors.")
    if not dry_run and errors == 0:
        print(f"Execute log: {EXECUTE_LOG}")


def _route(row: dict, dry_run: bool) -> str:
    verdict = row.get("verdict", "").strip()
    title = row.get("title", "")
    file_path = row.get("file_path", "")

    if verdict == "promote-work":
        _check_island_date(title, file_path, row.get("created", ""), row.get("modified", ""))
        if not dry_run:
            _run_script("move_note.applescript", title, "Active \u2013 Work")
        return "Active \u2013 Work"

    elif verdict == "promote-personal":
        if not dry_run:
            _run_script("move_note.applescript", title, "Active \u2013 Personal")
        return "Active \u2013 Personal"

    elif verdict in ARCHIVE_VERDICTS:
        folder = "Archive \u2013 Fortinet" if verdict == "archive-fortinet" else "Archive \u2013 Personal"
        source = "Fortinet era (2011\u20132024)" if verdict == "archive-fortinet" else "Personal archive"
        date_str = datetime.now().strftime("%Y-%m-%d")
        if not dry_run:
            _run_script("archive_note.applescript", title, folder, date_str, source)
        return folder

    elif verdict == "extract":
        if not dry_run:
            _do_extract(title, file_path)
        return "Drafts (new note) + Archive \u2013 Fortinet (original)"

    elif verdict == "review":
        if not dry_run:
            _run_script("move_note.applescript", title, "INBOX")
        return "INBOX"

    elif verdict == "discard":
        if not dry_run:
            _run_script("delete_note.applescript", title)
        return "deleted"

    else:
        raise ValueError(f"Unknown verdict: {verdict!r}")


def _check_island_date(title: str, file_path: str, created: str, modified: str) -> None:
    """Warn (non-blocking) if note doesn't appear to meet Active-Work criteria."""
    try:
        cutoff = datetime.fromisoformat(ACTIVE_WORK_CUTOFF)
    except ValueError:
        return

    c = _parse_date(created)
    m = _parse_date(modified)
    date_ok = (c and c >= cutoff) or (m and m >= cutoff)

    content = ""
    if file_path and Path(file_path).exists():
        content = Path(file_path).read_text(errors="replace").lower()
    text = title.lower() + " " + content
    island_ok = any(kw in text for kw in ALL_ISLAND)

    if not date_ok or not island_ok:
        reasons = []
        if not date_ok:
            reasons.append("date predates Sept 2025")
        if not island_ok:
            reasons.append("no Island keywords found")
        print(f"\n    Warning: Active-Work criteria not fully met ({', '.join(reasons)}). Moving anyway.", end="")


def _do_extract(title: str, file_path: str) -> None:
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        raise RuntimeError("ANTHROPIC_API_KEY not set — cannot run extract.")

    try:
        import anthropic
    except ImportError:
        raise RuntimeError("anthropic package not installed. Run: pip install anthropic")

    content = _load_note_content(file_path)
    client = anthropic.Anthropic(api_key=api_key)
    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=512,
        system=EXTRACT_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": f"Note title: {title}\n\nContent:\n{content}"}],
    )
    clean_text = response.content[0].text.strip()

    # First line is the new title, rest is the body
    lines = clean_text.splitlines()
    new_title = lines[0].strip() if lines else title
    new_body = "\n".join(lines[2:]).strip() if len(lines) > 2 else clean_text

    # Write body to a temp file — avoids arg-length limits with osascript
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False, encoding="utf-8") as f:
        f.write(new_body)
        tmp_path = f.name

    try:
        _run_script("create_note.applescript", "Drafts", new_title, tmp_path)
    finally:
        Path(tmp_path).unlink(missing_ok=True)

    time.sleep(0.5)

    # Archive the original
    date_str = datetime.now().strftime("%Y-%m-%d")
    _run_script("archive_note.applescript", title, "Archive \u2013 Fortinet", date_str, "Fortinet era (2011\u20132024)")


def _run_script(script_name: str, *args: str) -> None:
    script_path = SCRIPTS_DIR / script_name
    if not script_path.exists():
        raise FileNotFoundError(f"Script not found: {script_path}")
    result = subprocess.run(
        ["osascript", str(script_path), *args],
        capture_output=True,
        text=True,
        timeout=30,
    )
    if result.returncode != 0:
        err = result.stderr.strip() or result.stdout.strip()
        raise RuntimeError(err or f"osascript exited with code {result.returncode}")


def _load_note_content(file_path: str) -> str:
    if file_path and Path(file_path).exists():
        try:
            text = Path(file_path).read_text(encoding="utf-8", errors="replace")
            sep = "----------------------------------------"
            if sep in text:
                return text.split(sep, 1)[1].strip()[:2000]
            return text[:2000]
        except OSError:
            pass
    return "(no content available)"


def _parse_date(s: str) -> datetime | None:
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.strptime(s.strip(), fmt)
        except (ValueError, AttributeError):
            pass
    return None


def _load_triage_log() -> list[dict]:
    if not TRIAGE_LOG.exists():
        return []
    with TRIAGE_LOG.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _load_executed_set() -> set[str]:
    if not EXECUTE_LOG.exists():
        return set()
    with EXECUTE_LOG.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    return {r["title"] for r in rows if r.get("status") == "ok"}


def _log_execute(title: str, verdict: str, destination: str, status: str, error: str) -> None:
    EXECUTE_LOG.parent.mkdir(parents=True, exist_ok=True)
    write_header = not EXECUTE_LOG.exists()
    with EXECUTE_LOG.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=EXECUTE_LOG_HEADER)
        if write_header:
            writer.writeheader()
        writer.writerow({
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "title": title,
            "verdict": verdict,
            "destination": destination,
            "status": status,
            "error": error,
        })
