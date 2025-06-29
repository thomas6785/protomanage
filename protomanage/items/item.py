"""Module defines 'Item' class."""

import uuid
from abc import ABC, abstractmethod

from ..words import wordify

def new_string_obj(s):
    """Creates a new string object with the same content as argument 's'"""
    return ''.join(s)

class Item(ABC):
    """Base class for items in Protomanage."""

    DISPLAY_NAME = "Item base class"
    UNIQUE_NAME = "protomanage.core.item-abstract-base-class"
    VERSION = "0.1"
    CHILD_CLASSES = []

    def __init_subclass__(cls):
        if cls.DISPLAY_NAME is cls.__base__.DISPLAY_NAME:
            raise ValueError("Subclass must override DISPLAY_NAME from its base class.")
        cls.DISPLAY_NAME = new_string_obj(cls.DISPLAY_NAME)

        if cls.UNIQUE_NAME is cls.__base__.UNIQUE_NAME:
            raise ValueError("Subclass must override UNIQUE_NAME from its base class.")
        cls.UNIQUE_NAME = new_string_obj(cls.UNIQUE_NAME)

        if cls.VERSION is cls.__base__.VERSION:
            raise ValueError("Subclass must override VERSION from its base class.")
        cls.VERSION = new_string_obj(cls.VERSION)

        cls.__base__.CHILD_CLASSES.append(cls)

    def __init__(self):
        """Initialize an item."""

        self._uuid = str(uuid.uuid4())

    @property
    def uuid(self) -> str:
        """Get the unique identifier of the item."""
        return self._uuid

    @property
    def formatted_uid(self) -> str:
        """Get the formatted unique identifier of the item."""
        return f"[{self.uuid[-10:-5]}_{self.uuid[-5:]}]"

    @property
    def word_uid(self) -> str:
        """Get the 'wordy' unique identifier of the item."""
        return wordify(self.uuid[-8:])

    def to_dict(self) -> str:
        """
        Transform the item instance into a dictionary.

        The resulting dict contains two main sections:
          - "type": An object with metadata about the item's type (Python class), including display name, unique name, and version.
          - "data": An object representing the item's data, as returned by the `_to_dict()` method.

        Returns:
            dict: A dictionary with all the item's data and metadata
        """
        return {
            "type": {
                "display_name": self.__class__.DISPLAY_NAME,
                "unique_name": self.__class__.UNIQUE_NAME,
                "version": self.__class__.VERSION
            },
            "data": self._to_dict()
        }

    @classmethod
    def from_dict(cls, dict : dict) -> "Item":
        """TODO docs: write docstring"""

        type_info = dict["type"]
        unique_name = type_info["unique_name"]
        version = type_info["version"]

        for child in cls.CHILD_CLASSES:
            if child.UNIQUE_NAME == unique_name and child.VERSION == version:
                return child._from_dict(dict["data"],dict["type"])

        raise ValueError(f"No matching Item subclass for UNIQUE_NAME={unique_name} and VERSION={version}")

    @classmethod
    @abstractmethod
    def _from_dict(cls,data,item_type) -> "Item":
        """Child classes must implement this"""

    @abstractmethod
    def _to_dict(self) -> str:
        """Child classes must implement this"""
