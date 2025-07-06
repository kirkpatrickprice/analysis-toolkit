"""Configuration validation utilities for CLI commands."""

import sys
from pathlib import Path

from pydantic import ValidationError

from kp_analysis_toolkit.models.types import ConfigValue, PathLike, T
from kp_analysis_toolkit.utils.rich_output import RichOutputService, get_rich_output


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
            handle_config_error(e)

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
        message: str = f"Configuration validation failed: {combined_message}"
        raise ValueError(message) from e


def handle_config_error(
    error: Exception,
    *,
    exit_on_error: bool = True,
    rich_output: RichOutputService | None = None,
) -> None:
    """
    Handle configuration validation errors with consistent messaging.

    Args:
        error: The exception that occurred during validation
        exit_on_error: Whether to exit the program after displaying the error
        rich_output: Optional RichOutput instance (will create one if not provided)

    Example:
        try:
            config = validate_program_config(ProgramConfig, **cli_args)
        except ValueError as e:
            handle_config_error(e)  # Will exit with error message

    """
    if rich_output is None:
        rich_output = get_rich_output()

    rich_output.error(f"Error validating configuration: {error}")

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
        message: str = f"Path is not a file: {path}"
        raise ValueError(message)

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
            message: str = (
                f"Invalid file extension '{file_extension}'. "
                f"Expected one of: {ext_list}"
            )
            raise ValueError(message)

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
                rich_output = get_rich_output()
                rich_output.debug(f"Created directory: {target_dir}")
            except OSError as e:
                message: str = f"Failed to create directory {target_dir}: {e}"
                raise ValueError(message) from e
        else:
            message: str = f"Output directory does not exist: {target_dir}"
            raise ValueError(message)

    # Verify the target directory is actually a directory
    if not target_dir.is_dir():
        message: str = f"Path is not a directory: {target_dir}"
        raise ValueError(message)

    # For files, check if we can write to the parent directory
    if is_file:
        # Check write permissions by testing parent directory
        if not target_dir.stat().st_mode & 0o200:  # Check write permission
            message: str = f"No write permission for directory: {target_dir}"
            raise ValueError(message)

        # If file already exists, check if it's writable
        if path.exists() and not path.is_file():
            message: str = f"Output path exists but is not a file: {path}"
            raise ValueError(message)

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
