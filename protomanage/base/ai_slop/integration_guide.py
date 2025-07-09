"""
Integration guide for adding enhanced repository functionality to your existing Repo class.
"""

from pathlib import Path
import logging
from typing import Dict, Any
import typer

from .enhanced_repo import EnhancedRepo
from .item import Item
from .repo import Repo, REPO_FOLDER_NAME
# Add this to your existing repo.py file:

from .enhanced_repo import EnhancedRepo

class Repo(EnhancedRepo):
    """Your existing Repo class with enhanced functionality."""
    
    def __init__(self, repo_path: Path):
        # Your existing initialization code
        self._logger = logging.getLogger(__name__)
        
        if not repo_path.is_dir():
            raise FileNotFoundError(f"repo path '{repo_path}' does not exist or is not a directory.")
        if repo_path.name != REPO_FOLDER_NAME:
            raise ValueError(f"repo path '{repo_path}' does not end with expected {REPO_FOLDER_NAME}")

        self._repo_path = repo_path
        self._load_config()
        self._uuid = self._load_uuid()
        self._plugins = self._load_plugins()
        self._items = self._load_items()
        self._pm_version = self._load_version()
        
        # EnhancedRepo methods are now available automatically


# Option 2: Composition approach
# If you prefer not to modify your existing Repo class:

from .enhanced_repo import EnhancedRepo

class RepoManager:
    """Wrapper that provides enhanced functionality for any Repo instance."""
    
    def __init__(self, repo: Repo):
        self._repo = repo
        self._enhanced = type('EnhancedWrapper', (EnhancedRepo,), {
            '__init__': lambda self, r: setattr(self, '__dict__', r.__dict__)
        })(repo)
    
    def __getattr__(self, name):
        # Delegate to enhanced functionality first, then to original repo
        if hasattr(self._enhanced, name):
            return getattr(self._enhanced, name)
        return getattr(self._repo, name)


# Option 3: Direct integration (modify your existing methods)
# Add these methods directly to your existing Repo class:

def add_enhanced_methods_to_repo():
    """
    Example of how to add specific enhanced methods to your existing Repo class
    without inheriting from EnhancedRepo.
    """
    
    # Add to your Repo class:
    def edit_items_by_uuid(self, uuid: str):
        """Simple context manager for editing a single item by UUID."""
        return self.edit_items(uuid_filter=uuid)
    
    def get_items_by_type(self, item_type: str):
        """Get all items of a specific type."""
        return [item for item in self.items if item.__class__.UNIQUE_NAME == item_type]
    
    def bulk_update_data(self, filter_criteria: dict, updates: dict):
        """Bulk update data fields for items matching criteria."""
        count = 0
        for item in self.items:
            if self._item_matches_criteria(item, filter_criteria):
                if hasattr(item, 'data'):
                    item.data.update(updates)
                    self._save_single_item(item)
                    count += 1
        return count
    
    def _item_matches_criteria(self, item: Item, criteria: dict) -> bool:
        """Check if an item matches the given criteria."""
        for key, value in criteria.items():
            if key == 'item_type':
                if item.__class__.UNIQUE_NAME != value:
                    return False
            elif key == 'uuid':
                if item.uuid != value:
                    return False
            # Add more criteria as needed
        return True


# Quick integration example for immediate use:
def quick_integration_example():
    """
    Quickest way to start using enhanced functionality with your existing repo.
    """
    
    # Assuming you have an existing repo instance
    from pathlib import Path
    from .repo import Repo, find_repo
    from .enhanced_repo import EnhancedRepo
    
    # Get your existing repo
    repo = find_repo(Path.cwd())
    
    # Create an enhanced version
    class QuickEnhancedRepo(repo.__class__, EnhancedRepo):
        pass
    
    # Transfer the instance
    enhanced_repo = QuickEnhancedRepo.__new__(QuickEnhancedRepo)
    enhanced_repo.__dict__.update(repo.__dict__)
    
    # Now you can use enhanced functionality
    with enhanced_repo.edit_items(item_type="protomanage.core.inbox-item") as items:
        for item in items:
            # Edit your items
            pass
    
    return enhanced_repo


# Integration with your CLI commands
def integrate_with_cli():
    """
    Example of how to integrate enhanced repo functionality with your CLI commands.
    """
    
    # In your cli.py file, you can add commands like:
    
    import typer
    from .repo import find_repo
    from .enhanced_repo import bulk_edit_items
    
    def mark_all_read_command():
        """CLI command to mark all inbox items as read."""
        repo = find_repo(Path.cwd())
        
        def mark_read(item):
            if hasattr(item, 'data'):
                item.data['read'] = True
        
        count = bulk_edit_items(
            repo,
            {'item_type': 'protomanage.core.inbox-item'},
            mark_read
        )
        
        typer.echo(f"Marked {count} items as read")
    
    def update_priority_command(uuid: str, priority: str):
        """CLI command to update item priority."""
        repo = find_repo(Path.cwd())
        
        with repo.edit_items(uuid_filter=uuid) as items:
            if items:
                item = items[0]
                if hasattr(item, 'data'):
                    item.data['priority'] = priority
                typer.echo(f"Updated priority for item {uuid}")
            else:
                typer.echo(f"Item {uuid} not found")


# Testing integration
def test_integration():
    """
    Simple test to verify the integration works.
    """
    from pathlib import Path
    from .repo import find_repo
    
    try:
        # Get repo
        repo = find_repo(Path.cwd())
        
        # Test basic functionality
        items = repo.get_items()
        print(f"Found {len(items)} items")
        
        # Test enhanced functionality if available
        if hasattr(repo, 'edit_items'):
            print("Enhanced functionality available!")
            
            # Test context manager
            with repo.edit_items(auto_save=False) as items:
                print(f"Editing session started with {len(items)} items")
                # Don't actually change anything in test
            
            print("Integration test successful!")
        else:
            print("Enhanced functionality not available - integration needed")
            
    except Exception as e:
        print(f"Integration test failed: {e}")


if __name__ == "__main__":
    test_integration()
