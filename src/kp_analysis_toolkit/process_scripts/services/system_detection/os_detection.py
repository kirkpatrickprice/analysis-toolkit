from kp_analysis_toolkit.process_scripts.models.base import RegexPatterns
from kp_analysis_toolkit.process_scripts.models.types import (
    OSFamilyType,
    ProducerType,
)
from kp_analysis_toolkit.process_scripts.services.system_detection.protocols import (
    OSDetector,
)


class RegexOSDetector(OSDetector):
    """OS detection using regex patterns."""

    def detect_os_family(self, content: str) -> OSFamilyType:
        """Detect OS family from system content."""
        # Enhanced implementation with better error handling

        # Configuration for each producer type using Pydantic models
        os_patterns: dict[ProducerType, RegexPatterns] = {
            ProducerType.KPWINAUDIT: RegexPatterns(
                patterns={
                    "product_name": r"^System_OSInfo::ProductName\s*:\s*(?P<product_name>.*)",
                    "release_id": r"^System_OSInfo::ReleaseId\s*:\s*(?P<release_id>.*)",
                    "current_build": r"^System_OSInfo::CurrentBuild\s*:\s*(?P<current_build>\d+)",
                    "ubr": r"^System_OSInfo::UBR\s*:\s*(?P<ubr>\d+)",
                },
                formatter=lambda data: f"{data['product_name']} (Build {data['current_build']}.{data['ubr']})",
            ),
            ProducerType.KPNIXAUDIT: RegexPatterns(
                patterns={
                    "system_os": r'^System_VersionInformation::/etc/os-release::PRETTY_NAME="(?P<system_os>.*)"',
                    "os_pretty_name": r'^System_VersionInformation::/etc/os-release::PRETTY_NAME="(?P<os_pretty_name>.*)"',
                },
                formatter=lambda data: data["system_os"],
            ),
            ProducerType.KPMACAUDIT: RegexPatterns(
                patterns={
                    "product_name": r"^System_VersionInformation::ProductName\s*:\s*(?P<product_name>.*)",
                    "product_version": r"^System_VersionInformation::ProductVersion\s*:\s*(?P<product_version>[\d.]+)",
                    "build_version": r"^System_VersionInformation::BuildVersion\s*:\s*(?P<build_version>[A-Za-z0-9]+)",
                },
                formatter=lambda data: f"{data['product_name']} {data['product_version']} (Build {data['build_version']})",
            ),
        }

        patterns: RegexPatterns | None = os_patterns.get(producer)
        if not patterns:
            return None, None

        extracted_data: tuple[str, dict[str, str]] = _extract_regex_data_with_raw(
            file=file,
            encoding=encoding,
            patterns=patterns,
        )
        if extracted_data:
            formatted_string, raw_data = extracted_data
            return formatted_string, raw_data

        return None, None
