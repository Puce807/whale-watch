import click
from utils import log
from config import *

def list_containers(client):
    containers = client.containers.list(all=True)
    if not containers:
        log("WARN: No containers found", 1)
        return None

    container_dict = {}
    for container in containers:
        name = container.name
        status = container.status
        short_id = container.short_id
        container_dict[short_id]["name"] = name
        container_dict[short_id]["status"] = status

    return container_dict
