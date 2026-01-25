import docker
from rich.console import Console
from rich.table import Table
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
    """List all docker containers"""
    # TO DO: Add flags for showing running and exited
    table = Table(title="Docker Containers")

    table.add_column("Name", style="cyan", no_wrap=True)
    table.add_column("ID", style="cyan")
    table.add_column("Status", style="cyan")

    for container, info in named_containers.items():
        status = info["status"]
        short_id = info["id"]
        status_color = "green" if status == "running" else "red"
        table.add_row(container, short_id, f"[{status_color}]{info['status']}[/{status_color}]")

    console.print(table)

if __name__ == "__main__":
    if AUTO_GIT_PULL: update_git()
    client = docker.from_env()
    console = Console()

    id_containers = list_containers(client)
    named_containers = {info["name"]: {"id": c_id, "status": info["status"]} for c_id, info in id_containers.items()}

    cli()