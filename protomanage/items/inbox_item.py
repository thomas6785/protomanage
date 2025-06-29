"""Module to define InboxItem item type"""

from dataclasses import dataclass

from .item import Item,ItemMeta
from ..execution_context import ExecutionContext

class InboxItem(Item,metaclass=ItemMeta):
    """The simplest item: an inbox item."""

    DISPLAY_NAME = "Inbox Item"
    UNIQUE_NAME = "protomanage.core.inbox-item"
    VERSION = "0.1"

    def __init__(self,context : ExecutionContext, text : str):
        self.context = context
        self.text = text

    def __str__(self) -> str:
        """Return a string representation of the InboxItem."""
        return self.formatted_uid + " - " + self.text

    def _to_dict(self):
        """TODO docs: write docstring"""

        return {
            "context": self.context.to_dict(),
            "text": self.text
        }

    @classmethod
    def _from_dict(cls,data : dict,item_type : dict):
        """TODO docs: write docstring"""

        context = ExecutionContext.from_dict(data["context"])
        text = data["text"]
        return cls(context=context, text=text)
