import docker
from rich.console import Console
from rich.table import Table
from docker_cmds import *
from config import *
from utils import *

__version__ = "0.1.0"

@click.group()
@click.option("-v", "--version", help="Show version")
def cli(version):
    """ Whale Watch CLI """
    if version:
        current_commit = get_local_commit()
        commit_msg = get_commit_message(current_commit)
        print(f"Whale Watch Version {__version__} Commit Message '{commit_msg}'")
    pass

@cli.command()
def update():
    """Pulls new commits from the repository"""
    update_git()
    log("Local repository updated successfully", 2)


@cli.command()
@click.option("--status", "-s", default="all",
              type=click.Choice(["all", "created", "restarting", "running", "removing", "paused", "exited", "dead"]),
              help="Filter output by container status. Eg: running")
def ls(status):
    """List all docker containers"""
    table = Table(title="Docker Containers")

    table.add_column("Name", style="cyan", no_wrap=True)
    table.add_column("ID", style="cyan")
    table.add_column("Status", style="cyan")

    for container, info in named_containers.items():
        c_status = info["status"]
        if status == "all" or c_status == status:
            short_id = info["id"]
            status_color = STATUS_COLORS.get(c_status, "white")
            table.add_row(container, short_id, f"[{status_color}]{c_status}[/{status_color}]")

    if table.rows:
        console.print(table)
    else:
        print("No containers found")

if __name__ == "__main__":
    if AUTO_GIT_PULL:
        if not check_git(): update_git()
    elif CHECK_GIT:
        if not check_git():
            print("Local repository outdated")
            answer = input("Pull new commits from repository? [y, n]")
            if answer.lower() == "y":
                update_git()

    client = docker.from_env()
    console = Console()

    id_containers = list_containers(client)
    named_containers = {info["name"]: {"id": c_id, "status": info["status"]} for c_id, info in id_containers.items()}

    cli()