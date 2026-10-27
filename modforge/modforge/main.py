

"""Main entry point for ModForge Game Mod Manager."""

import sys
import os
import argparse
from datetime import datetime
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

    def __init__(self, headless=False):
        """Initialize the application."""
        self.headless = headless
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
        if self.headless:
            print("Running in headless mode")
            # In headless mode, we could add command-line operations here
            # For now, just show basic info
            print(f"Current profile: {self.data.get_current_profile().name if self.data.get_current_profile() else 'None'}")
            print(f"Total mods: {len(self.data.mods)}")
            print(f"Total profiles: {len(self.data.profiles)}")
            return 0
        else:
            self.main_window.show()
            return self.app.exec()

def main():
    """Main entry point."""
    try:
        # Parse command line arguments
        parser = argparse.ArgumentParser(description="ModForge Game Mod Manager")
        parser.add_argument("--headless", action="store_true", help="Run in headless mode")
        parser.add_argument("--game-dir", "--game-directory", help="Set game directory")
        args = parser.parse_args()

        app = ModForgeApplication(headless=args.headless)
        if args.game_dir:
            app.data.settings.game_directory = args.game_dir
            app.data.settings.updated_at = datetime.now()
            app.persistence.save_data(app.data)
        return app.run()
    except Exception as e:
        print(f"Fatal error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())

