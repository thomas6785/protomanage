"""Create classes for Protomanage repositories, home repository, and repository config."""

from pathlib import Path
from dataclasses import dataclass
import uuid as uuid_lib
import logging
from typing import List
import json

from .item import Item
from . import strings
from .execution_context import ExecutionContext

REPO_FOLDER_NAME = ".protomanage"
HOME_REPO_PATH = (Path("~") / REPO_FOLDER_NAME).expanduser()

@dataclass
class RepoConfig():
    """Dataclass to store config for a Protomanage repository."""

    default_text_editor : str = None

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
        if not isinstance(self, HomeRepo):
            self.home_repo = HomeRepo()
            self._touch()
        else:
            self.home_repo = self

        self._config     = self._load_config()
        self._uuid       = self._load_uuid()
        self._items      = self._load_items()
        self._pm_version = self._load_version()

    def _touch(self) -> None:
        """Ensures the repo is registered with the home repo"""
        self.home_repo.register_repo(self)

    def _load_config(self) -> RepoConfig:
        """Load the repo config. Take the local config.json first, then the home repo config.json, then the defaults from Protomanage."""

        config = RepoConfig()

        config_files = [
            self.repo_path / "config.json",
            HOME_REPO_PATH / "config.json",
            Path(__file__).parent / "default_config.json"  # Default config file in the Protomanage package
        ]
        if isinstance(self, HomeRepo):
            config_files.pop(1)

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

        items_file = self._repo_path / "items.json"
        if not items_file.exists():
            self._logger.error(f"Items file {items_file} missing.")
            raise FileNotFoundError(f"Items file {items_file} missing.")

        try:
            items_data = json.loads(items_file.read_text())
            items = [Item.from_dict(i) for i in items_data]
            return items
        except json.JSONDecodeError as e:
            self._logger.error(f"Invalid JSON in {items_file}: {e}")
            raise ValueError(f"Invalid JSON in {items_file}: {e}") from e

    def _load_version(self) -> str:
        """Get the Protomanage version from the PM_VERSION file."""

        version_file = self._repo_path / "PM_VERSION"
        if not version_file.exists():
            self._logger.error(f"Version file {version_file} missing.")
            raise FileNotFoundError(f"Version file {version_file} missing.")

        return version_file.read_text().strip()

    def __str__(self) -> str:
        """String representation of the repo, showing the path and UUID."""

        return f"Repo(path={self._repo_path}, uuid={self._uuid})"

    def add_item(self, item: Item) -> None:
        """Add an item to the repo's items list."""

        if not isinstance(item, Item):
            raise TypeError("item must be an instance of Item")

        self._items.append(item)
        self._save_items()

    def _save_items(self) -> None:
        """Save the items to the items.json file."""

        items_file = self._repo_path / "items.json"

        pretty_json = json.dumps([item.to_dict() for item in self.items], indent=4)
        items_file.write_text(pretty_json)

    @staticmethod
    def create_new(repo_path : Path) -> None:
        """Create a new Protomanage repo at the specified location."""

        repo_path.mkdir(parents=True, exist_ok=True)

        uuid = str(uuid_lib.uuid4())

        # Create boilerplate repo
        (repo_path / "config.json"     ).write_text("{}")
        (repo_path / "items.json"      ).write_text("{}")
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

class HomeRepo(Repo):
    """The home repo is a special repo at ~. In addition to being a normal repo, it contains a list of all other repos, and all other repos inherit config from it."""

    def __init__(self):
        """Load in a home repo."""

        if not HOME_REPO_PATH.exists():
            self.create_new(HOME_REPO_PATH)

        super().__init__(HOME_REPO_PATH)

        # Load the repo list
        repo_list_path = self._repo_path / "repo_list.json"

        if not repo_list_path.exists():
            self._logger.error(f"Repo list file {repo_list_path} was not found!")
            raise FileNotFoundError(f"Repo list file {repo_list_path} was not found!")

        self.repo_list = json.loads(repo_list_path.read_text())

    @staticmethod
    def create_new(repo_path : Path) -> None:
        """Create a new home repo."""

        if repo_path != HOME_REPO_PATH:
            raise ValueError(f"Home repo must be created at {HOME_REPO_PATH}, not {repo_path}")

        Repo.create_new(repo_path)
        ( repo_path / "repo_list.json" ).write_text("{}") # Create the repo list file

    def register_repo(self,repo : Repo):
        """Register a new repo with the home repo."""

        # Load existing repo list
        repo_list_path = self._repo_path / "repo_list.json"
        if not repo_list_path.exists():
            self._logger.warning(f"Repo list file {repo_list_path} does not exist, creating a new one.")
            repo_list = {}
        else:
            repo_list = json.loads(repo_list_path.read_text())

        # Add the new repo
        repo_list[repo.uuid] = str(repo.repo_path)

        # Save the updated list
        repo_list_path.write_text(json.dumps(repo_list, indent=4))

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
    return HomeRepo()

def get_home_repo() -> HomeRepo:
    """Return the Protomanage home repo"""
    
    return HomeRepo()

if __name__ == "__main__":
    my_repo = find_repo(Path.cwd())
    print(f"Found repo: {my_repo}")
