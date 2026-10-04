"""Filesystem paths for the manual's bundled assets/templates."""

# Lazy imports (PEP 810), ignored before Python 3.15
from stouputils.lazy import ALWAYS_LAZY

__lazy_modules__ = ALWAYS_LAZY

# Imports
import atexit
import os
import shutil
import tempfile

import stouputils as stp

MANUAL_ASSETS_PATH: str = stp.get_root_path(__file__)
""" Root of this plugin package. """
TEMPLATES_PATH: str = tempfile.mkdtemp(prefix="stewbeet_manual_v2_templates_").replace("\\", "/")
""" Runtime templates folder, filled with the assets at build time and overlaid with the project's manual_overrides.

It is a per-process temporary directory, so concurrent builds never share it, removed on interpreter exit.
"""
atexit.register(shutil.rmtree, TEMPLATES_PATH, ignore_errors=True)


def template_path(filename: str) -> str:
	""" Path to a template file: the runtime templates dir once copy_templates() populated it
	(so manual_overrides win), else the bundled asset (lets code run before the beet entrypoint,
	e.g. in doctests). """
	runtime: str = f"{TEMPLATES_PATH}/{filename}"
	if os.path.exists(runtime):
		return runtime
	return f"{MANUAL_ASSETS_PATH}/assets/{filename}"

