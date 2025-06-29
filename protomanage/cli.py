"""
TODO docs: write docstring
"""

# Standard imports
from typing import List
from pathlib import Path

# Third-party imports
import typer

# Local imports
from . import base
from . import strings
from . import repo as repo_lib
from .execution_context import ExecutionContext

app = typer.Typer(
    no_args_is_help=True,
    help=strings.PROTOMANAGE_CLI_DESCRIPTION
)

APP_NAME = "protomanage"

@app.command(rich_help_panel="Configuration")
def config():
    """Edit the Protomanage configuration file."""
    base.open_config_file()

@app.command(rich_help_panel="Inbox")
def inbox(text: List[str]):
    """
    Adds a text entry to the Protomanage inbox.

    Args:
        text (str): The text to be added to the inbox.
    """
    current_repo.add_to_inbox(
        text = " ".join(text),
        context = context
    )

@app.command(rich_help_panel="Inbox")
def show_inbox():
    """
    TODO docs write docstring
    """
    current_repo.show_inbox()

def main():
    """Main entry point for the Protomanage CLI."""
    global current_repo, context

    current_repo = repo_lib.find_repo(Path.cwd())
    context = ExecutionContext()

    app()
