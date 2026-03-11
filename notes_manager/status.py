import csv
import sys
from collections import Counter

from .config import CANDIDATES_CSV, TRIAGE_LOG

VERDICT_ORDER = [
    "promote-work",
    "promote-personal",
    "archive-fortinet",
    "archive-personal",
    "extract",
    "review",
    "discard",
]


def show_status() -> None:
    if not CANDIDATES_CSV.exists():
        print(
            f"No candidates CSV found at {CANDIDATES_CSV}\n"
            "Run 'nm scan' to generate it.",
            file=sys.stderr,
        )
        sys.exit(1)

    with CANDIDATES_CSV.open(newline="", encoding="utf-8") as f:
        candidates = list(csv.DictReader(f))

    total = len(candidates)
    triaged_in_csv = [r for r in candidates if r.get("triage_verdict", "").strip()]

    # Read triage log for verdict breakdown (more reliable than CSV column)
    log_rows = _load_triage_log()
    log_verdicts = Counter(r.get("verdict", "") for r in log_rows)

    triaged_count = len(log_rows) if log_rows else len(triaged_in_csv)
    remaining = max(0, total - triaged_count)
    pct = (triaged_count / total * 100) if total else 0

    print(f"\nFortinet Audit — Status")
    print("=" * 40)
    print(f"  Total candidates:  {total}")
    print(f"  Triaged:           {triaged_count} ({pct:.0f}%)")
    print(f"  Remaining:         {remaining}")
    print()

    if log_verdicts:
        print("Verdict breakdown:")
        for verdict in VERDICT_ORDER:
            count = log_verdicts.get(verdict, 0)
            bar = "#" * count
            print(f"  {verdict:<10} {count:4d}  {bar}")
        unknown = {k: v for k, v in log_verdicts.items() if k not in VERDICT_ORDER}
        for verdict, count in unknown.items():
            print(f"  {verdict:<10} {count:4d}")
        print()

    # List active and extract notes so David can see what's moving
    active = [r for r in log_rows if r.get("verdict") in ("promote-work", "promote-personal", "extract")]
    if active:
        print("Notes moving to active / drafts:")
        for r in active:
            label = r["verdict"].upper()
            title = r.get("title", "(untitled)")
            print(f"  [{label}]  {title}")
        print()


def _load_triage_log() -> list[dict]:
    if not TRIAGE_LOG.exists():
        return []
    with TRIAGE_LOG.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))
