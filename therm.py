# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "questionary",
# ]
# ///

import platform
import subprocess
import sys
from enum import StrEnum, auto

import questionary


def execute(command: str) -> subprocess.CompletedProcess:
    return subprocess.run(command, shell=True, capture_output=True, check=True)


def execute_pipeline(*commands: str) -> subprocess.CompletedProcess:
    return execute(" | ".join(commands))


class MessageException(Exception):
    def __init__(self, message: str):
        super().__init__(message)


class Exit(MessageException):
    pass


class Error(MessageException):
    pass


class Distribution(StrEnum):
    FEDORA = auto()


def identify_distribution() -> Distribution:
    system = platform.system()
    if system != "Linux":
        raise Exit("This script is designed for Linux systems only.")

    raw_distribution = platform.freedesktop_os_release().get("ID")
    if not raw_distribution:
        raise Error("Could not determine the Linux distribution from /etc/os-release.")

    try:
        distribution = Distribution(raw_distribution)
    except ValueError:
        raise Exit(
            f"Unsupported Linux distribution: {raw_distribution}.\n"
            f"This script currently supports: {', '.join(Distribution)}."
        )

    return distribution


def run() -> None:
    distribution = identify_distribution()
    questionary.print(f"You are running {distribution}.")


def main() -> None:
    try:
        run()
    except Exit as e:
        print(f"{e}")
        raise SystemExit(0)
    except Error as e:
        print(f"error: {e}", file=sys.stderr)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
