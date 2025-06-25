from pathlib import Path

from kp_analysis_toolkit.process_scripts.process_systems import get_config_files


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
