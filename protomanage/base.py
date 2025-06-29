"""
TODO docs: write docstring
"""

import subprocess
import tempfile
import os

def open_file_for_edit(file_path):
    """TODO docs: write docstring"""
    editor = config.default_text_editor
    subprocess.run([editor, file_path], check=True)

def let_user_edit_string(string):
    """
    Allows the user to edit a given string using their default text editor.

    This function writes the provided string to a temporary file, opens the file for editing
    using open_file_for_edit() and then reads back the edited contents. The temporary file
    is deleted after editing.

    Args:
        string (str): The initial string to be edited by the user.

    Returns:
        str: The string after being edited by the user.

    Raises:
        Any exception raised by `open_file_for_edit` or file operations will propagate.
    """
    with tempfile.NamedTemporaryFile(mode="w+", delete=False, suffix=".temp") as tmp_file:
        tmp_file.write(string)
        tmp_file_path = tmp_file.name

    try:
        open_file_for_edit(tmp_file_path)
        with open(tmp_file_path, "r",encoding="utf8") as f:
            edited_string = f.read()
    finally:
        os.remove(tmp_file_path)

    return edited_string

def open_config_file():
    """TODO docs: write docstring"""

    open_file_for_edit(env.CONFIG_FILE_PATH)


def add_to_inbox(context,text):
    """TODO docs: write docstring"""

    pass
