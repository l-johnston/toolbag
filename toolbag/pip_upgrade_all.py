"""Script to upgrade all installed packages"""
import subprocess
import asyncio
import itertools
from dataclasses import dataclass
import sys
from collections import OrderedDict
import argparse

# pylint: disable=invalid-name
def get_installed_pkgs():
    """Get installed packages"""
    proc = subprocess.run(["pip", "list"], check=True, capture_output=True, text=True)
    pip_list = proc.stdout.strip().split("\n")[2:]
    pkgs = OrderedDict()
    for line in pip_list:
        try:
            p, v = line.split()
        except ValueError:
            # package is locally installed
            pass
        pkgs[p] = v
    return pkgs


@dataclass
class State:
    """Signal for controlling asyncio tasks"""

    running: bool = False


GLYPH = itertools.cycle(["-", "\\", "|", "/"])


async def show_spinner(state):
    """Show spinner during upgrade process"""
    while state.running:
        sys.stdout.write(next(GLYPH))
        sys.stdout.flush()
        await asyncio.sleep(0.5)
        sys.stdout.write("\b")
    sys.stdout.write(" ")


async def upgrade(pkg, state):
    """Upgrade package pkg"""
    proc = subprocess.Popen(
        ["pip", "install", "-U"] + pkg,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
        text=True,
    )
    while proc.poll() is None:
        await asyncio.sleep(0.5)
    state.running = False
    _, errs = proc.communicate()
    if errs != "":
        print("\b \n" + errs)


async def upgrade_pip(state):
    """Upgrade pip"""
    proc = subprocess.Popen(
        ["python", "-m", "pip", "install", "-U", "pip"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
        text=True,
    )
    while proc.poll() is None:
        await asyncio.sleep(0.5)
    state.running = False
    _, errs = proc.communicate()
    if errs != "":
        print("\b \n" + errs)


def check_integrity():
    """run pip check"""
    proc = subprocess.run(["pip", "check"], check=True, capture_output=True, text=True)
    print(proc.stdout)


async def _main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--exclude", help="Exclude package", default=None)
    args = parser.parse_args()
    state = State()
    pkgs = get_installed_pkgs()
    pkg_lst = list(pkgs.keys())
    # remove pip to upgrade it first
    pkg_lst.remove("pip")
    try:
        pkg_lst.remove(args.exclude)
    except ValueError:
        pass
    state.running = True
    task = asyncio.gather(show_spinner(state), upgrade_pip(state))
    await asyncio.wait_for(task, timeout=None)
    task.exception()
    state.running = True
    sys.stdout.write("\b")
    task = asyncio.gather(show_spinner(state), upgrade(pkg_lst, state))
    await asyncio.wait_for(task, timeout=None)
    task.exception()
    pkgs_after = get_installed_pkgs()
    for pkg, original_version in pkgs.items():
        latest_version = pkgs_after[pkg]
        if latest_version != original_version:
            print(f"{pkg} {original_version} -> {latest_version}")
    check_integrity()


def main():
    """Upgrade all installed packages"""
    asyncio.run(_main())
