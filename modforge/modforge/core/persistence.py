

"""Persistence layer for ModForge Game Mod Manager."""

import os
import json
import sqlite3
from typing import Optional, Dict, Any
from pathlib import Path
from datetime import datetime

from ..models import ModForgeData, Mod, Profile, Settings, ModStatus

class PersistenceManager:
    """Handles saving and loading application data."""

    def __init__(self, data_dir: Optional[str] = None):
        """
        Initialize persistence manager.

        Args:
            data_dir: Directory to store application data. If None, uses default.
        """
        self.data_dir = self._get_data_directory(data_dir)
        self.db_path = self.data_dir / "modforge.db"

        # Ensure directory exists
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def _get_data_directory(self, custom_dir: Optional[str] = None) -> Path:
        """Get the application data directory."""
        if custom_dir:
            return Path(custom_dir)

        # Default: Use user's app data directory
        if os.name == 'nt':  # Windows
            appdata = os.getenv('APPDATA')
            if appdata:
                return Path(appdata) / "ModForge"
        elif os.name == 'posix':  # Linux/Mac
            home = Path.home()
            return home / ".local" / "share" / "ModForge"

        # Fallback
        return Path.home() / ".modforge"

    def _initialize_database(self):
        """Initialize the SQLite database schema."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Create tables
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS mods (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    source_path TEXT NOT NULL,
                    status TEXT NOT NULL,
                    detected_files TEXT,
                    metadata TEXT,
                    created_at TEXT,
                    updated_at TEXT
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS profiles (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    enabled_mods TEXT,
                    load_order TEXT,
                    created_at TEXT,
                    updated_at TEXT
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS settings (
                    id INTEGER PRIMARY KEY CHECK (id = 1),
                    default_mod_library TEXT,
                    last_used_profile TEXT,
                    created_at TEXT,
                    updated_at TEXT
                )
            """)

            # Create settings record if it doesn't exist
            cursor.execute("SELECT COUNT(*) FROM settings")
            if cursor.fetchone()[0] == 0:
                cursor.execute("""
                    INSERT INTO settings (id, default_mod_library, last_used_profile, created_at, updated_at)
                    VALUES (1, '', '', ?, ?)
                """, (datetime.now().isoformat(), datetime.now().isoformat()))

            conn.commit()

    def save_data(self, data: ModForgeData) -> bool:
        """Save all application data to database."""
        try:
            self._initialize_database()

            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Save mods
                cursor.execute("DELETE FROM mods")
                for mod in data.mods.values():
                    self._save_mod(cursor, mod)

                # Save profiles
                cursor.execute("DELETE FROM profiles")
                for profile in data.profiles.values():
                    self._save_profile(cursor, profile)

                # Save settings
                self._save_settings(cursor, data.settings)

                conn.commit()
                return True

        except Exception as e:
            print(f"Error saving data: {e}")
            return False

    def _save_mod(self, cursor, mod: Mod):
        """Save a single mod to database."""
        cursor.execute("""
            INSERT INTO mods (id, name, source_path, status, detected_files, metadata, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            mod.id,
            mod.name,
            mod.source_path,
            mod.status.value,
            json.dumps(mod.detected_files),
            json.dumps(mod.metadata),
            mod.created_at.isoformat(),
            mod.updated_at.isoformat()
        ))

    def _save_profile(self, cursor, profile: Profile):
        """Save a single profile to database."""
        cursor.execute("""
            INSERT INTO profiles (id, name, enabled_mods, load_order, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            profile.id,
            profile.name,
            json.dumps(profile.enabled_mods),
            json.dumps(profile.load_order),
            profile.created_at.isoformat(),
            profile.updated_at.isoformat()
        ))

    def _save_settings(self, cursor, settings: Settings):
        """Save settings to database."""
        cursor.execute("""
            UPDATE settings SET
                default_mod_library = ?,
                last_used_profile = ?,
                updated_at = ?
            WHERE id = 1
        """, (
            settings.default_mod_library,
            settings.last_used_profile,
            datetime.now().isoformat()
        ))

    def load_data(self) -> Optional[ModForgeData]:
        """Load all application data from database."""
        try:
            self._initialize_database()

            data = ModForgeData()

            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Load mods
                cursor.execute("SELECT * FROM mods")
                for row in cursor.fetchall():
                    mod = self._load_mod(row)
                    data.add_mod(mod)

                # Load profiles
                cursor.execute("SELECT * FROM profiles")
                for row in cursor.fetchall():
                    profile = self._load_profile(row)
                    data.add_profile(profile)

                # Load settings
                cursor.execute("SELECT * FROM settings WHERE id = 1")
                settings_row = cursor.fetchone()
                if settings_row:
                    data.settings = self._load_settings(settings_row)
                    data.current_profile_id = data.settings.last_used_profile

            return data

        except Exception as e:
            print(f"Error loading data: {e}")
            return None

    def _load_mod(self, row) -> Mod:
        """Load a single mod from database row."""
        return Mod(
            id=row[0],
            name=row[1],
            source_path=row[2],
            status=ModStatus(row[3]),
            detected_files=json.loads(row[4]) if row[4] else [],
            metadata=json.loads(row[5]) if row[5] else {},
            created_at=datetime.fromisoformat(row[6]),
            updated_at=datetime.fromisoformat(row[7])
        )

    def _load_profile(self, row) -> Profile:
        """Load a single profile from database row."""
        return Profile(
            id=row[0],
            name=row[1],
            enabled_mods=json.loads(row[2]) if row[2] else [],
            load_order=json.loads(row[3]) if row[3] else [],
            created_at=datetime.fromisoformat(row[4]),
            updated_at=datetime.fromisoformat(row[5])
        )

    def _load_settings(self, row) -> Settings:
        """Load settings from database row."""
        return Settings(
            default_mod_library=row[1],
            last_used_profile=row[2],
            created_at=datetime.fromisoformat(row[3]),
            updated_at=datetime.fromisoformat(row[4])
        )

    def get_data_directory(self) -> str:
        """Get the application data directory path."""
        return str(self.data_dir)

    def backup_data(self, backup_path: str) -> bool:
        """Create a backup of the database."""
        try:
            backup_path = Path(backup_path)
            if not backup_path.parent.exists():
                backup_path.parent.mkdir(parents=True, exist_ok=True)

            import shutil
            shutil.copy2(self.db_path, backup_path)
            return True
        except Exception as e:
            print(f"Error creating backup: {e}")
            return False

    def restore_data(self, backup_path: str) -> bool:
        """Restore data from a backup."""
        try:
            backup_path = Path(backup_path)
            if not backup_path.exists():
                return False

            import shutil
            shutil.copy2(backup_path, self.db_path)
            return True
        except Exception as e:
            print(f"Error restoring backup: {e}")
            return False

