from pathlib import Path
from unittest.mock import MagicMock, patch

from kp_analysis_toolkit.process_scripts.models.types.enums import ProducerType
from kp_analysis_toolkit.process_scripts.process_systems import (
    enumerate_systems_from_source_files,
    get_config_files,
    get_producer_type,
)


class TestGetConfigFiles:
    """Tests for the get_config_files function."""

    def test_with_yaml_files(self, tmp_path: Path) -> None:
        """Test get_config_files returns all YAML files in the directory."""
        # Create test YAML files
        yaml_files: list[Path] = []
        max_files: int = 3
        for i in range(max_files):
            file_path: Path = tmp_path / f"config{i}.yaml"
            file_path.touch()
            yaml_files.append(file_path)

        # Get config files
        result: list[Path] = get_config_files(tmp_path)

        # Verify all files are found and paths are correct
        assert len(result) == max_files, f"Should find exactly {max_files} YAML files"
        for file in yaml_files:
            assert file.name in [f.name for f in result], f"Should find {file.name}"

    def test_with_mixed_files(self, tmp_path: Path) -> None:
        """Test get_config_files returns only YAML files when directory has mixed file types."""
        # Create YAML files
        yaml_file1: Path = tmp_path / "config1.yaml"
        yaml_file2: Path = tmp_path / "config2.yaml"
        yaml_file1.touch()
        yaml_file2.touch()

        # Create non-YAML files
        txt_file: Path = tmp_path / "readme.txt"
        json_file: Path = tmp_path / "data.json"
        txt_file.touch()
        json_file.touch()

        # Get config files
        result: list[Path] = get_config_files(tmp_path)

        # Verify only YAML files are returned
        assert len(result) == 2, "Should find exactly 2 YAML files"  # noqa: PLR2004
        assert yaml_file1.name in [f.name for f in result], "Should find config1.yaml"
        assert yaml_file2.name in [f.name for f in result], "Should find config2.yaml"
        assert txt_file.name not in [f.name for f in result], "Should not find txt file"
        assert json_file.name not in [f.name for f in result], (
            "Should not find json file"
        )

    def test_with_empty_directory(self, tmp_path: Path) -> None:
        """Test get_config_files returns empty list for empty directory."""
        # Get config files from empty directory
        result: list[Path] = get_config_files(tmp_path)

        # Verify result is empty list
        assert result == [], "Should return empty list for empty directory"

    def test_with_nested_directories(self, tmp_path: Path) -> None:
        """Test get_config_files doesn't include files from subdirectories."""
        # Create YAML file in main directory
        yaml_file: Path = tmp_path / "config.yaml"
        yaml_file.touch()

        # Create subdirectory with YAML file
        subdir: Path = tmp_path / "subdir"
        subdir.mkdir()
        nested_yaml: Path = subdir / "nested.yaml"
        nested_yaml.touch()

        # Get config files
        result: list[Path] = get_config_files(tmp_path)

        # Verify only top-level YAML file is returned
        assert len(result) == 1, "Should find exactly 1 YAML file"
        assert yaml_file.name in [f.name for f in result], "Should find config.yaml"
        assert nested_yaml.name not in [f.name for f in result], (
            "Should not find nested.yaml"
        )


class TestFileSkippingLogic:
    """Tests for file skipping logic to prevent regression of encoding and producer detection fixes."""

    @patch("kp_analysis_toolkit.process_scripts.process_systems.detect_encoding")
    @patch("kp_analysis_toolkit.process_scripts.process_systems.get_source_files")
    def test_skip_files_with_encoding_detection_failure(
        self,
        mock_get_source_files: MagicMock,
        mock_detect_encoding: MagicMock,
        tmp_path: Path,
    ) -> None:
        """Test that files with encoding detection failure are skipped."""
        # Create a test file
        test_file = tmp_path / "encoding_failure_test.txt"
        test_file.write_text("Test content")

        # Mock get_source_files to return our test file
        mock_get_source_files.return_value = [test_file]

        # Mock detect_encoding to return None (encoding detection failure)
        mock_detect_encoding.return_value = None

        # Create a simple mock program config (don't need full validation for this test)
        from unittest.mock import MagicMock

        program_config = MagicMock()

        # Process files
        systems = list(enumerate_systems_from_source_files(program_config))

        # Should return empty list (file was skipped)
        assert len(systems) == 0
        mock_detect_encoding.assert_called_once_with(test_file)

    @patch("kp_analysis_toolkit.process_scripts.process_systems.warning")
    @patch("kp_analysis_toolkit.process_scripts.process_systems.get_producer_type")
    @patch("kp_analysis_toolkit.process_scripts.process_systems.detect_encoding")
    @patch("kp_analysis_toolkit.process_scripts.process_systems.get_source_files")
    def test_skip_files_with_unknown_producer(
        self,
        mock_get_source_files: MagicMock,
        mock_detect_encoding: MagicMock,
        mock_get_producer_type: MagicMock,
        mock_warning: MagicMock,
        tmp_path: Path,
    ) -> None:
        """Test that files with unknown producer are skipped."""
        # Create a test file
        test_file = tmp_path / "unknown_producer_test.txt"
        test_file.write_text("Test content without known producer patterns")

        # Mock get_source_files to return our test file
        mock_get_source_files.return_value = [test_file]

        # Mock detect_encoding to return valid encoding
        mock_detect_encoding.return_value = "utf-8"

        # Mock get_producer_type to return OTHER (unknown producer)
        mock_get_producer_type.return_value = (ProducerType.OTHER, "Unknown")

        # Create a simple mock program config
        from unittest.mock import MagicMock

        program_config = MagicMock()

        # Process files
        systems = list(enumerate_systems_from_source_files(program_config))

        # Should return empty list (file was skipped)
        assert len(systems) == 0

        # Should have called warning about unknown producer
        mock_warning.assert_called_once()
        warning_call_args = mock_warning.call_args[0][0]
        assert "Skipping file due to unknown producer" in warning_call_args
        assert str(test_file) in warning_call_args

    @patch("kp_analysis_toolkit.process_scripts.process_systems.get_distro_family")
    @patch("kp_analysis_toolkit.process_scripts.process_systems.generate_file_hash")
    @patch("kp_analysis_toolkit.process_scripts.process_systems.get_system_details")
    @patch("kp_analysis_toolkit.process_scripts.process_systems.get_producer_type")
    @patch("kp_analysis_toolkit.process_scripts.process_systems.detect_encoding")
    @patch("kp_analysis_toolkit.process_scripts.process_systems.get_source_files")
    def test_process_valid_files_successfully(  # noqa: PLR0913
        self,
        mock_get_source_files: MagicMock,
        mock_detect_encoding: MagicMock,
        mock_get_producer_type: MagicMock,
        mock_get_system_details: MagicMock,
        mock_generate_file_hash: MagicMock,
        mock_get_distro_family: MagicMock,
        tmp_path: Path,
    ) -> None:
        """Test that valid files are processed successfully."""
        # Create a test file
        test_file = tmp_path / "valid_producer_test.txt"
        test_file.write_text("KPNIXVERSION: 0.6.21")

        # Mock get_source_files to return our test file
        mock_get_source_files.return_value = [test_file]

        # Mock detect_encoding to return valid encoding
        mock_detect_encoding.return_value = "utf-8"

        # Mock get_producer_type to return valid producer
        mock_get_producer_type.return_value = (ProducerType.KPNIXAUDIT, "0.6.21")

        # Mock get_system_details
        mock_get_system_details.return_value = (
            "Ubuntu 22.04",
            {"os_pretty_name": "Ubuntu 22.04"},
        )

        # Mock file hash generation
        mock_generate_file_hash.return_value = "test_hash_123"

        # Mock distro family for Linux
        mock_get_distro_family.return_value = None

        # Create a simple mock program config
        from unittest.mock import MagicMock

        program_config = MagicMock()

        # Process files
        systems = list(enumerate_systems_from_source_files(program_config))

        # Should successfully process the file
        assert len(systems) == 1
        system = systems[0]
        assert system.system_name == "valid_producer_test"
        assert system.producer == ProducerType.KPNIXAUDIT
        assert system.producer_version == "0.6.21"
        assert system.encoding == "utf-8"


class TestGetProducerType:
    """Tests for the get_producer_type function to ensure proper producer detection."""

    def test_detect_kpnix_producer(self, tmp_path: Path) -> None:
        """Test detection of KPNIX producer type."""
        # Create a file with KPNIX producer pattern
        test_file = tmp_path / "kpnix_test.txt"
        content = """System Report for test-system
This report was generated Mon Jan 01 12:00:00 UTC 2024
KPNIXVERSION: 0.6.21
+ + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + +"""
        test_file.write_text(content, encoding="utf-8")

        # Test producer detection
        producer, version = get_producer_type(test_file, "utf-8")

        assert producer == ProducerType.KPNIXAUDIT
        assert version == "0.6.21"

    def test_detect_kpwin_producer(self, tmp_path: Path) -> None:
        """Test detection of KPWIN producer type."""
        # Create a file with KPWIN producer pattern
        test_file = tmp_path / "kpwin_test.txt"
        content = """System Report for WIN-TEST-01
This report was generated Mon Jan 01 12:00:00 UTC 2024
System_PSDetails::KPWINVERSION: 0.4.8
+ + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + +"""
        test_file.write_text(content, encoding="utf-8")

        # Test producer detection
        producer, version = get_producer_type(test_file, "utf-8")

        assert producer == ProducerType.KPWINAUDIT
        assert version == "0.4.8"

    def test_detect_kpmac_producer(self, tmp_path: Path) -> None:
        """Test detection of KPMAC producer type."""
        # Create a file with KPMAC producer pattern
        test_file = tmp_path / "kpmac_test.txt"
        content = """System Report for MAC-TEST-01
This report was generated Mon Jan 01 12:00:00 UTC 2024
KPMACVERSION: 0.1.0
+ + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + +"""
        test_file.write_text(content, encoding="utf-8")

        # Test producer detection
        producer, version = get_producer_type(test_file, "utf-8")

        assert producer == ProducerType.KPMACAUDIT
        assert version == "0.1.0"

    def test_detect_unknown_producer(self, tmp_path: Path) -> None:
        """Test that files without known producer patterns return OTHER."""
        # Create a file without any known producer patterns
        test_file = tmp_path / "unknown_test.txt"
        content = """Some random file content
Without any known producer version strings
Just regular text content here"""
        test_file.write_text(content, encoding="utf-8")

        # Test producer detection
        producer, version = get_producer_type(test_file, "utf-8")

        assert producer == ProducerType.OTHER
        assert version == "Unknown"

    def test_detect_partial_match_producer(self, tmp_path: Path) -> None:
        """Test that files with partial matches but wrong format return OTHER."""
        # Create a file with partial match (missing version)
        test_file = tmp_path / "partial_test.txt"
        content = """System Report for test-system
This report contains KPNIXVERSION but no proper version
KPNIXVERSION:
Some other content here"""
        test_file.write_text(content, encoding="utf-8")

        # Test producer detection
        producer, version = get_producer_type(test_file, "utf-8")

        # Should return OTHER because regex doesn't match (no version number)
        assert producer == ProducerType.OTHER
        assert version == "Unknown"

    def test_detect_empty_file_producer(self, tmp_path: Path) -> None:
        """Test producer detection on empty files."""
        # Create an empty file
        test_file = tmp_path / "empty_test.txt"
        test_file.touch()

        # Test producer detection
        producer, version = get_producer_type(test_file, "utf-8")

        assert producer == ProducerType.OTHER
        assert version == "Unknown"
