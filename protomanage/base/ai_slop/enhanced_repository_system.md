# Enhanced Repository System for Protomanage

## Summary

I've created a comprehensive solution for giving Python methods easy access to retrieve, edit, and save files from your database. The solution provides:

1. **Context Manager Pattern** - Transaction-like behavior with automatic save/rollback
2. **Flexible Querying** - Multiple ways to filter and select items
3. **Safe Operations** - Automatic error handling and rollback
4. **Bulk Operations** - Efficient batch processing
5. **Easy Integration** - Works with your existing Repo class

## Key Components

### 1. Enhanced Repository (`enhanced_repo.py`)
- `EnhancedRepo` class with advanced querying and editing capabilities
- `ItemEditSession` context manager for transaction-like behavior
- `ItemFilter` dataclass for structured filtering
- Utility functions for common operations

### 2. Usage Examples (`enhanced_repo_examples.py`)
- 10 comprehensive examples showing different use patterns
- Integration examples with your existing code
- Service layer patterns for business logic separation

### 3. Integration Guide (`integration_guide.py`)
- Multiple integration approaches (mixin, composition, direct)
- CLI integration examples
- Testing and validation code

## Basic Usage Patterns

### 1. Simple Item Editing
```python
# Edit a specific item
with repo.edit_items(uuid_filter="some-uuid") as items:
    if items:
        items[0].some_property = "new_value"
        # Automatically saved on success
```

### 2. Bulk Operations
```python
# Edit all items of a specific type
with repo.edit_items(item_type="protomanage.core.inbox-item") as items:
    for item in items:
        item.data['processed'] = True
```

### 3. Conditional Editing
```python
# Edit items based on data content
with repo.edit_items(data_filter={'status': 'pending'}) as items:
    for item in items:
        item.data['status'] = 'in_progress'
```

### 4. Safe Operations with Error Handling
```python
def update_item_safely(item: Item) -> bool:
    item.data['last_modified'] = datetime.now().isoformat()
    return True

success = safe_item_operation(repo, "uuid", update_item_safely)
```

## Key Benefits

1. **Transaction Safety**: Changes are only saved if the entire operation succeeds
2. **Automatic Rollback**: Any exception automatically reverts changes
3. **Flexible Filtering**: Query by UUID, type, data content, or custom functions
4. **Memory Efficient**: Only loads and modifies items that match your criteria
5. **Easy Integration**: Works with your existing Repo class structure

## Integration Options

### Option 1: Mixin Approach (Recommended)
```python
from .enhanced_repo import EnhancedRepo

class Repo(EnhancedRepo):
    # Your existing Repo code
    # Enhanced methods are automatically available
```

### Option 2: Composition
```python
enhanced_repo = RepoManager(your_existing_repo)
# Use enhanced_repo for advanced operations
```

### Option 3: Service Layer
```python
item_service = ItemService(repo)
item_service.mark_items_as_read(["uuid1", "uuid2"])
```

## Advanced Features

- **Nested Data Filtering**: Use dot notation for nested data structures
- **Batch Processing**: Handle large datasets efficiently in batches
- **Manual Save Control**: Option to disable auto-save for complex operations
- **Validation Hooks**: Add custom validation before saving
- **Logging Integration**: Comprehensive logging for debugging and monitoring

## Files Created

1. `/protomanage/base/enhanced_repo.py` - Core enhanced repository functionality
2. `/protomanage/base/enhanced_repo_examples.py` - Comprehensive usage examples
3. `/protomanage/base/integration_guide.py` - Integration instructions and patterns

## Next Steps

1. **Choose Integration Approach**: Pick the integration method that best fits your codebase
2. **Add Import**: Import the enhanced functionality into your existing code
3. **Test Integration**: Use the provided test functions to verify everything works
4. **Implement Business Logic**: Use the examples as templates for your specific use cases
5. **Add CLI Commands**: Integrate with your existing CLI system for user-facing operations

This solution addresses your core need while maintaining compatibility with your existing codebase and following Python best practices for database/file operations.
