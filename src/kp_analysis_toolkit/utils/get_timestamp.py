# Generate timestamp for filenames
def get_timestamp() -> str:
    """Generate a timestamp string in the format YYYYMMDD-HHMMSS."""
    from kp_analysis_toolkit.core.containers.application import container

    return container.core.timestamp_service().get_timestamp()
