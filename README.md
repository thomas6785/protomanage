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