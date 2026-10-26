

"""Core mod management functionality for ModForge Game Mod Manager."""

import os
import uuid
from typing import List, Dict, Optional, Tuple
from pathlib import Path
from datetime import datetime

from ..models import Mod, ModStatus, ModForgeData

class ModManager:
    """Manages game mods including discovery, validation, and library operations."""

    def __init__(self, data: ModForgeData):
        self.data = data

    def discover_mod(self, folder_path: str) -> Tuple[Optional[Mod], str]:
        """
        Discover and validate a mod from a folder path.

        Returns:
            Tuple of (Mod object if successful, error message if failed)
        """
        try:
            path = Path(folder_path)

            # Validate path
            if not path.exists():
                return None, f"Path does not exist: {folder_path}"
            if not path.is_dir():
                return None, f"Path is not a directory: {folder_path}"

            # Check for duplicate
            existing_mod = self._find_mod_by_path(folder_path)
            if existing_mod:
                return None, f"Mod already exists: {existing_mod.name}"

            # Detect mod name
            mod_name = self._detect_mod_name(path)

            # Scan for files
            detected_files = self._scan_mod_directory(path)

            # Create mod
            mod = Mod(
                id=str(uuid.uuid4()),
                name=mod_name,
                source_path=str(path.absolute()),
                status=ModStatus.ENABLED,
                detected_files=detected_files,
                metadata={"discovery_date": datetime.now().isoformat()}
            )

            return mod, ""

        except Exception as e:
            return None, f"Error discovering mod: {str(e)}"

    def _find_mod_by_path(self, path: str) -> Optional[Mod]:
        """Find a mod by its source path."""
        path = str(Path(path).absolute())
        for mod in self.data.mods.values():
            if str(Path(mod.source_path).absolute()) == path:
                return mod
        return None

    def _detect_mod_name(self, path: Path) -> str:
        """Detect a sensible name for the mod."""
        # Try to find a common name file first
        name_files = ["modname.txt", "name.txt", "info.json", "modinfo.json"]
        for name_file in name_files:
            name_path = path / name_file
            if name_path.exists():
                try:
                    with open(name_path, 'r', encoding='utf-8') as f:
                        content = f.read().strip()
                        if content:
                            return content
                except:
                    continue

        # Fall back to folder name
        return path.name

    def _scan_mod_directory(self, path: Path) -> List[str]:
        """Scan directory for mod files and subdirectories."""
        detected_files = []

        try:
            for root, dirs, files in os.walk(path):
                # Skip hidden directories
                dirs[:] = [d for d in dirs if not d.startswith('.')]

                for file in files:
                    if not file.startswith('.'):
                        rel_path = os.path.relpath(os.path.join(root, file), path)
                        detected_files.append(rel_path)

        except (PermissionError, OSError) as e:
            # Handle permission errors gracefully
            pass

        return sorted(detected_files)

    def add_mod_to_library(self, mod: Mod) -> bool:
        """Add a discovered mod to the library."""
        if not mod:
            return False

        # Check for duplicates
        existing_mod = self._find_mod_by_path(mod.source_path)
        if existing_mod:
            return False

        self.data.add_mod(mod)
        return True

    def remove_mod_from_library(self, mod_id: str) -> bool:
        """Remove a mod from the library (does not delete files)."""
        if mod_id in self.data.mods:
            self.data.remove_mod(mod_id)
            return True
        return False

    def enable_mod(self, mod_id: str) -> bool:
        """Enable a mod."""
        mod = self.data.get_mod(mod_id)
        if mod:
            mod.status = ModStatus.ENABLED
            return True
        return False

    def disable_mod(self, mod_id: str) -> bool:
        """Disable a mod."""
        mod = self.data.get_mod(mod_id)
        if mod:
            mod.status = ModStatus.DISABLED
            return True
        return False

    def refresh_mod_info(self, mod_id: str) -> Tuple[bool, str]:
        """Refresh mod information by rescanning the directory."""
        mod = self.data.get_mod(mod_id)
        if not mod:
            return False, "Mod not found"

        try:
            path = Path(mod.source_path)
            if not path.exists():
                return False, "Mod directory does not exist"

            # Rescan files
            detected_files = self._scan_mod_directory(path)

            # Update mod
            mod.refresh_files(detected_files)

            return True, "Mod information refreshed successfully"

        except Exception as e:
            return False, f"Error refreshing mod: {str(e)}"

    def search_mods(self, query: str, enabled_only: bool = False) -> List[Mod]:
        """Search mods by name and filter by enabled status."""
        results = []

        for mod in self.data.mods.values():
            if enabled_only and mod.status != ModStatus.ENABLED:
                continue

            if query.lower() in mod.name.lower():
                results.append(mod)

        return results

    def get_mods_by_status(self, status: ModStatus) -> List[Mod]:
        """Get mods filtered by status."""
        return [mod for mod in self.data.mods.values() if mod.status == status]

