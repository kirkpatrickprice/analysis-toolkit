from typing import Any

from kp_analysis_toolkit.models.base import KPATBaseModel
from kp_analysis_toolkit.process_scripts.models.base import ConfigModel
from kp_analysis_toolkit.process_scripts.models.search.base import (
    GlobalConfig,
    SearchConfig,
)


class IncludeConfig(KPATBaseModel):
    """Configuration for including other YAML files."""

    files: list[str]


class YamlConfig(KPATBaseModel, ConfigModel):
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
                config_data = value.copy()

                # Set Excel sheet name if not provided
                if "excel_sheet_name" not in config_data:
                    config_data["excel_sheet_name"] = key

                search_configs[key] = SearchConfig(name=key, **config_data)

        config = cls(
            global_config=global_config,
            search_configs=search_configs,
            include_configs=include_configs,
        )

        config.validate_sheet_names()

        return config

    def validate_sheet_names(self) -> list["ValidationMessage"]:  # noqa: C901
        """Validate Excel sheet names for uniqueness and length."""
        messages = []

        # Group search configs by OS family
        os_configs: dict[str, dict[str, SearchConfig]] = {}

        for name, config in self.search_configs.items():
            # Determine OS family from sys_filter if present
            os_family = "Unknown"
            if hasattr(config, "sys_filter") and config.sys_filter:
                for filter_item in config.sys_filter:
                    if filter_item.attr == "os_family" and filter_item.comp == "eq":
                        os_family = str(filter_item.value)
                        break

            if os_family not in os_configs:
                os_configs[os_family] = {}

            os_configs[os_family][name] = config

        # Check uniqueness and length within each OS family
        for os_family, configs in os_configs.items():
            sheet_names: set[str] = set()

            for name, config in configs.items():
                sheet_name = config.excel_sheet_name or name

                # Check length
                if len(sheet_name) > 31:  # noqa: PLR2004
                    messages.append(
                        ValidationMessage(
                            level="ERROR",
                            search_name=name,
                            message=f"Excel sheet name '{sheet_name}' exceeds 31 characters",
                        ),
                    )

                # Check for invalid characters
                invalid_chars = ["/", "\\", "?", "*", "[", "]", ":"]
                for char in invalid_chars:
                    if char in sheet_name:
                        messages.append(
                            ValidationMessage(
                                level="ERROR",
                                search_name=name,
                                message=f"Excel sheet name '{sheet_name}' contains invalid character '{char}'",
                            ),
                        )

                # Check uniqueness within OS family
                sanitized_name = self._sanitize_sheet_name(sheet_name)
                if sanitized_name in sheet_names:
                    messages.append(
                        ValidationMessage(
                            level="ERROR",
                            search_name=name,
                            message=f"Duplicate Excel sheet name '{sanitized_name}' for OS family '{os_family}'",
                        ),
                    )
                else:
                    sheet_names.add(sanitized_name)

        return messages

    @staticmethod
    def _sanitize_sheet_name(name: str) -> str:
        """
        Sanitize sheet name for Excel compatibility.

        This is similar to the function in excel_exporter.py but needed here for validation.
        """
        invalid_chars = ["/", "\\", "?", "*", "[", "]", ":"]
        max_sheet_name_length = 31

        sanitized = name
        for char in invalid_chars:
            sanitized = sanitized.replace(char, "_")

        # Remove leading/trailing spaces
        sanitized = sanitized.strip()

        # Ensure it's not empty
        if not sanitized:
            sanitized = "Unnamed_Search"

        # Limit to 31 characters (Excel limitation)
        if len(sanitized) > max_sheet_name_length:
            sanitized = sanitized[: max_sheet_name_length - 3] + "..."

        return sanitized


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

    @classmethod
    def validate(cls, config: YamlConfig) -> "ConfigValidationResult":
        """Validate the configuration and return results."""
        messages = []

        # Existing validation logic
        # ...

        # Add sheet name validation
        sheet_messages = config.validate_sheet_names()
        messages.extend(sheet_messages)

        # Count errors and warnings
        error_count = sum(1 for msg in messages if msg.level == "ERROR")
        warning_count = sum(1 for msg in messages if msg.level == "WARNING")

        return cls(
            is_valid=error_count == 0,
            messages=messages,
            error_count=error_count,
            warning_count=warning_count,
        )
