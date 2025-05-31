from pathlib import Path

from chardet import UniversalDetector  # To detect file encoding


def detect_encoding(file_path: str | Path) -> str:
    """
    Attempt to detect the encoding of the file.

    Uses chardet's UniversalDetector to analyze the file content.

    Args:
        file_path (str | Path): The path to the file whose encoding is to be detected.

    Returns:
        str: The detected encoding of the file, or "unknown" if detection fails.

    """
    detector = UniversalDetector()
    with Path(file_path).open("rb") as f:
        for line in f:
            detector.feed(line)
            if detector.done:
                break
        detector.close()
    encoding: str = detector.result.get("encoding", "unknown")

    return encoding
