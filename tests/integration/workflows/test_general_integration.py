#!/usr/bin/env python3
"""Integration test script to verify our encoding and producer detection fixes work correctly."""

from pathlib import Path

from kp_analysis_toolkit.process_scripts.models.types.enums import ProducerType
from kp_analysis_toolkit.process_scripts.process_systems import get_producer_type
from kp_analysis_toolkit.utils.get_file_encoding import detect_encoding


def test_encoding_detection() -> None:
    """Test encoding detection on problematic file."""
    print("=== Testing Encoding Detection ===")

    # Test the problematic file from the real data
    problematic_file = Path(
        "../../Customers/test-script-results/kpat-test-data/non-ascii-chars/tol-web1.txt",
    )

    if problematic_file.exists():
        print(f"Testing file: {problematic_file}")
        encoding = detect_encoding(problematic_file)
        print(f"Detected encoding: {encoding}")

        if encoding is None:
            print("✅ PASS: File correctly returns None (will be skipped)")
        else:
            print(f"❌ FAIL: File should return None but got: {encoding}")
    else:
        print(f"⚠️  Test file not found: {problematic_file}")


def test_producer_detection() -> None:
    """Test producer detection on various files."""
    print("\n=== Testing Producer Detection ===")

    # Create test files
    test_dir = Path("temp_test_files")
    test_dir.mkdir(exist_ok=True)

    # Test KPNIX file
    kpnix_file = test_dir / "kpnix_test.txt"
    kpnix_file.write_text("KPNIXVERSION: 0.6.21\nSome other content")

    producer, version = get_producer_type(kpnix_file, "utf-8")
    print(f"KPNIX test - Producer: {producer}, Version: {version}")
    if producer == ProducerType.KPNIXAUDIT:
        print("✅ PASS: KPNIX correctly detected")
    else:
        print("❌ FAIL: KPNIX not detected correctly")

    # Test unknown file
    unknown_file = test_dir / "unknown_test.txt"
    unknown_file.write_text("Some random content without producer signature")

    producer, version = get_producer_type(unknown_file, "utf-8")
    print(f"Unknown test - Producer: {producer}, Version: {version}")
    if producer == ProducerType.OTHER:
        print("✅ PASS: Unknown file correctly returns OTHER")
    else:
        print("❌ FAIL: Unknown file should return OTHER")

    # Cleanup
    kpnix_file.unlink()
    unknown_file.unlink()
    test_dir.rmdir()


if __name__ == "__main__":
    test_encoding_detection()
    test_producer_detection()
    print("\n=== Integration Test Complete ===")
