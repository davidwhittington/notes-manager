import csv
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path

from .config import CANDIDATES_CSV, TRIAGE_LOG

VERDICTS = {"a": "archive", "p": "promote", "e": "extract", "r": "review"}
TRIAGE_LOG_HEADER = ["timestamp", "title", "file_path", "verdict", "reason"]

SYSTEM_PROMPT = """\
You are a triage assistant helping a former Fortinet employee audit thousands of old notes.

Classify each note using exactly one of these verdicts:
- archive   — Fortinet-specific content with no enduring value (org charts, meeting logistics,
              account maps, names with no transferable ideas, product-specific ops).
              Default lean for anything that's just a record of something that happened.
- promote   — Contains a framework, strategy, or insight that transfers to current work.
              Worth turning into a real doc. Should be immediately useful or instructive today.
- extract   — Has 1-2 specific ideas buried in noise. The container is junk but there's a gem.
              Pull the gem, trash the container.
- review    — Genuinely unclear — mixed signal, could go either way.

Respond ONLY with valid JSON in this exact shape:
{"verdict": "<archive|promote|extract|review>", "reason": "<1-2 sentences>"}
"""


# ── Interactive triage ───────────────────────────────────────────────────────

def run_interactive() -> None:
    candidates = _load_candidates()
    if not candidates:
        print("No candidates found. Run 'nm scan' first.")
        return

    untriaged = [r for r in candidates if not r.get("triage_verdict", "").strip()]
    if not untriaged:
        print("All candidates are already triaged.")
        return

    print(f"{len(untriaged)} notes remaining to triage.\n")
    triaged_this_session = 0

    for row in untriaged:
        _print_note_card(row)
        verdict = _prompt_verdict()
        if verdict == "quit":
            break
        if verdict == "skip":
            continue

        _append_triage_log(row["title"], row.get("file_path", ""), verdict, reason="")
        _update_candidates_csv(candidates, row, verdict)
        triaged_this_session += 1
        print(f"  Logged: {verdict}\n")

    print(f"\nSession complete. Triaged {triaged_this_session} notes.")


def _print_note_card(row: dict) -> None:
    print("=" * 60)
    print(f"  Title:   {row.get('title', '(untitled)')}")
    print(f"  Folder:  {row.get('folder', '')}")
    print(f"  Keyword: {row.get('matched_keyword', '')}")
    print(f"  Created: {row.get('created', '')}")

    file_path = row.get("file_path", "")
    if file_path and Path(file_path).exists():
        try:
            text = Path(file_path).read_text(encoding="utf-8", errors="replace")
            # Strip the metadata header (up to the dashes line)
            separator = "----------------------------------------"
            if separator in text:
                body = text.split(separator, 1)[1].strip()
            else:
                body = text
            preview = body[:500]
            if len(body) > 500:
                preview += "..."
            print(f"\n{preview}")
        except OSError:
            pass
    print()


def _prompt_verdict() -> str:
    prompt = "[a]rchive  [p]romote  [e]xtract  [r]eview  [s]kip  [q]uit > "
    while True:
        try:
            choice = input(prompt).strip().lower()
        except (EOFError, KeyboardInterrupt):
            print()
            return "quit"
        if choice in VERDICTS:
            return VERDICTS[choice]
        if choice == "s":
            return "skip"
        if choice == "q":
            return "quit"
        print("  Invalid choice. Enter a, p, e, r, s, or q.")


# ── Auto triage (Claude API) ─────────────────────────────────────────────────

def run_auto(dry_run: bool = False) -> None:
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        print(
            "Error: ANTHROPIC_API_KEY is not set.\n"
            "Export it first:  export ANTHROPIC_API_KEY=sk-ant-...",
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        import anthropic
    except ImportError:
        print(
            "Error: anthropic package not installed.\n"
            "Run: pip install anthropic",
            file=sys.stderr,
        )
        sys.exit(1)

    candidates = _load_candidates()
    if not candidates:
        print("No candidates found. Run 'nm scan' first.")
        return

    untriaged = [r for r in candidates if not r.get("triage_verdict", "").strip()]
    if not untriaged:
        print("All candidates are already triaged.")
        return

    client = anthropic.Anthropic(api_key=api_key)
    mode_label = "DRY RUN — " if dry_run else ""
    print(f"{mode_label}Auto-triaging {len(untriaged)} notes with Claude...\n")

    for i, row in enumerate(untriaged, 1):
        title = row.get("title", "(untitled)")
        file_path = row.get("file_path", "")
        content = _load_note_content(file_path)

        print(f"[{i}/{len(untriaged)}] {title[:60]}", end="", flush=True)

        verdict, reason = _call_claude(client, title, content)
        print(f"  -> {verdict}")

        if not dry_run:
            _append_triage_log(title, file_path, verdict, reason)
            _update_candidates_csv(candidates, row, verdict)

        if i < len(untriaged):
            time.sleep(0.5)

    if dry_run:
        print("\n(dry run — nothing written)")
    else:
        print(f"\nAuto-triage complete. {len(untriaged)} notes processed.")


def _load_note_content(file_path: str) -> str:
    if file_path and Path(file_path).exists():
        try:
            text = Path(file_path).read_text(encoding="utf-8", errors="replace")
            separator = "----------------------------------------"
            if separator in text:
                return text.split(separator, 1)[1].strip()[:2000]
            return text[:2000]
        except OSError:
            pass
    return "(no content available)"


def _call_claude(client, title: str, content: str) -> tuple[str, str]:
    user_msg = f"Note title: {title}\n\nNote content:\n{content}"
    try:
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=256,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_msg}],
        )
        raw = response.content[0].text.strip()
        data = json.loads(raw)
        verdict = data.get("verdict", "review")
        if verdict not in ("archive", "promote", "extract", "review"):
            verdict = "review"
        reason = data.get("reason", "")
        return verdict, reason
    except (json.JSONDecodeError, KeyError, IndexError):
        return "review", "parse error"
    except Exception as e:
        return "review", str(e)


# ── Shared helpers ───────────────────────────────────────────────────────────

def _load_candidates() -> list[dict]:
    if not CANDIDATES_CSV.exists():
        return []
    with CANDIDATES_CSV.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _append_triage_log(title: str, file_path: str, verdict: str, reason: str) -> None:
    TRIAGE_LOG.parent.mkdir(parents=True, exist_ok=True)
    write_header = not TRIAGE_LOG.exists()
    with TRIAGE_LOG.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=TRIAGE_LOG_HEADER)
        if write_header:
            writer.writeheader()
        writer.writerow({
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "title": title,
            "file_path": file_path,
            "verdict": verdict,
            "reason": reason,
        })


def _update_candidates_csv(candidates: list[dict], target_row: dict, verdict: str) -> None:
    """Write verdict back into the candidates CSV for the matching row."""
    for row in candidates:
        if (
            row.get("title") == target_row.get("title")
            and row.get("file_path") == target_row.get("file_path")
        ):
            row["triage_verdict"] = verdict
            break

    fieldnames = list(candidates[0].keys()) if candidates else []
    with CANDIDATES_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(candidates)
