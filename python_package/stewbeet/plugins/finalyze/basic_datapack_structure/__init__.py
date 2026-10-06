""" ⏱️ Sets up the timed functions of the datapack, run every 2 ticks, second, 5 seconds and minute. """
# Lazy imports (PEP 810), ignored before Python 3.15
from stouputils.lazy import ALWAYS_LAZY

__lazy_modules__ = ALWAYS_LAZY

# Imports
from dataclasses import dataclass

import stouputils as stp
from beet import Context

from ....core.__memory__ import Mem
from ....core.utils.io import write_tick_file, write_versioned_function


# Classes
@dataclass(frozen=True)
class Timer:
	""" A versioned function the tick function calls every few ticks, counted on a score of its own. """

	name: str
	reset: int
	""" Score the timer restarts from once its function ran. tick_2 and second_5 run off sync with the others, to spread the load. """
	threshold: int
	""" Score at which its function runs. """


# Constants
TIMERS: tuple[Timer, ...] = (
	Timer(name="tick_2", reset=1, threshold=3),
	Timer(name="second", reset=0, threshold=20),
	Timer(name="second_5", reset=-10, threshold=90),
	Timer(name="minute", reset=1, threshold=1200),
)
""" Every timer, in the order the tick function counts and calls them. """


# Main entry point
@stp.measure_time(message="Execution time of 'stewbeet.plugins.finalyze.basic_datapack_structure'")
def beet_default(ctx: Context) -> None:
	""" Main entry point for the basic datapack structure plugin.
	This plugin sets up basic timing structures for a Minecraft datapack with tick functions
	for different intervals (tick_2, second, second_5, minute).

	Args:
		ctx: The beet context.
	"""
	# Get namespace and version
	Mem.ctx = ctx
	assert ctx.project_id, "Project ID is not set. Please set it in the project configuration."
	ns: str = ctx.project_id
	version: str = ctx.project_version

	timers: list[Timer] = [timer for timer in TIMERS if f"{ns}:v{version}/{timer.name}" in ctx.data.functions]
	for timer in timers:
		reset: str = f"# Reset timer\nscoreboard players set #{timer.name} {ns}.data {timer.reset}\n"
		write_versioned_function(timer.name, reset, prepend=True)
	if timers:
		write_tick_file(
			"# Timers\n"
			+ "".join(f"scoreboard players add #{timer.name} {ns}.data 1\n" for timer in timers)
			+ "".join(
				f"execute if score #{timer.name} {ns}.data matches {timer.threshold}.. run function {ns}:v{version}/{timer.name}\n"
				for timer in timers
			),
			prepend=True,
		)

