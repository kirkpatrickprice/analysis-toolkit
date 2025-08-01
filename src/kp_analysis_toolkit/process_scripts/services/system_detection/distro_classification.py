# AI-GEN: gpt-4o|2025-01-30|system-detection-modular-refactor|reviewed:no
"""Distribution classification implementation for system detection service."""

from __future__ import annotations

from typing import TYPE_CHECKING

from kp_analysis_toolkit.process_scripts.models.types import DistroFamilyType
from kp_analysis_toolkit.process_scripts.services.system_detection.protocols import (
    DistroClassifier,
)

if TYPE_CHECKING:
    from kp_analysis_toolkit.core.services.file_processing.protocols import ContentStreamer


class DefaultDistroFamilyClassifier(DistroClassifier):
    """Default implementation for Linux distribution family classification."""

    def classify_distribution(self, content_stream: ContentStreamer, os_info: str) -> DistroFamilyType:
        """
        Classify Linux distribution family based on content and OS information.

        Args:
            content_stream: Content streamer for the file
            os_info: OS information string

        Returns:
            Distribution family type

        """
        os_info_lower = os_info.lower()

        # Define distribution mappings
        distro_mappings = {
            DistroFamilyType.DEB: ["ubuntu", "debian", "mint", "kali"],
            DistroFamilyType.RPM: [
                "rhel",
                "centos",
                "fedora",
                "red hat",
                "suse",
                "opensuse",
            ],
            DistroFamilyType.APK: ["alpine"],
        }

        # Check for known distributions by name
        for family, keywords in distro_mappings.items():
            if any(keyword in os_info_lower for keyword in keywords):
                return family

        # If not detected from name, try to detect from package manager presence
        package_manager_mappings = {
            DistroFamilyType.DEB: ["apt", "dpkg"],
            DistroFamilyType.RPM: ["yum", "rpm"],
            DistroFamilyType.APK: ["apk"],
        }

        for line in content_stream.stream_pattern_matches(
            r"apt|dpkg|yum|rpm|apk|zypper",
            max_matches=1,
        ):
            line_lower = line.lower()
            for family, managers in package_manager_mappings.items():
                if any(manager in line_lower for manager in managers):
                    return family

        return DistroFamilyType.OTHER

    def get_supported_distributions(self) -> list[DistroFamilyType]:
        """
        Get list of supported distributions.

        Returns:
            List of supported distribution family types

        """
        return [DistroFamilyType.DEB, DistroFamilyType.RPM, DistroFamilyType.APK, DistroFamilyType.OTHER]
