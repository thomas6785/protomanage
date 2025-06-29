"""
inbox is a core plugin that enables you to create a list of items that you want
to work on later. Inspired by David Allen's "Getting Things Done" (and many
subsequent texts which have adopted the same principles), the inbox is a place
to collect tasks, ideas, and other items that you want to process later.

Critically, the inbox is not a place to store items indefinitely. It is a
temporary holding area. It MUST be cleared very regularly to ensure you can
'trust' it. Once something is in your inbox, you are free to put it out of your
mind, knowing that it will be processed later. If you allow your inbox to fill
up with 'stale' items, you will begin to unconsciously worry that items you put
in there will be lost among the noise. This will result in your inbox becoming
a source of stress rather than a place of calm.
"""

from typing import List
import typer

from ..item import Item,ItemMeta
from ..execution_context import ExecutionContext
from .. import cli
from .. import repo as repo_lib
from .. import strings # TOOD migrate this to local strings

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

def _add_to_inbox(text : str, repo : repo_lib.Repo, context : ExecutionContext) -> None:
    """Add a simple InboxItem to the repo's item list."""

    item = InboxItem(context=context, text=text)  # Create an InboxItem instance
    cli.current_repo.add_item(item)  # Add the item to the repo's items
    #cli.logger.info(strings.INBOX_ITEM_ADDED) TODO add logging here

@cli.app.command()
def inbox(text: List[str]) -> None:
    """Add a simple InboxItem to the repo's item list."""

    _add_to_inbox(
        text = " ".join(text),
        repo = cli.current_repo,
        context = cli.execution_context
    )
    #current_repo._logger.info(strings.INBOX_ITEM_ADDED) TODO add logging here

def _show_inbox(repo : repo_lib.Repo, context : ExecutionContext) -> None:
    """Retrieve all InboxItems from the repo's item list and display to the user"""

    inbox_items = [item for item in repo.items if isinstance(item,InboxItem)]
    if not inbox_items:
        print("No items in inbox!")
    else:
        for item in inbox_items:
            print(str(item))

@cli.app.command()
def show_inbox() -> None:
    """Retrieve all InboxItems from the repo's items list."""

    _show_inbox(
        repo = cli.current_repo,
        context = cli.execution_context
    )
