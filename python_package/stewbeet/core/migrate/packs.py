""" Find the datapacks and resource packs a folder holds, before `stewbeet migrate` turns it into a project. """
# Lazy imports (PEP 810), ignored before Python 3.15
from stouputils.lazy import ALWAYS_LAZY

__lazy_modules__ = ALWAYS_LAZY

# Imports
import json
from dataclasses import dataclass
from pathlib import Path

from stouputils.typing import JsonDict

# Constants
SEARCH_DEPTH: int = 2
""" How many folders below the working directory a pack is looked for. """

SKIPPED_FOLDERS: frozenset[str] = frozenset({"build", "node_modules", "__pycache__"})
""" Folders never searched, on top of hidden ones: they hold outputs and dependencies, not sources. """

PLAIN_PACK_KEYS: frozenset[str] = frozenset({"pack_format", "description"})
""" Keys of the "pack" object that beet.yml and StewBeet already produce, so a pack.mcmeta holding only these can go. """


# Classes
@dataclass(frozen=True)
class FoundPack:
	""" A folder holding a pack.mcmeta next to a data/ folder, an assets/ folder, or both. """
	root: Path
	has_data: bool
	has_assets: bool
	mcmeta: JsonDict

	@staticmethod
	def read(folder: Path) -> FoundPack | None:
		""" The pack in `folder`, or None when it holds no pack.mcmeta or neither data/ nor assets/. """
		mcmeta_path: Path = folder / "pack.mcmeta"
		has_data, has_assets = (folder / "data").is_dir(), (folder / "assets").is_dir()
		if not mcmeta_path.is_file() or not (has_data or has_assets):
			return None
		mcmeta: JsonDict = json.loads(mcmeta_path.read_text(encoding="utf-8"))
		return FoundPack(root=folder, has_data=has_data, has_assets=has_assets, mcmeta=mcmeta)

	@property
	def is_plain(self) -> bool:
		""" Whether pack.mcmeta holds nothing beyond a description and a pack format.

		>>> FoundPack(Path("."), True, False, {"pack": {"pack_format": 61, "description": "Hi"}}).is_plain
		True
		>>> FoundPack(Path("."), True, False, {"pack": {"pack_format": 61}, "overlays": {}}).is_plain
		False
		"""
		return self.mcmeta.keys() <= {"pack"} and self.mcmeta.get("pack", {}).keys() <= PLAIN_PACK_KEYS

	@property
	def description_yaml(self) -> str | None:
		""" The description as a YAML value for beet.yml, None when pack.mcmeta has none.
		JSON is valid YAML, which keeps a text component description intact.

		>>> FoundPack(Path("."), True, False, {"pack": {"description": "Épée"}}).description_yaml
		'"Épée"'
		"""
		description = self.mcmeta.get("pack", {}).get("description")
		return None if description is None else json.dumps(description, ensure_ascii=False)

	@property
	def kind(self) -> str:
		""" What the pack holds, as the terminal names it.

		>>> FoundPack(Path("."), True, True, {}).kind
		'datapack and resource pack'
		"""
		return " and ".join(kind for kind, present in (("datapack", self.has_data), ("resource pack", self.has_assets)) if present)

	@property
	def namespaces(self) -> list[str]:
		""" Namespaces under data/, without minecraft, which a pack only uses to tag its own functions. """
		data: Path = self.root / "data"
		return sorted(child.name for child in data.iterdir() if child.is_dir() and child.name != "minecraft") if self.has_data else []


# Functions
def find_packs(folder: Path, depth: int = SEARCH_DEPTH) -> list[FoundPack]:
	""" Every pack in `folder` and up to `depth` levels below it, without looking inside a pack. """
	if pack := FoundPack.read(folder):
		return [pack]
	if depth == 0:
		return []
	children: list[Path] = sorted(
		child for child in folder.iterdir()
		if child.is_dir() and not child.name.startswith(".") and child.name not in SKIPPED_FOLDERS
	)
	return [pack for child in children for pack in find_packs(child, depth - 1)]

