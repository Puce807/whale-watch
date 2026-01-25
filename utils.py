import subprocess
from config import *

def log(msg, tier):
    if DEBUG >= tier:
        print(msg)

def get_commit_message(commit):
    result = subprocess.run(["git", "log", "--format=%B", "-n", "1", commit])

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