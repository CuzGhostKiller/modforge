

"""Profile view for ModForge Game Mod Manager."""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QListWidget,
                              QListWidgetItem, QPushButton, QLineEdit, QMessageBox,
                              QGroupBox, QLabel)
from PySide6.QtCore import Qt, Signal, Slot

class ProfileView(QWidget):
    """View for managing mod profiles."""

    profile_changed = Signal()

    def __init__(self, data, profile_manager, load_order_manager):
        super().__init__()
        self.data = data
        self.profile_manager = profile_manager
        self.load_order_manager = load_order_manager

        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout()

        # Profile list
        self.profile_list = QListWidget()
        self.profile_list.setSelectionMode(QListWidget.SingleSelection)
        layout.addWidget(self.profile_list)

        # Profile details panel
        self.details_panel = QGroupBox("Profile Details")
        details_layout = QVBoxLayout()

        self.profile_name_label = QLabel("No profile selected")
        self.profile_name_label.setStyleSheet("font-weight: bold; font-size: 16px;")

        self.profile_mods_label = QLabel("Enabled mods: 0")
        self.profile_load_order_label = QLabel("Load order: 0 mods")

        details_layout.addWidget(self.profile_name_label)
        details_layout.addWidget(self.profile_mods_label)
        details_layout.addWidget(self.profile_load_order_label)

        self.details_panel.setLayout(details_layout)
        layout.addWidget(self.details_panel)

        # Action buttons
        button_layout = QHBoxLayout()

        self.new_profile_button = QPushButton("New Profile")
        self.duplicate_button = QPushButton("Duplicate")
        self.rename_button = QPushButton("Rename")
        self.delete_button = QPushButton("Delete")
        self.switch_button = QPushButton("Switch")

        button_layout.addWidget(self.new_profile_button)
        button_layout.addWidget(self.duplicate_button)
        button_layout.addWidget(self.rename_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addWidget(self.switch_button)

        layout.addLayout(button_layout)

        self.setLayout(layout)

    def _connect_signals(self):
        """Connect signals and slots."""
        self.profile_list.itemSelectionChanged.connect(self._on_profile_selected)
        self.new_profile_button.clicked.connect(self._create_new_profile)
        self.duplicate_button.clicked.connect(self._duplicate_profile)
        self.rename_button.clicked.connect(self._rename_profile)
        self.delete_button.clicked.connect(self._delete_profile)
        self.switch_button.clicked.connect(self._switch_profile)

    @Slot()
    def update_profile_list(self):
        """Update the list of profiles."""
        self.profile_list.clear()

        for profile in self.data.profiles.values():
            item = QListWidgetItem(profile.name)
            item.setData(Qt.UserRole, profile.id)

            # Highlight current profile
            if profile.id == self.data.current_profile_id:
                item.setBackground(Qt.darkGreen)
                item.setTextColor(Qt.white)

            self.profile_list.addItem(item)

    @Slot()
    def _on_profile_selected(self):
        """Handle profile selection."""
        selected_items = self.profile_list.selectedItems()
        if not selected_items:
            return

        item = selected_items[0]
        profile_id = item.data(Qt.UserRole)
        profile = self.data.profiles.get(profile_id)

        if profile:
            self._display_profile_details(profile)

    @Slot()
    def _display_profile_details(self, profile):
        """Display details for the selected profile."""
        self.profile_name_label.setText(profile.name)

        enabled_count = len(profile.enabled_mods)
        self.profile_mods_label.setText(f"Enabled mods: {enabled_count}")

        load_order_count = len(profile.load_order)
        self.profile_load_order_label.setText(f"Load order: {load_order_count} mods")

    @Slot()
    def _create_new_profile(self):
        """Create a new profile."""
        name, ok = QInputDialog.getText(
            self,
            "New Profile",
            "Enter profile name:"
        )

        if ok and name.strip():
            try:
                profile = self.profile_manager.create_profile(name)
                self.update_profile_list()
                self._show_message("Profile created successfully!")
                self.profile_changed.emit()
            except ValueError as e:
                self._show_message(str(e), is_error=True)

    @Slot()
    def _duplicate_profile(self):
        """Duplicate the selected profile."""
        selected_items = self.profile_list.selectedItems()
        if not selected_items:
            return

        item = selected_items[0]
        profile_id = item.data(Qt.UserRole)

        name, ok = QInputDialog.getText(
            self,
            "Duplicate Profile",
            "Enter name for duplicated profile:"
        )

        if ok and name.strip():
            try:
                profile = self.profile_manager.duplicate_profile(profile_id, name)
                self.update_profile_list()
                self._show_message("Profile duplicated successfully!")
                self.profile_changed.emit()
            except ValueError as e:
                self._show_message(str(e), is_error=True)

    @Slot()
    def _rename_profile(self):
        """Rename the selected profile."""
        selected_items = self.profile_list.selectedItems()
        if not selected_items:
            return

        item = selected_items[0]
        profile_id = item.data(Qt.UserRole)

        name, ok = QInputDialog.getText(
            self,
            "Rename Profile",
            "Enter new profile name:",
            text=self.data.profiles[profile_id].name
        )

        if ok and name.strip():
            success = self.profile_manager.rename_profile(profile_id, name)
            if success:
                self.update_profile_list()
                self._show_message("Profile renamed successfully!")
                self.profile_changed.emit()
            else:
                self._show_message("Error: Profile name already exists", is_error=True)

    @Slot()
    def _delete_profile(self):
        """Delete the selected profile."""
        selected_items = self.profile_list.selectedItems()
        if not selected_items:
            return

        item = selected_items[0]
        profile_id = item.data(Qt.UserRole)
        profile = self.data.profiles.get(profile_id)

        if not profile:
            return

        # Cannot delete current profile
        if profile_id == self.data.current_profile_id:
            self._show_message("Cannot delete the current profile", is_error=True)
            return

        # Confirm deletion
        reply = QMessageBox.question(
            self,
            "Confirm Deletion",
            f"Are you sure you want to delete profile '{profile.name}'?\n\n"
            f"This cannot be undone.",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.profile_manager.delete_profile(profile_id)
            self.update_profile_list()
            self._show_message("Profile deleted successfully!")
            self.profile_changed.emit()

    @Slot()
    def _switch_profile(self):
        """Switch to the selected profile."""
        selected_items = self.profile_list.selectedItems()
        if not selected_items:
            return

        item = selected_items[0]
        profile_id = item.data(Qt.UserRole)

        self.profile_manager.switch_profile(profile_id)
        self.update_profile_list()
        self._show_message("Profile switched successfully!")
        self.profile_changed.emit()

    def _show_message(self, message: str, is_error: bool = False):
        """Show a message to the user."""
        if is_error:
            QMessageBox.critical(self, "Error", message)
        else:
            QMessageBox.information(self, "Success", message)

