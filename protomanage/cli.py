"""
TODO docs: write docstring
"""

import argparse
from dataclasses import dataclass
import sys

from . import strings

def subcommand_help():
    """TODO docs: write docstring"""
    pass

def subcommand_config():
    """TODO docs: write docstring"""
    pass

def subcommand_inbox():
    """TODO docs: write docstring"""
    pass

def handle_invalid_command():
    """TODO docs: write docstring"""
    pass

@dataclass
class Subcommand:
    """TODO docs: write docstring"""
    help_text: str
    method: callable

subcommands = {
    "config":          Subcommand(strings.CLI_SUBCOMMAND_CONFIG_HELP,       subcommand_config),
    "help":            Subcommand(strings.CLI_SUBCOMMAND_HELP_HELP,         subcommand_help),
    "inbox":           Subcommand(strings.CLI_SUBCOMMAND_INBOX_HELP,        subcommand_inbox),
}

def main():
    """TODO docs: write docstring"""

    subcommand_str = sys.argv[1]

    # Match the subcommand
    if subcommand_str not in subcommands:
        handle_invalid_command()
        sys.exit(1)
    else:
        subcommand = subcommands[subcommand_str]
        subcommand.method()

if __name__ == "__main__":
    main()
