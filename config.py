DEBUG = 2 # 0 = No debug (essential messages only), 1 = Warning Messages, 2 = Info

AUTO_GIT_PULL = True # Pull from the repository if there are new commits
CHECK_GIT = True # Check for new git commits and warn the user. Note: Has no effect if `AUTO_GIT_PULL` is True

STATUS_COLORS = {
    "running": "green",
    "exited": "red",
    "restarting": "orange",
    "created": "blue",
    "paused": "yellow",
    "removing": "magenta",
    "dead": "grey50"
}
