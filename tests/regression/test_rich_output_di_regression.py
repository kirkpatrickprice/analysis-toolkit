"""
Regression tests for RichOutput Dependency Injection implementation.

This file provides a focused set of tests to verify that the DI implementation
for RichOutput continues to work correctly. It serves as documentation for
the key changes made and as a guard against regressions.
"""

import pytest
from click.testing import CliRunner

from kp_analysis_toolkit.core.containers.application import (
    container,
    initialize_dependency_injection,
)
from kp_analysis_toolkit.core.services.rich_output import RichOutputService
from kp_analysis_toolkit.utils.rich_output import get_rich_output


class TestRichOutputDIRegression:
    """Regression tests for RichOutput DI implementation."""

    def test_di_initialization_and_configuration(self) -> None:
        """Test that DI can be initialized and configured."""
        # Reset to ensure clean state
        container.reset_singletons()

        # Initialize with specific configuration
        initialize_dependency_injection(verbose=True, quiet=False, console_width=100)

        # Get service from DI container
        service = container.core().rich_output()

        # Verify configuration was applied
        assert isinstance(service, RichOutputService)
        assert service.verbose is True
        assert service.quiet is False
        # Use tolerant assertion for CI environments
        from tests.conftest import assert_console_width_tolerant
        assert_console_width_tolerant(service.console.width, 100)

    def test_backward_compatibility_maintained(self) -> None:
        """Test that existing code continues to work."""
        # Reset container
        container.reset_singletons()

        # Initialize DI
        initialize_dependency_injection(quiet=True)

        # Test legacy import still works
        from kp_analysis_toolkit.utils.rich_output import RichOutput

        assert RichOutput is RichOutputService

        # Test legacy function still works and uses DI when no params given
        rich_output = get_rich_output()
        assert isinstance(rich_output, RichOutputService)
        assert rich_output.quiet is True  # Should get DI configuration

    def test_convenience_functions_still_work(self) -> None:
        """Test that convenience functions continue to work."""
        # Reset container
        container.reset_singletons()

        # Initialize DI
        initialize_dependency_injection()

        # Test convenience functions don't crash
        from kp_analysis_toolkit.utils.rich_output import (
            debug,
            error,
            info,
            success,
            warning,
        )

        # These should execute without errors
        info("Test message")
        success("Success message")
        warning("Warning message")
        error("Error message", force=True)  # Force to ensure it shows
        debug("Debug message")

    def test_singleton_behavior_preserved(self) -> None:
        """Test that singleton behavior is preserved."""
        # Reset container
        container.reset_singletons()

        # Initialize DI
        initialize_dependency_injection()

        # Multiple calls should return same instance
        instance1 = container.core().rich_output()
        instance2 = container.core().rich_output()
        instance3 = get_rich_output()  # Through legacy function

        assert instance1 is instance2
        assert instance1 is instance3

    def test_cli_integration_preserved(self, cli_runner: CliRunner) -> None:
        """Test that CLI integration works."""
        from kp_analysis_toolkit.cli import cli

        # CLI should start without errors
        result = cli_runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "KP Analysis Toolkit" in result.output

        # Version command should work
        result = cli_runner.invoke(cli, ["--version"])
        assert result.exit_code == 0
        assert "kpat_cli version" in result.output

    def test_configuration_flexibility(self) -> None:
        """Test that configuration can be changed dynamically."""
        # Test different configurations
        configurations = [
            {"verbose": True, "quiet": False, "console_width": 80},
            {"verbose": False, "quiet": True, "console_width": 120},
            {"verbose": False, "quiet": False, "console_width": 100},
        ]

        for config in configurations:
            # Reset and configure
            container.reset_singletons()
            initialize_dependency_injection(**config)

            # Get service and verify configuration
            service = container.core().rich_output()
            assert service.verbose == config["verbose"]
            assert service.quiet == config["quiet"]
            # Use tolerant assertion for CI environments
            from tests.conftest import assert_console_width_tolerant
            assert_console_width_tolerant(service.console.width, config["console_width"])

    def test_error_handling_robustness(self) -> None:
        """Test that error handling is robust."""
        # Reset container
        container.reset_singletons()

        # Test that get_rich_output works even without DI initialization
        # (should fall back to legacy behavior)
        try:
            rich_output = get_rich_output(verbose=True)
            assert isinstance(rich_output, RichOutputService)
            assert rich_output.verbose is True
        except Exception as e:  # noqa: BLE001
            pytest.fail(
                f"get_rich_output should handle uninitialized DI gracefully: {e}",
            )

    @pytest.mark.performance
    def test_performance_characteristics(self) -> None:
        """Test that performance characteristics are acceptable."""
        import time

        # Reset container
        container.reset_singletons()

        # Initialize DI
        start_time = time.time()
        initialize_dependency_injection()
        init_time = time.time() - start_time

        # Should initialize quickly
        assert init_time < 0.1  # 100ms should be more than enough  # noqa: PLR2004

        # Subsequent accesses should be fast
        start_time = time.time()
        for _ in range(100):
            container.core().rich_output()
        access_time = time.time() - start_time

        # 100 accesses should be very fast due to singleton caching
        assert access_time < 0.1  # 100ms for 100 accesses  # noqa: PLR2004


class TestDIImplementationDocumentation:
    """Documentation tests for DI implementation details."""

    def test_di_container_structure(self) -> None:
        """Document the DI container structure."""
        # The ApplicationContainer should have a core container
        assert hasattr(container, "core")

        # The core container should have rich_output provider
        core_container = container.core()
        assert hasattr(core_container, "rich_output")
        assert hasattr(core_container, "config")

    def test_configuration_model_structure(self) -> None:
        """Document the configuration model structure."""
        from kp_analysis_toolkit.models.rich_config import RichOutputConfig

        # RichOutputConfig should have expected fields
        config = RichOutputConfig()
        expected_fields = [
            "verbose",
            "quiet",
            "console_width",
            "force_terminal",
            "stderr_enabled",
        ]

        for field in expected_fields:
            assert hasattr(config, field), f"RichOutputConfig missing field: {field}"

    def test_service_interface_preserved(self) -> None:
        """Document that the RichOutputService interface is preserved."""
        # Reset and initialize
        container.reset_singletons()
        initialize_dependency_injection()

        service = container.core().rich_output()

        # All expected methods should be available
        expected_methods = [
            "info",
            "success",
            "warning",
            "error",
            "debug",
            "header",
            "subheader",
        ]

        for method in expected_methods:
            assert hasattr(service, method), (
                f"RichOutputService missing method: {method}"
            )
            assert callable(getattr(service, method)), (
                f"RichOutputService.{method} not callable"
            )
