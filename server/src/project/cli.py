import click
from . import scripts


@click.group()
def cli():
    pass


@cli.command("run-tg-bot")
def run_tg_bot():
    scripts.run_tg_bot()


@cli.command("run-fastapi")
def run_fastapi():
    scripts.run_fastapi()


if __name__ == "__main__":
    cli()
