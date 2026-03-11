import sys

import click


@click.group()
def main():
    """nm — Notes Manager CLI for the Fortinet audit and beyond."""
    pass


@main.command()
def export():
    """Export all Apple Notes to ~/Desktop/NotesExport/ via AppleScript."""
    from .export import run_export
    run_export()


@main.command()
@click.option("--direct", is_flag=True, default=False, help="Read Apple Notes SQLite directly instead of scanning exported files.")
def scan(direct):
    """Scan exported notes (or SQLite) for Fortinet keywords and write candidates CSV."""
    if direct:
        from .scan import scan_sqlite
        scan_sqlite()
    else:
        from .scan import scan_files
        scan_files()


@main.command()
@click.option("--auto", is_flag=True, default=False, help="AI batch triage via Claude API.")
@click.option("--dry-run", is_flag=True, default=False, help="Print verdicts without writing (only with --auto).")
def triage(auto, dry_run):
    """Triage Fortinet candidate notes interactively, or automatically with Claude."""
    if dry_run and not auto:
        click.echo("--dry-run only applies with --auto. Add --auto to use it.", err=True)
        sys.exit(1)

    if auto:
        from .triage import run_auto
        run_auto(dry_run=dry_run)
    else:
        from .triage import run_interactive
        run_interactive()


@main.command()
def status():
    """Show triage progress summary."""
    from .status import show_status
    show_status()


@main.command()
@click.option("--dry-run", is_flag=True, default=False, help="Preview actions without touching Notes.")
def execute(dry_run):
    """Move notes in Apple Notes based on triage verdicts."""
    from .execute import run_execute
    run_execute(dry_run=dry_run)


@main.command()
def setup():
    """Create target folder structure and install templates in Apple Notes."""
    from .setup_notes import run_setup
    run_setup()


@main.command()
@click.option("--dry-run", is_flag=True, default=False, help="Pass --dry-run to the auto-triage step.")
def pipeline(dry_run):
    """Run the full pipeline: export -> scan -> triage --auto -> status."""
    from .export import run_export
    from .scan import scan_files
    from .triage import run_auto
    from .status import show_status

    click.echo("=== Step 1/4: Export ===")
    run_export()

    click.echo("\n=== Step 2/4: Scan ===")
    scan_files()

    click.echo("\n=== Step 3/4: Triage (auto) ===")
    run_auto(dry_run=dry_run)

    click.echo("\n=== Step 4/4: Status ===")
    show_status()


if __name__ == "__main__":
    main()
