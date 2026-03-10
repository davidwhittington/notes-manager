import csv
import re
import shutil
import sqlite3
import sys
import tempfile
from datetime import datetime
from pathlib import Path

from .config import (
    ALL_KEYWORDS,
    CANDIDATES_CSV,
    EXPORT_DIR,
    SCAN_SUMMARY,
    SQLITE_PATH,
)

CSV_HEADER = ["folder", "title", "created", "modified", "matched_keyword", "file_path", "triage_verdict"]


# ── File-based scan ──────────────────────────────────────────────────────────

def scan_files() -> int:
    """Walk EXPORT_DIR, find keyword matches, write candidates CSV. Returns match count."""
    if not EXPORT_DIR.exists():
        print(
            f"Error: export directory not found at {EXPORT_DIR}\n"
            "Run 'nm export' first.",
            file=sys.stderr,
        )
        sys.exit(1)

    txt_files = list(EXPORT_DIR.rglob("*.txt"))
    if not txt_files:
        print(f"No .txt files found in {EXPORT_DIR}. Run 'nm export' first.")
        sys.exit(1)

    print(f"Scanning {len(txt_files)} notes in {EXPORT_DIR}...")

    pattern = re.compile(
        "|".join(re.escape(kw) for kw in ALL_KEYWORDS),
        re.IGNORECASE,
    )

    rows = []
    keyword_counts: dict[str, int] = {}
    folder_counts: dict[str, int] = {}

    for path in txt_files:
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue

        match = pattern.search(text)
        if not match:
            continue

        matched_kw = match.group(0).lower()
        meta = _parse_header(text)

        rows.append({
            "folder": meta["folder"],
            "title": meta["title"],
            "created": meta["created"],
            "modified": meta["modified"],
            "matched_keyword": matched_kw,
            "file_path": str(path),
            "triage_verdict": "",
        })

        keyword_counts[matched_kw] = keyword_counts.get(matched_kw, 0) + 1
        folder = meta["folder"]
        folder_counts[folder] = folder_counts.get(folder, 0) + 1

    _write_candidates_csv(rows)
    _write_summary(len(txt_files), len(rows), keyword_counts, folder_counts, mode="file")
    _print_summary(len(txt_files), len(rows), keyword_counts, folder_counts)
    return len(rows)


def _parse_header(text: str) -> dict:
    def extract(label: str, default: str = "") -> str:
        m = re.search(rf"^{label}: (.+)$", text, re.MULTILINE)
        return m.group(1).strip() if m else default

    return {
        "title": extract("TITLE", "untitled"),
        "created": extract("CREATED"),
        "modified": extract("MODIFIED"),
        "folder": extract("FOLDER", "No Folder"),
    }


# ── SQLite direct scan ───────────────────────────────────────────────────────

def scan_sqlite() -> int:
    """Read Apple Notes SQLite directly. Returns match count."""
    if not SQLITE_PATH.exists():
        print(
            f"Error: Apple Notes database not found at {SQLITE_PATH}\n"
            "Make sure Notes has been opened at least once.",
            file=sys.stderr,
        )
        sys.exit(1)

    # Copy DB to temp location — Notes holds a write lock on the live file
    tmp = tempfile.NamedTemporaryFile(suffix=".sqlite", delete=False)
    tmp_path = Path(tmp.name)
    tmp.close()

    shutil.copy2(SQLITE_PATH, tmp_path)
    wal = Path(str(SQLITE_PATH) + "-wal")
    shm = Path(str(SQLITE_PATH) + "-shm")
    if wal.exists():
        shutil.copy2(wal, Path(str(tmp_path) + "-wal"))
    if shm.exists():
        shutil.copy2(shm, Path(str(tmp_path) + "-shm"))

    print(f"Scanning Apple Notes database directly...")

    try:
        rows, keyword_counts, folder_counts = _query_sqlite(tmp_path)
    finally:
        tmp_path.unlink(missing_ok=True)
        Path(str(tmp_path) + "-wal").unlink(missing_ok=True)
        Path(str(tmp_path) + "-shm").unlink(missing_ok=True)

    _write_candidates_csv(rows)
    _write_summary(None, len(rows), keyword_counts, folder_counts, mode="sqlite")
    _print_summary(None, len(rows), keyword_counts, folder_counts)
    return len(rows)


def _query_sqlite(db_path: Path) -> tuple[list[dict], dict, dict]:
    pattern = re.compile(
        "|".join(re.escape(kw) for kw in ALL_KEYWORDS),
        re.IGNORECASE,
    )

    rows = []
    keyword_counts: dict[str, int] = {}
    folder_counts: dict[str, int] = {}

    con = sqlite3.connect(str(db_path))
    con.row_factory = sqlite3.Row

    try:
        # Try the richer join first; fall back to simpler query if schema differs
        try:
            cur = con.execute("""
                SELECT
                    n.ZTITLE1 AS title,
                    datetime(n.ZCREATIONDATE + 978307200, 'unixepoch', 'localtime') AS created,
                    datetime(n.ZMODIFICATIONDATE + 978307200, 'unixepoch', 'localtime') AS modified,
                    COALESCE(f.ZTITLE2, 'No Folder') AS folder,
                    nd.ZTEXT AS body
                FROM ZICCLOUDSYNCINGOBJECT n
                LEFT JOIN ZICCLOUDSYNCINGOBJECT f ON f.Z_PK = n.ZFOLDER
                LEFT JOIN (
                    SELECT ZOWNER, GROUP_CONCAT(ZTEXT, ' ') AS ZTEXT
                    FROM ZICNOTEDATA
                    GROUP BY ZOWNER
                ) nd ON nd.ZOWNER = n.Z_PK
                WHERE n.ZTITLE1 IS NOT NULL
                  AND n.ZTRASHEDSTATE = 0
            """)
        except sqlite3.OperationalError:
            # Fallback: simpler query using ZTITLE / ZSNIPPET
            cur = con.execute("""
                SELECT
                    ZTITLE1 AS title,
                    NULL AS created,
                    NULL AS modified,
                    'unknown' AS folder,
                    ZSNIPPET AS body
                FROM ZICCLOUDSYNCINGOBJECT
                WHERE ZTYPEUTI = 'com.apple.notes.note'
                  AND ZTITLE1 IS NOT NULL
            """)

        for row in cur:
            title = row["title"] or "untitled"
            body = row["body"] or ""
            text = f"{title} {body}"

            match = pattern.search(text)
            if not match:
                continue

            matched_kw = match.group(0).lower()
            folder = row["folder"] or "No Folder"

            rows.append({
                "folder": folder,
                "title": title,
                "created": row["created"] or "",
                "modified": row["modified"] or "",
                "matched_keyword": matched_kw,
                "file_path": "",
                "triage_verdict": "",
            })

            keyword_counts[matched_kw] = keyword_counts.get(matched_kw, 0) + 1
            folder_counts[folder] = folder_counts.get(folder, 0) + 1

    finally:
        con.close()

    return rows, keyword_counts, folder_counts


# ── Shared helpers ───────────────────────────────────────────────────────────

def _write_candidates_csv(rows: list[dict]) -> None:
    CANDIDATES_CSV.parent.mkdir(parents=True, exist_ok=True)
    with CANDIDATES_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_HEADER)
        writer.writeheader()
        writer.writerows(rows)
    print(f"\nCandidates CSV: {CANDIDATES_CSV}")


def _write_summary(
    total_files,
    match_count: int,
    keyword_counts: dict,
    folder_counts: dict,
    mode: str,
) -> None:
    SCAN_SUMMARY.parent.mkdir(parents=True, exist_ok=True)
    with SCAN_SUMMARY.open("w", encoding="utf-8") as f:
        f.write(f"Fortinet Scan Summary — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Mode: {mode}\n\n")
        if total_files is not None:
            f.write(f"Total notes scanned:   {total_files}\n")
        f.write(f"Candidate notes found: {match_count}\n\n")
        f.write("-- By folder --\n")
        for folder, count in sorted(folder_counts.items(), key=lambda x: -x[1]):
            f.write(f"  {count:4d}  {folder}\n")
        f.write("\n-- By matched keyword --\n")
        for kw, count in sorted(keyword_counts.items(), key=lambda x: -x[1]):
            f.write(f"  {count:4d}  {kw}\n")
    print(f"Summary:       {SCAN_SUMMARY}")


def _print_summary(total_files, match_count, keyword_counts, folder_counts) -> None:
    print()
    if total_files is not None:
        print(f"Total notes scanned:   {total_files}")
    print(f"Candidate notes found: {match_count}")

    if folder_counts:
        print("\nBy folder:")
        for folder, count in sorted(folder_counts.items(), key=lambda x: -x[1]):
            print(f"  {count:4d}  {folder}")

    if keyword_counts:
        print("\nBy matched keyword:")
        for kw, count in sorted(keyword_counts.items(), key=lambda x: -x[1]):
            print(f"  {count:4d}  {kw}")
    print()
