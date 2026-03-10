import subprocess
import sys
from pathlib import Path

from .config import EXPORT_DIR, SCRIPTS_DIR


def run_export() -> int:
    """Run export_notes.applescript and return the count of exported .txt files."""
    script = SCRIPTS_DIR / "export_notes.applescript"
    if not script.exists():
        print(f"Error: applescript not found at {script}", file=sys.stderr)
        sys.exit(1)

    print("Running export_notes.applescript via osascript...")
    print("This may take several minutes for a large note library.\n")

    # Strip any `display dialog` lines — they block subprocess indefinitely
    source = script.read_text(encoding="utf-8")
    source = "\n".join(
        line for line in source.splitlines()
        if not line.strip().startswith("display dialog")
    )

    try:
        result = subprocess.run(
            ["osascript", "-"],
            input=source,
            timeout=300,
            capture_output=True,
            text=True,
        )
    except subprocess.TimeoutExpired:
        print(
            "Error: export timed out after 300 seconds. "
            "Try running the applescript manually via Script Editor.",
            file=sys.stderr,
        )
        sys.exit(1)

    if result.returncode != 0:
        stderr = result.stderr.strip()
        print(f"Error: osascript exited with code {result.returncode}", file=sys.stderr)
        if stderr:
            print(f"  {stderr}", file=sys.stderr)
        sys.exit(1)

    count = _count_exported_files()
    print(f"Export complete. {count} notes written to {EXPORT_DIR}")
    return count


def _count_exported_files() -> int:
    if not EXPORT_DIR.exists():
        return 0
    return sum(1 for _ in EXPORT_DIR.rglob("*.txt"))
