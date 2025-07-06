"""Tests for table layout utilities."""

from unittest.mock import Mock

from kp_analysis_toolkit.cli.utils.table_layouts import (
    create_config_display_table,
    create_file_listing_table,
    create_file_selection_table,
    create_system_info_table,
)

# Constants for expected column counts
COLUMNS_CHOICE_FILE_SIZE = 3
COLUMNS_FILE_SIZE = 2
COLUMNS_SYSTEM_DETAILS = 3
COLUMNS_SYSTEM_BASIC = 2
COLUMNS_CONFIG_WITH_ORIGINAL = 4
COLUMNS_CONFIG_BASIC = 3


class TestTableLayouts:
    """Test cases for table layout utilities."""

    def test_create_file_selection_table_with_all_options(self) -> None:
        """Test file selection table creation with all options enabled."""
        mock_rich_output = Mock()
        mock_table = Mock()
        mock_rich_output.table.return_value = mock_table

        result = create_file_selection_table(
            mock_rich_output,
            title="Test Files",
            include_size=True,
            include_choice_column=True,
        )

        assert result == mock_table
        mock_rich_output.table.assert_called_once_with(
            title="Test Files",
            show_header=True,
            header_style="bold cyan",
            border_style="blue",
        )
        # Should add 3 columns: Choice, File Name, Size
        assert mock_table.add_column.call_count == COLUMNS_CHOICE_FILE_SIZE

    def test_create_file_selection_table_minimal(self) -> None:
        """Test file selection table creation with minimal options."""
        mock_rich_output = Mock()
        mock_table = Mock()
        mock_rich_output.table.return_value = mock_table

        result = create_file_selection_table(
            mock_rich_output,
            include_size=False,
            include_choice_column=False,
        )

        assert result == mock_table
        # Should add only 1 column: File Name
        assert mock_table.add_column.call_count == 1

    def test_create_file_listing_table(self) -> None:
        """Test file listing table creation."""
        mock_rich_output = Mock()
        mock_table = Mock()
        mock_rich_output.table.return_value = mock_table

        result = create_file_listing_table(
            mock_rich_output,
            title="Source Files",
            file_column_name="File Path",
        )

        assert result == mock_table
        mock_rich_output.table.assert_called_once()
        # Should add 2 columns: File Path, Size
        assert mock_table.add_column.call_count == COLUMNS_FILE_SIZE

    def test_create_system_info_table_with_details(self) -> None:
        """Test system info table creation with details."""
        mock_rich_output = Mock()
        mock_table = Mock()
        mock_rich_output.table.return_value = mock_table

        result = create_system_info_table(
            mock_rich_output,
            title="Systems",
            include_details=True,
        )

        assert result == mock_table
        # Should add 3 columns: System Name, File Hash, Details
        assert mock_table.add_column.call_count == COLUMNS_SYSTEM_DETAILS

    def test_create_system_info_table_without_details(self) -> None:
        """Test system info table creation without details."""
        mock_rich_output = Mock()
        mock_table = Mock()
        mock_rich_output.table.return_value = mock_table

        result = create_system_info_table(
            mock_rich_output,
            include_details=False,
        )

        assert result == mock_table
        # Should add 2 columns: System Name, File Hash
        assert mock_table.add_column.call_count == COLUMNS_SYSTEM_BASIC

    def test_create_config_display_table_with_original_values(self) -> None:
        """Test config display table creation with original values."""
        mock_rich_output = Mock()
        mock_table = Mock()
        mock_rich_output.table.return_value = mock_table

        result = create_config_display_table(
            mock_rich_output,
            show_original_values=True,
        )

        assert result == mock_table
        # Should add 4 columns: Parameter, Original Value, Effective Value, Type
        assert mock_table.add_column.call_count == COLUMNS_CONFIG_WITH_ORIGINAL

    def test_create_config_display_table_without_original_values(self) -> None:
        """Test config display table creation without original values."""
        mock_rich_output = Mock()
        mock_table = Mock()
        mock_rich_output.table.return_value = mock_table

        result = create_config_display_table(
            mock_rich_output,
            show_original_values=False,
        )

        assert result == mock_table
        # Should add 3 columns: Parameter, Effective Value, Type
        assert mock_table.add_column.call_count == COLUMNS_CONFIG_BASIC

    def test_table_creation_quiet_mode(self) -> None:
        """Test table creation returns None in quiet mode."""
        mock_rich_output = Mock()
        mock_rich_output.table.return_value = None

        result = create_file_selection_table(mock_rich_output)

        assert result is None
        mock_rich_output.table.assert_called_once()
