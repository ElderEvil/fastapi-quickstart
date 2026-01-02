"""Migration management CLI commands using Alembic."""

import logging
from pathlib import Path
from typing import Annotated

import typer
from alembic import command
from alembic.config import Config

logger = logging.getLogger(__name__)
migrations = typer.Typer(help="Manage Alembic database migrations")


@migrations.command()
def init(
    module: Annotated[Path, typer.Option(help="Project root directory")] = Path(),
    config_file: Annotated[Path, typer.Option(help="Alembic config file path")] = Path("alembic.ini"),
    directory: Annotated[Path, typer.Option(help="Migration directory path")] = Path("migrations"),
    template: Annotated[str, typer.Option(help="Migration template to use")] = "async",
    target_metadata: Annotated[str | None, typer.Argument(help="Target metadata module path")] = None,
):
    """
    Initialize Alembic migration structure in your project.

    Creates the necessary directory structure and configuration files for managing
    database migrations with Alembic.

    Examples:
        # Initialize with default settings (async template)
        fastapi-quickstart migrate init

        # Initialize with custom directory
        fastapi-quickstart migrate init --directory alembic

        # Initialize with specific metadata
        fastapi-quickstart migrate init myapp.models.metadata
    """
    _config_file = module / config_file
    _directory = module / directory
    config = Config(_config_file)

    template_path = Path(__file__).parent.absolute() / "templates" / template
    command.init(config, str(_directory), template=str(template_path), package=True)

    typer.secho("[OK] Alembic initialized successfully!", fg=typer.colors.GREEN, bold=True)

    if target_metadata:
        from configparser import ConfigParser  # Import here to avoid unnecessary overhead

        updated_config = ConfigParser()
        updated_config.read(_config_file)
        updated_config["alembic"].update({"target_metadata": target_metadata})
        with open(_config_file, "w") as configfile:
            updated_config.write(configfile)
        typer.secho(f"[OK] Target metadata set to: {target_metadata}", fg=typer.colors.GREEN)


@migrations.command()
def revision(
    message: Annotated[str | None, typer.Argument(help="Description of the migration")] = None,
    module: Annotated[Path, typer.Option(help="Project root directory")] = Path(),
    config_file: Annotated[Path, typer.Option(help="Alembic config file path")] = Path("alembic.ini"),
    autogenerate: Annotated[bool, typer.Option(help="Auto-detect model changes")] = True,
    sql: Annotated[bool, typer.Option(help="Generate SQL scripts instead of Python")] = False,
    dry_run: Annotated[bool, typer.Option("--dry-run", help="Show what would be generated without creating files")] = False,
):
    """
    Create a new migration revision based on model changes.

    By default, this command auto-detects changes to your SQLModel models and
    generates a migration script. Use --dry-run to preview changes without creating files.

    Examples:
        # Create migration with auto-detected changes
        fastapi-quickstart migrate revision "add users table"

        # Preview migration without creating files
        fastapi-quickstart migrate revision "add users table" --dry-run

        # Create empty migration template
        fastapi-quickstart migrate revision "custom migration" --no-autogenerate

        # Generate SQL migration
        fastapi-quickstart migrate revision "add users table" --sql
    """
    if dry_run:
        typer.secho("[DRY RUN] DRY RUN: Preview mode enabled", fg=typer.colors.YELLOW, bold=True)
        typer.echo("\nThis would create a migration with:")
        typer.echo(f"  Message: {message or '(no message)'}")
        typer.echo(f"  Autogenerate: {autogenerate}")
        typer.echo(f"  SQL mode: {sql}")
        typer.echo("\nNo files will be created in dry-run mode.")
        return

    config = Config(module / config_file)
    command.revision(
        config,
        message=message,
        autogenerate=autogenerate,
        sql=sql,
    )
    typer.secho(f"[OK] Migration '{message}' created successfully!", fg=typer.colors.GREEN, bold=True)


@migrations.command()
def upgrade(
    revision: Annotated[str, typer.Argument(help="Target revision (default: head)")] = "head",
    module: Annotated[Path, typer.Option(help="Project root directory")] = Path(),
    config_file: Annotated[Path, typer.Option(help="Alembic config file path")] = Path("alembic.ini"),
    sql: Annotated[bool, typer.Option(help="Generate SQL without executing")] = False,
    dry_run: Annotated[bool, typer.Option("--dry-run", help="Show SQL that would be executed")] = False,
):
    """
    Apply migrations up to a specific revision.

    By default, upgrades to the latest migration (head). Use --dry-run to preview
    SQL statements without executing them.

    Examples:
        # Upgrade to latest migration
        fastapi-quickstart migrate upgrade

        # Preview SQL without executing
        fastapi-quickstart migrate upgrade --dry-run

        # Upgrade to specific revision
        fastapi-quickstart migrate upgrade abc123

        # Generate SQL script
        fastapi-quickstart migrate upgrade --sql
    """
    config = Config(module / config_file)

    if dry_run or sql:
        typer.secho(f"[DRY RUN] Generating SQL for upgrade to: {revision}", fg=typer.colors.YELLOW, bold=True)
        command.upgrade(config, revision, sql=True)
        if dry_run:
            typer.echo("\n(SQL shown above - no changes applied)")
        return

    command.upgrade(config, revision)
    typer.secho(f"[OK] Successfully upgraded to {revision}!", fg=typer.colors.GREEN, bold=True)


@migrations.command()
def downgrade(
    revision: Annotated[str, typer.Argument(help="Target revision (default: -1 for previous)")] = "-1",
    module: Annotated[Path, typer.Option(help="Project root directory")] = Path(),
    config_file: Annotated[Path, typer.Option(help="Alembic config file path")] = Path("alembic.ini"),
    sql: Annotated[bool, typer.Option(help="Generate SQL without executing")] = False,
    dry_run: Annotated[bool, typer.Option("--dry-run", help="Show SQL that would be executed")] = False,
):
    """
    Revert migrations down to a specific revision.

    By default, downgrades to the previous migration (-1). Use --dry-run to preview
    SQL statements without executing them.

    Examples:
        # Downgrade to previous migration
        fastapi-quickstart migrate downgrade

        # Preview SQL without executing
        fastapi-quickstart migrate downgrade --dry-run

        # Downgrade to specific revision
        fastapi-quickstart migrate downgrade abc123

        # Downgrade all migrations
        fastapi-quickstart migrate downgrade base
    """
    config = Config(module / config_file)

    if dry_run or sql:
        typer.secho(f"[DRY RUN] Generating SQL for downgrade to: {revision}", fg=typer.colors.YELLOW, bold=True)
        command.downgrade(config, revision, sql=True)
        if dry_run:
            typer.echo("\n(SQL shown above - no changes applied)")
        return

    command.downgrade(config, revision)
    typer.secho(f"[OK] Successfully downgraded to {revision}!", fg=typer.colors.GREEN, bold=True)


@migrations.command()
def current(
    module: Annotated[Path, typer.Option(help="Project root directory")] = Path(),
    config_file: Annotated[Path, typer.Option(help="Alembic config file path")] = Path("alembic.ini"),
):
    """
    Display the current migration revision.

    Shows which migration is currently applied to the database.

    Examples:
        fastapi-quickstart migrate current
    """
    config = Config(module / config_file)
    command.current(config)


@migrations.command()
def history(
    module: Annotated[Path, typer.Option(help="Project root directory")] = Path(),
    config_file: Annotated[Path, typer.Option(help="Alembic config file path")] = Path("alembic.ini"),
    verbose: Annotated[bool, typer.Option("--verbose", "-v", help="Show detailed history")] = False,
):
    """
    Display migration history.

    Shows the complete history of migrations in the project.

    Examples:
        # Show migration history
        fastapi-quickstart migrate history

        # Show detailed history
        fastapi-quickstart migrate history --verbose
    """
    config = Config(module / config_file)
    command.history(config, verbose=verbose)


@migrations.command()
def heads(
    module: Annotated[Path, typer.Option(help="Project root directory")] = Path(),
    config_file: Annotated[Path, typer.Option(help="Alembic config file path")] = Path("alembic.ini"),
):
    """
    Show current available heads in the migration script directory.

    Useful for identifying the latest migration revision.

    Examples:
        fastapi-quickstart migrate heads
    """
    config = Config(module / config_file)
    command.heads(config)


@migrations.command()
def stamp(
    revision: Annotated[str, typer.Argument(help="Revision to stamp (e.g., 'head', 'base')")],
    module: Annotated[Path, typer.Option(help="Project root directory")] = Path(),
    config_file: Annotated[Path, typer.Option(help="Alembic config file path")] = Path("alembic.ini"),
    sql: Annotated[bool, typer.Option(help="Generate SQL without executing")] = False,
):
    """
    Mark database as being at a specific revision without running migrations.

    Useful for initializing Alembic on an existing database or recovering from
    migration issues.

    Examples:
        # Mark database as up-to-date
        fastapi-quickstart migrate stamp head

        # Mark as base (no migrations applied)
        fastapi-quickstart migrate stamp base

        # Stamp specific revision
        fastapi-quickstart migrate stamp abc123
    """
    config = Config(module / config_file)
    command.stamp(config, revision, sql=sql)

    if not sql:
        typer.secho(f"[OK] Stamped database at revision: {revision}", fg=typer.colors.GREEN, bold=True)


if __name__ == "__main__":
    migrations()
