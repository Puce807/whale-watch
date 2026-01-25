import docker
from docker_cmds import *
from config import *
from utils import update_git

@click.group()
def cli():
    pass

@cli.command()
def update():
    update_git()

@cli.command()
def ls():
    for container, info in named_containers.items():
        print(f"{container}: Status {info["status"]} | ID {info["id"]}")

if __name__ == "__main__":
    if AUTO_GIT_PULL: update_git()
    client = docker.from_env()

    id_containers = list_containers(client)
    named_containers = {info["name"]: {"id": c_id, "status": info["status"]} for c_id, info in id_containers.items()}

    cli()