
"""Test settings enhancements."""

import unittest
from modforge.models import Settings

class TestSettingsEnhancements(unittest.TestCase):
    """Test new settings fields."""

    def test_settings_initialization(self):
        """Test that new settings fields are properly initialized."""
        settings = Settings()
        self.assertEqual(settings.game_directory, "")
        self.assertEqual(settings.headless_mode, False)
        self.assertIsNotNone(settings.updated_at)

    def test_settings_updates(self):
        """Test that settings can be updated."""
        settings = Settings()

        # Test game directory
        settings.game_directory = "/test/game/directory"
        self.assertEqual(settings.game_directory, "/test/game/directory")

        # Test headless mode
        settings.headless_mode = True
        self.assertEqual(settings.headless_mode, True)

        # Test updated_at is updated
        import time
        old_time = settings.updated_at
        time.sleep(0.01)  # Small delay to ensure time difference
        settings.updated_at = "2023-01-01 00:00:00"
        self.assertEqual(settings.updated_at, "2023-01-01 00:00:00")

    def test_settings_string_representation(self):
        """Test string representation of settings."""
        settings = Settings()
        settings.game_directory = "/test/game"
        settings.headless_mode = True

        # Just verify it doesn't crash
        str_repr = str(settings)
        self.assertTrue(len(str_repr) > 0)

if __name__ == '__main__':
    unittest.main()
