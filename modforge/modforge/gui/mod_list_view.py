

"""Mod list view for ModForge Game Mod Manager."""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QListWidget,
                              QListWidgetItem, QPushButton, QLineEdit, QCheckBox,
                              QLabel, QMessageBox, QFileDialog, QGroupBox)
from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtGui import QStandardItemModel, QStandardItem

from ..models import Mod, ModStatus

class ModListView(QWidget):
    """View for displaying and managing mods in the library."""

    mod_enabled_changed = Signal(str)
    mod_disabled_changed = Signal(str)
    mod_selected = Signal(str)

    def __init__(self, data, mod_manager, profile_manager, load_order_manager):
        super().__init__()
        self.data = data
        self.mod_manager = mod_manager
        self.profile_manager = profile_manager
        self.load_order_manager = load_order_manager

        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout()

        # Search and filter controls
        search_layout = QHBoxLayout()

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search mods...")
        search_layout.addWidget(self.search_input)

        self.enabled_only_checkbox = QCheckBox("Enabled only")
        search_layout.addWidget(self.enabled_only_checkbox)

        layout.addLayout(search_layout)

        # Mod list
        self.mod_list = QListWidget()
        self.mod_list.setSelectionMode(QListWidget.SingleSelection)
        layout.addWidget(self.mod_list)

        # Mod details panel
        self.details_panel = QGroupBox("Mod Details")
        details_layout = QVBoxLayout()

        self.mod_name_label = QLabel("No mod selected")
        self.mod_name_label.setStyleSheet("font-weight: bold; font-size: 16px;")

        self.mod_path_label = QLabel()
        self.mod_status_label = QLabel()

        self.mod_files_label = QLabel("Files: 0")
        self.mod_enabled_checkbox = QCheckBox("Enabled")

        details_layout.addWidget(self.mod_name_label)
        details_layout.addWidget(self.mod_path_label)
        details_layout.addWidget(self.mod_status_label)
        details_layout.addWidget(self.mod_files_label)
        details_layout.addWidget(self.mod_enabled_checkbox)

        self.details_panel.setLayout(details_layout)
        layout.addWidget(self.details_panel)

        # Action buttons
        button_layout = QHBoxLayout()

        self.import_button = QPushButton("Import Mod")
        self.refresh_button = QPushButton("Refresh")
        self.remove_button = QPushButton("Remove")

        button_layout.addWidget(self.import_button)
        button_layout.addWidget(self.refresh_button)
        button_layout.addWidget(self.remove_button)

        layout.addLayout(button_layout)

        self.setLayout(layout)

    def _connect_signals(self):
        """Connect signals and slots."""
        self.search_input.textChanged.connect(self._filter_mods)
        self.enabled_only_checkbox.stateChanged.connect(self._filter_mods)
        self.mod_list.itemSelectionChanged.connect(self._on_mod_selected)
        self.mod_enabled_checkbox.stateChanged.connect(self._toggle_mod_enabled)
        self.import_button.clicked.connect(self.import_mod)
        self.refresh_button.clicked.connect(self._refresh_selected_mod)
        self.remove_button.clicked.connect(self._remove_selected_mod)

    @Slot()
    def import_mod(self):
        """Import a new mod from a folder."""
        folder_path = QFileDialog.getExistingDirectory(
            self,
            "Select Mod Folder",
            self.data.settings.default_mod_library
        )

        if folder_path:
            mod, error = self.mod_manager.discover_mod(folder_path)
            if mod:
                success = self.mod_manager.add_mod_to_library(mod)
                if success:
                    self.update_mod_list()
                    self._show_message("Mod imported successfully!")
                else:
                    self._show_message("Error: Mod already exists in library", is_error=True)
            else:
                self._show_message(f"Error: {error}", is_error=True)

    @Slot()
    def update_mod_list(self):
        """Update the list of mods."""
        self.mod_list.clear()

        # Get current profile mod states
        profile_mod_states = self.profile_manager.get_current_profile_mods()

        for mod in self.data.mods.values():
            item = QListWidgetItem(mod.name)
            item.setData(Qt.UserRole, mod.id)

            # Set checkbox state based on profile
            is_enabled = profile_mod_states.get(mod.id, False)
            item.setCheckState(Qt.Checked if is_enabled else Qt.Unchecked)

            self.mod_list.addItem(item)

        self._filter_mods()

    @Slot()
    def _filter_mods(self):
        """Filter mods based on search and filter criteria."""
        search_text = self.search_input.text().lower()
        enabled_only = self.enabled_only_checkbox.isChecked()

        profile_mod_states = self.profile_manager.get_current_profile_mods()

        for i in range(self.mod_list.count()):
            item = self.mod_list.item(i)
            mod_id = item.data(Qt.UserRole)
            mod = self.data.mods.get(mod_id)

            if not mod:
                continue

            # Check search filter
            matches_search = search_text in mod.name.lower()
            # Check enabled filter
            matches_enabled = not enabled_only or profile_mod_states.get(mod.id, False)

            item.setHidden(not (matches_search and matches_enabled))

    @Slot()
    def _on_mod_selected(self):
        """Handle mod selection."""
        selected_items = self.mod_list.selectedItems()
        if not selected_items:
            return

        item = selected_items[0]
        mod_id = item.data(Qt.UserRole)
        mod = self.data.mods.get(mod_id)

        if mod:
            self._display_mod_details(mod)
            self.mod_selected.emit(mod_id)

    @Slot()
    def _display_mod_details(self, mod: Mod):
        """Display details for the selected mod."""
        self.mod_name_label.setText(mod.name)
        self.mod_path_label.setText(f"Path: {mod.source_path}")
        self.mod_status_label.setText(f"Status: {mod.status.value}")

        file_count = len(mod.detected_files)
        self.mod_files_label.setText(f"Files: {file_count}")

        # Get current profile state
        profile_mod_states = self.profile_manager.get_current_profile_mods()
        is_enabled = profile_mod_states.get(mod.id, False)
        self.mod_enabled_checkbox.setChecked(is_enabled)

    @Slot()
    def _toggle_mod_enabled(self, state):
        """Toggle mod enabled/disabled state."""
        selected_items = self.mod_list.selectedItems()
        if not selected_items:
            return

        item = selected_items[0]
        mod_id = item.data(Qt.UserRole)

        if state == Qt.Checked:
            self.mod_manager.enable_mod(mod_id)
            self.mod_enabled_changed.emit(mod_id)
        else:
            self.mod_manager.disable_mod(mod_id)
            self.mod_disabled_changed.emit(mod_id)

        # Update the checkbox state in the list
        item.setCheckState(Qt.Checked if state == Qt.Checked else Qt.Unchecked)

        # Update profile state
        profile_mod_states = self.profile_manager.get_current_profile_mods()
        profile_mod_states[mod_id] = (state == Qt.Checked)
        self.profile_manager.update_current_profile_mods(profile_mod_states)

    @Slot()
    def _refresh_selected_mod(self):
        """Refresh information for the selected mod."""
        selected_items = self.mod_list.selectedItems()
        if not selected_items:
            return

        item = selected_items[0]
        mod_id = item.data(Qt.UserRole)

        success, message = self.mod_manager.refresh_mod_info(mod_id)
        if success:
            self._show_message("Mod refreshed successfully!")
            self.update_mod_list()
        else:
            self._show_message(f"Error: {message}", is_error=True)

    @Slot()
    def _remove_selected_mod(self):
        """Remove the selected mod from the library."""
        selected_items = self.mod_list.selectedItems()
        if not selected_items:
            return

        item = selected_items[0]
        mod_id = item.data(Qt.UserRole)
        mod = self.data.mods.get(mod_id)

        if not mod:
            return

        # Confirm removal
        reply = QMessageBox.question(
            self,
            "Confirm Removal",
            f"Are you sure you want to remove '{mod.name}' from the library?\n\n"
            f"This will not delete the mod files, only remove it from your library.",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.mod_manager.remove_mod_from_library(mod_id)
            self.update_mod_list()
            self._show_message("Mod removed from library")

    @Slot()
    def refresh_library(self):
        """Refresh the entire mod library."""
        for mod in self.data.mods.values():
            self.mod_manager.refresh_mod_info(mod.id)

        self.update_mod_list()
        self._show_message("Library refreshed")

    def _show_message(self, message: str, is_error: bool = False):
        """Show a message to the user."""
        if is_error:
            QMessageBox.critical(self, "Error", message)
        else:
            QMessageBox.information(self, "Success", message)


