Protomanage is a command line utility for tracking to-do items.

Long-term it is intended to integrate with:
- Obsidian parsing to do items and moving them into Protomanage
- Google Calendar for adding scheduled items to the calendar
- A command line utility
- A GUI
- An interactive terminal application
- A mobile app for sending Protomanage commands to a personal server

# Items
Protomanage tracks 'items'. An item can be:
- A simple task with only a name and status
- A complex task with due dates, dependencies, and more
- A text file
- An automatically generated list of tasks
- A hardcoded list of tasks

Items are highly extensible and employ inheritance and mixins to create a large, flexible library of items.
You can configure your repo to support which item type you like.

# Inbox
Protomanage's 'inbox' features allows you to quickly note down thoughts, tasks, or notes for later.

You should FULLY clear your inbox FREQUENTLY to ensure you can trust that items in it will not be forgotten about!

You can ask Protomanage to run through your inbox items and prompt you for each one. Usually, each item will:
- Be deleted
- Be marked as 'done'
- Be transformed from an "inbox item" to another item type such as "simple task" or "complex task"

The last of these will often require you to enter more information, depending on the item type.

**Keeping your inbox clean is imperative.** If you find your inbox is growing and has large numbers of 'stale' items sitting in it, you will begin to fear that important items will be forgotten about, and stop trusting your inbox as a system.

# Repositories
Protomanage is built on a hierarchy of 'repositories' (or 'repos'). Each repo has its own configuration, extensions, and set of items.

You can create a separate repo for each project. There is also a 'home repo' located at ~/.protomanage.

Protomanage observes an "everything is local" philosophy, meaning the .protomanage folders contains the full state of a repository and can be moved around portably - with one exception: a complete list of repos on your drive is maintained at the home repo.

Generally, you will not need to worry about maintaining this list, because:
- When you run any command in a repo, it is automatically registered with the home repo.
- When you run any Protomanage command anywhere, the home repo automatically checks on its children.

If you move a repo, simply run "pm touch" to ensure it is registered correctly.
"pm touch -r" will recursively touch all repos from your current directory downward.

The only scenario which poses a risk is when a repo is moved, copied, downloaded, or otherwise created without using 'pm', and the user forgets to 'pm touch' it. This repos contents will not be visible from the home repo until an update occurs in it (any command is run in it).

## Creating repositories
When "init" is run, it creates a ".protomanage" folder at the current working directory.


# Commands
When any Protomanage command is run, it checks the current directory for a .protomanage, and moves up the directories until it finds one. If none are found, it will default to the home repository (~/.protomanage).

You can explicitly use the home repo with the "--home" or "-g" flag.

# Project structure
protomanage/                                   #
    views/                                     # Each view creates an object that can be imported into each plugin to configure the plugin's behaviour
        cli.py                                 # Creates the CLI app and defines its callback
    core_plugins/                              #
        inbox.py                               #
        simple_tasks.py                        #
    custom_plugins/                            #
        whatever.py                            #
    misc/                                      #
        strings.py                             # Strings for non-plugins
        words.py                               # Words utility (could make this a plugin down the line? not sure what the API is going to be like there)
        exceptions.py                          # Exception classes
    plugins.py                                 # Methods for importing core and custom plugins - needs to access config.json to know which ones to import!
    repo.py                                    # Repo and HomeRepo classes
    execution_context.py                       # ExecutionContext for noting context around a command
    item.py                                    # Item ABC and metaclass
    __init__.py                                # entry-point for module import - should give Python API
    __main__.py                                # entry-point for module invocation - should point to CLI

Basic execution order:
- the view creates an application object
- call plugins.py to import all the plugins, which will each configure the app to suit their needs (may need arbitration in case of conflicts)
- the view receives one or more commands - the callback or view entry point should:
    - set current_repo
    - set execution_context
    - call upon the appropriate plugin method
- plugin executes the command

__main__.py
    current_repo = find_current_repo
    app = cli.create_app()
    plugins_list = read config.json from current_repo
    plugins.configure_app(app, plugins_list )

Entry point (script), should:
    Create an 'app' object, which could be:
        cli
        pcli
        Python API
    
    Configure the app
        For each plugin, call plugin.configure_app(app) (it will need to infer the application type)

An entry point script creates an app object (could be imported but doesn't need to be tbh)
Configures the app by calling on the appropriate plugins
Runs the app by looping through a series of incoming commands
Saves and exits

cli:
    Create a typer 'app' object
    Get the current repository and read config.json
    For each plugin, call configure_app(app) to add new commands to app
    Execute the application

# New design philosophy
Okay, so we are leaning heavier into the "everything is local" plan:
- The home repo no longer tracks local repos - all repos behave exactly the same except for the fact that apps/views generally treat home as the default
- Plugins are no longer stored with the install - instead, they are repo specific
    - Each repo has a plugins/ folder
    - You can "pm plugin install" to add to this folder FOR THE CURRENT REPO
    - When you do, you can either install 'core' plugins (which will get copied from the install source) or from the web
        The fact that we are making a copy means it is frozen and will be future-proof!
        When a new update occurs, we can try automatically detect this and offer to migrate, but it is not required


Separate Item Files Idea:
- Consider having "items" stored as separate files instead?
- Name would be their uuid and they contain their data
- This makes them a bit more portable for moving between repos (for example)
- Also makes tracking with git a lot simpler
- and saves us from having a MASSIVE items.json file
- probably more expensive to load in?
- but if we get smart with loading in selectively, could be a lot more efficient
- maybe maintain a "cache index" JSON file of all the items which can be used for quicker access

.protomanage/
    config.json                          # no longer inherits absent values from home repo - but can still inherit defaults at install
                                         # Choose when creating a repo if you want a "full" config file (with 'null' in everything to
                                         # inherit) or an empty one
    repo_info.json                       # UUID, other stuff? PM version?
    items/
        10249084329685924802.json        # Each item gets its own file named for its UUID
        item_index_cache.json            # Maybe ? could get very complicated
    plugins/
        protomanage.core.inbox/          # See naming convention for plugins below
            inbox.py
            strings.py
            plugin_info.json             # # Version number? or store this with each item?
        protomanage.thomas6785.obsidian/ # See naming convention for plugins below
            obsidian.py
            strings.py
            plugin_info.json             # Version number? or store this with each item?

Plugin unique naming:
    protomanage.devusername.plugin-name
Item type unique naming:
    protomanage.devusername.plugin-name.item-name