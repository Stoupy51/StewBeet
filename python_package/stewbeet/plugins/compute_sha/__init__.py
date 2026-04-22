
# Imports
import hashlib
import os
from typing import Callable

import stouputils as stp
from beet import Context

from ...core.__memory__ import Mem

def compute_hashes(ctx: Context, algorithm: tuple[Callable[[bytes],str],str]) -> None:
	""" Main entry point for the compute SHA plugin.
	This plugin computes SHA hashes for each zip file in the build folder.

	Args:
		ctx (Context): The beet context.
		algorithm (tuple[Callable[[bytes],str],str]): A tuple containing the hashing function and the name of the algorithm.
	"""
	if Mem.ctx is None: # pyright: ignore[reportUnnecessaryComparison]
		Mem.ctx = ctx

	# Assertions
	assert Mem.ctx.output_directory, "Output directory must be specified in the project configuration."

	# Get SHA hash for each zip file in build folder
	sha_hashes: dict[str, str] = {}
	for file in os.listdir(Mem.ctx.output_directory):
		if file.endswith(".zip"):
			with open(f"{Mem.ctx.output_directory}/{file}", "rb") as f:
				sha_hashes[file] = algorithm[0](f.read())

	# Write SHA hashes to JSON file
	stp.json_dump(sha_hashes, f"{Mem.ctx.output_directory}/{algorithm[1]}_hashes.json")

# Main entry point
@stp.measure_time(message="Execution time of 'stewbeet.plugins.compute_sha'")
def beet_default(ctx: Context) -> None:
	""" Main entry point for the compute SHA plugin.
	This plugin computes sha1 hashes for each zip file in the build folder.

	Args:
		ctx (Context): The beet context.
	"""
	return compute_hashes(ctx, (lambda f: hashlib.sha1(f).hexdigest(), "sha1"))

