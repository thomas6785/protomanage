"""Module defines 'Item' class."""

import uuid
from abc import ABC, ABCMeta, abstractmethod

from ..words import wordify

def new_string_obj(s):
    """Creates a new string object with the same content as argument 's'"""
    return ''.join(s)

class ItemMeta(ABCMeta):
    """
    Use a metaclass to enforce:
    - Class metadata should be set explicitly and not inherited
    - Class constructor should call base class constructor
    - from_dict(to_dict) should always return the same data
    """
    def __new__(mcs, name, bases, namespace, **kwargs):
        cls = super().__new__(mcs, name, bases, namespace, **kwargs)

        if len(bases) > 0:
            ################################################################################
            # Enforce that the new class's __init__ calls its base class' __init__
            ################################################################################
            if "__init__" in cls.__dict__:
                orig_init = cls.__init__

                def wrapped_init(self, *args, **kwargs):
                    # Call base class __init__ first
                    for base in cls.__mro__[1:]:
                        if "__init__" in base.__dict__:
                            base.__init__(self)
                        orig_init(self, *args, **kwargs)

                cls.__init__ = wrapped_init

            ################################################################################
            # Enforce that the new class's __init_subclass__ calls the base class' __init_subclass__
            ################################################################################
            if "__init_subclass__" in cls.__dict__:
                orig_init_subclass = cls.__init_subclass__

                def wrapped_init_subclass(self,*args,**kwargs):
                    # Call base class __init_subclass__ first
                    for base in cls.__mro__[1:]:
                        if "__init_subclass__" in base.__dict__:
                            base.__init_subclass__(self)
                        orig_init_subclass(self,*args,**kwargs)

                cls.__init_subclass__ = wrapped_init_subclass

            ################################################################################
            # Verify that class meta data has been set explicitly
            ################################################################################
            assert "DISPLAY_NAME" in cls.__dict__
            assert "UNIQUE_NAME" in cls.__dict__
            assert "VERSION" in cls.__dict__
            assert cls.UNIQUE_NAME != cls.__base__.UNIQUE_NAME

        cls.CHILD_CLASSES = []

        return cls

class Item(metaclass=ItemMeta):
    """Base class for items in Protomanage."""

    DISPLAY_NAME = "Item base class"
    UNIQUE_NAME = "protomanage.core.item-abstract-base-class"
    VERSION = "0.1"

    def __init_subclass__(cls):
        assert isinstance(cls,ItemMeta), "Subclass must use ItemMeta or a descendant as its metaclass"
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
            "uuid": self.uuid,
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
