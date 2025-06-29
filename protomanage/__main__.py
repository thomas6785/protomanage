"""TODO docs: write docstring"""

from pathlib import Path

from .core import *
from .cli import app
from . import repo
from .execution_context import ExecutionContext

def main():
    """Main entry point for the Protomanage CLI."""

    current_repo = repo.find_repo(Path.cwd())
    context = ExecutionContext()

    app()

if __name__ == "__main__":
    main()
