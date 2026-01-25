import click
import docker
from docker_cmds import *
from config import *
from utils import update_git

@click.group()
def cli():
    pass

@cli.command()
@click.option("--count", default=1, help="Number of greetings")
@click.option("--name", prompt="Your name", help="The person to greet")
def test(count, name):
    for i in range(count):
        print(f"Hello {name}")

if __name__ == "__main__":
    if AUTO_GIT_PULL: update_git()
    client = docker.from_env()
    cli()