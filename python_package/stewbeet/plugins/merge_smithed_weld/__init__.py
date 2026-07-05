
# Imports
import logging
import os
from pathlib import Path

import stouputils as stp
from beet import Context
from stouputils.ctx import Muffle

from .weld import prepare_weld, weld_to


# Main entry point
@stp.measure_time(message="Execution time of 'stewbeet.plugins.merge_smithed_weld'")
def beet_default(ctx: Context) -> None:
	""" Merge Smithed Weld plugin for StewBeet.
	Merges the generated datapack and resource pack with libraries using Smithed Weld.

	Args:
		ctx (Context): The beet context.
	"""
	# Assertions
	assert ctx.output_directory, "Output directory must be specified in the project configuration."
	assert ctx.project_name, "Project name must be specified in the project configuration."

	# Ensure output directory exists
	os.makedirs(ctx.output_directory, exist_ok=True)

	project_name_simple = ctx.project_name.replace(" ", "")

	# Gather sources for each pack that has a base archive (warnings stay visible: this runs unmuffled)
	tasks: list[tuple[list[str], str, str]] = []
	for pack_type in ("datapack", "resource_pack"):
		source = str(Path(ctx.output_directory) / f"{project_name_simple}_{pack_type}.zip")
		dest = str(Path(ctx.output_directory) / f"{project_name_simple}_{pack_type}_with_libs.zip")
		if os.path.exists(source):
			to_merge: list[str] | None = prepare_weld(ctx, dest, pack_type)
			if to_merge is not None:
				tasks.append((to_merge, dest, pack_type))
	if not tasks:
		return

	# Run both welds in parallel (they are independent and the zlib work releases the GIL).
	# Weld logs failures through the "weld" logger instead of raising, so capture its (noisy)
	# output around the whole parallel section and only replay it when an error actually happens.
	@stp.handle_error
	def run_weld_task(task: tuple[list[str], str, str]) -> None:
		to_merge, dest, pack_type = task
		weld_to(ctx, to_merge, dest, pack_type)

	with Muffle(mute_stderr=True, replay_on_error=True, error_log_level=logging.ERROR, watch_loggers=["weld"]):
		stp.multithreading(run_weld_task, tasks, max_workers=len(tasks))

