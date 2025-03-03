import logging
from pathlib import Path
from typing import Annotated, Literal

import typer
from alembic import command
from alembic.config import Config

logger = logging.getLogger(__name__)
migrations = typer.Typer(help="Manage Alembic migrations")


@migrations.command()
def init(
    module: Path = Path(),
    config_file: Path = Path("alembic.ini"),
    directory: Path = Path("migrations"),
    template: Literal["generic", "async"] = "async",
    target_metadata: Annotated[str | None, typer.Argument()] = None,
):
    """
    Initialize Alembic migration structure.
    """
    _config_file = module / config_file
    _directory = module / directory
    config = Config(_config_file)

    template_path = Path(__file__).parent.absolute() / "templates" / template
    command.init(config, str(_directory), template=str(template_path), package=True)

    logger.debug("✅ Alembic initialized!")

    if target_metadata:
        from configparser import ConfigParser  # Import here to avoid unnecessary overhead

        updated_config = ConfigParser()
        updated_config.read(_config_file)
        updated_config["alembic"].update({"target_metadata": target_metadata})
        with open(_config_file, "w") as configfile:
            updated_config.write(configfile)
        logger.debug("✅ Alembic defaults overridden")


@migrations.command()
def revision(
    module: Path = Path(),
    config_file: Path = Path("alembic.ini"),
    message: Annotated[str | None, typer.Argument()] = None,
    *,
    autogenerate: bool = True,
    sql: bool = False,
):
    """
    Create a new Alembic revision with detected model changes.
    """
    config = Config(module / config_file)
    command.revision(
        config,
        message=message,
        autogenerate=autogenerate,
        sql=sql,
    )
    msg = f"✅ Migration '{message}' created!"
    logger.debug(msg)


@migrations.command()
def upgrade(
    revision: str = "head",
    module: Path = Path(),
    config_file: Path = Path("alembic.ini"),
):
    """
    Apply migrations up to a specific revision.
    """
    config = Config(module / config_file)
    command.upgrade(config, revision)
    msg = f"✅ Upgraded to {revision}!"
    logger.debug(msg)


@migrations.command()
def downgrade(
    revision: str = "-1",
    module: Path = Path(),
    config_file: Path = Path("alembic.ini"),
):
    """
    Revert migrations down to a specific revision.
    """
    config = Config(module / config_file)
    command.downgrade(config, revision)
    msg = f"⏪ Downgraded to {revision}!"
    logger.debug(msg)


if __name__ == "__main__":
    migrations()
