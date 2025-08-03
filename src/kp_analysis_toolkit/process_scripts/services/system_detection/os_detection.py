"""OS detection implementation for system detection service."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from kp_analysis_toolkit.process_scripts.models.types import (
    OSFamilyType,
    ProducerType,
)
from kp_analysis_toolkit.process_scripts.services.system_detection.protocols import (
    OSDetector,
)

if TYPE_CHECKING:
    from kp_analysis_toolkit.core.services.file_processing.protocols import (
        ContentStreamer,
    )


class RegexOSDetector(OSDetector):
    """OS detection using regex patterns."""

    def detect_os(
        self,
        content_stream: ContentStreamer,
        producer_type: ProducerType,
    ) -> dict[str, str | None]:
        """
        Detect OS details from system content.

        Args:
            content_stream: Content streamer for the file
            producer_type: The detected producer type

        Returns:
            Dictionary of OS-specific details

        """
        if producer_type == ProducerType.KPWINAUDIT:
            return self._get_windows_details(content_stream)
        if producer_type == ProducerType.KPNIXAUDIT:
            return self._get_linux_details(content_stream)
        if producer_type == ProducerType.KPMACAUDIT:
            return self._get_darwin_details(content_stream)
        return {}

    def get_supported_os_types(self) -> list[OSFamilyType]:
        """
        Get list of supported OS types.

        Returns:
            List of supported OS family types

        """
        return [OSFamilyType.WINDOWS, OSFamilyType.LINUX, OSFamilyType.DARWIN]

    def _get_windows_details(
        self,
        content_stream: ContentStreamer,
    ) -> dict[str, str | None]:
        """
        Extract Windows-specific system details.

        Args:
            content_stream: Content streamer for the file

        Returns:
            Dictionary of Windows-specific details

        """
        details: dict[str, str | None] = {
            "product_name": None,
            "release_id": None,
            "current_build": None,
            "ubr": None,
            "system_os": None,
        }

        # Look for Windows version information
        for line in content_stream.stream_pattern_matches(
            r"ProductName|ReleaseId|CurrentBuild|UBR|Windows",
        ):
            # Extract ProductName
            if "ProductName" in line:
                match: re.Match[str] | None = re.search(
                    r"ProductName[:\s]+(.+)", line, re.IGNORECASE,
                )
                if match:
                    details["product_name"] = match.group(1).strip()
                    details["system_os"] = match.group(1).strip()

            # Extract ReleaseId
            elif "ReleaseId" in line:
                match = re.search(r"ReleaseId[:\s]+(.+)", line, re.IGNORECASE)
                if match:
                    details["release_id"] = match.group(1).strip()

            # Extract CurrentBuild
            elif "CurrentBuild" in line:
                match = re.search(r"CurrentBuild[:\s]+(.+)", line, re.IGNORECASE)
                if match:
                    details["current_build"] = match.group(1).strip()

            # Extract UBR
            elif "UBR" in line:
                match = re.search(r"UBR[:\s]+(.+)", line, re.IGNORECASE)
                if match:
                    details["ubr"] = match.group(1).strip()

        return details

    def _get_linux_details(
        self,
        content_stream: ContentStreamer,
    ) -> dict[str, str | None]:
        """
        Extract Linux-specific system details.

        Args:
            content_stream: Content streamer for the file

        Returns:
            Dictionary of Linux-specific details

        """
        details = {
            "os_pretty_name": None,
            "os_version": None,
            "system_os": None,
        }

        # Look for Linux distribution information
        for line in content_stream.stream_pattern_matches(
            r"PRETTY_NAME|VERSION|ID=|Ubuntu|CentOS|RHEL|Debian|SUSE",
        ):
            # Extract PRETTY_NAME
            if "PRETTY_NAME" in line:
                match = re.search(r'PRETTY_NAME[=\s]+"?([^"]+)"?', line, re.IGNORECASE)
                if match:
                    details["os_pretty_name"] = match.group(1).strip()
                    details["system_os"] = match.group(1).strip()

            # Extract VERSION
            elif "VERSION=" in line and "VERSION_ID" not in line:
                match = re.search(r'VERSION[=\s]+"?([^"]+)"?', line, re.IGNORECASE)
                if match:
                    details["os_version"] = match.group(1).strip()

        return details

    def _get_darwin_details(
        self,
        content_stream: ContentStreamer,
    ) -> dict[str, str | None]:
        """
        Extract Darwin/macOS-specific system details.

        Args:
            content_stream: Content streamer for the file

        Returns:
            Dictionary of Darwin-specific details

        """
        details = {
            "system_os": None,
            "os_version": None,
        }

        # Look for macOS version information
        for line in content_stream.stream_pattern_matches(
            r"macOS|Darwin|ProductVersion|SystemVersion",
        ):
            # Extract macOS version information
            if "ProductVersion" in line or "SystemVersion" in line:
                match = re.search(
                    r"(?:Product|System)Version[:\s]+(.+)",
                    line,
                    re.IGNORECASE,
                )
                if match:
                    details["os_version"] = match.group(1).strip()
                    details["system_os"] = f"macOS {match.group(1).strip()}"
            elif "macOS" in line:
                match = re.search(r"macOS\s+(.+)", line, re.IGNORECASE)
                if match:
                    details["system_os"] = f"macOS {match.group(1).strip()}"

        return details
