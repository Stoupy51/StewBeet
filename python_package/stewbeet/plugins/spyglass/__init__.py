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
from collections.abc import Iterator

import stouputils as stp
from beet import Context
from stouputils.typing import JsonDict

from ...core.__memory__ import Mem
from .config import config_path, exclusions_of, read_config, with_exclusions, write_config
from .confirm import may_manage, remember_exclusions, remembered_exclusions
from .detect import unparseable_sources


# Main entry point
@stp.measure_time(message="Execution time of 'stewbeet.plugins.spyglass'")
def beet_default(ctx: Context) -> Iterator[None]:
	""" Update the project's Spyglass exclusions from what this build compiled.

	Runs at the end, because the compilation database is what it reads. Anywhere in the pipeline
	after `mecha` works.

	Args:
		ctx (Context): The beet context.
	"""
	Mem.ctx = ctx
	yield

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
