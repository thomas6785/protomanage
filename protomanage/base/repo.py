"""Create classes for Protomanage repositories, home repository, and repository config."""

from pathlib import Path
from dataclasses import dataclass
import uuid as uuid_lib
import logging
from typing import List
import json

from .item import Item

REPO_FOLDER_NAME = ".protomanage"
HOME_REPO_PATH = (Path("~") / REPO_FOLDER_NAME).expanduser()

@dataclass
class RepoConfig():
    """Dataclass to store config for a Protomanage repository."""
    # Everything should be initialised to 'None' so it can be overwritten by config.json first and than by default_config.json

    default_text_editor : str = None
    use_pretty_json : bool = False

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
        self._config     = self._load_config()
        self._uuid       = self._load_uuid()
        self._items      = self._load_items()
        self._pm_version = self._load_version()

    def _load_config(self) -> RepoConfig:
        """Load the repo config. Take the local config.json first, then the defaults from the install."""

        config = RepoConfig()

        config_files = [
            self.repo_path / "config.json",
            Path(__file__).parent / "default_config.json"  # Default config file in the Protomanage package
        ]

        for config_file in config_files:
            if config_file.exists():
                try:
                    self._logger.debug(f"Loading config from {config_file}")
                    config_data = json.loads(config_file.read_text())
                    for key, value in config_data.items():
                        if not hasattr(config, key):
                            self._logger.error(f"Unknown config key '{key}' in {config_file}")
                            raise ValueError(f"Unknown config key '{key}' in {config_file}")
                        if getattr(config, key, None) is not None:
                            self._logger.debug(f"Setting config '{key}' to '{value}' from {config_file}")
                            setattr(config, key, value)
                        else:
                            self._logger.debug(f"Config '{key}' is already set to '{value}', skipping from {config_file}")
                except json.JSONDecodeError as e:
                    self._logger.error(f"Invalid JSON in {config_file}: {e}")
                    raise ValueError(f"Invalid JSON in {config_file}: {e}") from e

        return config

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
