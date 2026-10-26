

"""Tests for the profile manager module."""

import unittest
from modforge.models import ModForgeData, Profile, Mod
from modforge.core.profile_manager import ProfileManager

class TestProfileManager(unittest.TestCase):
    """Test cases for the ProfileManager class."""

    def setUp(self):
        """Set up test fixtures."""
        self.data = ModForgeData()
        self.profile_manager = ProfileManager(self.data)

        # Add some mods for testing
        mod1 = Mod(id="mod1", name="Mod 1", source_path="/path1")
        mod2 = Mod(id="mod2", name="Mod 2", source_path="/path2")
        mod3 = Mod(id="mod3", name="Mod 3", source_path="/path3")

        self.data.add_mod(mod1)
        self.data.add_mod(mod2)
        self.data.add_mod(mod3)

    def test_create_profile(self):
        """Test creating a new profile."""
        profile = self.profile_manager.create_profile("Test Profile")

        self.assertIsNotNone(profile)
        self.assertEqual(profile.name, "Test Profile")
        self.assertIn(profile.id, self.data.profiles)
        self.assertEqual(self.data.current_profile_id, profile.id)

    def test_create_duplicate_profile_name(self):
        """Test creating a profile with duplicate name."""
        profile1 = self.profile_manager.create_profile("Test Profile")

        with self.assertRaises(ValueError):
            self.profile_manager.create_profile("Test Profile")

    def test_duplicate_profile(self):
        """Test duplicating a profile."""
        # Create original profile
        profile1 = self.profile_manager.create_profile("Original")
        self.profile_manager.update_current_profile_mods({"mod1": True, "mod2": True})

        # Duplicate it
        profile2 = self.profile_manager.duplicate_profile(profile1.id, "Copy")

        self.assertIsNotNone(profile2)
        self.assertEqual(profile2.name, "Copy")
        self.assertEqual(profile2.enabled_mods, ["mod1", "mod2"])
        self.assertIn(profile2.id, self.data.profiles)

    def test_rename_profile(self):
        """Test renaming a profile."""
        profile = self.profile_manager.create_profile("Original")

        success = self.profile_manager.rename_profile(profile.id, "Renamed")
        self.assertTrue(success)
        self.assertEqual(self.data.profiles[profile.id].name, "Renamed")

    def test_rename_to_existing_name(self):
        """Test renaming to an existing profile name."""
        profile1 = self.profile_manager.create_profile("Profile 1")
        profile2 = self.profile_manager.create_profile("Profile 2")

        success = self.profile_manager.rename_profile(profile1.id, "Profile 2")
        self.assertFalse(success)

    def test_delete_profile(self):
        """Test deleting a profile."""
        profile1 = self.profile_manager.create_profile("Test Profile 1")
        profile2 = self.profile_manager.create_profile("Test Profile 2")

        # Switch to profile2 so we can delete profile1
        success = self.profile_manager.switch_profile(profile2.id)
        self.assertTrue(success)

        # Now delete profile1
        success = self.profile_manager.delete_profile(profile1.id)
        self.assertTrue(success)
        self.assertNotIn(profile1.id, self.data.profiles)

    def test_delete_current_profile(self):
        """Test deleting the current profile."""
        profile = self.profile_manager.create_profile("Test Profile")
        self.data.set_current_profile(profile.id)

        success = self.profile_manager.delete_profile(profile.id)
        self.assertFalse(success)
        self.assertIn(profile.id, self.data.profiles)

    def test_switch_profile(self):
        """Test switching profiles."""
        profile1 = self.profile_manager.create_profile("Profile 1")
        profile2 = self.profile_manager.create_profile("Profile 2")

        success = self.profile_manager.switch_profile(profile2.id)
        self.assertTrue(success)
        self.assertEqual(self.data.current_profile_id, profile2.id)

    def test_switch_to_nonexistent_profile(self):
        """Test switching to a nonexistent profile."""
        success = self.profile_manager.switch_profile("nonexistent")
        self.assertFalse(success)

    def test_enable_disable_mods(self):
        """Test enabling and disabling mods in current profile."""
        profile = self.profile_manager.create_profile("Test Profile")

        # Enable mods
        success = self.profile_manager.update_current_profile_mods({"mod1": True, "mod2": True})
        self.assertTrue(success)
        self.assertIn("mod1", profile.enabled_mods)
        self.assertIn("mod2", profile.enabled_mods)

        # Disable mod
        success = self.profile_manager.update_current_profile_mods({"mod1": False, "mod2": True})
        self.assertTrue(success)
        self.assertNotIn("mod1", profile.enabled_mods)

    def test_get_current_profile_mods(self):
        """Test getting current profile mod states."""
        profile = self.profile_manager.create_profile("Test Profile")
        self.profile_manager.update_current_profile_mods({"mod1": True, "mod3": True})

        mod_states = self.profile_manager.get_current_profile_mods()

        # The method returns all mods, not just the ones explicitly set
        self.assertEqual(len(mod_states), 3)  # mod1, mod2, mod3
        self.assertTrue(mod_states["mod1"])
        self.assertTrue(mod_states["mod3"])
        self.assertFalse(mod_states["mod2"])

    def test_update_current_profile_mods(self):
        """Test updating current profile mod states."""
        profile = self.profile_manager.create_profile("Test Profile")

        new_states = {
            "mod1": True,
            "mod2": False,
            "mod3": True
        }

        success = self.profile_manager.update_current_profile_mods(new_states)
        self.assertTrue(success)
        self.assertEqual(profile.enabled_mods, ["mod1", "mod3"])

    def test_get_load_order(self):
        """Test getting load order."""
        profile = self.profile_manager.create_profile("Test Profile")
        profile.update_load_order(["mod1", "mod2", "mod3"])

        load_order = self.profile_manager.get_load_order()
        self.assertEqual(load_order, ["mod1", "mod2", "mod3"])

    def test_set_load_order(self):
        """Test setting load order."""
        profile = self.profile_manager.create_profile("Test Profile")

        success = self.profile_manager.set_load_order(["mod2", "mod1", "mod3"])
        self.assertTrue(success)
        self.assertEqual(profile.load_order, ["mod2", "mod1", "mod3"])

    def test_set_invalid_load_order(self):
        """Test setting invalid load order."""
        profile = self.profile_manager.create_profile("Test Profile")

        # Try to set load order with nonexistent mod
        success = self.profile_manager.set_load_order(["mod1", "nonexistent"])
        self.assertFalse(success)

    def test_move_mod_in_load_order(self):
        """Test moving mod in load order."""
        profile = self.profile_manager.create_profile("Test Profile")
        profile.update_load_order(["mod1", "mod2", "mod3"])

        # Move mod2 up
        success = self.profile_manager.move_mod_in_load_order("mod2", "up")
        self.assertTrue(success)
        self.assertEqual(profile.load_order, ["mod2", "mod1", "mod3"])

        # Move mod1 down
        success = self.profile_manager.move_mod_in_load_order("mod1", "down")
        self.assertTrue(success)
        self.assertEqual(profile.load_order, ["mod2", "mod3", "mod1"])

    def test_get_profile_summary(self):
        """Test getting profile summary."""
        profile = self.profile_manager.create_profile("Test Profile")
        self.profile_manager.update_current_profile_mods({"mod1": True, "mod2": True})
        profile.update_load_order(["mod1", "mod2"])

        summary = self.profile_manager.get_profile_summary(profile.id)

        self.assertEqual(summary["id"], profile.id)
        self.assertEqual(summary["name"], "Test Profile")
        self.assertEqual(summary["enabled_mods_count"], 2)
        self.assertEqual(summary["total_mods_count"], 3)
        self.assertEqual(summary["load_order_count"], 2)
        self.assertTrue(summary["is_current"])

if __name__ == "__main__":
    unittest.main()

