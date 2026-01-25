import subprocess
from config import *

def log(msg, tier):
    if DEBUG >= tier:
        print(msg)

def update_git():
    log("Checking for new commits...", 2)
    result = subprocess.run(["git", "rev-parse", "HEAD"],
                                  capture_output=True,
                                  text=True, check=True,
                                  stdout=subprocess.DEVNULL,
                                  stderr=subprocess.DEVNULL)
    local_commit = result.stdout.strip()
    result = subprocess.run(["git", "ls-remote","origin", "HEAD"],
                                 capture_output=True,
                                 text=True, check=True)
    repo_commit = result.stdout.split()[0]
    if local_commit == repo_commit:
        log("Git up-to-date", 2)
    else:
        log("Git out of date", 2)
        subprocess.run(["git", "pull"])
