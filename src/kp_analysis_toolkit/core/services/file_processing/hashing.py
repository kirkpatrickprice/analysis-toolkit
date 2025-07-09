"""File hashing implementations for the file processing service."""

from __future__ import annotations

import hashlib
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

# Standard hash algorithm for file processing
DEFAULT_HASH_ALGORITHM = "sha384"
DEFAULT_CHUNK_SIZE = 8192


class SHA384FileHashGenerator:
    """SHA384 hash generator specifically optimized for file processing."""

    def __init__(self, chunk_size: int = DEFAULT_CHUNK_SIZE) -> None:
        """
        Initialize the file hash generator.

        Args:
            chunk_size: Size of chunks to read when processing large files

        """
        self.algorithm = DEFAULT_HASH_ALGORITHM
        self.chunk_size = self._validate_chunk_size(chunk_size)

    def generate_hash(self, file_path: Path) -> str:
        """
        Generate SHA384 hash for a file.

        Args:
            file_path: Path to the file to hash

        Returns:
            The SHA384 hash as a hexadecimal string

        Raises:
            ValueError: If file doesn't exist or can't be read

        """
        if not file_path.exists():
            message = f"File does not exist: {file_path}"
            raise ValueError(message)

        hasher = hashlib.new(self.algorithm)

        try:
            with file_path.open("rb") as f:
                for chunk in iter(lambda: f.read(self.chunk_size), b""):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except (OSError, PermissionError) as e:
            message = f"Error reading file {file_path}: {e}"
            raise ValueError(message) from e

    def _validate_chunk_size(self, chunk_size: int) -> int:
        """Validate that chunk size is positive."""
        if chunk_size <= 0:
            message = f"Chunk size must be positive, got: {chunk_size}"
            raise ValueError(message)
        return chunk_size


class ConfigurableFileHashGenerator:
    """Configurable hash generator supporting different algorithms."""

    def __init__(
        self,
        algorithm: str = DEFAULT_HASH_ALGORITHM,
        chunk_size: int = DEFAULT_CHUNK_SIZE,
    ) -> None:
        """
        Initialize with configurable algorithm and chunk size.

        Args:
            algorithm: Hash algorithm to use (default: sha384)
            chunk_size: Size of chunks to read when processing large files

        """
        self.algorithm = algorithm.lower()
        self.chunk_size = self._validate_chunk_size(chunk_size)
        self._validate_algorithm()

    def generate_hash(self, file_path: Path) -> str:
        """
        Generate hash for a file using the configured algorithm.

        Args:
            file_path: Path to the file to hash

        Returns:
            The generated hash as a hexadecimal string

        Raises:
            ValueError: If file doesn't exist or can't be read

        """
        if not file_path.exists():
            message = f"File does not exist: {file_path}"
            raise ValueError(message)

        hasher = hashlib.new(self.algorithm)

        try:
            with file_path.open("rb") as f:
                for chunk in iter(lambda: f.read(self.chunk_size), b""):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except (OSError, PermissionError) as e:
            message = f"Error reading file {file_path}: {e}"
            raise ValueError(message) from e

    def _validate_algorithm(self) -> None:
        """Validate that the algorithm is supported."""
        if self.algorithm not in hashlib.algorithms_available:
            message = f"Hash algorithm '{self.algorithm}' is not available"
            raise ValueError(message)

    def _validate_chunk_size(self, chunk_size: int) -> int:
        """Validate that chunk size is positive."""
        if chunk_size <= 0:
            message = f"Chunk size must be positive, got: {chunk_size}"
            raise ValueError(message)
        return chunk_size
