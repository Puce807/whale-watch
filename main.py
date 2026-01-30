import docker
import click
from rich.console import Console
from pathlib import Path
from docker_cmds import *
from utils import *

@click.group()
@click.pass_context
def cli(ctx):
    """ Whale Watch CLI """
    if ctx.invoked_subcommand == "update":
        return

    if AUTO_GIT_PULL:
        if not check_git():
            update_git()
            log("Local repository updated, will take affect upon next run", 1)
    elif PROMPT_UPDATES:
        if not check_git():
            log("Local repository outdated", 0)
            answer = input("Pull new commits from repository? [y, n] ")
            if answer.lower() == "y":
                update_git()

@cli.command()
@click.option("-g", "--git", is_flag=True, help="Include git info")
def update(git):
    """Pulls new commits from the repository"""
    update_git()
    log("Local repository updated successfully", 2)
    log(f"Whale Watch Version {VERSION}", 2)
    if git:
        current_commit = get_local_commit()
        commit_msg = get_commit_message(current_commit)
        print(f"Commit: {current_commit}")
        print(f"Message: {commit_msg}")

@cli.command(name="version")
@click.option("-g", "--git", is_flag=True, help="Include git info")
def version(git):
    """Displays version"""
    current_commit = get_local_commit()
    commit_msg = get_commit_message(current_commit)
    print(f"Whale Watch Version {VERSION}")
    if git:
        print(f"Commit: {current_commit}")
        print(f"Message: {commit_msg}")

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
        cpu_percent = info["cpu"]
        ram_usage, ram_limit, ram_percent = info["memory"] # Bytes
        net_down, net_up = info["network"] # Bytes

        cpu_color = "green" if cpu_percent < 40 else "yellow" if cpu_percent < 80 else "red"
        mem_color = "green" if ram_percent < 60 else "yellow" if cpu_percent < 80 else "red"
        cpu = f"[{cpu_color}]{round(cpu_percent, 2)}%[/{cpu_color}]"
        mem_use = f"[cyan]{bytes_to_human(ram_usage)}[/cyan]"
        mem_lim = f"[white]{bytes_to_human(ram_limit)}[/white]"
        mem_percent = f"[{mem_color}]{round(ram_percent, 2)}%[/{mem_color}]"
        mem = f"{mem_use}/{mem_lim} ({mem_percent})"
        net_d = bytes_to_human(net_down)
        net_u = bytes_to_human(net_up)
        net = f"{net_d} ˅ / {net_u} ˄"
        table.add_row(name, container, cpu, mem, net)

    if table.rows:
        console.print(table)
    else:
        print("No containers found")

@cli.command()
@click.option("-d", "--drive", default="all", type=click.Choice(build_drive_options()),
              help="Select a specific drive to scan")
@click.option("-q", "--quiet", default=False, is_flag=True,
              help="Only print summary")
@click.option("-t", "--timeout", default="60", type=click.IntRange(0, 600),
              help="Timeout in seconds, 0 = No timeout")
def scan(drive, quiet, timeout):
    """Scan system for docker compose files"""
    # TODO: Add Flags
    # TODO: Add caching
    if drive == "all":
        drives = discover_drives()
    else:
        drives = [f"{drive}:\\"]
    container_names = named_containers.keys()
    if quiet:
        compose_dict = scan_compose(console, drives, container_names, cache, True, timeout)
    else:
        compose_dict = scan_compose(console, drives, container_names, cache, timeout=timeout)

    to_write = {}
    for name, path in compose_dict.items():
        container_id = named_containers[name]["id"]
        is_compose = path is not None
        to_write[name] = {"id": container_id, "compose": is_compose, "compose_path": path}
    cache_dict = cache | to_write
    write_json(cache_dict, CACHE_PATH)

if __name__ == "__main__":
    try: client = docker.from_env()
    except:
        log("ERROR: Docker not found", 0)
        client = ""
    console = Console()

    if file_exists(CACHE_PATH):
        cache = read_json(CACHE_PATH)
    else:
        cache = {}
        write_json({}, CACHE_PATH)
    print(f"Initial Cache: {cache}")

    id_containers = list_containers(client)
    named_containers = {info["name"]: {"id": c_id, "status": info["status"], "service": info["service"]} for c_id, info in id_containers.items()}
    new_cache = cache | named_containers
    cache.update(new_cache)
    write_json(new_cache, CACHE_PATH)
    print(f"New Cache: {new_cache}")

    cli()