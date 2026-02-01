DEBUG = 2 # 0 = No debug (essential messages only), 1 = Warning Messages, 2 = Info

AUTO_GIT_PULL = False # Pull from the repository if there are new commits. NOTE: May appear to slow down cli
PROMPT_UPDATES = True # Prompt the user for new commits. Note: Has no effect if `AUTO_GIT_PULL` is True

# --- Compose Scanning ---
IGNORE_DIRECTORIES = ["photos", "media", "documents", "windows", "system volume information", "$recycle.bin", "venv",
                      ".venv", "application data", "local settings", "temporary internet files",
                      "backups", "node_modules", "cache", "temp", "settings", "microsoft"] # Directories to ignore in scan
TARGET_FILE_TYPES = [".yml", ".yaml"] # Files types to target in scan, else will be ignored
TARGET_FILES = ["docker-compose.yml", "docker-compose.yaml", "compose.yml", "compose.yaml"] # Files to search for in scan
SIZE_LIMIT = 1000000 # Size limit for checking compose files, in bytes
GENERIC_SERVICE_NAMES = ["app", "db", "database", "postgres", "mysql",
                         "redis", "backend", "frontend", "api", "web"] # Generic service names to ignore to reduce false positives


# --- Cosmetic ---

STATUS_COLORS = {
    "running": "green",
    "exited": "red",
    "restarting": "orange",
    "created": "blue",
    "paused": "yellow",
    "removing": "magenta",
    "dead": "grey50"
}

# --- No need to change ---

CONTAINER_STATUS = ["all", "created", "restarting", "running", "removing", "paused", "exited", "dead"]

CACHE_PATH = "cache.json"

CMD_NAME = "ww" # If you would like to change the command used to access whale watch, this must be changed before install.py is run

VERSION = "0.3.7"