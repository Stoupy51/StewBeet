

# Lazy imports (PEP 810), ignored before Python 3.15
from stouputils.lazy import ALWAYS_LAZY

__lazy_modules__ = ALWAYS_LAZY

# Imports
import os

import stouputils as stp
from beet import ProjectConfig, load_config, locate_config


def get_project_config() -> ProjectConfig:
	""" The beet configuration of the project the current directory belongs to, which becomes the current directory.

	Raises:
		AssertionError: When neither the current directory nor a parent holds a beet configuration.
	"""
	directory: str = os.getcwd()
	cfg: ProjectConfig | None = None
	if config_path := locate_config(directory, parents=True):
		cfg = load_config(filename=config_path)
		if cfg:
			os.chdir(config_path.parent)
	assert cfg is not None, f"No beet config file found in the current directory '{stp.clean_path(directory)}'"
	return cfg

