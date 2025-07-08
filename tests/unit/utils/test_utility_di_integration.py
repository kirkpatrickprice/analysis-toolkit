"""Test utility DI integration functionality."""

from __future__ import annotations

from unittest.mock import Mock, create_autospec

from kp_analysis_toolkit.core.services.file_processing import FileProcessingService
from kp_analysis_toolkit.utils.di_state import (
    DIState,
    FileProcessingDIState,
    create_file_processing_di_manager,
)


class TestDIState:
    """Test the basic DIState class functionality."""

    def test_initial_state(self) -> None:
        """Test DIState initial state is disabled with no service."""
        di_state = DIState[FileProcessingService]()

        assert not di_state.enabled
        assert di_state.service is None
        assert not di_state.is_enabled()
        assert di_state.get_service() is None

    def test_set_service_enables_di(self, mock_file_processing_service: Mock) -> None:
        """Test that setting a service enables DI."""
        di_state = DIState[FileProcessingService]()

        di_state.set_service(mock_file_processing_service)

        assert di_state.enabled
        assert di_state.service is mock_file_processing_service
        assert di_state.is_enabled()
        assert di_state.get_service() is mock_file_processing_service

    def test_clear_service_disables_di(
        self, mock_file_processing_service: Mock
    ) -> None:
        """Test that clearing service disables DI."""
        di_state = DIState[FileProcessingService]()
        di_state.set_service(mock_file_processing_service)

        di_state.clear_service()

        assert not di_state.enabled
        assert di_state.service is None
        assert not di_state.is_enabled()
        assert di_state.get_service() is None

    def test_get_service_when_disabled(
        self, mock_file_processing_service: Mock
    ) -> None:
        """Test that get_service returns None when DI is disabled."""
        di_state = DIState[FileProcessingService]()
        di_state.service = mock_file_processing_service  # Set service but don't enable

        assert di_state.get_service() is None


class TestFileProcessingDIState:
    """Test the specialized FileProcessingDIState class."""

    def test_inherits_from_base_di_state(self) -> None:
        """Test that FileProcessingDIState properly inherits from DIState."""
        di_state = FileProcessingDIState()

        assert isinstance(di_state, DIState)
        assert not di_state.enabled
        assert di_state.service is None

    def test_type_safety_with_file_processing_service(
        self, mock_file_processing_service: Mock
    ) -> None:
        """Test type safety when working with FileProcessingService."""
        di_state = FileProcessingDIState()

        di_state.set_service(mock_file_processing_service)

        service = di_state.get_service()
        assert service is mock_file_processing_service
        assert di_state.is_enabled()


class TestFileProcessingDIManager:
    """Test the file processing DI manager factory function."""

    def test_create_manager_returns_complete_interface(self) -> None:
        """Test that the manager factory returns all expected components."""
        di_state, get_service, set_service, clear_service = (
            create_file_processing_di_manager()
        )

        assert isinstance(di_state, FileProcessingDIState)
        assert callable(get_service)
        assert callable(set_service)
        assert callable(clear_service)

    def test_manager_functions_work_together(
        self, mock_file_processing_service: Mock
    ) -> None:
        """Test that all manager functions work together correctly."""
        di_state, get_service, set_service, clear_service = (
            create_file_processing_di_manager()
        )

        # Initially no service
        assert get_service() is None
        assert not di_state.is_enabled()

        # Set service
        set_service(mock_file_processing_service)
        assert get_service() is mock_file_processing_service
        assert di_state.is_enabled()

        # Clear service
        clear_service()
        assert get_service() is None
        assert not di_state.is_enabled()

    def test_manager_isolation(self, mock_file_processing_service: Mock) -> None:
        """Test that different manager instances are isolated."""
        manager1 = create_file_processing_di_manager()
        manager2 = create_file_processing_di_manager()

        _, get_service_1, set_service_1, _ = manager1
        _, get_service_2, set_service_2, _ = manager2

        # Set service in first manager
        set_service_1(mock_file_processing_service)

        # Second manager should be unaffected
        assert get_service_1() is mock_file_processing_service
        assert get_service_2() is None

    def test_manager_functions_reference_same_state(
        self, mock_file_processing_service: Mock
    ) -> None:
        """Test that manager functions all reference the same underlying state."""
        di_state, get_service, set_service, clear_service = (
            create_file_processing_di_manager()
        )

        # Changes through functions should be reflected in state
        set_service(mock_file_processing_service)
        assert di_state.get_service() is mock_file_processing_service

        clear_service()
        assert di_state.get_service() is None

        # Changes through state should be reflected in functions
        di_state.set_service(mock_file_processing_service)
        assert get_service() is mock_file_processing_service


class TestDIStateEdgeCases:
    """Test edge cases and error conditions in DI state management."""

    def test_multiple_service_assignments(
        self, mock_file_processing_service: Mock
    ) -> None:
        """Test that multiple service assignments work correctly."""
        di_state = DIState[FileProcessingService]()
        mock_service_2 = create_autospec(FileProcessingService, spec_set=True)

        # Set first service
        di_state.set_service(mock_file_processing_service)
        assert di_state.get_service() is mock_file_processing_service

        # Replace with second service
        di_state.set_service(mock_service_2)
        assert di_state.get_service() is mock_service_2
        assert di_state.get_service() is not mock_file_processing_service

    def test_clear_when_already_cleared(self) -> None:
        """Test that clearing an already cleared state is safe."""
        di_state = DIState[FileProcessingService]()

        # Clear when already clear - should be safe
        di_state.clear_service()

        assert not di_state.enabled
        assert di_state.service is None
        assert not di_state.is_enabled()

    def test_is_enabled_consistency(self, mock_file_processing_service: Mock) -> None:
        """Test that is_enabled is consistent with enabled flag and service presence."""
        di_state = DIState[FileProcessingService]()

        # Initially disabled
        assert not di_state.is_enabled()
        assert di_state.is_enabled() == (
            di_state.enabled and di_state.service is not None
        )

        # After setting service
        di_state.set_service(mock_file_processing_service)
        assert di_state.is_enabled()
        assert di_state.is_enabled() == (
            di_state.enabled and di_state.service is not None
        )

        # After clearing
        di_state.clear_service()
        assert not di_state.is_enabled()
        assert di_state.is_enabled() == (
            di_state.enabled and di_state.service is not None
        )
