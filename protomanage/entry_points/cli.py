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
from ..misc import strings
from ..base import repo as repo_lib
from ..base.execution_context import ExecutionContext

app = typer.Typer(
    no_args_is_help=True,
    help=strings.PROTOMANAGE_CLI_DESCRIPTION
)

APP_NAME = "protomanage"

@app.callback(invoke_without_command=True)
def app_callback(
    verbose : Annotated[bool, typer.Option("--verbose", "-v")] = False
):
    """TODO docs write docstring"""

    if verbose:
        print("Hello from the application callback!")

execution_context = ExecutionContext()
current_repo = repo_lib.find_repo(execution_context.cwd)
current_repo.configure_app(app,execution_context)

app()
