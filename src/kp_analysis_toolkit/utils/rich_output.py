"""
Backward compatibility layer for RichOutput.

This file provides the legacy global singleton interface while delegating
to the dependency-injected service. This ensures existing code continues
to work during the transition period.
"""

from __future__ import annotations

from kp_analysis_toolkit.core.services.rich_output import RichOutputService

# Re-export the main class for backward compatibility
RichOutput = RichOutputService
RichOutput = RichOutputService

# Global instance for backward compatibility (will be deprecated)
_rich_output: RichOutputService | None = None


def get_rich_output(*, verbose: bool = False, quiet: bool = False) -> RichOutputService:
    """
    Get or create the global RichOutput instance.

    DEPRECATED: This function is maintained for backward compatibility.
    New code should use dependency injection instead.

    If verbose or quiet parameters are provided, a new instance is created
    with those settings. Otherwise, returns the DI-managed singleton.
    """
    global _rich_output

    # If no parameters are overridden, try to use DI container
    if not verbose and not quiet:
        try:
            from kp_analysis_toolkit.core.containers.application import container

            return container.core().rich_output()
        except Exception:
            # Fall back to legacy behavior if DI not initialized
            pass

    # Create new instance or update existing one if parameters are provided
    if _rich_output is None or verbose or quiet:
        from kp_analysis_toolkit.models.rich_config import RichOutputConfig

        config = RichOutputConfig(verbose=verbose, quiet=quiet)
        _rich_output = RichOutputService(config)

    return _rich_output


# Convenience functions maintained for backward compatibility
def info(text: str, *, force: bool = False) -> None:
    """DEPRECATED: Use dependency-injected RichOutput service instead."""
    get_rich_output().info(text, force=force)


def success(text: str, *, force: bool = False) -> None:
    """DEPRECATED: Use dependency-injected RichOutput service instead."""
    get_rich_output().success(text, force=force)


def warning(text: str, *, force: bool = False) -> None:
    """DEPRECATED: Use dependency-injected RichOutput service instead."""
    get_rich_output().warning(text, force=force)


def error(text: str, *, force: bool = True) -> None:
    """DEPRECATED: Use dependency-injected RichOutput service instead."""
    get_rich_output().error(text, force=force)


def debug(text: str) -> None:
    """DEPRECATED: Use dependency-injected RichOutput service instead."""
    get_rich_output().debug(text)


def header(text: str, *, force: bool = False) -> None:
    """DEPRECATED: Use dependency-injected RichOutput service instead."""
    get_rich_output().header(text, force=force)


def subheader(text: str, *, force: bool = False) -> None:
    """DEPRECATED: Use dependency-injected RichOutput service instead."""
    get_rich_output().subheader(text, force=force)
