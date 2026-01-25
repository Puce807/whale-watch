import subprocess
from config import *

def log(msg, tier):
    if DEBUG >= tier:
        print(msg)

def check_git():
    result = subprocess.run(["git", "rev-parse", "HEAD"],
                            capture_output=True,
                            text=True, check=True, )
    local_commit = result.stdout.strip()
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