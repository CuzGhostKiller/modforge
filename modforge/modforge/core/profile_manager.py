

"""Profile management functionality for ModForge Game Mod Manager."""

import uuid
from typing import List, Optional, Dict
from ..models import Profile, ModForgeData

class ProfileManager:
    """Manages mod profiles including creation, switching, and load order."""

    def __init__(self, data: ModForgeData):
        self.data = data

    def create_profile(self, name: str, based_on: Optional[str] = None) -> Profile:
        """
        Create a new profile.

        Args:
            name: Name of the profile
            based_on: ID of profile to duplicate (optional)

        Returns:
            The created profile
        """
        # Check if profile name already exists
        for profile in self.data.profiles.values():
            if profile.name.lower() == name.lower():
                raise ValueError(f"Profile with name '{name}' already exists")

        # Create new profile
        profile_id = str(uuid.uuid4())
        profile = Profile(
            id=profile_id,
            name=name
        )

        # If duplicating from another profile, copy its settings
        if based_on and based_on in self.data.profiles:
            source_profile = self.data.profiles[based_on]
            profile.enabled_mods = source_profile.enabled_mods.copy()
            profile.load_order = source_profile.load_order.copy()

        self.data.add_profile(profile)

        # Set as current profile if no current profile exists
        if not self.data.current_profile_id:
            self.data.set_current_profile(profile_id)

        return profile

    def duplicate_profile(self, profile_id: str, new_name: str) -> Profile:
        """
        Duplicate an existing profile.

        Args:
            profile_id: ID of profile to duplicate
            new_name: Name for the new profile

        Returns:
            The duplicated profile
        """
        return self.create_profile(new_name, based_on=profile_id)

    def rename_profile(self, profile_id: str, new_name: str) -> bool:
        """Rename a profile."""
        profile = self.data.get_profile(profile_id)
        if not profile:
            return False

        # Check if new name already exists
        for existing_profile in self.data.profiles.values():
            if existing_profile.id != profile_id and existing_profile.name.lower() == new_name.lower():
                return False

        profile.name = new_name
        return True

    def delete_profile(self, profile_id: str) -> bool:
        """Delete a profile."""
        if profile_id not in self.data.profiles:
            return False

        # Cannot delete the current profile
        if profile_id == self.data.current_profile_id:
            return False

        self.data.remove_profile(profile_id)
        return True

    def switch_profile(self, profile_id: str) -> bool:
        """Switch to a different profile."""
        if profile_id not in self.data.profiles:
            return False

        self.data.set_current_profile(profile_id)
        return True

    def get_current_profile_mods(self) -> Dict[str, bool]:
        """
        Get the current profile's mod enable/disable state.

        Returns:
            Dictionary mapping mod IDs to enabled status
        """
        current_profile = self.data.get_current_profile()
        if not current_profile:
            return {}

        mod_states = {}
        for mod_id in self.data.mods.keys():
            mod_states[mod_id] = mod_id in current_profile.enabled_mods

        return mod_states

    def update_current_profile_mods(self, mod_states: Dict[str, bool]) -> bool:
        """
        Update the current profile's mod enable/disable states.

        Args:
            mod_states: Dictionary mapping mod IDs to enabled status

        Returns:
            True if successful
        """
        current_profile = self.data.get_current_profile()
        if not current_profile:
            return False

        current_profile.enabled_mods = [
            mod_id for mod_id, enabled in mod_states.items() if enabled
        ]
        return True

    def get_load_order(self) -> List[str]:
        """Get the current load order."""
        current_profile = self.data.get_current_profile()
        if not current_profile:
            return []

        return current_profile.load_order

    def set_load_order(self, new_order: List[str]) -> bool:
        """
        Set the load order for the current profile.

        Args:
            new_order: List of mod IDs in desired load order

        Returns:
            True if successful
        """
        current_profile = self.data.get_current_profile()
        if not current_profile:
            return False

        # Validate that all mods exist
        for mod_id in new_order:
            if mod_id not in self.data.mods:
                return False

        current_profile.update_load_order(new_order)
        return True

    def move_mod_in_load_order(self, mod_id: str, direction: str) -> bool:
        """
        Move a mod up or down in the load order.

        Args:
            mod_id: ID of mod to move
            direction: "up" or "down"

        Returns:
            True if successful
        """
        current_profile = self.data.get_current_profile()
        if not current_profile:
            return False

        load_order = current_profile.load_order
        if mod_id not in load_order:
            return False

        current_index = load_order.index(mod_id)

        if direction == "up" and current_index > 0:
            # Swap with previous mod
            load_order[current_index], load_order[current_index - 1] = \
                load_order[current_index - 1], load_order[current_index]
            current_profile.update_load_order(load_order)
            return True

        elif direction == "down" and current_index < len(load_order) - 1:
            # Swap with next mod
            load_order[current_index], load_order[current_index + 1] = \
                load_order[current_index + 1], load_order[current_index]
            current_profile.update_load_order(load_order)
            return True

        return False

    def get_profile_summary(self, profile_id: str) -> Dict:
        """Get a summary of a profile's state."""
        profile = self.data.get_profile(profile_id)
        if not profile:
            return {}

        return {
            "id": profile.id,
            "name": profile.name,
            "enabled_mods_count": len(profile.enabled_mods),
            "total_mods_count": len(self.data.mods),
            "load_order_count": len(profile.load_order),
            "is_current": profile.id == self.data.current_profile_id
        }

