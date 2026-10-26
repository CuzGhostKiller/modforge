

"""Widget components for ModForge Game Mod Manager."""

from PySide6.QtWidgets import (QWidget, QHBoxLayout, QPushButton, QLabel)
from PySide6.QtCore import Signal

class ToolbarWidget(QWidget):
    """Toolbar widget for the main window."""

    import_mod_requested = Signal()
    refresh_library_requested = Signal()
    save_requested = Signal()

    def __init__(self, parent):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        """Set up the toolbar layout."""
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        # Import mod button
        self.import_button = QPushButton("Import Mod")
        self.import_button.clicked.connect(self.import_mod_requested.emit)

        # Refresh library button
        self.refresh_button = QPushButton("Refresh Library")
        self.refresh_button.clicked.connect(self.refresh_library_requested.emit)

        # Save button
        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.save_requested.emit)

        layout.addWidget(self.import_button)
        layout.addWidget(self.refresh_button)
        layout.addWidget(self.save_button)

        self.setLayout(layout)

class StatusWidget(QWidget):
    """Status widget for displaying information."""

    def __init__(self, parent):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        """Set up the status widget layout."""
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        self.status_label = QLabel("Ready")
        layout.addWidget(self.status_label)

        self.setLayout(layout)

    def set_status(self, message: str):
        """Set the status message."""
        self.status_label.setText(message)

