import os
import click
from importer_generator.wordpress.probe import JsonResponseProbe
from dotenv import load_dotenv

load_dotenv()


def defaults():
    return {
        "host": os.environ.get("HOST"),
        "url": os.environ.get("URL"),
        "endpoint": os.environ.get("ENDPOINT"),
    }


def good_keys():
    return {
        "": ["routes"],
    }


@click.group()
@click.option("--host", default=defaults()["host"])
@click.option("--url", default=defaults()["url"])
@click.pass_context
def cli(ctx: click.Context, host: str, url: str):
    """A CLI for probing a JSON HTTP endpoints."""

    ctx.ensure_object(dict)
    ctx.obj["host"] = host
    ctx.obj["url"] = url


@cli.command()
@click.argument("endpoint", default=defaults()["endpoint"])
@click.option("--keys", is_flag=True, default=False)
@click.pass_context
def inspect(ctx: click.Context, keys: bool, endpoint: str):
    probe = JsonResponseProbe(
        host=ctx.obj.get("host"),
        url=ctx.obj.get("url"),
        endpoint=endpoint,
    )

    click.echo(f"Endpoint: {probe.full_url}")
    click.echo(f"Total pages: {probe.get_total_pages}")
    click.echo(f"Total results: {probe.get_total_results}")
    if not keys:
        click.echo("Keys: ", nl=False)
        for key in probe.get_keys:
            click.echo(f"'{key}', ", nl=False)
    else:
        for key in probe.get_keys:
            click.echo(f"Key: {key}")
    click.echo(nl=True)
