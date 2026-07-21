
# Imports
import hashlib
import os

import stouputils as stp
from beet import Context

from ...core.__memory__ import Mem


# Main entry point
@stp.measure_time(message="Execution time of 'stewbeet.plugins.compute_sha1'")
def beet_default(ctx: Context):
	""" Main entry point for the compute SHA1 plugin.
	This plugin computes SHA1 hashes for each zip file in the build folder.

	Args:
		ctx (Context): The beet context.
	"""
	# Assertions
	Mem.ctx = ctx
	assert Mem.ctx.output_directory, "Output directory must be specified in the project configuration."

	# Get SHA1 hash for each zip file in build folder
	sha1_hashes: dict[str, str] = {}
	for file in os.listdir(Mem.ctx.output_directory):
		if file.endswith(".zip"):
			with open(f"{Mem.ctx.output_directory}/{file}", "rb") as f:
				sha1_hashes[file] = hashlib.sha1(f.read()).hexdigest()

	# Write SHA1 hashes to JSON file
	stp.json_dump(sha1_hashes, f"{Mem.ctx.output_directory}/sha1_hashes.json")

