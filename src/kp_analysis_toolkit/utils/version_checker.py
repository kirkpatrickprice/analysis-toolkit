"""Version checking utility for the KP Analysis Toolkit."""

import json
import sys
from typing import Any
from urllib.error import URLError
from urllib.request import urlopen

from packaging import version

from kp_analysis_toolkit import __version__
from kp_analysis_toolkit.utils.rich_output import get_rich_output


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

    def prompt_for_upgrade(self, latest_version: str) -> None:
        """
        Inform user about available upgrade and provide instructions.

        Args:
            latest_version: The latest available version

        """
        rich = get_rich_output()

        rich.header("📦 Update Available")

        # Get the command that was actually run
        actual_command = "kpat_cli"
        if len(sys.argv) > 0:
            # If running via python -m, show the expected command format
            if (
                sys.argv[0].endswith(("cli.py", "__main__.py"))
                or "kp_analysis_toolkit" in sys.argv[0]
            ):
                actual_command = "kpat_cli"
            else:
                # Use the actual command if it looks like our CLI
                cmd_name = sys.argv[0]
                if "kpat" in cmd_name.lower() or cmd_name.endswith(".exe"):
                    actual_command = cmd_name

        # Show version comparison in a panel
        version_info = f"""[yellow]Current version:[/yellow] {self.current_version}
[green]Latest version:[/green]  {latest_version}

To upgrade, run:
[bold cyan]pipx upgrade {self.package_name}[/bold cyan]

Or if you want to skip this check in the future:
[bold cyan]{actual_command} --skip-update-check[/bold cyan]"""

        rich.panel(version_info, title="Upgrade Instructions", border_style="yellow")

        rich.info(
            "The application will now exit. Please run the upgrade command above and then run your command again."
        )
        rich.warning(
            "Note: Upgrade checks can be disabled using the --skip-update-check option."
        )


def check_and_prompt_update(package_name: str = "kp-analysis-toolkit") -> None:
    """
    Check for updates and inform user if available.

    This function should be called at the start of CLI execution.
    If an update is available, it will display upgrade instructions and exit.

    Args:
        package_name: The PyPI package name to check

    """
    checker = VersionChecker(package_name)
    rich = get_rich_output()

    try:
        has_update, latest_version = checker.check_for_updates()

        if latest_version is None:
            # Network error or other issue - fail silently
            rich.debug("Unable to check for updates (network unavailable)")
            return

        if has_update and latest_version:
            checker.prompt_for_upgrade(latest_version)
            sys.exit(0)  # Exit after showing upgrade instructions

    except Exception:  # noqa: BLE001, S110
        # Any unexpected error - fail silently and continue
        pass
