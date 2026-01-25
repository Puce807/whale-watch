import click
from utils import log
from config import *

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
