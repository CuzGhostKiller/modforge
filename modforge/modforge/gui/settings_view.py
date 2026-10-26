

"""Settings view for ModForge Game Mod Manager."""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                              QLineEdit, QPushButton, QFileDialog, QMessageBox,
                              QGroupBox, QInputDialog)
from PySide6.QtCore import Qt, Signal, Slot
from datetime import datetime

class SettingsView(QWidget):
    """View for managing application settings."""

    settings_changed = Signal()

    def __init__(self, data, persistence):
        super().__init__()
        self.data = data
        self.persistence = persistence

        self._setup_ui()
        self._connect_signals()
        self._load_settings()

    def _setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout()

        # General settings
        general_group = QGroupBox("General Settings")
        general_layout = QVBoxLayout()

        # Default mod library
        library_layout = QHBoxLayout()
        library_layout.addWidget(QLabel("Default Mod Library:"))
        self.library_path_input = QLineEdit()
        self.library_path_input.setReadOnly(True)
        library_layout.addWidget(self.library_path_input)

        browse_button = QPushButton("Browse...")
        library_layout.addWidget(browse_button)
        general_layout.addLayout(library_layout)

        general_group.setLayout(general_layout)
        layout.addWidget(general_group)

        # Data management
        data_group = QGroupBox("Data Management")
        data_layout = QVBoxLayout()

        self.backup_button = QPushButton("Create Backup")
        self.restore_button = QPushButton("Restore from Backup")
        self.data_dir_label = QLabel()

        data_layout.addWidget(self.backup_button)
        data_layout.addWidget(self.restore_button)
        data_layout.addWidget(self.data_dir_label)

        data_group.setLayout(data_layout)
        layout.addWidget(data_group)

        # Save button
        self.save_button = QPushButton("Save Settings")
        layout.addWidget(self.save_button)

        self.setLayout(layout)

    def _connect_signals(self):
        """Connect signals and slots."""
        self.save_button.clicked.connect(self._save_settings)
        self.backup_button.clicked.connect(self._create_backup)
        self.restore_button.clicked.connect(self._restore_backup)

    @Slot()
    def _load_settings(self):
        """Load current settings into the UI."""
        self.library_path_input.setText(self.data.settings.default_mod_library)
        self.data_dir_label.setText(f"Data directory: {self.persistence.get_data_directory()}")

    @Slot()
    def _save_settings(self):
        """Save settings from the UI."""
        self.data.settings.default_mod_library = self.library_path_input.text()
        self.data.settings.updated_at = datetime.now()

        success = self.persistence.save_data(self.data)
        if success:
            self._show_message("Settings saved successfully!")
            self.settings_changed.emit()
        else:
            self._show_message("Error saving settings", is_error=True)

    @Slot()
    def _create_backup(self):
        """Create a backup of the application data."""
        backup_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Backup",
            f"modforge_backup_{datetime.now().strftime('%Y%m%d')}.db",
            "Database Files (*.db)"
        )

        if backup_path:
            success = self.persistence.backup_data(backup_path)
            if success:
                self._show_message("Backup created successfully!")
            else:
                self._show_message("Error creating backup", is_error=True)

    @Slot()
    def _restore_backup(self):
        """Restore data from a backup."""
        backup_path, _ = QFileDialog.getOpenFileName(
            self,
            "Restore Backup",
            "",
            "Database Files (*.db)"
        )

        if backup_path:
            reply = QMessageBox.question(
                self,
                "Confirm Restore",
                "Restoring will overwrite your current data. Are you sure?",
                QMessageBox.Yes | QMessageBox.No
            )

            if reply == QMessageBox.Yes:
                success = self.persistence.restore_data(backup_path)
                if success:
                    # Reload data
                    loaded_data = self.persistence.load_data()
                    if loaded_data:
                        self.data = loaded_data
                        self._show_message("Data restored successfully!")
                        self.settings_changed.emit()
                    else:
                        self._show_message("Error loading restored data", is_error=True)
                else:
                    self._show_message("Error restoring backup", is_error=True)

    def _show_message(self, message: str, is_error: bool = False):
        """Show a message to the user."""
        if is_error:
            QMessageBox.critical(self, "Error", message)
        else:
            QMessageBox.information(self, "Success", message)

