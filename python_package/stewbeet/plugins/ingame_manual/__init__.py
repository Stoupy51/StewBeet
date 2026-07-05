"""ingame_manual — modern, extensible, dialog-first in-game manual generator.

Opt in by replacing ``stewbeet.plugins.ingame_manual`` with ``stewbeet.plugins.ingame_manual``
in your beet pipeline. See :mod:`.api` (`get_manual`, `Page` subclasses, `Phase`, `ButtonLayout`,
`BakedText`) for the customization API.
"""

# Imports
import os
import shutil
import sys

import stouputils as stp
from beet import Context

from ...core.__memory__ import Mem
from .api import get_manual
from .config import ManualConfig
from .iso_renders import generate_all_iso_renders
from .paths import MANUAL_ASSETS_PATH, TEMPLATES_PATH
from .special import register_heavy_workbench


def copy_templates(config: ManualConfig) -> None:
	""" Copy bundled assets (and optional manual_overrides) into the temporary templates dir. """
	shutil.copytree(MANUAL_ASSETS_PATH + "/assets", TEMPLATES_PATH, dirs_exist_ok=True)
	if config.manual_overrides and os.path.exists(config.manual_overrides):
		shutil.copytree(config.manual_overrides, TEMPLATES_PATH, dirs_exist_ok=True)


@stp.measure_time(message="Execution time of 'stewbeet.plugins.ingame_manual'")
@stp.handle_error(message="An error occurred while generating the in-game manual", error_log=stp.LogLevels.ERROR_TRACEBACK)
def beet_default(ctx: Context) -> None:
	""" Entry point: build the manual (reusing any Manual registered during setup). """
	if Mem.ctx is None:  # pyright: ignore[reportUnnecessaryComparison]
		Mem.ctx = ctx

	if not Mem.definitions:
		stp.warning("Database is empty, skipping manual generation.", file=sys.stdout)
		return

	# Reuse the Manual the developer may have created during setup, else create it now.
	manual = get_manual()
	config = manual.config

	# Prepare assets, register special blocks, render item textures, then build.
	copy_templates(config)
	os.makedirs(f"{config.cache_path}/font/page", exist_ok=True)
	os.makedirs(f"{config.cache_path}/font/wiki_icons", exist_ok=True)
	os.makedirs(f"{config.cache_path}/font/high_res", exist_ok=True)
	register_heavy_workbench()
	generate_all_iso_renders(config)
	manual.build()

	# Reset so `beet watch` starts each cycle with a fresh, hook-free Manual.
	Mem.manual = None

