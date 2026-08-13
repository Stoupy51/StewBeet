
# Lazy imports (PEP 810), ignored before Python 3.15
from stouputils.lazy import ALWAYS_LAZY

__lazy_modules__ = ALWAYS_LAZY

# Imports
import stouputils as stp
from beet import Context

from ....core.__memory__ import Mem
from ....core.utils.io import write_load_file


# Main entry point
@stp.measure_time(message="Execution time of 'stewbeet.plugins.auto.scoreboard_constants'")
def beet_default(ctx: Context):
	""" Main entry point for the scoreboard constants plugin.
	This plugin looks for all usage of scoreboard constants in the project and generates their set commands in the load function.

	Pattern is ``#{integer} {ctx.project_id}.data``

	Args:
		ctx (Context): The beet context.
	"""
	Mem.ctx = ctx

	# Get data from memory
	assert ctx.project_id, "Project ID is not set. Please set it in the project configuration."
	ns: str = ctx.project_id

	# Prepare regex pattern for scoreboard constants
	import re
	pattern = re.compile(rf"#(-?\d+) {re.escape(ns)}\.data")

	# Loop through all functions and list all used scoreboard constants
	constants: set[int] = set()
	for func in ctx.data.functions.values():
		for line in func.text.splitlines():
			match = pattern.search(line)
			if match:
				constant_value = int(match.group(1))
				constants.add(constant_value)

	# Generate set commands for each constant and write to load function
	if constants:
		content: str = "\n".join([f"scoreboard players set #{constant} {ns}.data {constant}" for constant in sorted(constants)])
		write_load_file(f"""
# Set scoreboard constants for {ns}.data
{content}
""")

