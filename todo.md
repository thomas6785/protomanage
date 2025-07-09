# TODO

- Modify Item's to use a wrapper object - composition not inheritance!
- Use uuid4().hex() instead of str()
- Write repo.get_items( uuidFilter, preObjectFilter, objectFilter )
- Move repo config load/save methods into the RepoConfig class
- Rewrite RepoConfig.get to first check parsed values, then fall back to default values
- Write repo methods for adding, retrieving, and removing items (need to consider how to handle dynamically loading in and saving items)
    Could use a context manager for editing items
    with repo.get_items(filters) as items:
        # do stuff



ItemEditSession (context manager class):
    __init__(item : Item)
    __enter__    - lock the items (use a static list to disallow the same item being checked out again) and create a backup of each one
    __exit__     - save the items (catch any exceptions and write to a 'recovery' file if needed) and delete the backups

    Example usage:
        inbox_items = repo.get_items( data_filter = lambda x : x['type']=="inbox-item" )
        with ItemEditSession( inbox_items ):
            inbox_items[0].status = 'whatever'

Repo class:
    get_items( uuid_filter, data_filter, object_filter ) -> List["Items"]
    get_uuid
    
    add_item (maybe this isn't even needed? just create the item yourself and save to file)

Item:
    Should have its own file path saved
    
    __save()
    __create_backup() - create backup, yield, then delete backup - catch errors and display backup location if needed
    __delete_backup()

