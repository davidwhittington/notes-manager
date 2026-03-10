import subprocess
import sys

from .config import SCRIPTS_DIR


def run_setup() -> None:
    scripts = [
        ("create_folder_structure.applescript", "Creating folder structure in Apple Notes..."),
        ("install_templates.applescript", "Installing note templates..."),
    ]

    for filename, message in scripts:
        script = SCRIPTS_DIR / filename
        if not script.exists():
            print(f"Error: script not found at {script}", file=sys.stderr)
            sys.exit(1)

        print(message)
        result = subprocess.run(
            ["osascript", str(script)],
            timeout=60,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            stderr = result.stderr.strip()
            print(
                f"Error: osascript exited with code {result.returncode}",
                file=sys.stderr,
            )
            if stderr:
                print(f"  {stderr}", file=sys.stderr)
            sys.exit(1)

        print("  Done.\n")

    print("Setup complete.")
    print("Folders created: INBOX, Active - Work, Active - Personal, Drafts,")
    print("                 Archive - Fortinet, Archive - General, Templates")
    print("Templates installed: Account Note, Idea Capture, Meeting Note, Project Note")
