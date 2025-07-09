"""Create classes for Protomanage repositories, home repository, and repository config."""

from pathlib import Path
from dataclasses import dataclass
import importlib.util
import uuid as uuid_lib
import logging
from typing import List
import json
import sys
import os

from .item import Item

REPO_FOLDER_NAME = ".protomanage"
HOME_REPO_PATH = (Path("~") / REPO_FOLDER_NAME).expanduser()

class MultiItemEditSession:
    """
    Context manager for editing multiple items. Instantiates ItemEditSession for each one.

    Sample usage:
        with MultiItemEditSession( inbox_items ) as inbox_items:
            # do stuff to those items knowing they are safely
            # backed up and will be saved when you're done
    """

    def __init__(self, items: List["Item"]):
        self.items = items
        self._logger = logging.getLogger(__name__)
        self.sessions = []

    def __enter__(self) -> List["Item"]:
        """Create an edit session for each item"""
        for item in self.items:
            item_edit_session = ItemEditSession(item)
            item_edit_session.__enter__()
            self.sessions.append(item_edit_session)

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Close the edit sessions open for each item"""
        for item_edit_session in self.sessions:
            item_edit_session.__exit__(exc_type, exc_val, exc_tb)
        return False # do not suppress exceptions

class ItemEditSession:
    """
    Context manager for editing items. Provides transaction-like behavior
    where changes are only saved if the context exits successfully.
    """
    locked_items = []

    def __init__(self, item: "Item"):
        self.item = item
        self._logger = logging.getLogger(__name__)

    def __enter__(self) -> "Item":
        """Enter the editing session and create a backup."""
        if self.item in ItemEditSession.locked_items:
            raise ItemLockedError(f"Item {self.item} is already opened for edit in another ItemEditSession")

        ItemEditSession.locked_items.append(self.item)

        # Create backup of original item data
        self.item._create_backup()

        self._logger.debug(f"Started edit session for item {self.item}")
        return self.item

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the editing session and handle saving/rollback."""

        if exc_type is None:
            self.item._save()
            self._logger.debug(f"Saved item {self.item}")
            self.item._delete_backup()
            self._logger.debug(f"Deleted backup for item {self.item}")
        else:
            # Exception occurred - rollback changes
            self._logger.error(
                f"Exception in edit session, item {self.item} may not have been saved. Find backup at {self.item._backup_path}"
            )

        # Remove the item from locked_items regardless of exception
        if self.item in ItemEditSession.locked_items:
            ItemEditSession.locked_items.remove(self.item)

        return False  # Don't suppress exceptions

@dataclass
class RepoConfig():
    """Dataclass to store config for a Protomanage repository."""

    def __init__(self, config_file_path : Path = None):
        self._logger = logging.getLogger(__name__)
        self.config_file_path = config_file_path
        self.customised_keys = []

        self.__init_defaults()
        self._logger.debug("Set default config values")

        if config_file_path:
            self._logger.debug(f"Loading config values from {config_file_path}")
            self.__load_from_file()
            self._logger.debug(f"Finished loading config values")
        else:
            self._logger.debug(f"Got no config file path, using default values")

    def __init_defaults(self) -> None:
        self.default_text_editor    : str     = os.environ.get("EDITOR") or ("notepad" if os.name == "nt" else "vim")
        self.use_pretty_json        : bool    = False
        self.plugin_configs         : dict    = {}
        # Want to add new config keys? Just put them right here.

    def __load_from_file(self) -> None:
        if not self.config_file_path or not Path(self.config_file_path).exists():
            self._logger.warning(f"Config file {self.config_file_path} does not exist.")
            return

        with open(self.config_file_path, "r", encoding="utf8") as f:
            try:
                config_data = json.load(f)
            except json.JSONDecodeError as e:
                self._logger.error(f"Invalid JSON in config file {self.config_file_path}: {e}")
                raise

        for key, value in config_data.items():
            self.__set_key(key,value)

        self.__save_to_file()

    def set_key(self,key,value):
        self.__set_key(key,value)
        self.__save_to_file()

    def __set_key(self,key,value):
        if hasattr(self, key):
            self._logger.debug(f"Setting config attribute '{key}' to '{value}'")
            setattr(self, key, value)
            self.customised_keys.append(key)
        else:
            self._logger.error(f"Unknown config key '{key}'")
            raise ValueError(f"Unknown config key '{key}'")

    def __save_to_file(self):
        config_to_save = {key: getattr(self, key) for key in self.customised_keys}
        with open(self.config_file_path, "w", encoding="utf8") as f:
            json.dump(config_to_save, f, indent=4 if self.use_pretty_json else None)
        self._logger.debug(f"Saved user's customised config keys to {self.config_file_path}")

class Repo():
    """A Protomanage repository class."""

    def __init__(self,repo_path : Path):
        """Load in a Protomanage repo from the specified path."""

        self._logger     = logging.getLogger(__name__)

        # Check the path provided is valid
        if not repo_path.is_dir():
            raise FileNotFoundError(f"repo path '{repo_path}' does not exist or is not a directory.")
        if repo_path.name != REPO_FOLDER_NAME:
            raise ValueError(f"repo path '{repo_path}' does not end with expected {REPO_FOLDER_NAME}")

        self._repo_path = repo_path
        self._load_config()
        self._uuid       = self._load_uuid() # TODO rewrite to assign var inside the method
        self._plugins    = self._load_plugins() # TODO rewrite to assign var inside the method
        self._items      = self._load_items() # TODO rewrite to assign var inside the method
        self._pm_version = self._load_version() # TODO rewrite to assign var inside the method

    def _load_config(self):
        """Load the repo config. Take the local config.json first, then the defaults from the install."""

        config = RepoConfig()
        config_file = self.repo_path / "config.json"

        if config_file.exists():
            try:
                self._logger.debug(f"Loading config from {config_file}")
                config_data = json.loads(config_file.read_text())
                for key, value in config_data.items():
                    if not hasattr(config, key):
                        self._logger.error(f"Unknown config key '{key}' in {config_file}")
                        raise ValueError(f"Unknown config key '{key}' in {config_file}")
                    if value is not None:
                        self._logger.debug(f"Setting config '{key}' to '{value}' from {config_file}")
                        setattr(config, key, value)
                    else:
                        self._logger.debug(f"Config key '{key}' in {config_file} is None, default value will be used.")
            except json.JSONDecodeError as e:
                self._logger.error(f"Invalid JSON in {config_file}: {e}")
                raise ValueError(f"Invalid JSON in {config_file}: {e}") from e

        self._config = config

    def update_config(self) -> None:
        self._load_config()

    def _load_uuid(self) -> str:
        """Get the UUID of the repo from the uuid file."""

        uuid_file = self._repo_path / "uuid"
        if not uuid_file.exists():
            self._logger.error(f"UUID file {uuid_file} missing.")
            raise FileNotFoundError(f"UUID file {uuid_file} missing.")

        return uuid_file.read_text().strip()

    def _load_items(self) -> List[Item]:
        """Load the items from the items.json file."""

        items_dir = self._repo_path / "items"
        if not items_dir.is_dir():
            self._logger.warning(f"Items directory {items_dir} missing. Creating a new one.")
            items_dir.mkdir()

        items = []
        for item_file in items_dir.iterdir():
            if item_file.is_file() and item_file.suffix == ".json":
                # Read in the file JSON
                try:
                    item_data = json.loads(item_file.read_text())
                except Exception as e:
                    self._logger.error(f"Failed to load item from {item_file}: {e}")
                    raise ValueError(f"Failed to load item from {item_file}: {e}") from e

                # Validate the file name matches the UUID in the JSON
                if item_file.stem != item_data.get("uuid"):
                    self._logger.error(f"UUID mismatch: file {item_file.name} vs item_data uuid {item_data.get("uuid")}")
                    raise ValueError(f"UUID mismatch: file {item_file.name} vs item_data uuid {item_data.get("uuid")}") from e

                # Convert to an Item and store it
                items.append(Item.from_dict(item_data))

        return items

    def _load_version(self) -> str:
        """Get the Protomanage version from the PM_VERSION file."""

        version_file = self._repo_path / "PM_VERSION"
        if not version_file.exists():
            self._logger.error(f"Version file {version_file} missing.")
            raise FileNotFoundError(f"Version file {version_file} missing.")

        return version_file.read_text().strip()

    def __str__(self) -> str:
        """String representation of the repo, showing the path and UUID."""

        return f"Repo(path={self.repo_path}, uuid={self.uuid})"

    def add_item(self, item: Item) -> None:
        """Add an item to the repo's items list."""

        if not isinstance(item, Item):
            raise TypeError("item must be an instance of Item")

        self._items.append(item)
        self._save_items()

    def _save_items(self) -> None:
        """Save the items to the items.json file."""

        items_dir = self._repo_path / "items"

        if not items_dir.is_dir():
            self._logger.warning(f"Items directory {items_dir} missing. Creating a new one.")
            items_dir.mkdir()

        for item in self.items:
            item_file = items_dir / f"{item.uuid}.json"
            item_json = json.dumps(item.to_dict(), indent=4 if self.config.use_pretty_json else None)
            item_file.write_text(item_json)

    def _load_plugins(self) -> None:
        """Load in plugins (module objects) and returns a list of these objects"""
        plugins = []
        plugins_dir = self.repo_path / "plugins"

        if plugins_dir.exists() and plugins_dir.is_dir():
            for plugin_path in plugins_dir.iterdir():
                init_file = plugin_path / "__init__.py"
                module_name = f"{plugin_path.name}"
                if init_file.exists():
                    plugins.append( _import_from_path(module_name,init_file) )
                else:
                    raise Exception(f"Plugin at directory {plugin_path} has no __init__.py file")

        return plugins

    def configure_app(self, app, execution_context) -> None:
        """Takes an arbitrary 'app' and passes it on to each plugin for configuration"""

        for plugin in self.plugins:
            if hasattr(plugin, "configure_app"):
                plugin.configure_app(app, self, execution_context)
            else:
                self._logger.error(f"Plugin package {plugin.__name__} does not have a configure_app function.")
                raise Exception(f"Plugin package {plugin.__name__} does not have a configure_app function.")

    @staticmethod
    def create_new(repo_path : Path) -> None: # TODO move this to init_repo.py ?
        """Create a new Protomanage repo at the specified location."""

        repo_path.mkdir(parents=True, exist_ok=True)

        uuid = str(uuid_lib.uuid4())

        # Create boilerplate repo
        (repo_path  / "items"          ).mkdir()
        (repo_path / "config.json"     ).write_text("{}") # TODO add option to create a config.json populated with nulls instead
        (repo_path / "PM_VERSION"      ).write_text("TODO version numbering")
        (repo_path / "uuid"            ).write_text(uuid)

    @property
    def plugins(self) -> List["module"]:
        return self._plugins

    @property
    def uuid(self) -> str:
        """Get the UUID of the repo."""
        return self._uuid

    @property
    def config(self) -> RepoConfig:
        """Get the repo config."""
        return self._config

    @property
    def items(self) -> List[Item]:
        """Get the items in the repo."""
        return self._items

    @property
    def pm_version(self) -> str:
        """Get the Protomanage version of the repo."""
        return self._pm_version

    @property
    def repo_path(self) -> Path:
        """Get the path to the repo."""
        return self._repo_path

def find_repo(cwd : Path) -> Repo:
    """Find a Protomanage repo starting from the current working directory and moving up the directory tree."""

    current_path = cwd
    while current_path != current_path.parent:
        repo_path = current_path / REPO_FOLDER_NAME
        if repo_path.exists() and repo_path.is_dir():
            try:
                return Repo(repo_path)
            except FileNotFoundError as e:
                logging.error(f"Failed to load repo at {repo_path}: {e}")
                raise FileNotFoundError(f"Failed to load repo at {repo_path}: {e}") from e
        current_path = current_path.parent
    return get_home_repo()

def get_home_repo() -> Repo:
    """Return the Protomanage home repo"""

    return Repo(HOME_REPO_PATH)

def _import_from_path(module_name, file_path):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module
