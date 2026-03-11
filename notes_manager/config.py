import os
from pathlib import Path

from dotenv import load_dotenv

# Load .env from project root if present
_ENV_FILE = Path(__file__).parent.parent / ".env"
load_dotenv(_ENV_FILE)

HOME = Path.home()

# ── Output paths ─────────────────────────────────────────────────────────────
EXPORT_DIR = HOME / "Desktop" / "NotesExport"
CANDIDATES_CSV = HOME / "Desktop" / "fortinet_candidates.csv"
SCAN_SUMMARY = HOME / "Desktop" / "fortinet_scan_summary.txt"
TRIAGE_LOG = HOME / "Desktop" / "fortinet_triage_log.csv"
EXECUTE_LOG = HOME / "Desktop" / "fortinet_execute_log.csv"
SQLITE_PATH = (
    HOME
    / "Library"
    / "Group Containers"
    / "group.com.apple.notes"
    / "NoteStore.sqlite"
)

# Scripts dir (relative to this file's parent)
SCRIPTS_DIR = Path(__file__).parent.parent / "scripts"

# ── Default product keywords (Fortinet product names — not personal data) ────
_DEFAULT_PRODUCT_KEYWORDS = [
    "fortinet",
    "fortigate",
    "fortimanager",
    "fortianalyzer",
    "fortisiem",
    "fortiedr",
    "forticlient",
    "forticloud",
    "fortiap",
    "fortiswitch",
    "fortiweb",
    "fortisoar",
]


def _parse_env_list(var: str) -> list[str]:
    """Parse a comma-separated env var into a stripped, lowercased list."""
    raw = os.environ.get(var, "")
    return [item.strip().lower() for item in raw.split(",") if item.strip()]


# ── Fortinet keywords (configurable via .env) ─────────────────────────────────
EXTRA_KEYWORDS: list[str] = _parse_env_list("NM_EXTRA_KEYWORDS")
PEOPLE: list[str] = _parse_env_list("NM_PEOPLE")
ACCOUNTS: list[str] = _parse_env_list("NM_ACCOUNTS")

PRODUCT_KEYWORDS: list[str] = _DEFAULT_PRODUCT_KEYWORDS + EXTRA_KEYWORDS
ALL_KEYWORDS: list[str] = PRODUCT_KEYWORDS + PEOPLE + ACCOUNTS

# ── Island keywords (current employer — Active Work routing) ──────────────────
ISLAND_KEYWORDS: list[str] = _parse_env_list("NM_ISLAND_KEYWORDS")
ISLAND_PEOPLE: list[str] = _parse_env_list("NM_ISLAND_PEOPLE")
ISLAND_ACCOUNTS: list[str] = _parse_env_list("NM_ISLAND_ACCOUNTS")
ALL_ISLAND: list[str] = ISLAND_KEYWORDS + ISLAND_PEOPLE + ISLAND_ACCOUNTS

# ── Active Work date cutoff ───────────────────────────────────────────────────
# Notes must be created or modified on or after this date to qualify for Active – Work
ACTIVE_WORK_CUTOFF: str = os.environ.get("NM_ACTIVE_WORK_CUTOFF", "2025-09-01")

# ── Personal GitHub project names (Active Personal routing) ──────────────────
PERSONAL_PROJECTS: list[str] = _parse_env_list("NM_PERSONAL_PROJECTS")


def validate() -> None:
    """Warn if no personal keywords are configured."""
    if not PEOPLE and not ACCOUNTS and not EXTRA_KEYWORDS:
        print(
            "Warning: NM_PEOPLE, NM_ACCOUNTS, and NM_EXTRA_KEYWORDS are all empty.\n"
            "Scanning with Fortinet product keywords only.\n"
            "Copy .env.example to .env and add your personal keywords.\n"
        )
