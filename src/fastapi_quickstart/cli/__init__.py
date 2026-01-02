import typer

from src.fastapi_quickstart.cli.migrations import migrations

app = typer.Typer(help="FastAPI Quickstart CLI")
app.add_typer(migrations, name="migrate")

if __name__ == "__main__":
    app()
