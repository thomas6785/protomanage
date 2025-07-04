import json

from protomanage.misc.text_edit import open_string_for_edit

def _configure_cli_app(app,current_repo,execution_context):
    @app.command(rich_help_panel="Config")
    def config_edit() -> None:
        """Edit the config.json file for this repo."""

        config_file = current_repo.repo_path / "config.json"
        config_json = json.dumps(json.loads(config_file.read_text()), indent=4) # load then dump again so we can prettify
        config_json = open_string_for_edit(config_json,editor=current_repo.config.default_text_editor)
        if current_repo.config.use_pretty_json:
            config_json = json.dumps(json.loads(config_json), indent=4)
        else:
            config_json = json.dumps(json.loads(config_json), indent=None)
        config_file.write_text(config_json)
        current_repo.update_config()

def configure_app(app,current_repo,execution_context):
    """TODO docs write docstring"""
    # TODO detect (or pass in?) the app type
    _configure_cli_app(app,current_repo,execution_context)
