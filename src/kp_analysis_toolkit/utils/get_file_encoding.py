from pathlib import Path

from charset_normalizer import CharsetMatch, from_path

from kp_analysis_toolkit.utils.rich_output import warning


def detect_encoding(file_path: str | Path) -> str | None:
    """
    Attempt to detect the encoding of the file.

    Uses charset-normalizer to analyze the file content.

    Args:
        file_path (str | Path): The path to the file whose encoding is to be detected.

    Returns:
        str | None: The detected encoding of the file, or None if detection fails.
                   None indicates the file should be skipped.

    """
    try:
        result: CharsetMatch | None = from_path(file_path).best()
    except (OSError, Exception):
        # Handle file access errors and charset_normalizer exceptions
        warning(f"Skipping file due to encoding detection failure: {file_path}")
        return None
    else:
        if result is not None:
            return result.encoding

        # Log the file that will be skipped due to encoding detection failure
        warning(f"Skipping file due to encoding detection failure: {file_path}")
        return None
