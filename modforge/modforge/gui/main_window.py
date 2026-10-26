

"""Main window for ModForge Game Mod Manager."""

from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                              QTabWidget, QSplitter, QMessageBox, QStatusBar)
from PySide6.QtCore import Qt, Slot

from .mod_list_view import ModListView
from .profile_view import ProfileView
from .settings_view import SettingsView
from .widgets import ToolbarWidget

class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self, data, mod_manager, profile_manager, load_order_manager, persistence):
        super().__init__()
        self.data = data
        self.mod_manager = mod_manager
        self.profile_manager = profile_manager
        self.load_order_manager = load_order_manager
        self.persistence = persistence

        self.setWindowTitle("ModForge Game Mod Manager")
        self.setMinimumSize(1024, 768)

        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Create toolbar
        self.toolbar = ToolbarWidget(self)
        main_layout.addWidget(self.toolbar)

        # Create main content area with tabs
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)

        # Create mod library tab
        self.mod_list_view = ModListView(
            self.data,
            self.mod_manager,
            self.profile_manager,
            self.load_order_manager
        )
        self.tabs.addTab(self.mod_list_view, "Mod Library")

        # Create profile management tab
        self.profile_view = ProfileView(
            self.data,
            self.profile_manager,
            self.load_order_manager
        )
        self.tabs.addTab(self.profile_view, "Profiles")

        # Create settings tab
        self.settings_view = SettingsView(
            self.data,
            self.persistence
        )
        self.tabs.addTab(self.settings_view, "Settings")

        # Create status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        # Connect signals
        self._connect_signals()

        # Initial update
        self._update_ui_state()

    def _connect_signals(self):
        """Connect signals and slots."""
        # Connect toolbar signals
        self.toolbar.import_mod_requested.connect(self._handle_import_mod)
        self.toolbar.refresh_library_requested.connect(self._refresh_library)
        self.toolbar.save_requested.connect(self._save_data)

        # Connect mod list view signals
        self.mod_list_view.mod_enabled_changed.connect(self._update_status)
        self.mod_list_view.mod_disabled_changed.connect(self._update_status)

        # Connect profile view signals
        self.profile_view.profile_changed.connect(self._update_status)

    @Slot()
    def _handle_import_mod(self):
        """Handle import mod request from toolbar."""
        self.mod_list_view.import_mod()

    @Slot()
    def _refresh_library(self):
        """Refresh the mod library."""
        self.mod_list_view.refresh_library()
        self._update_status("Library refreshed")

    @Slot()
    def _save_data(self):
        """Save application data."""
        success = self.persistence.save_data(self.data)
        if success:
            self._update_status("Data saved successfully")
        else:
            self._update_status("Error saving data", is_error=True)

    def _update_ui_state(self):
        """Update the UI state based on current data."""
        # Update mod list view
        self.mod_list_view.update_mod_list()

        # Update profile view
        self.profile_view.update_profile_list()

        # Update status bar
        current_profile = self.data.get_current_profile()
        if current_profile:
            self.status_bar.showMessage(f"Current profile: {current_profile.name}")
        else:
            self.status_bar.showMessage("No profile selected")

    def _update_status(self, message: str, is_error: bool = False):
        """Update the status bar with a message."""
        if is_error:
            self.status_bar.showMessage(f"Error: {message}", 5000)
        else:
            self.status_bar.showMessage(message, 3000)

    def closeEvent(self, event):
        """Handle window close event."""
        # Save data before closing
        self.persistence.save_data(self.data)
        event.accept()

