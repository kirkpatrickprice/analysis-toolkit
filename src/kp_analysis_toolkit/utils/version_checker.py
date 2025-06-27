"""Version checking utility for the KP Analysis Toolkit."""

import json
import shutil
import subprocess
import sys
from typing import Any
from urllib.error import URLError
from urllib.request import urlopen

import click
from packaging import version

from kp_analysis_toolkit import __version__


class VersionChecker:
    """Utility class to check for package updates on PyPI."""

    def __init__(self, package_name: str = "kp-analysis-toolkit") -> None:
        """
        Initialize the version checker.

        Args:
            package_name: The PyPI package name to check for updates

        """
        self.package_name = package_name
        self.current_version = __version__

    def check_for_updates(self, timeout: int = 5) -> tuple[bool, str | None]:
        """
        Check PyPI for available updates.

        Args:
            timeout: Timeout in seconds for the network request

        Returns:
            Tuple of (has_update, latest_version)
            - has_update: True if an update is available
            - latest_version: The latest version string, or None if check failed

        """
        try:
            url = f"https://pypi.org/pypi/{self.package_name}/json"
            # Only allow HTTPS URLs for security
            if not url.startswith("https://"):
                return False, None

            with urlopen(url, timeout=timeout) as response:  # noqa: S310
                data: dict[str, Any] = json.loads(response.read().decode())
                latest_version = data["info"]["version"]

            # Compare versions
            current = version.parse(self.current_version)
            latest = version.parse(latest_version)
        except (URLError, json.JSONDecodeError, KeyError, Exception):
            # Network error, JSON parsing error, or other issues
            return False, None
        else:
            return latest > current, latest_version

    def prompt_for_upgrade(self, latest_version: str) -> bool:
        """
        Prompt user to upgrade to the latest version.

        Args:
            latest_version: The latest available version

        Returns:
            True if user wants to upgrade, False otherwise

        """
        click.echo()
        click.secho(
            f"📦 Update available: {self.current_version} → {latest_version}",
            fg="yellow",
            bold=True,
        )
        click.echo(
            f"Current version: {self.current_version}\n"
            f"Latest version:  {latest_version}",
        )
        click.echo()

        return click.confirm(
            "Would you like to upgrade now?",
            default=False,
        )

    def _find_pipx_executable(self) -> str | None:
        """Find the pipx executable path."""
        return shutil.which("pipx")

    def upgrade_package(self) -> bool:
        """
        Upgrade the package using pipx.

        Returns:
            True if upgrade was successful, False otherwise

        """
        pipx_path = self._find_pipx_executable()
        if not pipx_path:
            click.secho(
                "❌ pipx not found. Please install pipx first:\n"
                "   pip install pipx\n"
                "   pipx ensurepath",
                fg="red",
            )
            return False

        try:
            click.echo("🔄 Upgrading package with pipx...")

            # First, try to upgrade using pipx upgrade
            result: subprocess.CompletedProcess[str] = subprocess.run(  # noqa: S603
                [pipx_path, "upgrade", self.package_name],
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
                check=False,  # Don't raise on non-zero exit
            )

            if result.returncode == 0:
                click.secho("✅ Package upgraded successfully!", fg="green", bold=True)
                return True

            # If upgrade fails, try reinstall
            click.echo("⚠️  Upgrade failed, trying reinstall...")
            result = subprocess.run(  # noqa: S603
                [pipx_path, "install", "--force", self.package_name],
                capture_output=True,
                text=True,
                timeout=300,
                check=False,
            )

            if result.returncode == 0:
                click.secho(
                    "✅ Package reinstalled successfully!",
                    fg="green",
                    bold=True,
                )
                return True

        except subprocess.TimeoutExpired:
            click.secho("❌ Upgrade timed out", fg="red")
            return False
        except subprocess.CalledProcessError as e:
            click.secho(f"❌ Upgrade failed: {e}", fg="red")
            return False
        else:
            click.secho(
                f"❌ Failed to upgrade package: {result.stderr}",
                fg="red",
            )
            return False

    def restart_application(self) -> None:
        """
        Attempt to restart the application.

        If restart is not feasible, notifies user to restart manually.
        """
        try:
            # Attempt to restart using the same command line arguments
            click.echo("🔄 Restarting application...")
            subprocess.Popen([sys.executable, *sys.argv])  # noqa: S603
            sys.exit(0)
        except Exception:  # noqa: BLE001
            # If restart fails, notify user
            click.secho(
                "✅ Upgrade complete! Please run the command again to use the new version.",
                fg="green",
                bold=True,
            )
            sys.exit(0)


def check_and_prompt_update(package_name: str = "kp-analysis-toolkit") -> None:
    """
    Check for updates and prompt user if available.

    This function should be called at the start of CLI execution.

    Args:
        package_name: The PyPI package name to check

    """
    checker = VersionChecker(package_name)

    try:
        has_update, latest_version = checker.check_for_updates()

        if latest_version is None:
            # Network error or other issue - fail silently
            click.echo("⚠️  Unable to check for updates (network unavailable)", err=True)
            return

        if has_update and latest_version:
            if checker.prompt_for_upgrade(latest_version):
                if checker.upgrade_package():
                    checker.restart_application()
                else:
                    click.echo("❌ Upgrade failed. Continuing with current version...")
            else:
                click.echo("Continuing with current version...")

    except Exception:  # noqa: BLE001, S110
        # Any unexpected error - fail silently and continue
        pass
