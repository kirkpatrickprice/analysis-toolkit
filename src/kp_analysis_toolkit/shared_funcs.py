from typing import NoReturn

import click


def print_help() -> NoReturn:
    """Print help for the kpat_cli command line interface."""
    ctx = click.get_current_context()
    click.echo(ctx.get_help())
    ctx.exit()
