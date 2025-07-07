from __future__ import annotations

from pydantic import Field

from kp_analysis_toolkit.models.base import KPATBaseModel


class RichOutputConfig(KPATBaseModel):
    """Configuration model for RichOutput service."""

    verbose: bool = Field(
        default=False,
        description="Enable verbose output including debug messages",
    )
    quiet: bool = Field(
        default=False,
        description="Suppress non-essential output (errors still shown)",
    )
    console_width: int = Field(
        default=120,
        description="Console width in characters",
        ge=40,  # Minimum width
        le=300,  # Maximum width
    )
    force_terminal: bool = Field(
        default=True,
        description="Force terminal output even when not in TTY",
    )
    stderr_enabled: bool = Field(
        default=True,
        description="Enable separate error console output",
    )
