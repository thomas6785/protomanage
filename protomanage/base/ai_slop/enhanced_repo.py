"""
Enhanced repository functionality for editing items with transaction-like behavior.
Provides context managers and query interfaces for safe item manipulation.
"""

from contextlib import contextmanager
from typing import List, Optional, Callable, Union, Dict, Any
from pathlib import Path
import logging
import json
from dataclasses import dataclass

from .item import Item


@dataclass
class ItemFilter:
    """Filter criteria for querying items."""
    uuid_filter: Optional[Union[str, List[str]]] = None
    item_type: Optional[str] = None
    custom_filter: Optional[Callable[[Item], bool]] = None
    data_filter: Optional[Dict[str, Any]] = None


class ItemEditSession:
    """
    Context manager for editing items. Provides transaction-like behavior
    where changes are only saved if the context exits successfully.
    """
    
    def __init__(self, repo: 'Repo', items: List[Item], auto_save: bool = True):
        self.repo = repo
        self.items = items
        self.auto_save = auto_save
        self.original_data = {}
        self._changes_made = False
        self._logger = logging.getLogger(__name__)
        
    def __enter__(self) -> List[Item]:
        """Enter the editing session and create backups."""
        # Create backup of original item data
        for item in self.items:
            self.original_data[item.uuid] = item.to_dict()
        
        self._logger.debug(f"Started edit session for {len(self.items)} items")
        return self.items
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the editing session and handle saving/rollback."""
        if exc_type is None:
            # Success - save changes if auto_save is enabled
            if self.auto_save:
                self.save()
                self._logger.debug(f"Auto-saved {len(self.items)} items")
        else:
            # Exception occurred - rollback changes
            self.rollback()
            self._logger.warning(f"Exception in edit session, rolled back {len(self.items)} items")
            
        return False  # Don't suppress exceptions
    
    def save(self) -> None:
        """Manually save all items in the session."""
        for item in self.items:
            self.repo._save_single_item(item)
        self._changes_made = False
        self._logger.info(f"Saved {len(self.items)} items")
    
    def rollback(self) -> None:
        """Rollback all items to their original state."""
        for item in self.items:
            if item.uuid in self.original_data:
                # Restore original data by reconstructing the item
                original_dict = self.original_data[item.uuid]
                restored_item = Item.from_dict(original_dict)
                
                # Update the current item's data
                item.__dict__.update(restored_item.__dict__)
        
        self._changes_made = False
        self._logger.info(f"Rolled back {len(self.items)} items")
    
    def mark_changed(self) -> None:
        """Mark that changes have been made (for manual tracking)."""
        self._changes_made = True


class EnhancedRepo:
    """
    Enhanced repository mixin/extension that provides advanced item querying
    and editing capabilities. Can be mixed into your existing Repo class.
    """
    
    def get_items(self, 
                  uuid_filter: Optional[Union[str, List[str]]] = None,
                  item_type: Optional[str] = None,
                  data_filter: Optional[Dict[str, Any]] = None,
                  custom_filter: Optional[Callable[[Item], bool]] = None) -> List[Item]:
        """
        Get items based on various filter criteria.
        
        Args:
            uuid_filter: Single UUID string or list of UUIDs to match
            item_type: Item type unique_name to filter by
            data_filter: Dictionary of key-value pairs to match in item data
            custom_filter: Custom function that takes an Item and returns bool
            
        Returns:
            List of items matching the criteria
        """
        filtered_items = list(self.items)  # Start with all items
        
        # Apply UUID filter
        if uuid_filter:
            if isinstance(uuid_filter, str):
                uuid_filter = [uuid_filter]
            filtered_items = [item for item in filtered_items if item.uuid in uuid_filter]
        
        # Apply item type filter
        if item_type:
            filtered_items = [item for item in filtered_items 
                            if item.__class__.UNIQUE_NAME == item_type]
        
        # Apply data filter
        if data_filter:
            filtered_items = [item for item in filtered_items 
                            if self._matches_data_filter(item, data_filter)]
        
        # Apply custom filter
        if custom_filter:
            filtered_items = [item for item in filtered_items if custom_filter(item)]
        
        return filtered_items
    
    def _matches_data_filter(self, item: Item, data_filter: Dict[str, Any]) -> bool:
        """Check if an item's data matches the filter criteria."""
        item_data = item._to_dict()
        
        for key, expected_value in data_filter.items():
            if key not in item_data:
                return False
            
            actual_value = item_data[key]
            
            # Support nested key access with dot notation
            if '.' in key:
                keys = key.split('.')
                actual_value = item_data
                for k in keys:
                    if isinstance(actual_value, dict) and k in actual_value:
                        actual_value = actual_value[k]
                    else:
                        return False
            
            if actual_value != expected_value:
                return False
        
        return True
    
    @contextmanager
    def edit_items(self, 
                   uuid_filter: Optional[Union[str, List[str]]] = None,
                   item_type: Optional[str] = None,
                   data_filter: Optional[Dict[str, Any]] = None,
                   custom_filter: Optional[Callable[[Item], bool]] = None,
                   auto_save: bool = True) -> ItemEditSession:
        """
        Context manager for editing items with transaction-like behavior.
        
        Usage:
            with repo.edit_items(uuid_filter="some-uuid") as items:
                for item in items:
                    item.some_property = "new_value"
                # Items are automatically saved on successful exit
        """
        items = self.get_items(uuid_filter, item_type, data_filter, custom_filter)
        
        session = ItemEditSession(self, items, auto_save)
        
        try:
            yield session.__enter__()
        except Exception as e:
            session.__exit__(type(e), e, e.__traceback__)
            raise
        else:
            session.__exit__(None, None, None)
    
    def _save_single_item(self, item: Item) -> None:
        """Save a single item to disk."""
        items_dir = self._repo_path / "items"
        
        if not items_dir.is_dir():
            items_dir.mkdir(parents=True, exist_ok=True)
        
        item_file = items_dir / f"{item.uuid}.json"
        item_json = json.dumps(item.to_dict(), indent=4 if self.config.use_pretty_json else None)
        item_file.write_text(item_json)
    
    def get_item_by_uuid(self, uuid: str) -> Optional[Item]:
        """Get a single item by UUID."""
        items = self.get_items(uuid_filter=uuid)
        return items[0] if items else None
    
    def update_item(self, item: Item) -> None:
        """Update a single item in the repository."""
        # Find and replace the item in memory
        for i, existing_item in enumerate(self._items):
            if existing_item.uuid == item.uuid:
                self._items[i] = item
                break
        else:
            # Item not found, add it
            self._items.append(item)
        
        # Save to disk
        self._save_single_item(item)
    
    def delete_item(self, uuid: str) -> bool:
        """Delete an item by UUID. Returns True if item was deleted."""
        # Remove from memory
        original_count = len(self._items)
        self._items = [item for item in self._items if item.uuid != uuid]
        
        if len(self._items) == original_count:
            return False  # Item not found
        
        # Remove from disk
        items_dir = self._repo_path / "items"
        item_file = items_dir / f"{uuid}.json"
        
        if item_file.exists():
            item_file.unlink()
        
        return True


# Example of how to integrate with your existing Repo class
class ExtendedRepo(EnhancedRepo):
    """
    Example of how to extend your existing Repo class with the enhanced functionality.
    You can either use this as a separate class or mix the EnhancedRepo methods directly
    into your existing Repo class.
    """
    
    def __init__(self, repo_path: Path):
        # Initialize your existing Repo functionality here
        # This is just an example - you'd use your actual Repo.__init__
        super().__init__(repo_path)


# Utility functions for common operations
def bulk_edit_items(repo: EnhancedRepo, 
                   filter_criteria: Dict[str, Any],
                   edit_function: Callable[[Item], None]) -> int:
    """
    Utility function for bulk editing items.
    
    Args:
        repo: Repository instance
        filter_criteria: Criteria for selecting items to edit
        edit_function: Function that takes an Item and modifies it
        
    Returns:
        Number of items that were edited
    """
    with repo.edit_items(**filter_criteria) as items:
        for item in items:
            edit_function(item)
        return len(items)


def safe_item_operation(repo: EnhancedRepo,
                       uuid: str,
                       operation: Callable[[Item], Any],
                       default_value: Any = None) -> Any:
    """
    Safely perform an operation on an item, with automatic rollback on error.
    
    Args:
        repo: Repository instance
        uuid: UUID of item to operate on
        operation: Function that takes an Item and returns a value
        default_value: Value to return if operation fails
        
    Returns:
        Result of operation or default_value if failed
    """
    try:
        with repo.edit_items(uuid_filter=uuid, auto_save=False) as items:
            if not items:
                return default_value
            
            result = operation(items[0])
            # Only save if operation completed successfully
            repo._save_single_item(items[0])
            return result
            
    except Exception as e:
        logging.error(f"Operation failed for item {uuid}: {e}")
        return default_value
