import os
import sys
import subprocess
import json

import psutil
from pathlib import Path
from config import *

def log(msg, tier):
    if DEBUG >= tier:
        print(msg)

def get_commit_message(commit):
    result = subprocess.run(
        ["git", "log", "--format=%B", "-n", "1", commit],
        capture_output=True,
        text=True,
        check=True
    )
    return result.stdout.strip()

def get_local_commit():
    result = subprocess.run(["git", "rev-parse", "HEAD"],
                            capture_output=True,
                            text=True, check=True, )
    return result.stdout.strip()

def check_git():
    local_commit = get_local_commit()
    result = subprocess.run(["git", "ls-remote", "origin", "HEAD"],
                            capture_output=True,
                            text=True, check=True)
    repo_commit = result.stdout.split()[0]
    if local_commit == repo_commit:
        return True # Up-to-date
    else:
        return False # New commits

def update_git():
    result = subprocess.run(["git", "pull"], capture_output=True)
    if "Already up to date" not in result:
        log("Run script again for update to take affect", 1)

def search_file(file_path, search_str):
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                if search_str in line:
                    return True
        return False
    except (PermissionError, FileNotFoundError):
        return False

def file_size(file):
    try:
        return os.path.getsize(file)
    except (FileNotFoundError, PermissionError):
        return None

def bytes_to_human(n_bytes):
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if n_bytes < 1024:
            return f"{n_bytes:.1f}{unit}"
        n_bytes /= 1024
    return f"{n_bytes:.1f}PB"


def shorten_path(path: str, max_len: int = 60) -> str:
    p = Path(path)
    name = p.name
    start = str(p.parent)
    display = f"{start}/{name}"
    if len(display) <= max_len:
        return display
    truncated_start = "…" + start[-(max_len - len(name) - 4):]
    return f"{truncated_start}/{name}"

def discover_drives():
    try:
        partitions = psutil.disk_partitions(all=False)
        drives = [p.device for p in partitions]
        return drives
    except Exception(FileNotFoundError, PermissionError, OSError) as e:
        log(f"Error discovering drives: {e}", 1)
        return []

def build_drive_options():
    drives = discover_drives()
    drives = [d.replace("\\", "").replace(":", "") for d in drives]
    drives.insert(0, "all")
    return drives

def write_json(msg, filepath):
    json_str = json.dumps(msg, indent=4)
    try:
        with open(filepath, "w") as f:
            f.write(json_str)
    except PermissionError:
        log("Error: Permission error when writing to file", 1)

def read_json(filepath):
    try:
        with open(filepath, "r") as f:
            data = json.load(f)
        return data
    except (FileNotFoundError, PermissionError):
        log("Error: File not found", 1)

def file_exists(filepath):
    return Path(CACHE_PATH).exists()