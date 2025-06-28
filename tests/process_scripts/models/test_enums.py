from kp_analysis_toolkit.process_scripts.models.enums import (
    DistroFamilyType,
    OSFamilyType,
    ProducerType,
    SysFilterAttr,
    SysFilterComparisonOperators,
)


class TestDistroFamilyType:
    """Tests for the DistroFamilyType enum."""

    def test_enum_values(self) -> None:
        """Test that enum values match expected string values."""
        assert DistroFamilyType.DEB.value == "deb"
        assert DistroFamilyType.RPM.value == "rpm"
        assert DistroFamilyType.APK.value == "apk"
        assert DistroFamilyType.OTHER.value == "other"

    def test_string_representation(self) -> None:
        """Test string representation works correctly."""
        assert str(DistroFamilyType.DEB) == "deb"
        assert str(DistroFamilyType.RPM) == "rpm"
        assert str(DistroFamilyType.APK) == "apk"
        assert str(DistroFamilyType.OTHER) == "other"

    def test_equality_comparison(self) -> None:
        """Test that EnumStrMixin provides string equality comparison."""
        assert DistroFamilyType.DEB == "deb"
        assert DistroFamilyType.RPM == "rpm"
        assert DistroFamilyType.DEB != "rpm"


class TestProducerType:
    """Tests for the ProducerType enum."""

    def test_enum_values(self) -> None:
        """Test that enum values match expected string values."""
        assert ProducerType.KPNIXAUDIT.value == "KPNIXAUDIT"
        assert ProducerType.KPWINAUDIT.value == "KPWINAUDIT"
        assert ProducerType.KPMACAUDIT.value == "KPMACAUDIT"
        assert ProducerType.OTHER.value == "Other"

    def test_string_representation(self) -> None:
        """Test string representation works correctly."""
        assert str(ProducerType.KPNIXAUDIT) == "KPNIXAUDIT"
        assert str(ProducerType.KPWINAUDIT) == "KPWINAUDIT"
        assert str(ProducerType.KPMACAUDIT) == "KPMACAUDIT"
        assert str(ProducerType.OTHER) == "Other"


class TestSysFilterAttr:
    """Tests for the SysFilterAttr enum."""

    def test_enum_values(self) -> None:
        """Test that enum values match expected string values."""
        assert SysFilterAttr.OS_FAMILY.value == "os_family"
        assert SysFilterAttr.DISTRO_FAMILY.value == "distro_family"
        assert SysFilterAttr.PRODUCER.value == "producer"
        assert SysFilterAttr.PRODUCER_VERSION.value == "producer_version"
        assert SysFilterAttr.PRODUCT_NAME.value == "product_name"
        assert SysFilterAttr.RELEASE_ID.value == "release_id"
        assert SysFilterAttr.CURRENT_BUILD.value == "current_build"
        assert SysFilterAttr.UBR.value == "ubr"
        assert SysFilterAttr.OS_PRETTY_NAME.value == "os_pretty_name"
        assert SysFilterAttr.OS_VERSION.value == "os_version"


class TestSysFilterComparisonOperators:
    """Tests for the SysFilterComparisonOperators enum."""

    def test_enum_values(self) -> None:
        """Test that enum values match expected string values."""
        assert SysFilterComparisonOperators.EQUALS.value == "eq"
        assert SysFilterComparisonOperators.GREATER_THAN.value == "gt"
        assert SysFilterComparisonOperators.LESS_THAN.value == "lt"
        assert SysFilterComparisonOperators.GREATER_EQUAL.value == "ge"
        assert SysFilterComparisonOperators.LESS_EQUAL.value == "le"
        assert SysFilterComparisonOperators.IN.value == "in"


class TestOSFamilyType:
    """Tests for the OSFamilyType enum."""

    def test_enum_values(self) -> None:
        """Test that enum values match expected string values."""
        assert OSFamilyType.DARWIN.value == "Darwin"
        assert OSFamilyType.LINUX.value == "Linux"
        assert OSFamilyType.WINDOWS.value == "Windows"
        assert OSFamilyType.OTHER.value == "Other"
        assert OSFamilyType.UNDEFINED.value == "Undefined"

    def test_string_representation(self) -> None:
        """Test string representation works correctly."""
        assert str(OSFamilyType.DARWIN) == "Darwin"
        assert str(OSFamilyType.LINUX) == "Linux"
        assert str(OSFamilyType.WINDOWS) == "Windows"
        assert str(OSFamilyType.OTHER) == "Other"
        assert str(OSFamilyType.UNDEFINED) == "Undefined"

    def test_equality_comparison(self) -> None:
        """Test that EnumStrMixin provides string equality comparison."""
        assert OSFamilyType.LINUX == "Linux"
        assert OSFamilyType.WINDOWS == "Windows"
        assert OSFamilyType.LINUX != "Windows"

    def test_membership(self) -> None:
        """Test enum membership checks."""
        assert OSFamilyType.LINUX in OSFamilyType
        assert "Linux" in OSFamilyType
        assert [os_type for os_type in OSFamilyType] == list(OSFamilyType)  # noqa: C416

    def test_enum_length(self) -> None:
        """Test the number of elements in the enum."""
        assert len(list(OSFamilyType)) == 5  # noqa: PLR2004
