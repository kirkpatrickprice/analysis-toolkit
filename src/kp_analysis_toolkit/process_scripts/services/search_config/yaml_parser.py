from kp_analysis_toolkit.models.base import KPATBaseModel
from kp_analysis_toolkit.process_scripts.models.search.configs import (
    GlobalConfig,
    IncludeConfig,
    SearchConfig,
    YamlConfig,
)
from kp_analysis_toolkit.process_scripts.models.types import (
    CollectionType,
    ConfigurationValueType,
)


class SearchConfigService:
    @classmethod
    def load_yaml(cls, data: dict[str, ConfigurationValueType]) -> "YamlConfig":
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
                config_data: CollectionType = value.copy()

                # Set Excel sheet name if not provided
                if "excel_sheet_name" not in config_data:
                    config_data["excel_sheet_name"] = key

                search_configs[key] = SearchConfig(name=key, **config_data)

        config = cls(
            global_config=global_config,
            search_configs=search_configs,
            include_configs=include_configs,
        )

        config.validate_configurations()

        return config

    # AI-GEN: GitHub Copilot|2025-07-29|fix/di/scripts-migration|reviewed:no
    def validate_configurations(self) -> list["ValidationMessage"]:
        """Validate search configurations for basic structural issues."""
        messages: list[ValidationMessage] = []

        # Basic validation that doesn't require business logic
        # Sheet name validation will be handled by the service layer
        # TODO(@flyguy62n): Implement basic configuration validation logic
        # https://github.com/kirkpatrickprice/analysis-toolkit/issues/57

        return messages

    # END AI-GEN


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

    # AI-GEN: GitHub Copilot|2025-07-29|fix/di/scripts-migration|reviewed:no
    @classmethod
    def validate(cls, config: YamlConfig) -> "ConfigValidationResult":
        """Validate the configuration and return results."""
        messages: list[ValidationMessage] = []

        # Basic configuration validation
        config_messages: list[ValidationMessage] = config.validate_configurations()
        messages.extend(config_messages)

        # Sheet name validation will be handled by the service layer
        # when Excel export actually occurs, using the proper DI services

        # Count errors and warnings
        error_count: int = sum(1 for msg in messages if msg.level == "ERROR")
        warning_count: int = sum(1 for msg in messages if msg.level == "WARNING")

        return cls(
            is_valid=error_count == 0,
            messages=messages,
            error_count=error_count,
            warning_count=warning_count,
        )

    # END AI-GEN
