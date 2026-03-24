"""Tests for is_attribute_applicable(), load_yaml_config(), and process_includes()."""
from pathlib import Path

import pytest

from kp_analysis_toolkit.process_scripts.models.enums import (
    OSFamilyType,
    ProducerType,
)
from kp_analysis_toolkit.process_scripts.models.search.sys_filters import SysFilterAttr
from kp_analysis_toolkit.process_scripts.models.systems import Systems
from kp_analysis_toolkit.process_scripts.search_engine import (
    is_attribute_applicable,
    load_yaml_config,
    process_includes,
)

win_file = Path("testdata/process_scripts/windows/windows10pro-cb19044-kp0.4.7.txt")
nix_file = Path("testdata/process_scripts/linux/ubuntu-22.04-0.6.22.txt")
mac_file = Path("testdata/process_scripts/macos/macos-13.3.1-kp0.1.0.txt")


def _make_system(os_family: OSFamilyType, file: Path) -> Systems:
    producer = (
        ProducerType.KPWINAUDIT
        if os_family == OSFamilyType.WINDOWS
        else ProducerType.KPMACAUDIT
        if os_family == OSFamilyType.DARWIN
        else ProducerType.KPNIXAUDIT
    )
    return Systems(
        system_name="test-system",
        os_family=os_family,
        producer=producer,
        file=file,
        producer_version="1.0.0",
    )


class TestIsAttributeApplicable:
    """Tests for is_attribute_applicable()."""

    @pytest.mark.parametrize(
        "attr",
        [
            SysFilterAttr.PRODUCT_NAME,
            SysFilterAttr.RELEASE_ID,
            SysFilterAttr.CURRENT_BUILD,
            SysFilterAttr.UBR,
        ],
    )
    def test_windows_only_attrs_rejected_for_linux(self, attr: SysFilterAttr) -> None:
        """Windows-only attributes must not apply to Linux systems."""
        system = _make_system(OSFamilyType.LINUX, nix_file)
        assert is_attribute_applicable(system, attr) is False

    @pytest.mark.parametrize(
        "attr",
        [
            SysFilterAttr.PRODUCT_NAME,
            SysFilterAttr.RELEASE_ID,
            SysFilterAttr.CURRENT_BUILD,
            SysFilterAttr.UBR,
        ],
    )
    def test_windows_only_attrs_accepted_for_windows(self, attr: SysFilterAttr) -> None:
        """Windows-only attributes must apply to Windows systems."""
        system = _make_system(OSFamilyType.WINDOWS, win_file)
        assert is_attribute_applicable(system, attr) is True

    @pytest.mark.parametrize(
        "attr",
        [
            SysFilterAttr.DISTRO_FAMILY,
            SysFilterAttr.OS_PRETTY_NAME,
        ],
    )
    def test_linux_only_attrs_rejected_for_windows(self, attr: SysFilterAttr) -> None:
        """Linux-only attributes must not apply to Windows systems."""
        system = _make_system(OSFamilyType.WINDOWS, win_file)
        assert is_attribute_applicable(system, attr) is False

    @pytest.mark.parametrize(
        "attr",
        [
            SysFilterAttr.DISTRO_FAMILY,
            SysFilterAttr.OS_PRETTY_NAME,
        ],
    )
    def test_linux_only_attrs_accepted_for_linux(self, attr: SysFilterAttr) -> None:
        """Linux-only attributes must apply to Linux systems."""
        system = _make_system(OSFamilyType.LINUX, nix_file)
        assert is_attribute_applicable(system, attr) is True

    @pytest.mark.parametrize(
        "attr",
        [
            SysFilterAttr.OS_FAMILY,
            SysFilterAttr.PRODUCER,
            SysFilterAttr.PRODUCER_VERSION,
        ],
    )
    def test_universal_attrs_accepted_for_windows(self, attr: SysFilterAttr) -> None:
        """Universal attributes must apply to Windows systems."""
        system = _make_system(OSFamilyType.WINDOWS, win_file)
        assert is_attribute_applicable(system, attr) is True

    @pytest.mark.parametrize(
        "attr",
        [
            SysFilterAttr.OS_FAMILY,
            SysFilterAttr.PRODUCER,
            SysFilterAttr.PRODUCER_VERSION,
        ],
    )
    def test_universal_attrs_accepted_for_linux(self, attr: SysFilterAttr) -> None:
        """Universal attributes must apply to Linux systems."""
        system = _make_system(OSFamilyType.LINUX, nix_file)
        assert is_attribute_applicable(system, attr) is True

    def test_windows_only_attr_rejected_for_mac(self) -> None:
        """Windows-only attributes must not apply to macOS systems."""
        system = _make_system(OSFamilyType.DARWIN, mac_file)
        assert is_attribute_applicable(system, SysFilterAttr.PRODUCT_NAME) is False

    def test_linux_only_attr_rejected_for_mac(self) -> None:
        """Linux-only attributes must not apply to macOS systems."""
        system = _make_system(OSFamilyType.DARWIN, mac_file)
        assert is_attribute_applicable(system, SysFilterAttr.DISTRO_FAMILY) is False


class TestLoadYamlConfig:
    """Tests for load_yaml_config()."""

    def test_valid_minimal_yaml_returns_yaml_config(self, tmp_path: Path) -> None:
        """A minimal valid YAML file loads into a YamlConfig successfully."""
        yaml_file = tmp_path / "test.yaml"
        yaml_file.write_text("search_os_version:\n  regex: 'OS Version.*'\n")
        config = load_yaml_config(yaml_file)
        assert "search_os_version" in config.search_configs

    def test_empty_yaml_raises_value_error(self, tmp_path: Path) -> None:
        """An empty YAML file raises ValueError with a descriptive message."""
        yaml_file = tmp_path / "empty.yaml"
        yaml_file.write_text("")
        with pytest.raises(ValueError, match="Empty YAML file"):
            load_yaml_config(yaml_file)

    def test_invalid_yaml_syntax_raises_value_error(self, tmp_path: Path) -> None:
        """Malformed YAML syntax raises ValueError."""
        yaml_file = tmp_path / "bad.yaml"
        yaml_file.write_text("key: [unclosed\n")
        with pytest.raises(ValueError):
            load_yaml_config(yaml_file)

    def test_yaml_with_invalid_regex_raises_value_error(self, tmp_path: Path) -> None:
        """A search section with an invalid regex pattern raises ValueError."""
        yaml_file = tmp_path / "invalid_regex.yaml"
        yaml_file.write_text("bad_search:\n  regex: '[invalid regex'\n")
        with pytest.raises(ValueError):
            load_yaml_config(yaml_file)

    def test_yaml_with_global_config_parsed_correctly(self, tmp_path: Path) -> None:
        """Global config section is parsed and available on the returned object."""
        yaml_file = tmp_path / "global.yaml"
        yaml_file.write_text(
            "global:\n"
            "  max_results: 50\n"
            "search_something:\n"
            "  regex: 'test.*'\n",
        )
        config = load_yaml_config(yaml_file)
        assert config.global_config is not None
        assert config.global_config.max_results == 50  # noqa: PLR2004


class TestProcessIncludes:
    """Tests for process_includes()."""

    def test_no_includes_returns_configs_from_current_file(self, tmp_path: Path) -> None:
        """When no includes are present, only the current file's configs are returned."""
        yaml_file = tmp_path / "main.yaml"
        yaml_file.write_text("search_os_version:\n  regex: 'OS Version.*'\n")
        yaml_config = load_yaml_config(yaml_file)
        configs = process_includes(yaml_config, tmp_path)
        assert len(configs) == 1
        assert configs[0].name == "search_os_version"

    def test_include_file_merges_configs(self, tmp_path: Path) -> None:
        """Configs from an included file are merged with the main file's configs."""
        included = tmp_path / "included.yaml"
        included.write_text("search_included:\n  regex: 'included.*'\n")
        main = tmp_path / "main.yaml"
        main.write_text(
            "search_main:\n"
            "  regex: 'main.*'\n"
            "include_extra:\n"
            "  files:\n"
            "    - included.yaml\n",
        )
        yaml_config = load_yaml_config(main)
        configs = process_includes(yaml_config, tmp_path)
        names = [c.name for c in configs]
        assert "search_main" in names
        assert "search_included" in names

    def test_missing_include_file_raises_file_not_found(self, tmp_path: Path) -> None:
        """A missing include file raises FileNotFoundError."""
        main = tmp_path / "main.yaml"
        main.write_text(
            "search_main:\n"
            "  regex: 'main.*'\n"
            "include_extra:\n"
            "  files:\n"
            "    - nonexistent.yaml\n",
        )
        yaml_config = load_yaml_config(main)
        with pytest.raises(FileNotFoundError):
            process_includes(yaml_config, tmp_path)

    def test_global_config_applied_to_search_configs(self, tmp_path: Path) -> None:
        """Global config settings are merged into each search config."""
        yaml_file = tmp_path / "global.yaml"
        yaml_file.write_text(
            "global:\n"
            "  max_results: 10\n"
            "search_something:\n"
            "  regex: 'test.*'\n",
        )
        yaml_config = load_yaml_config(yaml_file)
        configs = process_includes(yaml_config, tmp_path)
        assert configs[0].max_results == 10  # noqa: PLR2004
