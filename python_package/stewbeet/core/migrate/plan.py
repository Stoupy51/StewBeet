""" Everything `stewbeet migrate` will do, worked out before anything on disk changes.

A dry run prints the plan, a real run prints it and then applies it, so `--dry-run` shows exactly what happens.
"""
# Lazy imports (PEP 810), ignored before Python 3.15
from stouputils.lazy import ALWAYS_LAZY

__lazy_modules__ = ALWAYS_LAZY

# Imports
import json
import re
import shutil
import zipfile
from dataclasses import dataclass
from pathlib import Path

from .packs import FoundPack

# Constants
TEMPLATE_ICONS: tuple[str, ...] = ("src/pack.png", "assets/pack.png")
""" Where a template may keep its pack.png. The migrated icon goes wherever the chosen template has it. """

RESOURCE_PACK_CONFIG: str = """
# Loads src/assets/, where `stewbeet migrate` moved your resource pack
resource_pack:
    name: "resource_pack"
    load: ["src"]
"""
""" Appended to a template's beet.yml that only builds a datapack, when a resource pack is migrated. """


# Classes
@dataclass(frozen=True)
class Move:
	source: Path
	destination: Path

@dataclass(frozen=True)
class Extract:
	""" A template file written as it is in the template. """
	member: str

@dataclass(frozen=True)
class Skip:
	""" A template file left out. """
	member: str
	reason: str

@dataclass(frozen=True)
class Delete:
	path: Path
	reason: str

@dataclass(frozen=True)
class RemoveFolder:
	""" A pack folder that the moves leave empty. """
	path: Path

@dataclass(frozen=True)
class WriteConfig:
	""" The template's beet.yml, filled in from the migrated packs. """
	text: str
	changes: tuple[str, ...]

Step = Move | Extract | Skip | Delete | RemoveFolder | WriteConfig


@dataclass(frozen=True)
class MigrationPlan:
	working_dir: Path
	steps: tuple[Step, ...]
	""" In the order they are applied. """
	warnings: tuple[str, ...]

	def describe(self) -> list[str]:
		""" One line per step, the way the terminal shows the plan. """
		return [line for step in self.steps for line in self.describe_step(step)]

	def conflicts(self) -> list[str]:
		""" Why the plan cannot run, empty when it can. Nothing is written unless this is empty. """
		moves: list[Move] = [step for step in self.steps if isinstance(step, Move)]
		written: list[Path] = [self.working_dir / step.member for step in self.steps if isinstance(step, Extract)]
		taken: list[str] = [f"{self.relative(move.destination)} already exists" for move in moves if move.destination.exists()]
		clashing: list[str] = [
			f"the template writes {self.relative(path)}, where {self.relative(move.source)} is moving"
			for move in moves for path in written if path.is_relative_to(move.destination)
		]
		return taken + clashing

	def apply(self, template: zipfile.ZipFile) -> None:
		for step in self.steps:
			match step:
				case Move(source, destination):
					destination.parent.mkdir(parents=True, exist_ok=True)
					shutil.move(source, destination)
				case Extract(member):
					template.extract(member, self.working_dir)
				case WriteConfig(text):
					(self.working_dir / "beet.yml").write_text(text, encoding="utf-8")
				case Delete(path):
					path.unlink()
				case RemoveFolder(path):
					path.rmdir()
				case Skip():
					pass

	def describe_step(self, step: Step) -> list[str]:
		match step:
			case Move(source, destination):
				return [f"move    {self.relative(source)} -> {self.relative(destination)}"]
			case Extract(member):
				return [f"add     {member}"]
			case Skip(member, reason):
				return [f"skip    {member} ({reason})"]
			case WriteConfig(_, changes):
				return ["write   beet.yml", *(f"          {change}" for change in changes)]
			case Delete(path, reason):
				return [f"delete  {self.relative(path)} ({reason})"]
			case RemoveFolder(path):
				return [f"remove  {self.relative(path)}/ (empty once moved)"]

	def relative(self, path: Path) -> str:
		return path.relative_to(self.working_dir).as_posix()


# Functions
def build_plan(working_dir: Path, template: zipfile.ZipFile, datapack: FoundPack | None, resource_pack: FoundPack | None) -> MigrationPlan:
	""" Everything moving these packs into the template takes, without touching the disk.

	Args:
		datapack:      The pack whose data/ is migrated, possibly the same folder as `resource_pack`.
		resource_pack: The pack whose assets/ is migrated.
	"""
	packs: list[FoundPack] = list({pack.root: pack for pack in (datapack, resource_pack) if pack}.values())
	icon: Path | None = next((pack.root / "pack.png" for pack in packs if (pack.root / "pack.png").is_file()), None)
	template_icon: str = next((member for member in TEMPLATE_ICONS if member in template.namelist()), TEMPLATE_ICONS[0])

	template_steps: list[Step] = plan_template_files(working_dir, template, datapack, resource_pack, replaced_icon=template_icon if icon else None)
	config, config_warnings = plan_config(template.read("beet.yml").decode("utf-8"), working_dir, datapack, resource_pack)
	moves: list[Step] = plan_moves(working_dir, packs, icon, working_dir / template_icon)
	mcmeta_steps, mcmeta_warnings = plan_mcmeta(working_dir, packs)
	pack_steps: list[Step] = [*moves, *mcmeta_steps]
	icon_warnings: list[str] = [
		f"{(pack.root / 'pack.png').relative_to(working_dir).as_posix()} is left in place, the other pack.png becomes the icon"
		for pack in packs if (pack.root / "pack.png").is_file() and pack.root / "pack.png" != icon
	]
	return MigrationPlan(
		working_dir=working_dir,
		steps=(*template_steps, config, *pack_steps, *plan_cleanup(working_dir, packs, pack_steps)),
		warnings=(*config_warnings, *mcmeta_warnings, *icon_warnings),
	)


def plan_template_files(working_dir: Path, template: zipfile.ZipFile, datapack: FoundPack | None, resource_pack: FoundPack | None, replaced_icon: str | None) -> list[Step]:
	""" Which template files are written, and why the others are not. The template never writes over a file. """
	steps: list[Step] = []
	for member in template.namelist():
		if member.endswith("/") or member == "beet.yml":
			continue
		if datapack and member.startswith("src/data/"):
			steps.append(Skip(member, "replaced by your datapack"))
		elif resource_pack and member.startswith("src/assets/"):
			steps.append(Skip(member, "replaced by your resource pack"))
		elif member == replaced_icon:
			steps.append(Skip(member, "replaced by your pack.png"))
		elif (working_dir / member).exists():
			steps.append(Skip(member, "already exists, yours is kept"))
		else:
			steps.append(Extract(member))
	return steps


def plan_config(text: str, working_dir: Path, datapack: FoundPack | None, resource_pack: FoundPack | None) -> tuple[WriteConfig, list[str]]:
	""" The template's beet.yml with the migrated project's own values, and what is still left to fill in by hand. """
	main_pack: FoundPack | None = datapack or resource_pack
	text, changes, warnings = fill_identity(text, main_pack, datapack.namespaces if datapack else [])
	if main_pack and (description := main_pack.description_yaml):
		text = set_config_key(text, "description", description)
		changes.append("description: from pack.mcmeta")
	if datapack and resource_pack and datapack.root != resource_pack.root and resource_pack.description_yaml not in (None, datapack.description_yaml):
		warnings.append("The resource pack's description differs from the datapack's: beet.yml now uses the datapack's for both")
	if resource_pack and not has_config_key(text, "resource_pack"):
		text = text.rstrip() + "\n" + RESOURCE_PACK_CONFIG
		changes.append("resource_pack: added, the template only builds a datapack")
	return WriteConfig(text, tuple(changes)), warnings


def fill_identity(text: str, main_pack: FoundPack | None, namespaces: list[str]) -> tuple[str, list[str], list[str]]:
	""" Replace the template's name and id with the pack's, for the templates that set them.

	Returns:
		The new config text, the changes made, and the warnings about what could not be filled in.
	"""
	changes: list[str] = []
	warnings: list[str] = []
	if main_pack and has_config_key(text, "name"):
		text = set_config_key(text, "name", json.dumps(main_pack.root.name, ensure_ascii=False))
		changes.append(f"name: {main_pack.root.name}")
	if has_config_key(text, "id") and len(namespaces) == 1:
		text = set_config_key(text, "id", json.dumps(namespaces[0]))
		changes.append(f"id: {namespaces[0]}")
	elif has_config_key(text, "id"):
		warnings.append(f"Set id in beet.yml to your namespace (found: {', '.join(namespaces) or 'none'})")
	if has_config_key(text, "author"):
		warnings.append("Set author in beet.yml: it still names the template's author")
	return text, changes, warnings


def plan_moves(working_dir: Path, packs: list[FoundPack], icon: Path | None, icon_destination: Path) -> list[Step]:
	""" data/ and assets/ into src/, and the icon to where the template keeps its own. """
	src: Path = working_dir / "src"
	moves: list[Move] = [
		Move(pack.root / folder, src / folder)
		for pack in packs
		for folder, present in (("data", pack.has_data), ("assets", pack.has_assets))
		if present
	]
	if icon:
		moves.append(Move(icon, icon_destination))
	return [move for move in moves if move.source != move.destination]


def plan_mcmeta(working_dir: Path, packs: list[FoundPack]) -> tuple[list[Step], list[str]]:
	""" A plain pack.mcmeta is folded into beet.yml, a richer one moves to src/ (at most one can). """
	steps: list[Step] = []
	warnings: list[str] = []
	kept: Path | None = None
	for pack in packs:
		mcmeta: Path = pack.root / "pack.mcmeta"
		relative: str = mcmeta.relative_to(working_dir).as_posix()
		if pack.is_plain:
			steps.append(Delete(mcmeta, "beet.yml and StewBeet write it at build time"))
		elif kept is None:
			kept = mcmeta
			if mcmeta != working_dir / "src" / "pack.mcmeta":
				steps.append(Move(mcmeta, working_dir / "src" / "pack.mcmeta"))
			warnings.append(f"{relative} holds more than a description and a pack format, so it is kept in src/. StewBeet still sets its pack_format and description")
		else:
			warnings.append(f"{relative} is left in place: only one pack.mcmeta can go to src/")
	return steps, warnings


def plan_cleanup(working_dir: Path, packs: list[FoundPack], pack_steps: list[Step]) -> list[Step]:
	""" The pack folders, and their parents, that nothing is left in once the files have moved. Deepest first. """
	leaving: set[Path] = {step.source for step in pack_steps if isinstance(step, Move)} | {step.path for step in pack_steps if isinstance(step, Delete)}
	emptied: list[Path] = [
		pack.root for pack in packs
		if pack.root not in (working_dir, working_dir / "src") and set(pack.root.iterdir()) <= leaving
	]
	# Grows while it is read, so a parent emptied by this very list is checked in turn
	for folder in emptied:
		parent: Path = folder.parent
		if parent != working_dir and parent not in emptied and set(parent.iterdir()) <= set(emptied):
			emptied.append(parent)
	return [RemoveFolder(folder) for folder in emptied]


def has_config_key(text: str, key: str) -> bool:
	""" Whether a top-level key is set in a YAML config.

	>>> has_config_key('id: "a"\\n  name: "b"', "name")
	False
	"""
	return re.search(rf"^{key}:", text, re.MULTILINE) is not None


def set_config_key(text: str, key: str, value: str) -> str:
	""" Set a top-level key of a YAML config, keeping every comment. A missing key is appended.

	Args:
		value: Already a YAML value, quotes included.

	>>> set_config_key('id: "a"\\nname: "b"\\n', "id", '"c"')
	'id: "c"\\nname: "b"\\n'
	>>> set_config_key('output: "build"\\n', "description", '"Hi"')
	'output: "build"\\n\\ndescription: "Hi"\\n'
	"""
	if has_config_key(text, key):
		return re.sub(rf"^{key}:.*$", lambda _: f"{key}: {value}", text, count=1, flags=re.MULTILINE)
	return f"{text.rstrip()}\n\n{key}: {value}\n"

