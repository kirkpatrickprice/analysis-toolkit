import uuid
from pathlib import Path

import pytest

from kp_analysis_toolkit.process_scripts.models.enums import (
    DistroFamilyType,
    OSFamilyType,
    ProducerType,
)
from kp_analysis_toolkit.process_scripts.models.systems import Systems

win_file = Path("testdata/windows/windows10pro-cb19044-kp0.4.7.txt")
mac_file = Path("testdata/macos/macos-13.3.1-kp0.1.0.txt")
nix_file = Path("testdata/linux/ubuntu-22.04-0.6.22.txt")


class TestSystems:
    """Test cases for Systems class."""

    def test_instantiation_minimum_fields(self) -> None:
        """Test Systems instantiation with minimum required fields."""
        system = Systems(
            system_name="test-system",
            os_family=OSFamilyType.WINDOWS,
            producer=ProducerType.KPWINAUDIT,
            file=win_file,
            producer_version="1.0.0",
        )
        assert system.system_name == "test-system"
        assert system.producer == ProducerType.KPWINAUDIT
        assert system.producer_version == "1.0.0"
        assert isinstance(system.system_id, uuid.UUID)
        assert system.os_family is OSFamilyType.WINDOWS

    def test_instantiation_all_fields(self) -> None:
        """Test Systems instantiation with all fields."""
        system_id = uuid.uuid4()
        system = Systems(
            system_id=system_id,
            file=win_file,
            system_name="windows-system",
            os_family=OSFamilyType.WINDOWS,
            system_os="Windows 10",
            producer=ProducerType.KPWINAUDIT,
            producer_version="2.3.4",
            product_name="Windows 10 Pro",
            release_id="1909",
            current_build="18363",
            ubr="1082",
            distro_family=DistroFamilyType.RPM,
            os_pretty_name="Pretty OS Name",
            os_version="10.0.18363",
        )
        assert system.system_id == system_id
        assert system.system_name == "windows-system"
        assert system.os_family == OSFamilyType.WINDOWS
        assert system.system_os == "Windows 10"
        assert system.producer == ProducerType.KPWINAUDIT
        assert system.producer_version == "2.3.4"
        assert system.product_name == "Windows 10 Pro"
        assert system.release_id == "1909"
        assert system.current_build == "18363"
        assert system.ubr == "1082"
        assert system.distro_family == DistroFamilyType.RPM
        assert system.os_pretty_name == "Pretty OS Name"
        assert system.os_version == "10.0.18363"

    def test_version_components_normal(self) -> None:
        """Test version_components property with normal version string."""
        system = Systems(
            system_name="test-system",
            file=win_file,
            os_family=OSFamilyType.WINDOWS,
            producer=ProducerType.KPWINAUDIT,
            producer_version="1.2.3",
        )
        assert system.version_components == [1, 2, 3]

    def test_version_components_complex(self) -> None:
        """Test version_components property with complex version string."""
        system = Systems(
            system_name="test-system",
            os_family=OSFamilyType.WINDOWS,
            file=win_file,
            producer=ProducerType.KPWINAUDIT,
            producer_version="10.20.30.40",
        )
        assert system.version_components == [10, 20, 30, 40]

    def test_version_components_empty(self) -> None:
        """Test version_components property with empty version string."""
        system = Systems(
            system_name="test-system",
            os_family=OSFamilyType.WINDOWS,
            file=win_file,
            producer=ProducerType.KPWINAUDIT,
            producer_version="",
        )
        assert system.version_components == [0, 0, 0]

    def test_version_components_invalid(self) -> None:
        """Test version_components property with invalid version string."""
        system = Systems(
            system_name="test-system",
            os_family=OSFamilyType.WINDOWS,
            file=win_file,
            producer=ProducerType.KPWINAUDIT,
            producer_version="1.2.abc",
        )
        with pytest.raises(ValueError):  # noqa: PT011
            _: list[int] = system.version_components

    def test_is_windows_true(self) -> None:
        """Test is_windows() returns True for Windows systems."""
        system = Systems(
            system_name="windows-system",
            os_family=OSFamilyType.WINDOWS,
            file=win_file,
            producer=ProducerType.KPWINAUDIT,
            producer_version="1.0.0",
        )
        assert system.is_windows() is True

    def test_is_windows_false(self) -> None:
        """Test is_windows() returns False for non-Windows systems."""
        system = Systems(
            system_name="linux-system",
            os_family=OSFamilyType.LINUX,
            producer=ProducerType.KPNIXAUDIT,
            file=nix_file,
            producer_version="1.0.0",
        )
        assert system.is_windows() is False

    def test_is_linux_true(self) -> None:
        """Test is_linux() returns True for Linux systems."""
        system = Systems(
            system_name="linux-system",
            os_family=OSFamilyType.LINUX,
            producer=ProducerType.KPNIXAUDIT,
            file=nix_file,
            producer_version="1.0.0",
        )
        assert system.is_linux() is True

    def test_is_linux_false(self) -> None:
        """Test is_linux() returns False for non-Linux systems."""
        system = Systems(
            system_name="windows-system",
            os_family=OSFamilyType.WINDOWS,
            producer=ProducerType.KPWINAUDIT,
            file=win_file,
            producer_version="1.0.0",
        )
        assert system.is_linux() is False

    def test_is_mac_true(self) -> None:
        """Test is_mac() returns True for macOS systems."""
        system = Systems(
            system_name="mac-system",
            os_family=OSFamilyType.DARWIN,
            producer=ProducerType.KPMACAUDIT,
            file=mac_file,
            producer_version="1.0.0",
        )
        assert system.is_mac() is True

    def test_is_mac_false(self) -> None:
        """Test is_mac() returns False for non-macOS systems."""
        system = Systems(
            system_name="windows-system",
            os_family=OSFamilyType.WINDOWS,
            producer=ProducerType.KPWINAUDIT,
            file=win_file,
            producer_version="1.0.0",
        )
        assert system.is_mac() is False

    def test_is_windows_none_os_family(self) -> None:
        """Test is_windows() returns False when os_family is None."""
        system = Systems(
            system_name="unknown-system",
            os_family=None,
            producer=ProducerType.KPWINAUDIT,
            file=win_file,
            producer_version="1.0.0",
        )
        assert system.is_windows() is False

    def test_is_linux_none_os_family(self) -> None:
        """Test is_linux() returns False when os_family is None."""
        system = Systems(
            system_name="unknown-system",
            os_family=None,
            producer=ProducerType.KPNIXAUDIT,
            file=nix_file,
            producer_version="1.0.0",
        )
        assert system.is_linux() is False

    def test_is_mac_none_os_family(self) -> None:
        """Test is_mac() returns False when os_family is None."""
        system = Systems(
            system_name="unknown-system",
            os_family=None,
            producer=ProducerType.KPMACAUDIT,
            file=mac_file,
            producer_version="1.0.0",
        )
        assert system.is_mac() is False
