from pathlib import Path

from kp_analysis_toolkit.models.types import PathLike
from kp_analysis_toolkit.utils.get_timestamp import get_timestamp
from kp_analysis_toolkit.utils.rich_output import RichOutputService, get_rich_output


def create_results_directory(
    results_path: PathLike,
    rich_output: RichOutputService | None = None,
    *,
    verbose: bool = False,
) -> Path:
    """
    Create results directory with proper messaging.

    Args:
        results_path: Path to the results directory
        verbose: Whether to show debug messages
        rich_output: Optional RichOutput instance

    Returns:
        Validated results directory Path

    Example:
        results_dir = create_results_directory("results/", verbose=True)

    """
    if rich_output is None:
        rich_output = get_rich_output()

    path = Path(results_path).resolve()

    if path.exists():
        if verbose:
            rich_output.info(f"Reusing results path: {path}")
        return path

    if verbose:
        rich_output.debug(f"Creating results path: {path}")

    try:
        path.mkdir(parents=True, exist_ok=False)
    except OSError as e:
        message: str = f"Failed to create results directory {path}: {e}"
        raise ValueError(message) from e
    else:
        return path


def discover_files_by_pattern(
    base_path: PathLike,
    pattern: str = "*",
    *,
    recursive: bool = False,
) -> list[Path]:
    """
    Discover files matching a pattern in a directory.

    Args:
        base_path: Directory to search for files
        pattern: Glob pattern to match files (default: "*")
        recursive: If True, search subdirectories recursively (default: False)

    Returns:
        List of Path objects for all matching files

    Raises:
        ValueError: If base_path doesn't exist or is not a directory

    Examples:
        # Find all CSV files in current directory
        csv_files = discover_files_by_pattern("./", "*.csv")

        # Find all text files recursively
        txt_files = discover_files_by_pattern("./data", "*.txt", recursive=True)

    """
    base_path = Path(base_path).resolve()
    if not base_path.exists():
        message: str = f"Path does not exist: {base_path}"
        raise ValueError(message)
    if not base_path.is_dir():
        message: str = f"Path is not a directory: {base_path}"
        raise ValueError(message)

    if recursive:
        return list(base_path.rglob(pattern))
    return list(base_path.glob(pattern))


def generate_timestamped_path(
    base_path: PathLike,
    filename_prefix: str,
    extension: str = ".xlsx",
    timestamp: str | None = None,
) -> Path:
    """Generate a timestamped file path."""
    if timestamp is None:
        timestamp = get_timestamp()

    filename: str = f"{filename_prefix}_{timestamp}{extension}"
    return Path(base_path) / filename


def resolve_config_path(config_file: PathLike, config_base_path: Path) -> Path:
    """
    Resolve config file path, checking relative to config base path if needed.

    Args:
        config_file: Config file path (absolute, relative, or filename)
        config_base_path: Base directory for config files

    Returns:
        Resolved absolute path to config file

    Examples:
        # Absolute path - returned as-is
        resolve_config_path("/full/path/config.yaml", base_path)

        # Relative path - resolved relative to base
        resolve_config_path("../configs/audit.yaml", base_path)

        # Filename only - resolved in base directory
        resolve_config_path("audit-all.yaml", base_path)

    """
    config_path = Path(config_file)

    if config_path.is_absolute():
        resolved_path = config_path
    else:
        resolved_path = config_base_path / config_path

    resolved_path = resolved_path.resolve()

    if not resolved_path.exists():
        message = f"Config file does not exist: {resolved_path}"
        raise ValueError(message)

    if not resolved_path.is_file():
        message = f"Config path is not a file: {resolved_path}"
        raise ValueError(message)

    return resolved_path
