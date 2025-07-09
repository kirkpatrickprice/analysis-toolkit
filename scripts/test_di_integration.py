#!/usr/bin/env python3
"""Simple test script to verify DI integration works."""

import tempfile
from pathlib import Path

from kp_analysis_toolkit.utils.hash_generator import (
    clear_file_processing_service,
    hash_file,
    set_file_processing_service,
)


def test_di_integration() -> None:
    """Test that DI integration works correctly."""
    # Create a test file
    with tempfile.NamedTemporaryFile(delete=False, mode="w") as f:
        f.write("Hello, DI integration test!")
        test_file = Path(f.name)

    try:
        # Test without DI (direct implementation)
        clear_file_processing_service()
        direct_hash = hash_file(test_file)
        print(f"Direct hash: {direct_hash}")

        # Create a mock service
        class MockFileProcessingService:
            def generate_hash(self, file_path: Path) -> str:  # noqa: ARG002
                return "mock_di_hash_result"

        # Test with DI
        mock_service = MockFileProcessingService()
        set_file_processing_service(mock_service)
        di_hash = hash_file(test_file)
        print(f"DI hash: {di_hash}")

        # Verify the DI integration worked
        assert di_hash == "mock_di_hash_result", (
            f"Expected 'mock_di_hash_result', got '{di_hash}'"
        )
        assert di_hash != direct_hash, "DI hash should be different from direct hash"

        print("✓ DI integration test passed!")

    finally:
        test_file.unlink()
        clear_file_processing_service()


if __name__ == "__main__":
    test_di_integration()
