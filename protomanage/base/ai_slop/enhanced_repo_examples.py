"""
Examples and documentation for using the enhanced repository system.
"""

from typing import List
from protomanage.base.enhanced_repo import EnhancedRepo, bulk_edit_items, safe_item_operation
from protomanage.base.repo import Repo
from protomanage.item import Item


class ExampleUsage:
    """Examples of how to use the enhanced repository system."""
    
    def __init__(self, repo: EnhancedRepo):
        self.repo = repo
    
    def example_1_basic_editing(self):
        """Example 1: Basic item editing with automatic save."""
        
        # Edit a specific item by UUID
        with self.repo.edit_items(uuid_filter="some-uuid-here") as items:
            if items:
                item = items[0]
                # Modify the item
                item.some_property = "new_value"
                # Item is automatically saved when context exits successfully
    
    def example_2_bulk_editing(self):
        """Example 2: Bulk editing with filters."""
        
        # Edit all items of a specific type
        with self.repo.edit_items(item_type="protomanage.core.inbox-item") as items:
            for item in items:
                # Add a timestamp to all inbox items
                if hasattr(item, 'data'):
                    item.data['last_modified'] = "2025-07-09"
    
    def example_3_conditional_editing(self):
        """Example 3: Conditional editing with custom filters."""
        
        # Edit items based on custom criteria
        def is_high_priority(item: Item) -> bool:
            data = item._to_dict()
            return data.get('priority') == 'high'
        
        with self.repo.edit_items(custom_filter=is_high_priority) as items:
            for item in items:
                # Mark high priority items as urgent
                if hasattr(item, 'data'):
                    item.data['urgent'] = True
    
    def example_4_data_filter_editing(self):
        """Example 4: Editing items based on data content."""
        
        # Edit items where specific data matches
        with self.repo.edit_items(data_filter={'status': 'pending', 'category': 'work'}) as items:
            for item in items:
                # Update all pending work items
                if hasattr(item, 'data'):
                    item.data['status'] = 'in_progress'
    
    def example_5_manual_save_control(self):
        """Example 5: Manual save control for complex operations."""
        
        with self.repo.edit_items(uuid_filter="some-uuid", auto_save=False) as items:
            try:
                for item in items:
                    # Perform complex operations
                    self._complex_transformation(item)
                    
                    # Validate the changes
                    if self._validate_item(item):
                        # Manually save only if validation passes
                        self.repo._save_single_item(item)
                    else:
                        # Skip this item, continue with others
                        continue
                        
            except Exception as e:
                # Items are automatically rolled back due to exception
                print(f"Error during transformation: {e}")
                raise
    
    def example_6_safe_operations(self):
        """Example 6: Safe operations with automatic error handling."""
        
        def update_priority(item: Item) -> bool:
            """Update an item's priority and return success status."""
            if hasattr(item, 'data'):
                item.data['priority'] = 'high'
                return True
            return False
        
        # Safe operation with automatic rollback on error
        success = safe_item_operation(
            self.repo,
            "some-uuid",
            update_priority,
            default_value=False
        )
        
        if success:
            print("Priority updated successfully")
        else:
            print("Failed to update priority")
    
    def example_7_bulk_utility_functions(self):
        """Example 7: Using bulk utility functions."""
        
        def mark_as_processed(item: Item):
            """Mark an item as processed."""
            if hasattr(item, 'data'):
                item.data['processed'] = True
                item.data['processed_date'] = "2025-07-09"
        
        # Bulk edit using utility function
        count = bulk_edit_items(
            self.repo,
            {'item_type': 'protomanage.core.inbox-item'},
            mark_as_processed
        )
        
        print(f"Processed {count} inbox items")
    
    def example_8_query_before_edit(self):
        """Example 8: Query items before editing to check what will be affected."""
        
        # First, query to see what items would be affected
        items_to_edit = self.repo.get_items(data_filter={'status': 'draft'})
        print(f"Found {len(items_to_edit)} draft items to update")
        
        # Confirm with user or apply business logic
        if len(items_to_edit) > 10:
            print("Too many items to update at once, processing in batches")
            
            # Process in batches
            batch_size = 5
            for i in range(0, len(items_to_edit), batch_size):
                batch_uuids = [item.uuid for item in items_to_edit[i:i+batch_size]]
                
                with self.repo.edit_items(uuid_filter=batch_uuids) as batch_items:
                    for item in batch_items:
                        if hasattr(item, 'data'):
                            item.data['status'] = 'published'
                
                print(f"Processed batch {i//batch_size + 1}")
        else:
            # Process all at once
            with self.repo.edit_items(data_filter={'status': 'draft'}) as items:
                for item in items:
                    if hasattr(item, 'data'):
                        item.data['status'] = 'published'
    
    def example_9_nested_data_filtering(self):
        """Example 9: Working with nested data structures."""
        
        # Filter items with nested data using dot notation
        with self.repo.edit_items(data_filter={'metadata.category': 'important'}) as items:
            for item in items:
                # Update nested data
                data = item._to_dict()
                if 'metadata' not in data:
                    data['metadata'] = {}
                data['metadata']['last_updated'] = "2025-07-09"
    
    def example_10_transaction_rollback(self):
        """Example 10: Demonstrating transaction rollback on error."""
        
        try:
            with self.repo.edit_items(item_type="protomanage.core.inbox-item") as items:
                for i, item in enumerate(items):
                    if hasattr(item, 'data'):
                        item.data['batch_number'] = i
                        
                        # Simulate an error condition
                        if i == 3:
                            raise ValueError("Simulated error during processing")
                        
        except ValueError as e:
            print(f"Error occurred: {e}")
            print("All changes have been automatically rolled back")
            
            # Verify rollback worked
            items_check = self.repo.get_items(item_type="protomanage.core.inbox-item")
            for item in items_check:
                data = item._to_dict()
                assert 'batch_number' not in data, "Rollback failed!"
            
            print("Rollback verification successful")
    
    def _complex_transformation(self, item: Item):
        """Simulate a complex transformation that might fail."""
        # This would contain your actual business logic
        pass
    
    def _validate_item(self, item: Item) -> bool:
        """Validate an item after transformation."""
        # This would contain your actual validation logic
        return True


# Integration example with your existing Repo class
class MyEnhancedRepo(Repo, EnhancedRepo):
    """
    Example of how to integrate enhanced functionality with your existing Repo class.
    This uses multiple inheritance to combine both sets of functionality.
    """
    
    def __init__(self, repo_path):
        # Initialize the base Repo class
        super().__init__(repo_path)
        # EnhancedRepo doesn't need separate initialization
    
    def get_urgent_items(self) -> List[Item]:
        """Business-specific method using enhanced functionality."""
        return self.get_items(data_filter={'urgent': True})
    
    def archive_completed_items(self) -> int:
        """Archive all completed items."""
        def mark_archived(item: Item):
            if hasattr(item, 'data'):
                item.data['archived'] = True
                item.data['archive_date'] = "2025-07-09"
        
        return bulk_edit_items(
            self,
            {'data_filter': {'status': 'completed'}},
            mark_archived
        )


# Alternative approach: Dependency injection pattern
class ItemService:
    """
    Service class that encapsulates item operations.
    This approach uses dependency injection instead of inheritance.
    """
    
    def __init__(self, repo: EnhancedRepo):
        self.repo = repo
    
    def mark_items_as_read(self, uuids: List[str]) -> int:
        """Mark specific items as read."""
        count = 0
        with self.repo.edit_items(uuid_filter=uuids) as items:
            for item in items:
                if hasattr(item, 'data'):
                    item.data['read'] = True
                    count += 1
        return count
    
    def update_item_priority(self, uuid: str, priority: str) -> bool:
        """Update the priority of a specific item."""
        def set_priority(item: Item) -> bool:
            if hasattr(item, 'data'):
                item.data['priority'] = priority
                return True
            return False
        
        return safe_item_operation(self.repo, uuid, set_priority, False)
    
    def batch_update_category(self, old_category: str, new_category: str) -> int:
        """Update category for all items with the old category."""
        def update_category(item: Item):
            if hasattr(item, 'data'):
                item.data['category'] = new_category
        
        return bulk_edit_items(
            self.repo,
            {'data_filter': {'category': old_category}},
            update_category
        )


if __name__ == "__main__":
    # Example of how to use the system
    from pathlib import Path
    
    # Create an enhanced repo
    repo = MyEnhancedRepo(Path("~/.protomanage").expanduser())
    
    # Use the examples
    examples = ExampleUsage(repo)
    examples.example_1_basic_editing()
    
    # Or use the service approach
    item_service = ItemService(repo)
    item_service.mark_items_as_read(["uuid1", "uuid2", "uuid3"])
