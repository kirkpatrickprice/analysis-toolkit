"""
System filter service implementation for filtering systems based on configuration criteria.

This module provides the DefaultSystemFilterService which evaluates system filters
according to OS family, version, producer, and other system attributes.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from kp_analysis_toolkit.process_scripts.models.search.filters import (
    SysFilterAttr,
    SysFilterComparisonOperators,
    SystemFilter,
)
from kp_analysis_toolkit.process_scripts.models.types import (
    ConfigurationValueType,
    OSFamilyType,
    PrimitiveType,
    SysFilterValueType,
)
from kp_analysis_toolkit.process_scripts.services.search_engine.protocols import (
    SystemFilterService,
)

if TYPE_CHECKING:
    from collections.abc import Callable

    from kp_analysis_toolkit.process_scripts.models.results.system import Systems


MIN_VERSION_COMPONENTS = 3


class DefaultSystemFilterService(SystemFilterService):
    """
    Default implementation of system filtering service.

    Evaluates systems against filter criteria including OS family,
    version comparisons, producer matching, and other system attributes.
    """

    def evaluate_system_filters(
        self,
        system: Systems,
        filters: list[SystemFilter],
    ) -> bool:
        """
        Evaluate whether a system passes all provided filters.

        Args:
            system: System object to evaluate
            filters: List of SystemFilter objects to apply

        Returns:
            True if system passes all filters (AND logic), False otherwise

        """
        if not filters:
            return True  # No filters means all systems pass

        for filter_item in filters:
            if not self._evaluate_single_filter(system, filter_item):
                return (
                    False  # AND logic - any filter failure fails the whole evaluation
                )

        return True

    def filter_systems_by_criteria(
        self,
        systems: list[Systems],
        filters: list[SystemFilter] | None,
    ) -> list[Systems]:
        """
        Filter a list of systems based on provided criteria.

        Args:
            systems: List of system objects to filter
            filters: List of SystemFilter objects to apply

        Returns:
            Filtered list of systems that pass all criteria

        """
        if not filters:
            return systems  # No filters means return all systems

        return [
            system
            for system in systems
            if self.evaluate_system_filters(system, filters)
        ]

    def _evaluate_single_filter(
        self,
        system: Systems,
        filter_item: SystemFilter,
    ) -> bool:
        """
        Evaluate a single filter against a system.

        Args:
            system: System object to evaluate
            filter_item: Single SystemFilter to apply

        Returns:
            True if system passes the filter, False otherwise

        """
        # Check if attribute is applicable to this system's OS family
        if not self._is_attribute_applicable(system, filter_item.attr):
            return True  # Skip non-applicable filters

        system_value: PrimitiveType = self._get_system_attribute_value(
            system,
            filter_item.attr,
        )
        filter_value = filter_item.value

        # Handle special case for version comparison
        if filter_item.attr in [
            SysFilterAttr.PRODUCER_VERSION,
            SysFilterAttr.CURRENT_BUILD,
            SysFilterAttr.UBR,
        ]:
            return self._compare_version(
                str(system_value) if system_value else None,
                filter_item.comp,
                str(filter_value),
            )

        # Convert enum values to strings for comparison if needed
        if hasattr(filter_value, "value"):
            filter_value = filter_value.value
        if system_value is not None and hasattr(system_value, "value"):
            system_value = system_value.value

        return self._compare_values(system_value, filter_item.comp, filter_value)

    def _is_attribute_applicable(self, system: Systems, attr: SysFilterAttr) -> bool:
        """
        Check if an attribute is applicable to the system's OS family.

        Args:
            system: System object containing OS family information
            attr: SysFilterAttr to check

        Returns:
            True if the attribute is applicable to the system's OS family, False otherwise

        """
        os_family: OSFamilyType | None = system.os_family

        # Windows-specific attributes
        windows_attrs: set[SysFilterAttr] = {
            SysFilterAttr.PRODUCT_NAME,
            SysFilterAttr.RELEASE_ID,
            SysFilterAttr.CURRENT_BUILD,
            SysFilterAttr.UBR,
        }

        # Linux-specific attributes
        linux_attrs: set[SysFilterAttr] = {
            SysFilterAttr.DISTRO_FAMILY,
            SysFilterAttr.OS_PRETTY_NAME,
            SysFilterAttr.OS_VERSION,
        }

        # Universal attributes (applicable to all OS families)
        universal_attrs: set[SysFilterAttr] = {
            SysFilterAttr.OS_FAMILY,
            SysFilterAttr.PRODUCER,
            SysFilterAttr.PRODUCER_VERSION,
        }

        # Check applicability
        if attr in universal_attrs:
            return True
        if attr in windows_attrs:
            return os_family == OSFamilyType.WINDOWS
        if attr in linux_attrs:
            return os_family == OSFamilyType.LINUX
        # Unknown attribute - assume applicable for safety
        return True

    def _get_system_attribute_value(
        self,
        system: Systems,
        attr: SysFilterAttr,
    ) -> ConfigurationValueType:
        """
        Get the value of a system attribute.

        Args:
            system: System object to extract value from
            attr: SysFilterAttr specifying which attribute to get

        Returns:
            The value of the specified attribute

        """
        attribute_map = {
            SysFilterAttr.OS_FAMILY: system.os_family,
            SysFilterAttr.DISTRO_FAMILY: system.distro_family,
            SysFilterAttr.PRODUCER: system.producer,
            SysFilterAttr.PRODUCER_VERSION: system.producer_version,
            SysFilterAttr.PRODUCT_NAME: system.product_name,
            SysFilterAttr.RELEASE_ID: system.release_id,
            SysFilterAttr.CURRENT_BUILD: system.current_build,
            SysFilterAttr.UBR: system.ubr,
            SysFilterAttr.OS_PRETTY_NAME: system.os_pretty_name,
            SysFilterAttr.OS_VERSION: system.os_version,
        }

        if attr in attribute_map:
            return attribute_map[attr]

        # Default return for unknown attributes
        return ""

    def _compare_values(
        self,
        system_value: ConfigurationValueType,
        operator: SysFilterComparisonOperators,
        filter_value: SysFilterValueType,
    ) -> bool:
        """
        Compare system value against filter value using specified operator.

        Args:
            system_value: Value from the system
            operator: Comparison operator to use
            filter_value: Value to compare against

        Returns:
            True if comparison passes, False otherwise

        """
        # Handle None/empty system values
        if system_value is None:
            system_value = ""

        # Handle IN operator separately (for list/set filter values)
        if operator == SysFilterComparisonOperators.IN:
            return system_value in filter_value  # type: ignore[operator]

        # Handle EQUALS operator
        if operator == SysFilterComparisonOperators.EQUALS:
            return system_value == filter_value

        # For comparison operators, delegate to helper methods
        return self._perform_comparison(system_value, operator, filter_value)

    def _perform_comparison(
        self,
        system_value: ConfigurationValueType,
        operator: SysFilterComparisonOperators,
        filter_value: SysFilterValueType,
    ) -> bool:
        """Perform numeric or string comparison based on value types."""
        # Try numeric comparison first
        if isinstance(system_value, int | float) and isinstance(
            filter_value,
            int | float,
        ):
            return self._compare_numeric(
                float(system_value),
                operator,
                float(filter_value),
            )

        # Fall back to string comparison
        return self._compare_string(str(system_value), operator, str(filter_value))

    def _compare_numeric(
        self,
        sys_val: float,
        operator: SysFilterComparisonOperators,
        filter_val: float,
    ) -> bool:
        """Compare numeric values."""
        if operator == SysFilterComparisonOperators.GREATER_THAN:
            return sys_val > filter_val
        if operator == SysFilterComparisonOperators.LESS_THAN:
            return sys_val < filter_val
        if operator == SysFilterComparisonOperators.GREATER_EQUAL:
            return sys_val >= filter_val
        if operator == SysFilterComparisonOperators.LESS_EQUAL:
            return sys_val <= filter_val
        return False

    def _compare_string(
        self,
        sys_str: str,
        operator: SysFilterComparisonOperators,
        filter_str: str,
    ) -> bool:
        """Compare string values."""
        if operator == SysFilterComparisonOperators.GREATER_THAN:
            return sys_str > filter_str
        if operator == SysFilterComparisonOperators.LESS_THAN:
            return sys_str < filter_str
        if operator == SysFilterComparisonOperators.GREATER_EQUAL:
            return sys_str >= filter_str
        if operator == SysFilterComparisonOperators.LESS_EQUAL:
            return sys_str <= filter_str
        return False

    def _compare_version(
        self,
        system_version: str | None,
        operator: SysFilterComparisonOperators,
        filter_version: str,
    ) -> bool:
        """
        Compare version strings using semantic version comparison.

        Args:
            system_version: Version string from system (e.g., "1.2.3")
            operator: Comparison operator to use
            filter_version: Version string to compare against

        Returns:
            True if version comparison passes, False otherwise

        """
        if system_version is None:
            return False

        try:
            # Parse version components
            system_components = self._parse_version_components(system_version)
            filter_components = self._parse_version_components(filter_version)

            # Set up comparison functions
            comparison_ops: dict[
                SysFilterComparisonOperators,
                Callable[[list[int], list[int]], bool],
            ] = {
                SysFilterComparisonOperators.EQUALS: lambda x, y: x == y,
                SysFilterComparisonOperators.GREATER_THAN: lambda x, y: x > y,
                SysFilterComparisonOperators.LESS_THAN: lambda x, y: x < y,
                SysFilterComparisonOperators.GREATER_EQUAL: lambda x, y: x >= y,
                SysFilterComparisonOperators.LESS_EQUAL: lambda x, y: x <= y,
            }

            if operator not in comparison_ops:
                return False

            comparison_func = comparison_ops[operator]
            return comparison_func(system_components, filter_components)

        except (ValueError, TypeError):
            # Fallback to string comparison if version parsing fails
            return self._compare_values(system_version, operator, filter_version)

    def _parse_version_components(self, version: str) -> list[int]:
        """
        Parse a version string into integer components for comparison.

        Args:
            version: Version string to parse (e.g., "1.2.3")

        Returns:
            List of integer components [1, 2, 3]

        Raises:
            ValueError: If version string cannot be parsed

        """
        if not version:
            return [0, 0, 0]

        # Clean up version string (remove non-numeric prefixes/suffixes)
        version_clean = version.strip()

        # Split by dots and convert to integers
        try:
            components = [int(x) for x in version_clean.split(".")]
            # Ensure at least 3 components (major, minor, patch)
            while len(components) < MIN_VERSION_COMPONENTS:
                components.append(0)
        except ValueError as e:
            msg = f"Unable to parse version string: {version}"
            raise ValueError(msg) from e
        else:
            return components
