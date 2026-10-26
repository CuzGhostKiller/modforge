

"""Load order management functionality for ModForge Game Mod Manager."""

from typing import List, Optional
from ..models import ModForgeData

class LoadOrderManager:
    """Manages mod load order with validation and persistence."""

    def __init__(self, data: ModForgeData):
        self.data = data

    def get_current_load_order(self) -> List[str]:
        """Get the current load order."""
        current_profile = self.data.get_current_profile()
        if not current_profile:
            return []

        return current_profile.load_order

    def set_current_load_order(self, new_order: List[str]) -> bool:
        """
        Set the load order for the current profile.

        Args:
            new_order: List of mod IDs in desired load order

        Returns:
            True if successful, False if validation fails
        """
        current_profile = self.data.get_current_profile()
        if not current_profile:
            return False

        # Validate that all mods exist and are enabled
        for mod_id in new_order:
            if mod_id not in self.data.mods:
                return False
            if mod_id not in current_profile.enabled_mods:
                return False

        # Check for duplicates
        if len(new_order) != len(set(new_order)):
            return False

        current_profile.update_load_order(new_order)
        return True

    def move_mod_up(self, mod_id: str) -> bool:
        """Move a mod up in the load order."""
        current_profile = self.data.get_current_profile()
        if not current_profile:
            return False

        load_order = current_profile.load_order
        if mod_id not in load_order:
            return False

        current_index = load_order.index(mod_id)
        if current_index == 0:
            return False  # Already at top

        # Swap with previous mod
        load_order[current_index], load_order[current_index - 1] = \
            load_order[current_index - 1], load_order[current_index]
        current_profile.update_load_order(load_order)
        return True

    def move_mod_down(self, mod_id: str) -> bool:
        """Move a mod down in the load order."""
        current_profile = self.data.get_current_profile()
        if not current_profile:
            return False

        load_order = current_profile.load_order
        if mod_id not in load_order:
            return False

        current_index = load_order.index(mod_id)
        if current_index == len(load_order) - 1:
            return False  # Already at bottom

        # Swap with next mod
        load_order[current_index], load_order[current_index + 1] = \
            load_order[current_index + 1], load_order[current_index]
        current_profile.update_load_order(load_order)
        return True

    def add_mod_to_load_order(self, mod_id: str, position: Optional[int] = None) -> bool:
        """
        Add a mod to the load order.

        Args:
            mod_id: ID of mod to add
            position: Position to insert at (None for end)

        Returns:
            True if successful
        """
        current_profile = self.data.get_current_profile()
        if not current_profile:
            return False

        # Check if mod exists and is enabled
        if mod_id not in self.data.mods:
            return False
        if mod_id not in current_profile.enabled_mods:
            return False
        if mod_id in current_profile.load_order:
            return False  # Already in load order

        load_order = current_profile.load_order

        if position is None:
            # Add to end
            load_order.append(mod_id)
        elif 0 <= position <= len(load_order):
            # Insert at position
            load_order.insert(position, mod_id)
        else:
            return False

        current_profile.update_load_order(load_order)
        return True

    def remove_mod_from_load_order(self, mod_id: str) -> bool:
        """Remove a mod from the load order."""
        current_profile = self.data.get_current_profile()
        if not current_profile:
            return False

        load_order = current_profile.load_order
        if mod_id not in load_order:
            return False

        load_order.remove(mod_id)
        current_profile.update_load_order(load_order)
        return True

    def get_load_order_validation(self) -> List[str]:
        """
        Validate the current load order.

        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []
        current_profile = self.data.get_current_profile()

        if not current_profile:
            return ["No current profile selected"]

        load_order = current_profile.load_order

        # Check for missing mods
        missing_mods = [mod_id for mod_id in load_order if mod_id not in self.data.mods]
        if missing_mods:
            errors.append(f"Load order contains missing mods: {', '.join(missing_mods)}")

        # Check for disabled mods
        disabled_mods = [mod_id for mod_id in load_order if mod_id not in current_profile.enabled_mods]
        if disabled_mods:
            errors.append(f"Load order contains disabled mods: {', '.join(disabled_mods)}")

        # Check for duplicates
        if len(load_order) != len(set(load_order)):
            errors.append("Load order contains duplicate mods")

        return errors

    def get_load_order_summary(self) -> dict:
        """Get a summary of the current load order."""
        current_profile = self.data.get_current_profile()
        if not current_profile:
            return {
                "total_mods": 0,
                "enabled_mods": 0,
                "in_load_order": 0,
                "validation_errors": ["No current profile"]
            }

        load_order = current_profile.load_order
        enabled_mods = current_profile.enabled_mods

        return {
            "total_mods": len(self.data.mods),
            "enabled_mods": len(enabled_mods),
            "in_load_order": len(load_order),
            "validation_errors": self.get_load_order_validation()
        }

