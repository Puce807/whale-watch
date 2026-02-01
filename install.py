import sys
import os
import platform
import subprocess
from config import CMD_NAME

def check_python_version():
    if sys.version_info < (3, 10):
        print("Whale Watch requires python 3.10 or later")
        sys.exit(1)
    elif sys.version_info != (3, 12):
        print("Warning: Whale Watch recommends python 3.12")

def path_in_env(path):
    paths = os.environ.get("PATH", "").split(os.pathsep)
    return any(os.path.abspath(path) == os.path.abspath(p) for p in paths)

def virtual_environment():
    if "VIRTUAL_ENV" in os.environ:
        return True
    else:
        return False

def main():
    print("Installing Whale Watch...")

    script_path = os.path.abspath("main.py")
    python_path = sys.executable
    cmd_name = CMD_NAME
    system = platform.system()

    if not virtual_environment():
        print("WARNING: Using a virtual environment is highly recommended")
        if input("Would you like to continue? [y/n]").lower() == "n":
            sys.exit(1)

    check_python_version()

    print("Installing dependencies...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])

    if system == "Windows":
        bin_dir = os.path.expandvars(r"%USERPROFILE%\bin")
        os.makedirs(bin_dir, exist_ok=True)
        bat_path = os.path.join(bin_dir, f"{cmd_name}.bat")
        with open(bat_path, "w") as f:
            f.write(f'@echo off\n"{python_path}" "{script_path}" %*\n')
        print(f"Shortcut created at {bat_path}")
        print(f"Ensure {bin_dir} is in your PATH to run '{cmd_name}' from anywhere. For instructions, check repo.")
    else:
        bin_dir = os.path.expanduser("~/.local/bin")
        os.makedirs(bin_dir, exist_ok=True)
        link_path = os.path.join(bin_dir, cmd_name)
        with open(link_path, "w") as f:
            f.write(f"""#!/usr/bin/env bash
            "{python_path}" "{script_path}" "$@"
            """)
        os.chmod(link_path, 0o775)
        print(f"Shortcut created at {link_path}")
        print(f"Ensure {bin_dir} is in your PATH to run '{cmd_name}' from anywhere. For instructions, check repo.")

    if not path_in_env(bin_dir):
        print(f"WARNING: '{bin_dir}' is not in your PATH")
        if system == "Windows":
            print("You can add it by running: ")
            print(f'setx PATH "%PATH%;{bin_dir}"')
            print("Then close and reopen your terminal")
        else:
            print("You can add it by adding this line to your shell config (~/.bashrc or ~/.zshrc):")
            print(f'export PATH="$PATH:{bin_dir}"')
            print("Then run: source ~/.bashrc  (or ~/.zshrc)")

    print(f"Done! You can now run '{cmd_name}' from any terminal.")

if __name__ == "__main__":
    main()
