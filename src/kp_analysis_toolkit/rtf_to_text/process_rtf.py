"""Core RTF to text processing functionality."""

import re
from pathlib import Path

from kp_analysis_toolkit.rtf_to_text.models.program_config import ProgramConfig
from kp_analysis_toolkit.utils.get_file_encoding import detect_encoding


def process_rtf_file(program_config: ProgramConfig) -> None:
    """
    Process an RTF file and convert it to plain text.

    Args:
        program_config: Configuration object containing input/output file paths

    Raises:
        FileNotFoundError: If the input file doesn't exist
        ValueError: If the file processing fails

    """
    input_file = program_config.input_file
    output_file = program_config.output_file

    # Check if input file exists
    if not input_file.exists():
        error_msg = f"Input file not found: {input_file}"
        raise FileNotFoundError(error_msg)

    # Check if input file has RTF extension
    if input_file.suffix.lower() != ".rtf":
        error_msg = f"Input file must have .rtf extension: {input_file}"
        raise ValueError(error_msg)

    try:
        # Try using striprtf first (preferred for pure Python)
        from striprtf.striprtf import rtf_to_text

        # Use charset-normalizer to detect the file encoding
        detected_encoding = detect_encoding(input_file)

        if detected_encoding != "unknown":
            rtf_content = input_file.read_text(encoding=detected_encoding)
        else:
            # Fallback to utf-8 with error handling if detection fails
            rtf_content = input_file.read_text(encoding="utf-8", errors="ignore")

        # Convert RTF to plain text
        plain_text = rtf_to_text(rtf_content)

    except ImportError:
        # Fallback to basic RTF parsing if striprtf is not available
        plain_text = _basic_rtf_to_text(input_file)

    # Write the plain text to output file with ASCII encoding
    output_file.write_text(plain_text, encoding="ascii", errors="ignore")


def _basic_rtf_to_text(input_file: Path) -> str:
    """
    Basic RTF to text conversion fallback.

    This is a simple fallback that strips basic RTF formatting.
    It's not as comprehensive as striprtf but works for basic files.

    Args:
        input_file: Path to the RTF file

    Returns:
        Plain text content

    """
    try:
        # Use charset-normalizer to detect the file encoding
        detected_encoding = detect_encoding(input_file)

        if detected_encoding != "unknown":
            rtf_content = input_file.read_text(encoding=detected_encoding)
        else:
            # Fallback to utf-8 with error handling if detection fails
            rtf_content = input_file.read_text(encoding="utf-8", errors="ignore")

        # Basic RTF control sequence removal
        # Remove RTF header and control words
        text = re.sub(r"{\\rtf.*?}", "", rtf_content, flags=re.DOTALL)
        text = re.sub(r"\\[a-z]+\d*\s?", "", text)
        text = re.sub(r"\\[^a-z]", "", text)
        text = re.sub(r"[{}]", "", text)

        # Clean up whitespace
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    except Exception as e:
        error_msg = f"Failed to process RTF file {input_file}: {e}"
        raise ValueError(error_msg) from e
