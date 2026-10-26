
"""Tests for the models module."""

import unittest
from datetime import datetime
from modforge.models import Mod, Profile, Settings, ModForgeData, ModStatus

class TestModels(unittest.TestCase):
    """Test cases for the models module."""

    def test_mod_creation(self):
        """Test Mod object creation."""
        mod = Mod(
            id="test-mod-1",
            name="Test Mod",
            source_path="/path/to/mod",
            status=ModStatus.ENABLED,
            detected_files=["file1.txt", "file2.txt"],
            metadata={"version": "1.0"}
        )

        self.assertEqual(mod.id, "test-mod-1")
        self.assertEqual(mod.name, "Test Mod")
        self.assertEqual(mod.source_path, "/path/to/mod")
        self.assertEqual(mod.status, ModStatus.ENABLED)
        self.assertEqual(len(mod.detected_files), 2)
        self.assertEqual(mod.metadata["version"], "1.0")
        self.assertIsNotNone(mod.created_at)
        self.assertIsNotNone(mod.updated_at)

    def test_mod_refresh_files(self):
        """Test Mod refresh_files method."""
        mod = Mod(
            id="test-mod-1",
            name="Test Mod",
            source_path="/path/to/mod",
            status=ModStatus.ENABLED,
            detected_files=["file1.txt"]
        )

        new_files = ["file1.txt", "file2.txt", "file3.txt"]
        mod.refresh_files(new_files)

        self.assertEqual(len(mod.detected_files), 3)
        self.assertEqual(mod.detected_files, new_files)

    def test_profile_creation(self):
        """Test Profile object creation."""
        profile = Profile(
            id="test-profile-1",
            name="Test Profile",
            enabled_mods=["mod1", "mod2"],
            load_order=["mod1", "mod2"]
        )

        self.assertEqual(profile.id, "test-profile-1")
        self.assertEqual(profile.name, "Test Profile")
        self.assertEqual(len(profile.enabled_mods), 2)
        self.assertEqual(len(profile.load_order), 2)

    def test_profile_update_load_order(self):
        """Test Profile update_load_order method."""
        profile = Profile(
            id="test-profile-1",
            name="Test Profile",
            enabled_mods=["mod1", "mod2", "mod3"],
            load_order=["mod1", "mod2"]
        )

        new_order = ["mod2", "mod1", "mod3"]
        profile.update_load_order(new_order)

        self.assertEqual(profile.load_order, new_order)

    def test_settings_creation(self):
        """Test Settings object creation."""
        settings = Settings(
            default_mod_library="/path/to/library",
            last_used_profile="profile1"
        )

        self.assertEqual(settings.default_mod_library, "/path/to/library")
        self.assertEqual(settings.last_used_profile, "profile1")
        self.assertIsNotNone(settings.created_at)
        self.assertIsNotNone(settings.updated_at)

    def test_mod_forge_data(self):
        """Test ModForgeData container."""
        data = ModForgeData()

        # Test adding mods
        mod1 = Mod(id="mod1", name="Mod 1", source_path="/path1", status=ModStatus.ENABLED)
        mod2 = Mod(id="mod2", name="Mod 2", source_path="/path2", status=ModStatus.DISABLED)

        data.add_mod(mod1)
        data.add_mod(mod2)

        self.assertEqual(len(data.mods), 2)
        self.assertIn("mod1", data.mods)
        self.assertIn("mod2", data.mods)

        # Test removing mods
        data.remove_mod("mod1")
        self.assertEqual(len(data.mods), 1)
        self.assertNotIn("mod1", data.mods)

        # Test adding profiles
        profile1 = Profile(id="profile1", name="Profile 1")
        profile2 = Profile(id="profile2", name="Profile 2")

        data.add_profile(profile1)
        data.add_profile(profile2)

        self.assertEqual(len(data.profiles), 2)

        # Test current profile
        data.set_current_profile("profile1")
        self.assertEqual(data.current_profile_id, "profile1")
        self.assertEqual(data.get_current_profile().id, "profile1")

if __name__ == "__main__":
    unittest.main()
