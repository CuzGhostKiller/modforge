

"""Test headless mode functionality."""

import unittest
import tempfile
import os
from unittest.mock import patch, MagicMock
from datetime import datetime

from modforge.models import ModForgeData, Settings, Mod, Profile

class TestHeadlessMode(unittest.TestCase):
    """Test headless mode functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.data = ModForgeData()
        self.data.settings = Settings()

        # Create test data
        mod1 = Mod(id="mod1", name="Test Mod 1", source_path="/test/path1")
        mod2 = Mod(id="mod2", name="Test Mod 2", source_path="/test/path2")
        self.data.add_mod(mod1)
        self.data.add_mod(mod2)

        profile = Profile(id="profile1", name="Test Profile")
        profile.enabled_mods = ["mod1", "mod2"]
        profile.load_order = ["mod1", "mod2"]
        self.data.add_profile(profile)
        self.data.set_current_profile("profile1")

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_headless_mode_basic(self):
        """Test basic headless mode functionality."""
        app = ModForgeApplication(headless=True)
        app.data = self.data

        # Mock the persistence to avoid file operations
        with patch.object(app.persistence, 'save_data', return_value=True):
            result = app.run()
            self.assertEqual(result, 0)

    def test_headless_mode_output(self):
        """Test that headless mode produces expected output."""
        app = ModForgeApplication(headless=True)
        app.data = self.data

        # Capture print output
        with patch('builtins.print') as mock_print:
            result = app.run()
            self.assertEqual(result, 0)

            # Check that expected messages were printed
            print_calls = [call[0][0] for call in mock_print.call_args_list]
            self.assertIn("Running in headless mode", print_calls)
            self.assertIn("Current profile: Test Profile", print_calls)
            self.assertIn("Total mods: 2", print_calls)
            self.assertIn("Total profiles: 1", print_calls)

    def test_settings_model_updates(self):
        """Test that new settings fields are properly initialized."""
        settings = Settings()
        self.assertEqual(settings.game_directory, "")
        self.assertEqual(settings.headless_mode, False)

        settings.game_directory = "/test/game"
        settings.headless_mode = True
        self.assertEqual(settings.game_directory, "/test/game")
        self.assertEqual(settings.headless_mode, True)

    def test_command_line_arguments(self):
        """Test command line argument parsing."""
        with patch('sys.argv', ['modforge', '--headless']):
            from modforge.main import main
            with patch('modforge.main.ModForgeApplication') as mock_app:
                mock_instance = mock_app.return_value
                mock_instance.run.return_value = 0
                result = main()
                self.assertEqual(result, 0)
                mock_app.assert_called_once_with(headless=True)

        with patch('sys.argv', ['modforge', '--game-dir', '/test/game']):
            from modforge.main import main
            with patch('modforge.main.ModForgeApplication') as mock_app:
                mock_instance = mock_app.return_value
                mock_instance.run.return_value = 0
                mock_instance.data = self.data
                mock_instance.persistence = MagicMock()
                result = main()
                self.assertEqual(result, 0)
                self.assertEqual(self.data.settings.game_directory, "/test/game")

if __name__ == '__main__':
    unittest.main()
