

# Imports
import os

from beet import ProjectConfig, load_config, locate_config
from stouputils.io import clean_path
from stouputils.print import error


# Try to find and load the beet configuration file
def get_project_config(directory: str = os.getcwd()) -> ProjectConfig | None:
    """ Get the project configuration from the current directory.

    If no configuration file is found, it returns None and prints an error message.

    Args:
        directory (str): The directory to search for the configuration file. Defaults to the current working directory.
    """
    cfg: ProjectConfig | None = None
    if config_path := locate_config(directory, parents=True):
        cfg = load_config(filename=config_path)
        if cfg:
            os.chdir(config_path.parent)
    if not cfg:
        error(f"No beet config file found in the current directory '{clean_path(directory)}'")
    return cfg

