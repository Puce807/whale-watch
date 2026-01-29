import os
import time
from pathlib import Path
from utils import log, file_size, search_file, shorten_path, bytes_to_human
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


def print_scan(return_dict, scan_path, end,
               files_scanned=0, size_scanned=0, files_per_sec=0):

    scan_path = shorten_path(scan_path)

    max_width = max(len(t) for t in return_dict.keys())
    col_width = min(max_width, 20)  # max 20 chars, but smaller if targets are short

    table = Table(show_header=True, header_style="bold green", expand=True)
    table.add_column("Target", style="cyan", no_wrap=True, width=col_width)
    table.add_column("Status", style="white")

    for target, path in return_dict.items():
        if path:
            status = f"[green]Found[/green] {shorten_path(path)}"
        elif end:
            status = "[red]Not found[/red]"
        else:
            status = f"[yellow]… scanning[/yellow] {scan_path}"

        table.add_row(target, status)


    stats = (
        f"[green]{files_scanned:,}[/green] files • "
        f"[green]{bytes_to_human(size_scanned)}[/green] • "
        f"[green]{files_per_sec:,.0f} f/s[/green] • "
    )

    return Panel(
        table,
        title=stats,
        border_style="green",
        padding=(1, 2),
    )

def scan_compose(console, starts, targets, quiet=False, timeout=60):
    stack = [str(s) for s in starts]

    targets = [t.lower() for t in targets]
    return_dict: dict[str, str | None] = {t: None for t in targets}

    files_scanned = 0
    size_scanned = 0
    start_time = time.time()
    last_render = 0
    last_path = stack[0] if stack else ""
    found = 0
    killed_by_timeout = False

    with Live(console=console, refresh_per_second=12) as live:
        while stack:
            path = stack.pop()
            last_path = path
            try:
                with os.scandir(path) as entries:
                    for entry in entries:
                        files_scanned += 1
                        try:
                            size_scanned += entry.stat(follow_symlinks=False).st_size
                        except OSError:
                            pass

                        path_obj = Path(entry.path)

                        if entry.is_dir(follow_symlinks=False):
                            if path_obj.name.lower() not in IGNORE_DIRECTORIES:
                                stack.append(entry.path)
                            continue

                        if (
                            path_obj.suffix.lower() in TARGET_FILE_TYPES
                            and entry.name.lower() in TARGET_FILES
                            and file_size(entry.path) <= SIZE_LIMIT
                        ):
                            for target in targets:
                                if return_dict[target] is None and search_file(entry.path, target):
                                    return_dict[target] = entry.path
                                    found += 1

                        now = time.time()
                        if now - last_render > 0.1:
                            elapsed = max(now - start_time, 0.01)
                            fps = int(files_scanned / elapsed)
                            if elapsed > timeout or timeout == 0:
                                killed_by_timeout = True
                                break

                            if not quiet: live.update(
                                print_scan(
                                    return_dict,
                                    last_path,
                                    end=False,
                                    files_scanned=files_scanned,
                                    size_scanned=size_scanned,
                                    files_per_sec=fps,
                                )
                            )
                            last_render = now

            except (PermissionError, FileNotFoundError, OSError):
                pass

        elapsed = max(time.time() - start_time, 0.01)
        fps = int(files_scanned / elapsed)
        if not quiet: live.update(
            print_scan(
                return_dict,
                last_path,
                end=True,
                files_scanned=files_scanned,
                size_scanned=size_scanned,
                files_per_sec=fps,
            )
        )
        print(f"Found the location of compose files for {found}/{targets}")
        if killed_by_timeout: print(f"Scan was ended by timeout ({timeout}). Scan may be incomplete, to try again use "
                                    f"scan --timeout 120")
        time.sleep(0.2)

    return return_dict

