from typing import Any

from kp_analysis_toolkit.models.base import KPATBaseModel
from kp_analysis_toolkit.process_scripts.models.search.base import (
    GlobalConfig,
    SearchConfig,
)


class IncludeConfig(KPATBaseModel):
    """Configuration for including other YAML files."""

    files: list[str]


class YamlConfig(KPATBaseModel):
    """Complete YAML configuration file structure."""

    global_config: GlobalConfig | None = None
    search_configs: dict[str, SearchConfig]
    include_configs: dict[str, IncludeConfig]

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "YamlConfig":
        """Create YamlConfig from parsed YAML dictionary."""
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
                search_configs[key] = SearchConfig(name=key, **value)

        return cls(
            global_config=global_config,
            search_configs=search_configs,
            include_configs=include_configs,
        )


class ValidationMessage(KPATBaseModel):
    """Validation message for search configurations."""

    level: str  # "WARNING", "ERROR", "INFO"
    search_name: str | None = None
    message: str

    def __str__(self) -> str:
        if self.search_name:
            return f"{self.level}: [{self.search_name}] {self.message}"
        return f"{self.level}: {self.message}"


class ConfigValidationResult(KPATBaseModel):
    """Result of configuration validation."""

    is_valid: bool
    messages: list[ValidationMessage]
    error_count: int = 0
    warning_count: int = 0
