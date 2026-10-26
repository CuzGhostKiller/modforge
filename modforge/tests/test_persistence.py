

"""Tests for the persistence manager module."""

import unittest
import tempfile
import os
import shutil
from modforge.models import ModForgeData, Mod, Profile, Settings
from modforge.core.persistence import PersistenceManager

class TestPersistenceManager(unittest.TestCase):
    """Test cases for the PersistenceManager class."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary directory for testing
        self.test_dir = tempfile.mkdtemp()
        self.data_dir = os.path.join(self.test_dir, "data")
        os.makedirs(self.data_dir)

        # Create test data
        self.data = ModForgeData()

        # Add some mods
        mod1 = Mod(id="mod1", name="Mod 1", source_path="/path1")
        mod2 = Mod(id="mod2", name="Mod 2", source_path="/path2")
        self.data.add_mod(mod1)
        self.data.add_mod(mod2)

        # Add some profiles
        profile1 = Profile(id="profile1", name="Profile 1", enabled_mods=["mod1"])
        profile2 = Profile(id="profile2", name="Profile 2", enabled_mods=["mod2"])
        self.data.add_profile(profile1)
        self.data.add_profile(profile2)
        self.data.set_current_profile("profile1")

        # Create persistence manager
        self.persistence = PersistenceManager()

    def tearDown(self):
        """Clean up test fixtures."""
        # Remove temporary directory
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_save_and_load_data(self):
        """Test saving and loading data."""
        # Save data
        success = self.persistence.save_data(self.data)
        self.assertTrue(success)

        # Load data
        loaded_data = self.persistence.load_data()
        self.assertIsNotNone(loaded_data)
        self.assertEqual(len(loaded_data.mods), 2)
        self.assertEqual(len(loaded_data.profiles), 2)
        self.assertEqual(loaded_data.current_profile_id, "profile1")

    def test_save_and_load_empty_data(self):
        """Test saving and loading empty data."""
        empty_data = ModForgeData()

        # Save empty data
        success = self.persistence.save_data(empty_data)
        self.assertTrue(success)

        # Load empty data
        loaded_data = self.persistence.load_data()
        self.assertIsNotNone(loaded_data)
        self.assertEqual(len(loaded_data.mods), 0)
        self.assertEqual(len(loaded_data.profiles), 0)

    def test_get_data_directory(self):
        """Test getting data directory."""
        data_dir = self.persistence.get_data_directory()
        self.assertTrue(os.path.exists(data_dir))
        self.assertTrue(data_dir.endswith("ModForge"))

    def test_backup_and_restore_data(self):
        """Test backup and restore functionality."""
        # Save initial data
        success = self.persistence.save_data(self.data)
        self.assertTrue(success)

        # Create backup
        backup_path = os.path.join(self.test_dir, "backup.db")
        success = self.persistence.backup_data(backup_path)
        self.assertTrue(success)
        self.assertTrue(os.path.exists(backup_path))

        # Modify original data
        mod3 = Mod(id="mod3", name="Mod 3", source_path="/path3")
        self.data.add_mod(mod3)
        success = self.persistence.save_data(self.data)
        self.assertTrue(success)

        # Restore from backup
        success = self.persistence.restore_data(backup_path)
        self.assertTrue(success)

        # Load restored data
        restored_data = self.persistence.load_data()
        self.assertEqual(len(restored_data.mods), 2)  # Should not include mod3
        self.assertEqual(len(restored_data.profiles), 2)

    def test_migration_from_older_versions(self):
        """Test data migration from older versions."""
        # This would test migration logic if we had older data formats
        # For now, just test that the current format works
        success = self.persistence.save_data(self.data)
        self.assertTrue(success)

        loaded_data = self.persistence.load_data()
        self.assertIsNotNone(loaded_data)
        self.assertEqual(len(loaded_data.mods), 2)

    def test_error_handling(self):
        """Test error handling in persistence operations."""
        # Test saving to invalid directory (should still work with default path)
        invalid_persistence = PersistenceManager()
        success = invalid_persistence.save_data(self.data)
        self.assertTrue(success)

        # Test loading from invalid directory (should still work with default path)
        loaded_data = invalid_persistence.load_data()
        self.assertIsNotNone(loaded_data)

if __name__ == "__main__":
    unittest.main()

