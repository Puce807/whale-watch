import docker
from rich.console import Console
from rich.table import Table
from docker_cmds import *
from utils import *

__version__ = "0.2.0"

@click.group()
@click.pass_context
def cli(ctx):
    """ Whale Watch CLI """
    if ctx.invoked_subcommand == "update":
        return

    if AUTO_GIT_PULL:
        if not check_git(): update_git()
    elif PROMPT_UPDATES:
        if not check_git():
            print("Local repository outdated")
            answer = input("Pull new commits from repository? [y, n] ")
            if answer.lower() == "y":
                update_git()

@cli.command()
def update():
    """Pulls new commits from the repository"""
    update_git()
    log("Local repository updated successfully", 2)

@cli.command(name="version")
@click.option("-g", "--git", is_flag=True, help="Include git info")
def version(git):
    """Displays version"""
    current_commit = get_local_commit()
    commit_msg = get_commit_message(current_commit)
    print(f"Whale Watch Version {__version__}")
    if git:
        print(f"Commit: {current_commit} Message: {commit_msg}")

@cli.command()
@click.option("-s", "--status", default="all",
              type=click.Choice(CONTAINER_STATUS),
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

@cli.command()
@click.option("-s", "--status", default="running", type=click.Choice(CONTAINER_STATUS),
              help="Filter stats by container status")
def stats(status):
    """Get docker container stats"""
    container_stat = container_stats(client, status)
    table = Table(title="Docker Container Stats")
    headers = ["CPU", "MEM", "NET"]

    table.add_column("Name", style="cyan", no_wrap=True)
    table.add_column("ID", style="cyan")
    for header in headers:
        table.add_column(header)
    for container, info in container_stat.items():
        name = info["name"]
        cpu_percent = info["cpu"] # Example: 0.0212
        ram_usage, ram_limit, ram_percent = info["memory"] # Bytes
        net_down, net_up = info["network"] # Bytes

        cpu_color = "green" if cpu_percent < 0.4 else "yellow" if cpu_percent < 80 else "red"
        mem_color = "green" if ram_percent < 0.6 else "yellow" if cpu_percent < 80 else "red"
        cpu = f"[{cpu_color}]{round(cpu_percent*100, 2)}%[/{cpu_color}]"
        mem_use = bytes_to_human(ram_usage)
        mem_lim = bytes_to_human(ram_limit)
        mem_percent = round(ram_percent*100, 2)
        mem = f"[{mem_color}]{mem_use}/{mem_lim} ({mem_percent}%)[/{mem_color}]"
        net_d = bytes_to_human(net_down)
        net_u = bytes_to_human(net_up)
        net = f"{net_d} ˅ / {net_up} ˄"
        table.add_row(name, container, cpu, mem)

    if table.rows:
        console.print(table)
    else:
        print("No containers found")

if __name__ == "__main__":
    try: client = docker.from_env()
    except:
        log("ERROR: Docker not found", 0)
        client = ""
    console = Console()

    id_containers = list_containers(client)
    named_containers = {info["name"]: {"id": c_id, "status": info["status"]} for c_id, info in id_containers.items()}

    cli()