

"""Tests for the mod manager module."""

import unittest
import tempfile
import os
from pathlib import Path
from unittest.mock import patch
from modforge.models import ModForgeData, Mod, ModStatus
from modforge.core.mod_manager import ModManager

class TestModManager(unittest.TestCase):
    """Test cases for the ModManager class."""

    def setUp(self):
        """Set up test fixtures."""
        self.data = ModForgeData()
        self.mod_manager = ModManager(self.data)

        # Create a temporary directory for testing
        self.test_dir = tempfile.mkdtemp()
        self.mod_dir = Path(self.test_dir) / "test_mod"
        self.mod_dir.mkdir()

        # Create some test files
        (self.mod_dir / "mod1.txt").write_text("content1")
        (self.mod_dir / "mod2.txt").write_text("content2")

    def tearDown(self):
        """Clean up test fixtures."""
        # Remove temporary directory
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_discover_mod_success(self):
        """Test successful mod discovery."""
        mod, error = self.mod_manager.discover_mod(str(self.mod_dir))

        self.assertIsNotNone(mod)
        self.assertEqual(error, "")
        self.assertEqual(mod.name, "test_mod")
        self.assertEqual(mod.source_path, str(self.mod_dir))
        self.assertEqual(mod.status, ModStatus.ENABLED)
        self.assertEqual(len(mod.detected_files), 2)

    def test_discover_mod_invalid_path(self):
        """Test mod discovery with invalid path."""
        mod, error = self.mod_manager.discover_mod("/nonexistent/path")

        self.assertIsNone(mod)
        self.assertIsNotNone(error)
        self.assertIn("does not exist", error)

    def test_add_mod_to_library(self):
        """Test adding a mod to the library."""
        mod = Mod(
            id="test-mod-1",
            name="Test Mod",
            source_path=str(self.mod_dir),
            status=ModStatus.DISABLED
        )

        success = self.mod_manager.add_mod_to_library(mod)
        self.assertTrue(success)
        self.assertIn("test-mod-1", self.data.mods)

    def test_add_duplicate_mod(self):
        """Test adding a duplicate mod."""
        mod1 = Mod(
            id="test-mod-1",
            name="Test Mod",
            source_path=str(self.mod_dir),
            status=ModStatus.DISABLED
        )

        mod2 = Mod(
            id="test-mod-2",
            name="Test Mod 2",
            source_path=str(self.mod_dir),
            status=ModStatus.DISABLED
        )

        self.mod_manager.add_mod_to_library(mod1)
        success = self.mod_manager.add_mod_to_library(mod2)

        self.assertFalse(success)
        self.assertEqual(len(self.data.mods), 1)

    def test_remove_mod_from_library(self):
        """Test removing a mod from the library."""
        mod = Mod(
            id="test-mod-1",
            name="Test Mod",
            source_path=str(self.mod_dir),
            status=ModStatus.DISABLED
        )

        self.mod_manager.add_mod_to_library(mod)
        success = self.mod_manager.remove_mod_from_library("test-mod-1")

        self.assertTrue(success)
        self.assertNotIn("test-mod-1", self.data.mods)

    def test_enable_disable_mod(self):
        """Test enabling and disabling mods."""
        mod = Mod(
            id="test-mod-1",
            name="Test Mod",
            source_path=str(self.mod_dir),
            status=ModStatus.DISABLED
        )

        self.mod_manager.add_mod_to_library(mod)

        # Test enable
        success = self.mod_manager.enable_mod("test-mod-1")
        self.assertTrue(success)
        self.assertEqual(self.data.mods["test-mod-1"].status, ModStatus.ENABLED)

        # Test disable
        success = self.mod_manager.disable_mod("test-mod-1")
        self.assertTrue(success)
        self.assertEqual(self.data.mods["test-mod-1"].status, ModStatus.DISABLED)

    def test_search_mods(self):
        """Test searching mods."""
        mod1 = Mod(id="mod1", name="Test Mod 1", source_path="/path1", status=ModStatus.ENABLED)
        mod2 = Mod(id="mod2", name="Another Mod", source_path="/path2", status=ModStatus.DISABLED)
        mod3 = Mod(id="mod3", name="Test Mod 3", source_path="/path3", status=ModStatus.ENABLED)

        self.mod_manager.add_mod_to_library(mod1)
        self.mod_manager.add_mod_to_library(mod2)
        self.mod_manager.add_mod_to_library(mod3)

        # Search for "Test"
        results = self.mod_manager.search_mods("Test")
        self.assertEqual(len(results), 2)
        self.assertIn("mod1", [r.id for r in results])
        self.assertIn("mod3", [r.id for r in results])

        # Search with enabled_only filter
        results = self.mod_manager.search_mods("Test", enabled_only=True)
        self.assertEqual(len(results), 2)

        results = self.mod_manager.search_mods("Another", enabled_only=True)
        self.assertEqual(len(results), 0)

    def test_get_mods_by_status(self):
        """Test getting mods by status."""
        mod1 = Mod(id="mod1", name="Enabled Mod", source_path="/path1", status=ModStatus.ENABLED)
        mod2 = Mod(id="mod2", name="Disabled Mod", source_path="/path2", status=ModStatus.DISABLED)

        self.mod_manager.add_mod_to_library(mod1)
        self.mod_manager.add_mod_to_library(mod2)

        enabled_mods = self.mod_manager.get_mods_by_status(ModStatus.ENABLED)
        disabled_mods = self.mod_manager.get_mods_by_status(ModStatus.DISABLED)

        self.assertEqual(len(enabled_mods), 1)
        self.assertEqual(len(disabled_mods), 1)
        self.assertEqual(enabled_mods[0].id, "mod1")
        self.assertEqual(disabled_mods[0].id, "mod2")

if __name__ == "__main__":
    unittest.main()

