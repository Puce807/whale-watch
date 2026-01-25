DEBUG = 2 # 0 = No debug (essential messages only), 1 = Warning Messages, 2 = Info

AUTO_GIT_PULL = False # Pull from the repository if there are new commits. NOTE: May appear to slow down cli
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