# File: src/kp_analysis_toolkit/core/__init__.py
"""
Core module providing dependency injection containers and services.

This module provides the main entry point for dependency injection
functionality across the toolkit.
"""

from __future__ import annotations

from kp_analysis_toolkit.core.containers import (
    ApplicationContainer,
    CoreContainer,
    FileProcessingContainer,
    configure_application_container,
    container,
    initialize_dependency_injection,
    wire_application_container,
    wire_module_containers,
)

__all__: list[str] = [
    "ApplicationContainer",
    "CoreContainer",
    "FileProcessingContainer",
    "configure_application_container",
    "container",
    "initialize_dependency_injection",
    "wire_application_container",
    "wire_module_containers",
]
