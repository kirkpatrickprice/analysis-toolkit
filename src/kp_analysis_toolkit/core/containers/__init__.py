# File: src/kp_analysis_toolkit/core/containers/__init__.py
"""
Core containers package for shared services.

This package provides dependency injection containers for core services
that are shared across all modules in the toolkit.
"""

from __future__ import annotations

from kp_analysis_toolkit.core.containers.application import (
    ApplicationContainer,
    configure_application_container,
    initialize_dependency_injection,
    wire_application_container,
    wire_module_containers,
)
from kp_analysis_toolkit.core.containers.core import CoreContainer

# NOTE: Commenting out until these containers are fully implemented
# from kp_analysis_toolkit.core.containers.excel_export import ExcelExportContainer
# from kp_analysis_toolkit.core.containers.file_processing import FileProcessingContainer

__all__: list[str] = [
    "ApplicationContainer",
    "CoreContainer",
    # NOTE: Removed until these containers are implemented
    # "ExcelExportContainer",
    # "FileProcessingContainer",
    "configure_application_container",
    "initialize_dependency_injection",
    "wire_application_container",
    "wire_module_containers",
]
