"""Centralized hashing utilities for the KP Analysis Toolkit."""

import hashlib
from pathlib import Path

# Standard hash algorithm for the toolkit
TOOLKIT_HASH_ALGORITHM = "sha384"


class HashGenerator:
    """Centralized hash generation utility."""

    def __init__(self, algorithm: str = TOOLKIT_HASH_ALGORITHM) -> None:
        """Initialize with specified algorithm (defaults to SHA384)."""
        self.algorithm: str = algorithm.lower()
        self._validate_algorithm()

    def _validate_algorithm(self) -> None:
        """Validate that the algorithm is supported."""
        if self.algorithm not in hashlib.algorithms_available:
            message: str = f"Hash algorithm '{self.algorithm}' is not available"
            raise ValueError(message)

    def hash_file(self, file_path: Path, chunk_size: int = 8192) -> str:
        """Generate hash for a file."""
        if not file_path.exists():
            message: str = f"File does not exist: {file_path}"
            raise ValueError(message)

        hasher = hashlib.new(self.algorithm)

        try:
            with file_path.open("rb") as f:
                for chunk in iter(lambda: f.read(chunk_size), b""):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except (OSError, PermissionError) as e:
            message: str = f"Error reading file {file_path}: {e}"
            raise ValueError(message) from e

    def hash_string(self, data: str, encoding: str = "utf-8") -> str:
        """Generate hash for a string."""
        hasher = hashlib.new(self.algorithm)
        hasher.update(data.encode(encoding))
        return hasher.hexdigest()

    def hash_bytes(self, data: bytes) -> str:
        """Generate hash for bytes."""
        hasher = hashlib.new(self.algorithm)
        hasher.update(data)
        return hasher.hexdigest()

    def validate_chunk_size(self, chunk_size: int) -> int:
        """Validate that chunk size is positive."""
        if chunk_size <= 0:
            message: str = f"Chunk size must be positive, got: {chunk_size}"
            raise ValueError(message)
        return chunk_size

    def hash_file_with_validation(self, file_path: Path, chunk_size: int = 8192) -> str:
        """Generate hash for a file with full validation."""
        # Validate inputs
        if not isinstance(file_path, Path):
            message: str = f"Expected Path object, got: {type(file_path)}"
            raise TypeError(message)

        self.validate_chunk_size(chunk_size)

        return self.hash_file(file_path, chunk_size)


def validate_file_path(file_path: Path) -> Path:
    """Validate that file path exists and is a file."""
    if not file_path.exists():
        message: str = f"File does not exist: {file_path}"
        raise ValueError(message)

    if not file_path.is_file():
        message: str = f"Path is not a file: {file_path}"
        raise ValueError(message)

    return file_path


def validate_hash_input(data: str | bytes | None) -> str | bytes:
    """Validate hash input data."""
    if data is None:
        message: str = "Hash input data cannot be None"
        raise ValueError(message)

    if isinstance(data, str) and len(data.strip()) == 0:
        message: str = "Hash input string cannot be empty"
        raise ValueError(message)

    if isinstance(data, bytes) and len(data) == 0:
        message: str = "Hash input bytes cannot be empty"
        raise ValueError(message)

    return data


# Convenience functions using the standard algorithm
def hash_file(file_path: Path, *, validate_input: bool = True) -> str:
    """Generate SHA384 hash for a file using toolkit standard."""
    if validate_input:
        validate_file_path(file_path)

    try:
        return HashGenerator().hash_file(file_path)
    except Exception as e:
        message: str = f"Failed to generate hash for file {file_path}: {e}"
        raise ValueError(message) from e


def hash_string(data: str, *, validate_input: bool = True) -> str:
    """Generate SHA384 hash for a string using toolkit standard."""
    if validate_input:
        validate_hash_input(data)

    try:
        return HashGenerator().hash_string(data)
    except Exception as e:
        message: str = f"Failed to generate hash for string data: {e}"
        raise ValueError(message) from e


def hash_bytes(data: bytes, *, validate_input: bool = True) -> str:
    """Generate SHA384 hash for bytes using toolkit standard."""
    if validate_input:
        validate_hash_input(data)

    try:
        return HashGenerator().hash_bytes(data)
    except Exception as e:
        message: str = f"Failed to generate hash for byte data: {e}"
        raise ValueError(message) from e


def create_hash_generator(algorithm: str) -> HashGenerator:
    """Create a hash generator with validation."""
    if not isinstance(algorithm, str):
        message: str = f"Algorithm must be a string, got: {type(algorithm)}"
        raise TypeError(message)

    if not algorithm.strip():
        message: str = "Algorithm name cannot be empty"
        raise ValueError(message)

    try:
        return HashGenerator(algorithm)
    except Exception as e:
        message: str = (
            f"Failed to create hash generator with algorithm '{algorithm}': {e}"
        )
        raise ValueError(message) from e
