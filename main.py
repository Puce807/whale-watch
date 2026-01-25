import docker
from docker_cmds import *
from config import *
from utils import update_git

@click.group()
def cli():
    pass

@cli.command()
def ls():
    print(list_containers(client))

if __name__ == "__main__":
    if AUTO_GIT_PULL: update_git()
    client = docker.from_env()
    cli()