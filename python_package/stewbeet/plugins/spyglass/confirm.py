""" One-time confirmation before this project's Spyglass config is written to.

Which files an editor checks is the project's decision and the file holding it is version
controlled, so the question is asked in the terminal the first time a build finds something to
exclude, and the answer is remembered in ``.beet_cache``.
``meta.stewbeet.spyglass.manage_exclusions`` answers it up front and skips the prompt.
"""

# Lazy imports (PEP 810), ignored before Python 3.15
from stouputils.lazy import ALWAYS_LAZY

__lazy_modules__ = ALWAYS_LAZY

# Imports
import sys
from typing import cast

import stouputils as stp

from ...core.__memory__ import Mem

# Constants
CACHE_NAME: str = "stewbeet_spyglass"
""" beet cache holding the answer and what it was applied to, next to the rest of the project cache. """

CACHE_ANSWER: str = "manage_exclusions"
""" Key the remembered answer is stored under. """

CACHE_OWNED: str = "excluded"
""" Key holding the patterns this plugin added, which are the only ones it may ever take back. """


# Functions
def prompt() -> bool | None:
	""" The answer typed in the terminal, or None when there is nobody to answer.

	A build driven by a script, a CI job or an editor has no terminal to read from, and blocking one
	forever on a question is worse than the diagnostics it was meant to silence.
	"""
	if sys.stdin is None or not sys.stdin.isatty():
		return None
	try:
		return not input("Add them to the Spyglass exclusions? [Y/n] ").strip().lower().startswith("n")
	except EOFError:
		return None


def may_manage(files: list[str]) -> bool:
	""" Ask once whether this project's Spyglass config may be written to, and remember the answer.

	Outside a terminal there is nobody to answer, so nothing is written and the reason is printed:
	a CI job must not commit a config change the author never agreed to.

	Args:
		files: Patterns that would be added, named in the question so the answer is informed.
	"""
	configured: object = Mem.ctx.meta.get("stewbeet", {}).get("spyglass", {}).get(CACHE_ANSWER)
	if isinstance(configured, bool):
		return configured

	cache = Mem.ctx.cache[CACHE_NAME]
	remembered: object = cache.json.get(CACHE_ANSWER)
	if isinstance(remembered, bool):
		return remembered

	listed: str = ", ".join(files[:3]) + (f" and {len(files) - 3} more" if len(files) > 3 else "")
	stp.warning(
		f"{listed} hold bolt or mecha syntax, which Spyglass cannot parse, so it reports most of "
		"each file as an error. Its own 'env.exclude' is the supported way to stop that, and it "
		"lives in a config file this project version controls."
	)

	typed: bool | None = prompt()
	if typed is None:
		stp.warning("Nobody to answer, so nothing is written. Set 'meta.stewbeet.spyglass.manage_exclusions' to decide up front.")
		return False

	# Only an answer somebody actually gave is remembered, so a build with no terminal never
	# decides for the author.
	cache.json[CACHE_ANSWER] = typed
	return typed


def remembered_exclusions() -> list[str]:
	""" Patterns an earlier build of this project added, which are the ones it may retract. """
	raw: object = Mem.ctx.cache[CACHE_NAME].json.get(CACHE_OWNED)
	return [str(pattern) for pattern in cast(list[object], raw)] if isinstance(raw, list) else []


def remember_exclusions(patterns: list[str]) -> None:
	""" Record what this plugin owns, so a pattern the author wrote by hand is never taken back. """
	Mem.ctx.cache[CACHE_NAME].json[CACHE_OWNED] = patterns

