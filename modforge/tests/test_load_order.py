

"""Tests for the load order manager module."""

import unittest
from modforge.models import ModForgeData, Profile, Mod
from modforge.core.load_order import LoadOrderManager

class TestLoadOrderManager(unittest.TestCase):
    """Test cases for the LoadOrderManager class."""

    def setUp(self):
        """Set up test fixtures."""
        self.data = ModForgeData()
        self.load_order_manager = LoadOrderManager(self.data)

        # Add some mods for testing
        mod1 = Mod(id="mod1", name="Mod 1", source_path="/path1")
        mod2 = Mod(id="mod2", name="Mod 2", source_path="/path2")
        mod3 = Mod(id="mod3", name="Mod 3", source_path="/path3")
        mod4 = Mod(id="mod4", name="Mod 4", source_path="/path4")

        self.data.add_mod(mod1)
        self.data.add_mod(mod2)
        self.data.add_mod(mod3)
        self.data.add_mod(mod4)

        # Create a profile and enable all mods
        profile = Profile(id="profile1", name="Test Profile")
        profile.enabled_mods = ["mod1", "mod2", "mod3", "mod4"]
        profile.load_order = ["mod1", "mod2", "mod3", "mod4"]
        self.data.add_profile(profile)
        self.data.set_current_profile("profile1")

    def test_get_current_load_order(self):
        """Test getting current load order."""
        load_order = self.load_order_manager.get_current_load_order()
        self.assertEqual(load_order, ["mod1", "mod2", "mod3", "mod4"])

    def test_set_current_load_order(self):
        """Test setting current load order."""
        new_order = ["mod2", "mod1", "mod3", "mod4"]
        success = self.load_order_manager.set_current_load_order(new_order)

        self.assertTrue(success)
        current_profile = self.data.get_current_profile()
        self.assertEqual(current_profile.load_order, new_order)

    def test_set_invalid_load_order(self):
        """Test setting invalid load order."""
        # Try with nonexistent mod
        invalid_order = ["mod1", "nonexistent", "mod3"]
        success = self.load_order_manager.set_current_load_order(invalid_order)
        self.assertFalse(success)

        # Try with disabled mod
        current_profile = self.data.get_current_profile()
        current_profile.enabled_mods = ["mod1", "mod2", "mod4"]  # Remove mod3
        invalid_order = ["mod1", "mod3", "mod4"]
        success = self.load_order_manager.set_current_load_order(invalid_order)
        self.assertFalse(success)

    def test_move_mod_up(self):
        """Test moving mod up in load order."""
        success = self.load_order_manager.move_mod_up("mod2")
        self.assertTrue(success)

        current_profile = self.data.get_current_profile()
        self.assertEqual(current_profile.load_order, ["mod2", "mod1", "mod3", "mod4"])

    def test_move_mod_down(self):
        """Test moving mod down in load order."""
        success = self.load_order_manager.move_mod_down("mod2")
        self.assertTrue(success)

        current_profile = self.data.get_current_profile()
        self.assertEqual(current_profile.load_order, ["mod1", "mod3", "mod2", "mod4"])

    def test_move_mod_at_boundaries(self):
        """Test moving mod at boundaries."""
        # Try to move first mod up
        success = self.load_order_manager.move_mod_up("mod1")
        self.assertFalse(success)

        # Try to move last mod down
        success = self.load_order_manager.move_mod_down("mod4")
        self.assertFalse(success)

    def test_add_mod_to_load_order(self):
        """Test adding mod to load order."""
        # Remove mod4 from load order first
        current_profile = self.data.get_current_profile()
        current_profile.load_order = ["mod1", "mod2", "mod3"]

        # Add mod4 at end
        success = self.load_order_manager.add_mod_to_load_order("mod4")
        self.assertTrue(success)
        self.assertEqual(current_profile.load_order, ["mod1", "mod2", "mod3", "mod4"])

        # Add mod4 at position 1
        current_profile.load_order = ["mod1", "mod2", "mod3"]
        success = self.load_order_manager.add_mod_to_load_order("mod4", 1)
        self.assertTrue(success)
        self.assertEqual(current_profile.load_order, ["mod1", "mod4", "mod2", "mod3"])

    def test_add_invalid_mod_to_load_order(self):
        """Test adding invalid mod to load order."""
        # Try to add nonexistent mod
        success = self.load_order_manager.add_mod_to_load_order("nonexistent")
        self.assertFalse(success)

        # Try to add disabled mod
        current_profile = self.data.get_current_profile()
        current_profile.enabled_mods = ["mod1", "mod2", "mod3"]  # Disable mod4
        success = self.load_order_manager.add_mod_to_load_order("mod4")
        self.assertFalse(success)

    def test_remove_mod_from_load_order(self):
        """Test removing mod from load order."""
        success = self.load_order_manager.remove_mod_from_load_order("mod2")
        self.assertTrue(success)

        current_profile = self.data.get_current_profile()
        self.assertEqual(current_profile.load_order, ["mod1", "mod3", "mod4"])

    def test_remove_nonexistent_mod_from_load_order(self):
        """Test removing nonexistent mod from load order."""
        success = self.load_order_manager.remove_mod_from_load_order("nonexistent")
        self.assertFalse(success)

    def test_get_load_order_validation(self):
        """Test load order validation."""
        # Valid load order
        errors = self.load_order_manager.get_load_order_validation()
        self.assertEqual(len(errors), 0)

        # Add missing mod to load order
        current_profile = self.data.get_current_profile()
        current_profile.load_order = ["mod1", "nonexistent", "mod3"]
        errors = self.load_order_manager.get_load_order_validation()
        self.assertEqual(len(errors), 2)
        self.assertIn("missing mods", errors[0])

        # Add disabled mod to load order
        current_profile.load_order = ["mod1", "mod2", "mod3"]
        current_profile.enabled_mods = ["mod1", "mod2"]  # Disable mod3
        errors = self.load_order_manager.get_load_order_validation()
        self.assertEqual(len(errors), 1)
        self.assertIn("disabled mods", errors[0])

        # Add duplicate to load order
        current_profile.load_order = ["mod1", "mod2", "mod2", "mod3"]
        current_profile.enabled_mods = ["mod1", "mod2", "mod3"]
        errors = self.load_order_manager.get_load_order_validation()
        self.assertEqual(len(errors), 1)
        self.assertIn("duplicate", errors[0])

    def test_get_load_order_summary(self):
        """Test getting load order summary."""
        summary = self.load_order_manager.get_load_order_summary()

        self.assertEqual(summary["total_mods"], 4)
        self.assertEqual(summary["enabled_mods"], 4)
        self.assertEqual(summary["in_load_order"], 4)
        self.assertEqual(len(summary["validation_errors"]), 0)

if __name__ == "__main__":
    unittest.main()

