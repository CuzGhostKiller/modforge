

"""Main entry point for ModForge Game Mod Manager."""

import sys
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
from PySide6.QtCore import QStandardPaths

from .models import ModForgeData
from .core.persistence import PersistenceManager
from .core.mod_manager import ModManager
from .core.profile_manager import ProfileManager
from .core.load_order import LoadOrderManager
from .gui.main_window import MainWindow

class ModForgeApplication:
    """Main application class that ties everything together."""

    def __init__(self):
        """Initialize the application."""
        self.app = QApplication(sys.argv)
        self.app.setApplicationName("ModForge Game Mod Manager")
        self.app.setOrganizationName("ModForge")
        self.app.setOrganizationDomain("modforge.app")

        # Set application icon
        try:
            icon = QIcon.fromTheme("application-x-executable")
            if not icon.isNull():
                self.app.setWindowIcon(icon)
        except:
            pass

        # Initialize data and managers
        self.data = ModForgeData()
        self.persistence = PersistenceManager()
        self.mod_manager = ModManager(self.data)
        self.profile_manager = ProfileManager(self.data)
        self.load_order_manager = LoadOrderManager(self.data)

        # Load existing data
        self._load_data()

        # Create default profile if none exists
        self._ensure_default_profile()

        # Create main window
        self.main_window = MainWindow(
            self.data,
            self.mod_manager,
            self.profile_manager,
            self.load_order_manager,
            self.persistence
        )

    def _load_data(self):
        """Load application data from persistence."""
        loaded_data = self.persistence.load_data()
        if loaded_data:
            self.data = loaded_data

    def _ensure_default_profile(self):
        """Ensure there's at least one profile."""
        if not self.data.profiles:
            # Create default profile
            default_profile = self.profile_manager.create_profile("Default")
            self.data.set_current_profile(default_profile.id)

    def run(self):
        """Run the application."""
        self.main_window.show()
        return self.app.exec()

def main():
    """Main entry point."""
    try:
        app = ModForgeApplication()
        return app.run()
    except Exception as e:
        print(f"Fatal error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())

