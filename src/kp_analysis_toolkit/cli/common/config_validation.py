"""Configuration validation utilities for CLI commands."""

import sys
from pathlib import Path

from pydantic import ValidationError

from kp_analysis_toolkit.core.containers.application import container
from kp_analysis_toolkit.core.services.rich_output import RichOutputService
from kp_analysis_toolkit.models.base import KPATBaseModel
from kp_analysis_toolkit.models.types import ConfigValue, PathLike, T

# Import for enhanced error display (conditional to avoid circular imports)
try:
    from kp_analysis_toolkit.cli.common.output_formatting import (
        ErrorDisplayOptions,
        display_cli_error,
    )

    _ENHANCED_ERROR_AVAILABLE = True
except ImportError:
    _ENHANCED_ERROR_AVAILABLE = False


class EnhancedErrorOptions(KPATBaseModel):
    """Options for enhanced error display."""

    context: str | None = None
    suggestions: list[str] | None = None
    error_code: str | None = None
    show_help_hint: bool = True


def validate_program_config(config_class: type[T], **kwargs: ConfigValue) -> T:
    """
    Validate program configuration using a Pydantic model.

    Args:
        config_class: The Pydantic model class to validate against
        **kwargs: Configuration parameters to validate

    Returns:
        Validated configuration object

    Raises:
        ValueError: If validation fails

    Example:
        try:
            config = validate_program_config(ProgramConfig, input_file=file_path)
        except ValueError as e:
            handle_fatal_error(e)

    """
    try:
        return config_class(**kwargs)
    except ValidationError as e:
        # Convert Pydantic ValidationError to a more user-friendly ValueError
        error_messages: list[str] = []
        for error in e.errors():
            field: str = (
                " -> ".join(str(loc) for loc in error["loc"])
                if error["loc"]
                else "config"
            )
            message: str = error["msg"]
            error_messages.append(f"{field}: {message}")

        combined_message: str = "; ".join(error_messages)
        error_msg: str = f"Configuration validation failed: {combined_message}"
        raise ValueError(error_msg) from e


def handle_fatal_error(
    error: Exception,
    *,
    error_prefix: str = "Error",
    exit_on_error: bool = True,
    rich_output: RichOutputService | None = None,
) -> None:
    """
    Handle fatal errors with consistent messaging and exit behavior.

    Args:
        error: The exception that occurred
        error_prefix: Custom prefix for the error message (default: "Error")
        exit_on_error: Whether to exit the program after displaying the error
        rich_output: Optional RichOutput instance (will create one if not provided)

    Example:
        try:
            config = validate_program_config(ProgramConfig, **cli_args)
        except ValueError as e:
            handle_fatal_error(e, error_prefix="Configuration validation failed")

        try:
            selected_file = get_input_file(...)
        except ValueError as e:
            handle_fatal_error(e, error_prefix="File selection failed")

    """
    if rich_output is None:
        rich_output = container.core.rich_output()

    rich_output.error(f"{error_prefix}: {error}")

    if exit_on_error:
        sys.exit(1)


def handle_enhanced_fatal_error(
    error: Exception,
    *,
    error_prefix: str = "Error",
    options: EnhancedErrorOptions | None = None,
    exit_on_error: bool = True,
    rich_output: RichOutputService | None = None,
) -> None:
    """
    Handle fatal errors with enhanced display including context and suggestions.

    This function provides sophisticated error formatting with optional
    context information, suggestions, and help hints for better user experience.
    Falls back to basic error display if enhanced formatting is not available.

    Args:
        error: The exception that occurred
        error_prefix: Custom prefix for the error message (default: "Error")
        options: Enhanced error display options
        exit_on_error: Whether to exit the program after displaying the error
        rich_output: Optional RichOutput instance (will create one if not provided)

    Example:
        options = EnhancedErrorOptions(
            context="Attempting to locate input file for processing",
            suggestions=[
                "Check that the file exists in the specified directory",
                "Verify file permissions allow reading",
                "Ensure the file has the correct extension"
            ],
            error_code="FILE_001"
        )
        try:
            selected_file = get_input_file(...)
        except ValueError as e:
            handle_enhanced_fatal_error(
                e,
                error_prefix="File selection failed",
                options=options
            )

    """
    if options is None:
        options = EnhancedErrorOptions()

    if rich_output is None:
        rich_output = container.core.rich_output()

    if _ENHANCED_ERROR_AVAILABLE:
        # Use enhanced error display
        error_options = ErrorDisplayOptions(
            context=options.context,
            suggestions=options.suggestions,
            error_code=options.error_code,
            show_help_hint=options.show_help_hint,
        )
        display_cli_error(
            rich_output,
            error,
            error_prefix=error_prefix,
            options=error_options,
        )
    else:
        # Fall back to basic error display
        rich_output.error(f"{error_prefix}: {error}")
        if options.context:
            rich_output.info(f"Context: {options.context}")
        if options.suggestions:
            rich_output.subheader("Suggestions:")
            for i, suggestion in enumerate(options.suggestions, 1):
                rich_output.print(f"  {i}. {suggestion}")

    if exit_on_error:
        sys.exit(1)


def validate_input_file(
    file_path: PathLike,
    required_extensions: list[str] | None = None,
    *,
    must_exist: bool = True,
) -> Path:
    """
    Validate an input file path and extension.

    Args:
        file_path: Path to the input file
        required_extensions: List of allowed file extensions (e.g., ['.csv', '.txt'])
        must_exist: Whether the file must already exist

    Returns:
        Validated Path object

    Raises:
        ValueError: If validation fails

    Example:
        # Validate CSV file exists
        file_path = validate_input_file("data.csv", [".csv"])

        # Validate any file type exists
        file_path = validate_input_file("report.txt")

        # Validate extension but don't require existence
        file_path = validate_input_file("output.xlsx", [".xlsx"], must_exist=False)

    """
    path = Path(file_path).resolve()

    # Check file existence
    if must_exist and not path.exists():
        message: str = f"Input file does not exist: {path}"
        raise ValueError(message)

    if must_exist and not path.is_file():
        file_message: str = f"Path is not a file: {path}"
        raise ValueError(file_message)

    # Check file extension if specified
    if required_extensions:
        # Normalize extensions to lowercase and ensure they start with '.'
        normalized_extensions = [
            ext.lower() if ext.startswith(".") else f".{ext.lower()}"
            for ext in required_extensions
        ]

        file_extension: str = path.suffix.lower()
        if file_extension not in normalized_extensions:
            ext_list: str = ", ".join(normalized_extensions)
            extension_message: str = (
                f"Invalid file extension '{file_extension}'. "
                f"Expected one of: {ext_list}"
            )
            raise ValueError(extension_message)

    return path


def validate_output_path(
    path: PathLike,
    *,
    create_if_missing: bool = True,
    is_file: bool = True,
) -> Path:
    """
    Validate and optionally create an output path.

    Args:
        path: Output path (file or directory)
        create_if_missing: Whether to create parent directories if they don't exist
        is_file: Whether the path represents a file (True) or directory (False)

    Returns:
        Validated Path object

    Raises:
        ValueError: If validation fails or path creation fails

    Example:
        # Validate output file path, create directories if needed
        output_file = validate_output_path("results/report.xlsx")

        # Validate output directory
        output_dir = validate_output_path("results/", is_file=False)

        # Validate but don't create missing directories
        output_file = validate_output_path("existing/report.csv", create_if_missing=False)

    """
    path = Path(path).resolve()

    if is_file:
        # For files, check the parent directory
        parent_dir = path.parent
        target_dir = parent_dir
    else:
        # For directories, check the directory itself
        target_dir = path

    # Check if target directory exists
    if not target_dir.exists():
        if create_if_missing:
            try:
                target_dir.mkdir(parents=True, exist_ok=True)
                rich_output = container.core.rich_output()
                rich_output.debug(f"Created directory: {target_dir}")
            except OSError as e:
                message: str = f"Failed to create directory {target_dir}: {e}"
                raise ValueError(message) from e
        else:
            missing_dir_message: str = f"Output directory does not exist: {target_dir}"
            raise ValueError(missing_dir_message)

    # Verify the target directory is actually a directory
    if not target_dir.is_dir():
        not_dir_message: str = f"Path is not a directory: {target_dir}"
        raise ValueError(not_dir_message)

    # For files, check if we can write to the parent directory
    if is_file:
        # Check write permissions by testing parent directory
        if not target_dir.stat().st_mode & 0o200:  # Check write permission
            permission_message: str = f"No write permission for directory: {target_dir}"
            raise ValueError(permission_message)

        # If file already exists, check if it's writable
        if path.exists() and not path.is_file():
            not_file_message: str = f"Output path exists but is not a file: {path}"
            raise ValueError(not_file_message)

    return path


# Convenience function that combines common validation patterns
def validate_cli_config(
    config_class: type[T],
    input_file: PathLike | None = None,
    source_files_path: PathLike | None = None,
    output_path: PathLike | None = None,
    required_extensions: list[str] | None = None,
    **kwargs: ConfigValue,
) -> T:
    """
    Convenience function that validates common CLI configuration patterns.

    This combines the common pattern of validating input files, output paths,
    and creating a program configuration object.

    Args:
        config_class: Pydantic model class for configuration
        input_file: Input file path (if provided)
        source_files_path: Source directory path
        output_path: Output file or directory path
        required_extensions: Required file extensions for input file
        **kwargs: Additional configuration parameters

    Returns:
        Validated configuration object

    Raises:
        ValueError: If any validation fails

    Example:
        config = validate_cli_config(
            ProgramConfig,
            input_file=args.input_file,
            source_files_path=args.source_dir,
            required_extensions=['.csv']
        )

    """
    validated_kwargs: dict[str, ConfigValue] = kwargs.copy()

    # Validate input file if provided
    if input_file is not None:
        validated_kwargs["input_file"] = validate_input_file(
            input_file,
            required_extensions=required_extensions,
        )

    # Validate source files path if provided
    if source_files_path is not None:
        validated_kwargs["source_files_path"] = validate_output_path(
            source_files_path,
            is_file=False,
        )

    # Validate output path if provided
    if output_path is not None:
        validated_kwargs["output_path"] = validate_output_path(output_path)

    # Create and validate the configuration
    return validate_program_config(config_class, **validated_kwargs)
