from pathlib import Path
from typing import Protocol


class YamlParser(Protocol):
    """Protocol for YAML parsing operations."""

    def load_yaml(self, file_path: Path) -> dict[str, str | bool | float]: ...
    def validate_yaml_structure(self, data: dict[str, str | bool | float]) -> bool: ...


class FileResolver(Protocol):
    """Protocol for resolving file paths and includes."""

    def resolve_path(self, base_path: Path, relative_path: str) -> Path: ...
    def find_include_files(self, config_dir: Path, pattern: str) -> list[Path]: ...


class IncludeProcessor(Protocol):
    """Protocol for processing YAML includes."""

    def process_includes(
        self,
        config_data: dict[str, str | bool | float],
        base_path: Path,
    ) -> dict[str, str | bool | float]: ...
