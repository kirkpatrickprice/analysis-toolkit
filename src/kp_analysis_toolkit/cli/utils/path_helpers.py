from pathlib import Path

from kp_analysis_toolkit.core.containers.application import container
from kp_analysis_toolkit.core.services.rich_output import RichOutputService
from kp_analysis_toolkit.models.types import PathLike


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
        rich_output = container.core.rich_output()

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
