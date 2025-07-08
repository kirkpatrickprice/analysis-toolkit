#!/usr/bin/env python3
"""Test script to check container type behavior."""

from dependency_injector import containers


class TestContainer(containers.DeclarativeContainer):
    pass


test = TestContainer()
print(f"Simple container type: {type(test)}")
print(f"Is TestContainer: {isinstance(test, TestContainer)}")

# Test our actual container
from kp_analysis_toolkit.core.containers.application import ApplicationContainer

app_test = ApplicationContainer()
print(f"App container type: {type(app_test)}")
print(f"Is ApplicationContainer: {isinstance(app_test, ApplicationContainer)}")
