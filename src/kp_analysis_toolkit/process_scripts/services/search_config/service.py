"""Search configuration service for loading and processing YAML configurations."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

    from kp_analysis_toolkit.core.services.rich_output import RichOutputService
    from kp_analysis_toolkit.process_scripts.models.search.configs import (
        SearchConfig,
        YamlConfig,
    )
    from kp_analysis_toolkit.process_scripts.services.search_config.protocols import (
        FileResolver,
        IncludeProcessor,
        YamlParser,
    )


class SearchConfigService:
    """Main service for loading and processing search configurations from YAML files."""

    def __init__(
        self,
        yaml_parser: YamlParser,
        file_resolver: FileResolver,
        include_processor: IncludeProcessor,
        rich_output: RichOutputService,
    ) -> None:
        """Initialize with required services."""
        self.yaml_parser = yaml_parser
        self.file_resolver = file_resolver
        self.include_processor = include_processor
        self.rich_output = rich_output

    def load_search_configs(self, config_file: Path) -> list[SearchConfig]:
        """
        Load and parse search configurations from YAML file, handling includes.

        This is the main entry point for loading search configurations. It:
        1. Loads the initial YAML file
        2. Processes any include directives recursively
        3. Merges global configurations with search configs
        4. Returns a flattened list of all search configurations

        Args:
            config_file: Path to the main YAML configuration file

        Returns:
            List of SearchConfig objects ready for execution

        Raises:
            ValueError: If configuration file cannot be loaded or parsed
            FileNotFoundError: If configuration file or included files don't exist

        """
        try:
            self.rich_output.debug(f"Loading search configuration from: {config_file}")

            # Load the initial YAML configuration
            yaml_config: YamlConfig = self._load_yaml_config(config_file)

            # Process includes and get all configurations
            all_configs: list[SearchConfig] = self._process_includes(
                yaml_config,
                config_file.parent,
            )

            self.rich_output.debug(f"Loaded {len(all_configs)} search configurations")

        except Exception as e:
            self.rich_output.error(
                f"Failed to load search configurations from {config_file}: {e}",
            )
            raise
        else:
            return all_configs

    def _load_yaml_config(self, config_file: Path) -> YamlConfig:
        """
        Load and parse YAML configuration file into structured data models.

        Args:
            config_file: Path to YAML configuration file

        Returns:
            YamlConfig object containing parsed configuration

        Raises:
            ValueError: If file cannot be loaded or parsed
            FileNotFoundError: If configuration file doesn't exist

        """
        if not config_file.exists():
            msg = f"Configuration file not found: {config_file}"
            raise FileNotFoundError(msg)

        try:
            # Load raw YAML data
            raw_data: dict[str, str | bool | float] = self.yaml_parser.load_yaml(
                config_file,
            )
        except Exception as e:
            msg = f"Failed to load YAML config from {config_file}: {e}"
            raise ValueError(msg) from e

        # Validate basic structure
        if not self.yaml_parser.validate_yaml_structure(raw_data):
            msg = f"Invalid YAML structure in {config_file}"
            raise ValueError(msg)

        # Convert to structured models
        return self._parse_yaml_data(raw_data)

    def _parse_yaml_data(self, data: dict[str, str | bool | float]) -> YamlConfig:
        """
        Parse raw YAML data into structured configuration models.

        Args:
            data: Raw YAML data as dictionary

        Returns:
            YamlConfig object with parsed configuration

        """
        from kp_analysis_toolkit.process_scripts.models.search.configs import (
            GlobalConfig,
            IncludeConfig,
            SearchConfig,
            YamlConfig,
        )

        global_config = None
        search_configs = {}
        include_configs = {}

        for key, value in data.items():
            if key == "global":
                global_config = GlobalConfig(**value)
            elif key.startswith("include_"):
                include_configs[key] = IncludeConfig(**value)
            else:
                # Regular search configuration
                config_data = dict(value)

                # Set Excel sheet name if not provided
                if "excel_sheet_name" not in config_data:
                    config_data["excel_sheet_name"] = key

                search_configs[key] = SearchConfig(name=key, **config_data)

        return YamlConfig(
            global_config=global_config,
            search_configs=search_configs,
            include_configs=include_configs,
        )

    def _process_includes(
        self,
        yaml_config: YamlConfig,
        base_path: Path,
    ) -> list[SearchConfig]:
        """
        Process include configurations and recursively load included files.

        Args:
            yaml_config: The main YAML configuration
            base_path: Base directory for resolving include paths

        Returns:
            List of all search configurations including those from included files

        """
        all_configs: list[SearchConfig] = []

        # Add configs from current file, applying global config if present
        for search_config in yaml_config.search_configs.values():
            if yaml_config.global_config:
                # Merge global configuration into search config
                merged_config = search_config.merge_global_config(
                    yaml_config.global_config,
                )
                all_configs.append(merged_config)
            else:
                all_configs.append(search_config)

        # Process includes recursively
        for include_config in yaml_config.include_configs.values():
            for include_file in include_config.files:
                # Resolve the include file path
                include_path = self.file_resolver.resolve_path(base_path, include_file)

                try:
                    # Recursively load included configurations
                    included_configs = self.load_search_configs(include_path)
                    all_configs.extend(included_configs)

                except (ValueError, FileNotFoundError, OSError) as e:
                    self.rich_output.warning(
                        f"Failed to load included file {include_path}: {e}",
                    )
                    # Continue processing other includes rather than failing completely

        return all_configs

    def validate_config_file(self, config_file: Path) -> list[str]:
        """
        Validate a configuration file and return any validation errors.

        Args:
            config_file: Path to the configuration file to validate

        Returns:
            List of validation error messages, empty list if valid

        """
        validation_errors: list[str] = []

        try:
            yaml_config = self._load_yaml_config(config_file)

            # Validate each search configuration
            for name in yaml_config.search_configs:
                try:
                    # Pydantic validation happens automatically during model creation
                    # Additional validation can be added here if needed
                    pass
                except (ValueError, TypeError) as e:
                    validation_errors.append(f"Search config '{name}': {e}")

            # Validate include files exist
            for include_name, include_config in yaml_config.include_configs.items():
                for include_file in include_config.files:
                    include_path = self.file_resolver.resolve_path(
                        config_file.parent,
                        include_file,
                    )
                    if not include_path.exists():
                        validation_errors.append(
                            f"Include '{include_name}': File not found: {include_path}",
                        )

        except (ValueError, FileNotFoundError, OSError, TypeError) as e:
            validation_errors.append(f"Failed to parse configuration file: {e}")

        return validation_errors

    def get_available_config_files(self, config_dir: Path) -> list[Path]:
        """
        Get list of available YAML configuration files in the config directory.

        Args:
            config_dir: Directory to search for configuration files

        Returns:
            List of Path objects for YAML configuration files

        """
        return self.file_resolver.find_include_files(config_dir, "*.yaml")

    def load_yaml_config(self, config_file: Path) -> YamlConfig:
        """
        Public method to load YAML configuration for external use.

        Args:
            config_file: Path to the YAML configuration file

        Returns:
            YamlConfig object containing parsed configuration

        """
        return self._load_yaml_config(config_file)
