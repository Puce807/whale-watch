import os
import time
from pathlib import Path
from utils import log, file_size, search_file, shorten_path
from config import *
from rich.progress import Progress, BarColumn, TextColumn, TimeElapsedColumn
from rich.live import Live
from rich.table import Table
from rich.panel import Panel

def list_containers(client):
    containers = client.containers.list(all=True)
    if not containers:
        log("WARN: No containers found", 1)
        return {}

    container_dict = {
        c.short_id: {"name": c.name, "status": c.status}
        for c in containers
    }

    return container_dict

def calculate_cpu_percent(stats):
    cpu_delta = stats["cpu_stats"]["cpu_usage"]["total_usage"] - stats["precpu_stats"]["cpu_usage"]["total_usage"]
    system_delta = stats["cpu_stats"]["system_cpu_usage"] - stats["precpu_stats"]["system_cpu_usage"]
    cores = len(stats["cpu_stats"]["cpu_usage"].get("percpu_usage", [])) or 1

    if system_delta > 0 and cpu_delta > 0:
        return (cpu_delta / system_delta) * cores * 100.0
    return 0.0

def get_memory_usage(stats):
    usage = stats["memory_stats"].get("usage", 0)
    limit = stats["memory_stats"].get("limit", 1)
    percent = (usage / limit) * 100.0
    return usage, limit, percent

def get_network_io(stats):
    rx_total = tx_total = 0
    networks = stats.get("networks", {})
    for iface in networks.values():
        rx_total += iface.get("rx_bytes", 0)
        tx_total += iface.get("tx_bytes", 0)
    return rx_total, tx_total

def container_stats(client, status="running"):
    containers = client.containers.list(all=True)
    stat_dict = {}

    for container in containers:
        if status != "all" and container.status != status:
            continue

        stats = container.stats(stream=False)

        cpu = calculate_cpu_percent(stats)
        memory = get_memory_usage(stats)
        network = get_network_io(stats)

        stat_dict[container.short_id] = {
            "name": container.name,
            "cpu": cpu,
            "memory": memory,
            "network": network,
        }

    return stat_dict


def print_scan(return_dict, scan_path, end, files_scanned=0, size_scanned=0, files_per_sec=0):
    scan_path = shorten_path(scan_path)

    table = Table(show_header=True, header_style="green", show_lines=False)
    table.add_column("Target")
    table.add_column("Status")

    for target, path in return_dict.items():
        if path is None:
            status = f"[yellow]Scanning... {scan_path}[/yellow]"
        else:
            status = f"[green]Found! {path}[/green]"
        if end and path is None:
            status = f"[red]Not found[/red]"
        table.add_row(target, status)

    progress_text = f"[cyan]{files_scanned} files[/cyan] • " \
                    f"[magenta]{size_scanned / 1e6:.2f} MB[/magenta] • " \
                    f"[green]{files_per_sec:.1f} f/s[/green]"

    panel = Panel.fit(table, title=progress_text, border_style="bright_blue")

    return panel

def scan_compose(console, start, targets):
    stack = [start]
    return_dict = {}
    for target in targets: return_dict[target] = None
    f = 0
    files_scanned = 0
    size_scanned = 0
    start_time = time.time()
    with Live(console=console, refresh_per_second=4) as live:
        while stack:
            f += 1
            path = stack.pop()
            try:
                with os.scandir(path) as entries:
                    for entry in entries:
                        files_scanned += 1
                        size_scanned = file_size(entry.path)
                        elapsed = max(time.time() - start_time, 0.01)
                        files_per_sec = int(files_scanned / elapsed)
                        #if f % 10 == 0:
                            #log(entry.path, 2)
                        path_obj = Path(entry.path)
                        if entry.is_dir(follow_symlinks=False):
                            last_dir = path_obj.name
                            if last_dir.lower() not in IGNORE_DIRECTORIES:
                                stack.append(entry.path)
                            else:
                                continue
                        else:
                            ext = path_obj.suffix.lower()
                            if ext not in TARGET_FILE_TYPES:
                                continue
                            elif entry.name.lower() in TARGET_FILES and file_size(entry.path) <= SIZE_LIMIT:
                                for target in targets:
                                    if return_dict[target] is None and search_file(entry.path, target):
                                        return_dict[target] = entry.path

                        live.update(print_scan(return_dict, entry.path, end=False,
                                               files_scanned=files_scanned,
                                               size_scanned=size_scanned,
                                               files_per_sec=files_per_sec))

                        if all(return_dict[t] is not None for t in targets):
                            live.update(print_scan(return_dict, entry.path, True))
                            return return_dict

            except (PermissionError, FileNotFoundError, OSError):
                pass

    return return_dict