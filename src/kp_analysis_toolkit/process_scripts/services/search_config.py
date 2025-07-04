from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

from kp_analysis_toolkit.process_scripts.models.search.base import SearchConfig
from kp_analysis_toolkit.utils.rich_output import RichOutput

if TYPE_CHECKING:
    from pathlib import Path

    from kp_analysis_toolkit.process_scripts.models.search.base import SearchConfig
    from kp_analysis_toolkit.utils.rich_output import RichOutput


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


class SearchConfigService:
    """Service for loading and processing YAML search configurations."""

    def __init__(
        self,
        yaml_parser: YamlParser,
        file_resolver: FileResolver,
        include_processor: IncludeProcessor,
        rich_output: RichOutput,
    ) -> None:
        self.yaml_parser: YamlParser = yaml_parser
        self.file_resolver: FileResolver = file_resolver
        self.include_processor: IncludeProcessor = include_processor
        self.rich_output: RichOutput = rich_output

    def load_search_configs(self, config_path: Path) -> list[SearchConfig]:
        """Load search configurations from YAML files with include processing."""
        try:
            # Load main configuration file
            config_data: dict[str, str | bool | float] = self.yaml_parser.load_yaml(
                config_path,
            )

            # Process any includes
            processed_data: dict[str, str | bool | float] = (
                self.include_processor.process_includes(
                    config_data,
                    config_path.parent,
                )
            )

            # Convert to SearchConfig models
            configs: list[SearchConfig] = self._convert_to_search_configs(
                processed_data,
            )

            self.rich_output.info(f"Loaded {len(configs)} search configurations")

        except Exception as e:
            self.rich_output.error(f"Failed to load search configurations: {e}")
            raise

        else:
            return configs

    def _convert_to_search_configs(
        self,
        data: dict[str, str | bool | float],
    ) -> list[SearchConfig]:
        """Convert YAML data to SearchConfig models."""
        # Implementation would convert YAML data to Pydantic models
