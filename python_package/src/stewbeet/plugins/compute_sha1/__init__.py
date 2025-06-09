
# Imports
import hashlib
import os

from beet import Context
from stouputils.decorators import measure_time
from stouputils.io import super_json_dump, super_open
from stouputils.print import progress


# Main entry point
@measure_time(progress, message="Execution time of 'stewbeet.plugins.compute_sha1'")
def beet_default(ctx: Context):
	""" Main entry point for the compute SHA1 plugin.
	This plugin computes SHA1 hashes for each zip file in the build folder.

	Args:
		ctx (Context): The beet context.
	"""
	# Assertions
	assert ctx.output_directory, "Output directory must be specified in the project configuration."

	# Get SHA1 hash for each zip file in build folder
	sha1_hashes: dict[str, str] = {}
	for file in os.listdir(ctx.output_directory):
		if file.endswith(".zip"):
			with open(f"{ctx.output_directory}/{file}", "rb") as f:
				sha1_hashes[file] = hashlib.sha1(f.read()).hexdigest()

	# Write SHA1 hashes to JSON file
	with super_open(f"{ctx.output_directory}/sha1_hashes.json", "w") as f:
		f.write(super_json_dump(sha1_hashes))

