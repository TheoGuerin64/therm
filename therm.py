# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "questionary",
#     "rich",
# ]
# ///

from __future__ import annotations

import os
import platform
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable, Protocol

from questionary import checkbox, confirm
from rich.status import Status

RAW_REPOSITORY_URL = "https://raw.githubusercontent.com/TheoGuerin64/therm/main"
GHOSTTY_CONFIG = Path("~/.config/ghostty/config").expanduser()


class Exit(Exception):
    pass


class Error(Exception):
    pass


def execute(
    command: str, *, capture: bool = False
) -> subprocess.CompletedProcess[bytes]:
    output = subprocess.PIPE if capture else subprocess.DEVNULL
    return subprocess.run(
        command,
        shell=True,
        check=True,
        stdout=output,
        stderr=output,
    )


def execute_pipeline(
    *commands: str, capture: bool = False
) -> subprocess.CompletedProcess[bytes]:
    return execute(" | ".join(commands), capture=capture)


class Distribution(Protocol):
    @staticmethod
    def system_upgrade() -> None: ...

    @staticmethod
    def is_package_missing(package: str) -> bool: ...

    @staticmethod
    def install_packages(*packages: str) -> None: ...

    @staticmethod
    def ghostty_installed() -> bool: ...

    @staticmethod
    def install_ghostty() -> None: ...


class Debian:
    @staticmethod
    def system_upgrade() -> None:
        execute("sudo apt update && sudo apt upgrade -y")

    @staticmethod
    def is_package_missing(package: str) -> bool:
        try:
            execute(f"dpkg -s {package}")
        except subprocess.CalledProcessError as e:
            if e.returncode == 1:
                return True
            raise
        return False

    @staticmethod
    def install_packages(*packages: str) -> None:
        execute(f"sudo apt install -y {' '.join(packages)}")

    @staticmethod
    def ghostty_installed() -> bool:
        return Debian.is_package_missing("ghostty") is False

    @staticmethod
    def install_ghostty() -> None:
        REPOSITORY_URL = "https://download.opensuse.org/repositories/home:/clayrisser:/bookworm/Debian_12"
        APT_SOURCE_LIST_PATH = "/etc/apt/sources.list.d/home:clayrisser:bookworm.list"
        TRUSTED_GPG_KEY_PATH = "/etc/apt/trusted.gpg.d/home_clayrisser_bookworm.gpg"

        execute_pipeline(
            f"echo 'deb {REPOSITORY_URL}/ /'",
            f"sudo tee {APT_SOURCE_LIST_PATH}",
        )
        execute_pipeline(
            f"curl -fsSL {REPOSITORY_URL}/Release.key",
            "gpg --dearmor",
            f"sudo tee {TRUSTED_GPG_KEY_PATH}",
        )
        execute("sudo apt update")
        execute("sudo apt install -y ghostty")


DISTRIBUTION_MAPPING = {
    "debian": Debian,
}


class Settings:
    pass


@dataclass
class GhosttySettings(Settings):
    overwrite: bool


def setup_ghostty_settings() -> GhosttySettings:
    settings = GhosttySettings(overwrite=False)
    if not GHOSTTY_CONFIG.exists():
        return settings

    print("Ghostty configuration file already exists")
    if confirm("Do you want to overwrite it?").ask():
        settings.overwrite = True

    return settings


def configure_ghostty(settings: GhosttySettings) -> None:
    CONFIG_URL = f"{RAW_REPOSITORY_URL}/ghostty/config"

    if not GHOSTTY_CONFIG.parent.exists():
        execute(f"mkdir -p '{GHOSTTY_CONFIG.parent}'")

    if GHOSTTY_CONFIG.exists():
        if not settings.overwrite:
            return
        execute(f"rm -f {GHOSTTY_CONFIG}")

    execute(f"curl -fsSL {CONFIG_URL} -o {GHOSTTY_CONFIG}")


@dataclass
class Component[T: Settings = Settings]:
    name: str
    required_packages: tuple[str, ...]
    installed: Callable[[Distribution], bool]
    install: Callable[[Distribution], None]
    setup_settings: Callable[[], T]
    configure: Callable[[T], None]
    settings: T | None = None


COMPONENTS = (
    Component(
        name="Ghostty",
        required_packages=("curl", "gpg"),
        installed=lambda d: d.ghostty_installed(),
        install=lambda d: d.install_ghostty(),
        setup_settings=setup_ghostty_settings,
        configure=configure_ghostty,
    ),
)


def identify_distribution() -> Distribution:
    system = platform.system()
    if system != "Linux":
        raise Error("this script is designed for Linux systems only")

    raw_distribution = platform.freedesktop_os_release().get("ID")
    if not raw_distribution:
        raise Error("could not determine the Linux distribution from /etc/os-release")

    distribution = DISTRIBUTION_MAPPING.get(raw_distribution)
    if not distribution:
        raise Exit(
            f"Unsupported Linux distribution: {raw_distribution}\n"
            f"This script currently supports: {', '.join(DISTRIBUTION_MAPPING.keys())}"
        )

    return distribution


def install_requirements(
    distribution: Distribution, requirements: Iterable[str]
) -> None:
    missing_packages = tuple(filter(distribution.is_package_missing, requirements))
    if not missing_packages:
        return

    print(f"Required packages missing: {', '.join(missing_packages)}")
    if not confirm("Install these packages to continue?").ask():
        raise Exit("Installation cancelled by user")

    with Status("Installing packages..."):
        distribution.install_packages(*missing_packages)


def install_components(distribution: Distribution) -> None:
    selected_components: list[Component] = checkbox(
        "This script will install the following components:",
        choices=[{"name": c.name, "value": c} for c in COMPONENTS],
    ).ask()
    if not selected_components:
        return

    for component in selected_components:
        component.settings = component.setup_settings()

    required_packages = [
        package
        for component in selected_components
        for package in component.required_packages
    ]
    install_requirements(distribution, required_packages)

    for component in selected_components:
        if not component.installed(distribution):
            with Status(f"Installing {component.name}..."):
                component.install(distribution)

        assert component.settings is not None
        component.configure(component.settings)


def main() -> None:
    distribution = identify_distribution()
    if os.geteuid() != 0:
        raise Error("script must be run as root (use sudo)")
    if confirm("Do you want to update the system?").ask():
        with Status("Updating system..."):
            distribution.system_upgrade()
    install_components(distribution)


if __name__ == "__main__":
    try:
        main()
    except Exit as e:
        print(f"{e}")
        raise SystemExit(0)
    except Error as e:
        print(f"error: {e}", file=sys.stderr)
        raise SystemExit(1)
