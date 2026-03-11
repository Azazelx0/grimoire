"""Self-updater — pull latest from GitHub and reinstall."""

import subprocess
import sys
from pathlib import Path


def get_install_dir() -> Path:
    return Path(__file__).resolve().parent.parent


def run_update():
    from grimoire import banner as b

    install_dir = get_install_dir()
    git_dir = install_dir / ".git"

    if not git_dir.exists():
        b.error("Not a git repository. Update requires a git clone install.")
        b.info("Install via: git clone https://github.com/Azazelx0/grimoire.git")
        return

    b.info("Pulling latest changes from GitHub...")
    result = subprocess.run(
        ["git", "pull", "origin", "main"],
        cwd=str(install_dir), capture_output=True, text=True,
    )

    if result.returncode != 0:
        b.error(f"Git pull failed: {result.stderr.strip()}")
        return

    pull_output = result.stdout.strip()
    b.success(f"Git: {pull_output}")

    if "Already up to date" in pull_output:
        b.success("GRIMOIRE is already up to date!")
        return

    b.info("Installing updated dependencies...")
    result = subprocess.run(
        [sys.executable, "-m", "pip", "install", "-r", "requirements.txt", "-q"],
        cwd=str(install_dir), capture_output=True, text=True,
    )

    if result.returncode != 0:
        b.warning(f"pip install warning: {result.stderr.strip()}")

    b.info("Reinstalling GRIMOIRE...")
    result = subprocess.run(
        [sys.executable, "-m", "pip", "install", "-e", ".", "-q"],
        cwd=str(install_dir), capture_output=True, text=True,
    )

    if result.returncode == 0:
        b.success("GRIMOIRE updated successfully!")
    else:
        b.error(f"Reinstall failed: {result.stderr.strip()}")
