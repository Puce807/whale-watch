import click
from utils import log
from config import *

def list_containers(client):
    containers = client.containers.list(all=True)
    if not containers:
        log("WARN: No containers found", 1)
        return None

    container_dict = {
        c.short_id: {"name": c.name, "status": c.status}
        for c in containers
    }

    return container_dict

def container_stats(client):
    container_names = list_containers(client).keys()
    stat_dict = {}
    for c_id in container_names:
        container = client.containers.get(c_id)
        stats = container.stats(stream=False)
        stat_dict[c_id] = stats
    return stat_dict