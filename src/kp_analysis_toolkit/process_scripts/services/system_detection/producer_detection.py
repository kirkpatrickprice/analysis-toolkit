# AI-GEN: gpt-4o|2025-01-30|system-detection-modular-refactor|reviewed:no
"""Producer detection implementation for system detection service."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from kp_analysis_toolkit.process_scripts.models.types import ProducerType
from kp_analysis_toolkit.process_scripts.services.system_detection.protocols import (
    ProducerDetector,
)

if TYPE_CHECKING:
    from kp_analysis_toolkit.core.services.file_processing.protocols import (
        ContentStreamer,
    )


class SignatureProducerDetector(ProducerDetector):
    """Producer detection using signature patterns."""

    def detect_producer(
        self, content_stream: ContentStreamer
    ) -> tuple[ProducerType, str] | None:
        """
        Detect system producer from content signatures.

        Args:
            content_stream: Content streamer for the file

        Returns:
            Tuple of (producer_type, version) or None if not detected

        """
        # Pattern to match KPWINVERSION, KPNIXVERSION, or KPMACVERSION with version
        pattern = r"(KPWINVERSION|KPNIXVERSION|KPMACVERSION):\s*(\d+\.\d+\.\d+)"

        # Search in the first few lines of the file for performance
        header_lines: list[str] = content_stream.get_file_header(lines=20)
        for line in header_lines:
            match: re.Match[str] | None = re.search(pattern, line, re.IGNORECASE)
            if match:
                producer_name = match.group(1).upper()
                version = match.group(2)

                # Map producer names to enum values
                producer_map = {
                    "KPWINVERSION": ProducerType.KPWINAUDIT,
                    "KPNIXVERSION": ProducerType.KPNIXAUDIT,
                    "KPMACVERSION": ProducerType.KPMACAUDIT,
                }

                producer_type = producer_map.get(producer_name)
                if producer_type:
                    return producer_type, version

        return None

    def get_known_producers(self) -> list[str]:
        """
        Get list of known producers.

        Returns:
            List of producer names that can be detected

        """
        return ["KPWINVERSION", "KPNIXVERSION", "KPMACVERSION"]
