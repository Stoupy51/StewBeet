""" Keeps Spyglass's `env.exclude` in step with the sources it cannot parse.

A `.mcfunction` holding bolt or mecha nesting is not vanilla mcfunction, and Spyglass underlines
most of it. Nothing can clear another extension's diagnostics, but Spyglass skips what its own
`env.exclude` names, and the build is the one place that knows exactly which files those are:
bolt says which files it generated Python for, and mecha says which ones it split in two.

The editor offers the same exclusion for the file being opened, which is what a project that has
never been built still needs. Both write the same key in the same file and both only ever add.
"""

# Lazy imports (PEP 810), ignored before Python 3.15
from stouputils.lazy import ALWAYS_LAZY

__lazy_modules__ = ALWAYS_LAZY

# Imports
import os
from collections.abc import Callable, Iterator

import stouputils as stp
from beet import Context, Pipeline
from beet.toolchain.pipeline import Task
from stouputils.typing import JsonDict

from ...core.__memory__ import Mem
from ...core.source_paths import remember_source_paths
from .config import config_path, exclusions_of, read_config, with_exclusions, write_config
from .confirm import may_manage, remember_exclusions, remembered_exclusions
from .detect import unparseable_sources


# Main entry point
def beet_default(ctx: Context) -> None:
	""" Queue the exclusion update for the very end of the build.

	What it reads is mecha's compilation database, which stays empty until mecha compiles, and mecha
	compiles when beet unwinds it. A generator listed after `mecha` unwinds *before* it and sees
	nothing, and a plugin requiring mecha from Python moves the compile later still.

	Args:
		ctx (Context): The beet context.
	"""
	# Now, while beet still says where each file came from: `beet.contrib.find_replace` makes it
	# forget as it goes, and a versioned project runs that over the whole pack before mecha parses.
	remember_source_paths(ctx)
	queue_at_end(ctx, apply_exclusions)


# Functions
def queue_at_end(ctx: Context, work: Callable[[Context], None]) -> None:
	""" Run `work` once every other plugin in the build has finished, wherever this one is listed.

	Beet pops its task list from the end, so a task put at the front of it is the last one left.
	It is queued as a generator because beet throws a failing build's exception into a task that
	has started: `work` then never runs on a pack whose compile gave up half way through.
	"""
	Mem.ctx = ctx

	def deferred(ctx: Context) -> Iterator[None]:
		yield
		work(ctx)

	ctx.inject(Pipeline).tasks.insert(0, Task(deferred))


@stp.measure_time(message="Execution time of 'stewbeet.plugins.spyglass'")
def apply_exclusions(ctx: Context) -> None:
	""" Write the sources this build could not parse into the project's Spyglass config.

	Args:
		ctx (Context): The beet context.
	"""
	path: str = config_path(os.path.abspath(str(ctx.directory)))
	current: JsonDict | None = read_config(path)
	if current is None:
		stp.warning(f"spyglass: {os.path.basename(path)} is not readable JSON, leaving it alone")
		return

	detected: list[str] = unparseable_sources(ctx)
	existing: list[str] = exclusions_of(current)

	# Retracting is not a decision to ask about: these name files an earlier build excluded and this one can parse.
	# Leaving them in keeps Spyglass off a file it has no trouble with.
	drop: list[str] = [pattern for pattern in remembered_exclusions() if pattern not in detected and pattern in existing]
	add: list[str] = [pattern for pattern in detected if pattern not in existing]
	if add and not may_manage(add):
		add = []

	updated: JsonDict | None = with_exclusions(current, add, drop)
	if updated is None:
		return

	write_config(path, updated)
	remember_exclusions(sorted((set(remembered_exclusions()) | set(add)) - set(drop)))
	stp.info(f"spyglass: {len(add)} exclusion(s) added and {len(drop)} retracted in {os.path.basename(path)}")
