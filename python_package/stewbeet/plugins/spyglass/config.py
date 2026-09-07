""" The project's Spyglass config, read and written without disturbing what else is in it. """

# Lazy imports (PEP 810), ignored before Python 3.15
from stouputils.lazy import ALWAYS_LAZY

__lazy_modules__ = ALWAYS_LAZY

# Imports
import json
import os
from typing import cast

from stouputils.typing import JsonDict

# Constants
CONFIG_NAMES: tuple[str, ...] = ("spyglass.json", ".spyglassrc", ".spyglassrc.json")
""" Names Spyglass looks for in a project root, in its own order. """

DEFAULT_NAME: str = ".spyglassrc.json"
""" Written when a project has none of them yet. """


# Functions
def config_path(root: str) -> str:
	""" The Spyglass config a project root uses, existing or to be created. """
	for name in CONFIG_NAMES:
		candidate: str = os.path.join(root, name)
		if os.path.isfile(candidate):
			return candidate
	return os.path.join(root, DEFAULT_NAME)


def read_config(path: str) -> JsonDict | None:
	""" The config as it stands, `{}` when there is no file, None when it is not readable JSON.

	A file this plugin cannot parse is a file it must not overwrite: it is the project's, and a
	comment or a syntax error in it is not a reason to lose the rest.
	"""
	if not os.path.isfile(path):
		return {}
	try:
		with open(path, encoding="utf-8") as file:
			loaded: object = json.load(file)
	except (OSError, json.JSONDecodeError):
		return None
	# A JSON object is a dict with string keys by definition, which is what the alias says.
	return cast(JsonDict, loaded) if isinstance(loaded, dict) else None


def exclusions_of(config: JsonDict) -> list[str]:
	""" The `env.exclude` patterns a config already carries.

	>>> exclusions_of({"env": {"exclude": ["a.mcfunction"]}})
	['a.mcfunction']
	>>> exclusions_of({}), exclusions_of({"env": {}}), exclusions_of({"env": {"exclude": "nope"}})
	([], [], [])
	"""
	env: object = config.get("env")
	if not isinstance(env, dict):
		return []
	raw: object = cast(object, env.get("exclude")) # pyright: ignore[reportUnknownMemberType]
	return [str(pattern) for pattern in cast(list[object], raw)] if isinstance(raw, list) else []


def with_exclusions(config: JsonDict, add: list[str], drop: list[str]) -> JsonDict | None:
	""" The same config with `env.exclude` brought up to date, or None when it already was.

	Everything outside `env.exclude` is carried through untouched, `env`'s own neighbours included:
	dependencies and feature switches are the project's business, not this plugin's.

	Args:
		add:  Patterns to append, in order, after the ones already there.
		drop: Patterns to remove, which are only ever ones an earlier build added.

	>>> with_exclusions({}, ["a.mcfunction"], [])
	{'env': {'exclude': ['a.mcfunction']}}
	>>> with_exclusions({"env": {"exclude": ["a.mcfunction"]}}, ["a.mcfunction"], []) is None
	True
	>>> with_exclusions({"env": {"exclude": ["a.mcfunction", "keep/**"]}}, [], ["a.mcfunction"])
	{'env': {'exclude': ['keep/**']}}
	>>> with_exclusions({"env": {"dependencies": ["@vanilla-mcdoc"]}}, ["a.mcfunction"], [])
	{'env': {'dependencies': ['@vanilla-mcdoc'], 'exclude': ['a.mcfunction']}}
	"""
	current: list[str] = exclusions_of(config)
	kept: list[str] = [pattern for pattern in current if pattern not in drop]
	updated: list[str] = kept + [pattern for pattern in add if pattern not in kept]
	if updated == current:
		return None

	env: JsonDict = dict(config["env"]) if isinstance(config.get("env"), dict) else {}
	return {**config, "env": {**env, "exclude": updated}}


def write_config(path: str, config: JsonDict) -> None:
	""" Write the config back.

	Two-space indent and a final newline, byte for byte what the editor side writes, so a project
	where both have run does not see the file rewritten by whichever touched it last.
	"""
	with open(path, "w", encoding="utf-8", newline="\n") as file:
		json.dump(config, file, indent=2)
		file.write("\n")
