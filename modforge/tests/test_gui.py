

"""Tests for the GUI components."""

import unittest
from unittest.mock import MagicMock, patch
from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtCore import Qt
from modforge.gui.main_window import MainWindow
from modforge.gui.mod_list_view import ModListView
from modforge.gui.profile_view import ProfileView
from modforge.gui.settings_view import SettingsView
from modforge.gui.widgets import ToolbarWidget

class TestGUIComponents(unittest.TestCase):
    """Test cases for GUI components."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a QApplication instance for testing
        self.app = QApplication.instance()
        if not self.app:
            self.app = QApplication([])

        # Create mock objects
        self.mock_data = MagicMock()
        self.mock_mod_manager = MagicMock()
        self.mock_profile_manager = MagicMock()
        self.mock_load_order_manager = MagicMock()
        self.mock_persistence = MagicMock()

        # Configure mock data
        self.mock_data.mods = {
            "mod1": MagicMock(id="mod1", name="Test Mod 1", source_path="/path1"),
            "mod2": MagicMock(id="mod2", name="Test Mod 2", source_path="/path2")
        }
        self.mock_data.profiles = {
            "profile1": MagicMock(id="profile1", name="Test Profile 1"),
            "profile2": MagicMock(id="profile2", name="Test Profile 2")
        }
        self.mock_data.current_profile_id = "profile1"
        self.mock_data.settings = MagicMock(default_mod_library="/default/path")

    def tearDown(self):
        """Clean up test fixtures."""
        self.app = None

    def test_main_window_creation(self):
        """Test MainWindow creation."""
        window = MainWindow(
            self.mock_data,
            self.mock_mod_manager,
            self.mock_profile_manager,
            self.mock_load_order_manager,
            self.mock_persistence
        )

        self.assertIsNotNone(window)
        self.assertEqual(window.windowTitle(), "ModForge Game Mod Manager")
        self.assertIsNotNone(window.centralWidget())
        self.assertIsNotNone(window.tabs)
        self.assertEqual(window.tabs.count(), 3)  # Mod Library, Profiles, Settings

    def test_mod_list_view_creation(self):
        """Test ModListView creation."""
        view = ModListView(
            self.mock_data,
            self.mock_mod_manager,
            self.mock_profile_manager,
            self.mock_load_order_manager
        )

        self.assertIsNotNone(view)
        self.assertIsNotNone(view.mod_list)
        self.assertIsNotNone(view.search_input)
        self.assertIsNotNone(view.enabled_only_checkbox)

    def test_profile_view_creation(self):
        """Test ProfileView creation."""
        view = ProfileView(
            self.mock_data,
            self.mock_profile_manager,
            self.mock_load_order_manager
        )

        self.assertIsNotNone(view)
        self.assertIsNotNone(view.profile_list)
        self.assertIsNotNone(view.new_profile_button)
        self.assertIsNotNone(view.duplicate_button)

    def test_settings_view_creation(self):
        """Test SettingsView creation."""
        view = SettingsView(self.mock_data, self.mock_persistence)

        self.assertIsNotNone(view)
        self.assertIsNotNone(view.library_path_input)
        self.assertIsNotNone(view.save_button)
        self.assertIsNotNone(view.backup_button)

    def test_toolbar_widget_creation(self):
        """Test ToolbarWidget creation."""
        toolbar = ToolbarWidget(None)

        self.assertIsNotNone(toolbar)
        self.assertIsNotNone(toolbar.import_button)
        self.assertIsNotNone(toolbar.refresh_button)
        self.assertIsNotNone(toolbar.save_button)

    @patch('PySide6.QtWidgets.QFileDialog.getExistingDirectory')
    def test_mod_list_view_import_mod(self, mock_dialog):
        """Test mod import functionality."""
        view = ModListView(
            self.mock_data,
            self.mock_mod_manager,
            self.mock_profile_manager,
            self.mock_load_order_manager
        )

        # Mock the file dialog to return a path
        mock_dialog.return_value = "/path/to/mod"

        # Mock successful mod discovery
        mock_mod = MagicMock(id="new_mod", name="New Mod", source_path="/path/to/mod")
        self.mock_mod_manager.discover_mod.return_value = (mock_mod, None)
        self.mock_mod_manager.add_mod_to_library.return_value = True

        # Test import
        view.import_mod()

        # Verify the mod was added
        self.mock_mod_manager.discover_mod.assert_called_once_with("/path/to/mod")
        self.mock_mod_manager.add_mod_to_library.assert_called_once_with(mock_mod)

    @patch('PySide6.QtWidgets.QMessageBox.question')
    def test_mod_list_view_remove_mod(self, mock_question):
        """Test mod removal functionality."""
        view = ModListView(
            self.mock_data,
            self.mock_mod_manager,
            self.mock_profile_manager,
            self.mock_load_order_manager
        )

        # Mock the list widget to have a selected item
        mock_item = MagicMock()
        mock_item.data.return_value = "mod1"
        view.mod_list.selectedItems.return_value = [mock_item]

        # Mock user confirming removal
        mock_question.return_value = QMessageBox.Yes

        # Test removal
        view._remove_selected_mod()

        # Verify removal was called
        self.mock_mod_manager.remove_mod_from_library.assert_called_once_with("mod1")

    @patch('PySide6.QtWidgets.QInputDialog.getText')
    def test_profile_view_create_profile(self, mock_dialog):
        """Test profile creation functionality."""
        view = ProfileView(
            self.mock_data,
            self.mock_profile_manager,
            self.mock_load_order_manager
        )

        # Mock the dialog to return a profile name
        mock_dialog.return_value = ("New Profile", True)

        # Mock successful profile creation
        mock_profile = MagicMock(id="new_profile", name="New Profile")
        self.mock_profile_manager.create_profile.return_value = mock_profile

        # Test creation
        view._create_new_profile()

        # Verify profile was created
        self.mock_profile_manager.create_profile.assert_called_once_with("New Profile")

    @patch('PySide6.QtWidgets.QFileDialog.getSaveFileName')
    def test_settings_view_backup(self, mock_dialog):
        """Test backup functionality."""
        view = SettingsView(self.mock_data, self.mock_persistence)

        # Mock the dialog to return a backup path
        mock_dialog.return_value = ("/path/to/backup.db", "Database Files (*.db)")

        # Mock successful backup
        self.mock_persistence.backup_data.return_value = True

        # Test backup
        view._create_backup()

        # Verify backup was created
        self.mock_persistence.backup_data.assert_called_once_with("/path/to/backup.db")

    @patch('PySide6.QtWidgets.QFileDialog.getOpenFileName')
    @patch('PySide6.QtWidgets.QMessageBox.question')
    def test_settings_view_restore(self, mock_question, mock_dialog):
        """Test restore functionality."""
        view = SettingsView(self.mock_data, self.mock_persistence)

        # Mock the dialog to return a backup path
        mock_dialog.return_value = ("/path/to/backup.db", "Database Files (*.db)")

        # Mock user confirming restore
        mock_question.return_value = QMessageBox.Yes

        # Mock successful restore
        self.mock_persistence.restore_data.return_value = True
        self.mock_persistence.load_data.return_value = self.mock_data

        # Test restore
        view._restore_backup()

        # Verify restore was called
        self.mock_persistence.restore_data.assert_called_once_with("/path/to/backup.db")
        self.mock_persistence.load_data.assert_called_once()

if __name__ == "__main__":
    unittest.main()

