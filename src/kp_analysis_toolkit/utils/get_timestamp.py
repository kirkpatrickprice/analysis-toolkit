from datetime import datetime


# Generate timestamp for filenames
def get_timestamp() -> str:
    """Generate a timestamp string in the format YYYYMMDD-HHMMSS."""
    return datetime.now().strftime("%Y%m%d-%H%M%S")  # noqa: DTZ005
