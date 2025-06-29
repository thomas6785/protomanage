"""
This module creates a Typer app
It creates the app with its basic help text and callback
It also sets the current_repo and execution_context objects
which are available for use in modules

Core and extension modules can import cli to access to app and add commands
as well as to access current_repo and execution_context in these commands

TODO wrap current_repo into execution_context and improve its flexibility to non-CLI accesses?
"""

# Third-party imports
import typer
from typing_extensions import Annotated

# Local imports
from . import base
from . import strings
from . import repo as repo_lib
from .execution_context import ExecutionContext

app = typer.Typer(
    no_args_is_help=True,
    help=strings.PROTOMANAGE_CLI_DESCRIPTION
)

APP_NAME = "protomanagee"

@app.command(rich_help_panel="Configuration")
def config():
    """Edit the Protomanage configuration file."""
    base.open_config_file()

@app.callback(invoke_without_command=True)
def app_callback(
    verbose : Annotated[bool, typer.Option("--verbose", "-v")] = False,
    home_repo : Annotated[bool, typer.Option("--home-repo", "-g")] = False
):
    """TODO docs write docstring"""

    if verbose:
        print("Hello from the application callback!")

    global current_repo, execution_context

    execution_context = ExecutionContext()
    if home_repo:
        current_repo = repo_lib.find_repo
    else:
        current_repo = repo_lib.find_repo(execution_context.cwd)
