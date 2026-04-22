
# Imports
import hashlib

import stouputils as stp
from beet import Context
from ..__init__ import compute_hashes

from ....core.__memory__ import Mem

# Main entry point
@stp.measure_time(message="Execution time of 'stewbeet.plugins.compute_sha.sha384")
def beet_default(ctx: Context) -> None:
	""" Main entry point for the compute SHA.sha384 plugin.
	This plugin computes sha384 hashes for each zip file in the build folder.

	Args:
		ctx (Context): The beet context.
	"""
	return compute_hashes(ctx, (lambda f: hashlib.sha384(f).hexdigest(), "sha384"))

