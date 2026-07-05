
# Imports
import stouputils as stp
from beet import Context


# Main entry point
@stp.measure_time(message="Execution time of 'stewbeet.plugins.verify_definitions'")
@stp.deprecated(message="The 'verify_definitions' plugin is now integrated into the main pipeline and runs when you make definitions, no need to require it manually.", version="3.0.0")
def beet_default(ctx: Context) -> None:
	return

