"""Module to define InboxItem item type"""

from dataclasses import dataclass

from .item import Item
from ..execution_context import ExecutionContext

@dataclass
class InboxItem(Item):
    """The simplest item: an inbox item."""
    context: ExecutionContext = None
    text: str = ""

    DISPLAY_NAME = "Inbox Item"
    UNIQUE_NAME = "protomanage.core.inbox-item"
    VERSION = "0.1"

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
