
"""Data models for ModForge Game Mod Manager."""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from enum import Enum
import uuid
import os
from datetime import datetime

class ModStatus(Enum):
    """Enumeration for mod status."""
    ENABLED = "enabled"
    DISABLED = "disabled"
    MISSING = "missing"

@dataclass
class Mod:
    """Represents a game mod in the library."""
    id: str
    name: str
    source_path: str
    status: ModStatus = ModStatus.ENABLED
    detected_files: List[str] = None
    metadata: Dict[str, Any] = None
    created_at: datetime = None
    updated_at: datetime = None

    def __post_init__(self):
        """Initialize default values."""
        if self.detected_files is None:
            self.detected_files = []
        if self.metadata is None:
            self.metadata = {}
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()

    def update_metadata(self, metadata: Dict[str, Any]):
        """Update mod metadata."""
        self.metadata.update(metadata)
        self.updated_at = datetime.now()

    def refresh_files(self, files: List[str]):
        """Refresh detected files."""
        self.detected_files = files
        self.updated_at = datetime.now()

@dataclass
class Profile:
    """Represents a mod profile with enabled mods and load order."""
    id: str
    name: str
    enabled_mods: List[str] = None  # List of mod IDs
    load_order: List[str] = None    # List of mod IDs in load order
    created_at: datetime = None
    updated_at: datetime = None

    def __post_init__(self):
        """Initialize default values."""
        if self.enabled_mods is None:
            self.enabled_mods = []
        if self.load_order is None:
            self.load_order = []
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()

    def update_load_order(self, new_order: List[str]):
        """Update the load order."""
        self.load_order = new_order
        self.updated_at = datetime.now()

    def toggle_mod(self, mod_id: str, enable: bool):
        """Enable or disable a mod in this profile."""
        if enable and mod_id not in self.enabled_mods:
            self.enabled_mods.append(mod_id)
        elif not enable and mod_id in self.enabled_mods:
            self.enabled_mods.remove(mod_id)
        self.updated_at = datetime.now()

@dataclass
class Settings:
    """Application settings."""
    default_mod_library: str = ""
    last_used_profile: str = ""
    created_at: datetime = None
    updated_at: datetime = None

    def __post_init__(self):
        """Initialize default values."""
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()

    def update_setting(self, key: str, value: Any):
        """Update a setting."""
        setattr(self, key, value)
        self.updated_at = datetime.now()

class ModForgeData:
    """Container for all application data."""
    def __init__(self):
        self.mods: Dict[str, Mod] = {}
        self.profiles: Dict[str, Profile] = {}
        self.settings: Settings = Settings()
        self.current_profile_id: Optional[str] = None

    def add_mod(self, mod: Mod):
        """Add a mod to the library."""
        self.mods[mod.id] = mod

    def remove_mod(self, mod_id: str):
        """Remove a mod from the library."""
        if mod_id in self.mods:
            del self.mods[mod_id]

    def get_mod(self, mod_id: str) -> Optional[Mod]:
        """Get a mod by ID."""
        return self.mods.get(mod_id)

    def add_profile(self, profile: Profile):
        """Add a profile."""
        self.profiles[profile.id] = profile

    def remove_profile(self, profile_id: str):
        """Remove a profile."""
        if profile_id in self.profiles:
            del self.profiles[profile_id]

    def get_profile(self, profile_id: str) -> Optional[Profile]:
        """Get a profile by ID."""
        return self.profiles.get(profile_id)

    def set_current_profile(self, profile_id: str):
        """Set the current profile."""
        self.current_profile_id = profile_id
        self.settings.last_used_profile = profile_id

    def get_current_profile(self) -> Optional[Profile]:
        """Get the current profile."""
        if self.current_profile_id:
            return self.get_profile(self.current_profile_id)
        return None
