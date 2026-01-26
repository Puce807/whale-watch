import os.path
import subprocess
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
    return result.stdout.strip()  # remove newlines

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
    subprocess.run(["git", "pull"], capture_output=True)

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
