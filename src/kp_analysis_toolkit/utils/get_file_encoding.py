from pathlib import Path

from charset_normalizer import CharsetMatch, from_path


def detect_encoding(file_path: str | Path) -> str:
    """
    Attempt to detect the encoding of the file.

    Uses charset-normalizer to analyze the file content.

    Args:
        file_path (str | Path): The path to the file whose encoding is to be detected.

    Returns:
        str: The detected encoding of the file, or "unknown" if detection fails.

    """
    result: CharsetMatch | None = from_path(file_path).best()

    if result is not None:
        return result.encoding

    return "unknown"
