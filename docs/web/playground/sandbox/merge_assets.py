""" Merge the textures and renders of several projects into the one folder the sandbox builds with.

Run once at image build time, over the sparse clones. StewBeet resolves a texture by filename, so
the three packs go into a single flat folder and a name can only belong to one of them: later
sources in SOURCES win, and every overwrite is reported.

Collisions are the normal case, not an error. Measured on the real repositories: 2 among the
textures, and 89 among the renders, almost all of them the vanilla `minecraft/` items that every
project caches. Failing the image build over that would mean it never builds.
"""
# Imports
import json
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path

# Constants
MAX_TOTAL_BYTES: int = 32 * 1024 * 1024
""" The merged folder ships in the image and is read by every build. Measured at roughly 9 MB. """


# Classes
@dataclass(frozen=True)
class Source:
	""" One cloned project contributing textures and renders. """

	name: str
	""" Shown in the manifest and in the collision report. """

	textures: str
	""" Path of its flat texture folder inside the clone. """

	renders: str
	""" Path of its `<namespace>/<item>.png` render cache inside the clone. """


SOURCES: list[Source] = [
	Source(name="simplenergy", textures="simplenergy/assets/textures", renders="simplenergy/iso_renders"),
	Source(name="stardust",    textures="stardust/assets/textures",    renders="stardust/iso_renders"),
	Source(name="extensive",   textures="extensive/templates/extensive/assets/textures", renders="extensive/templates/extensive/iso_renders"),
]
""" Lowest precedence first: the extensive template is the documented one, so it wins a tie. """


# Functions
def merge(clones: Path, destination: Path, attribute: str) -> dict[str, str]:
	""" Copy one kind of asset from every source, later sources overwriting earlier ones.

	Args:
		clones      (Path): Directory holding the sparse clones.
		destination (Path): Directory to fill.
		attribute   (str):  Either "textures" or "renders".
	Returns:
		dict[str, str]: Destination relative path -> name of the source that ended up owning it.
	"""
	owners: dict[str, str] = {}
	for source in SOURCES:
		root: Path = clones / getattr(source, attribute)
		if not root.is_dir():
			print(f"  {source.name}: no {attribute} at {root}, skipped")
			continue

		count: int = 0
		for path in sorted(root.rglob("*")):
			if not path.is_file():
				continue
			relative: str = path.relative_to(root).as_posix()
			target: Path = destination / relative
			target.parent.mkdir(parents=True, exist_ok=True)
			shutil.copy2(path, target)
			owners[relative] = source.name
			count += 1
		print(f"  {source.name}: {count} {attribute}")
	return owners


def report(clones: Path, attribute: str) -> int:
	""" Count how many names more than one source provides.

	Args:
		clones    (Path): Directory holding the sparse clones.
		attribute (str):  Either "textures" or "renders".
	Returns:
		int: Number of colliding names.
	"""
	seen: set[str] = set()
	collisions: set[str] = set()
	for source in SOURCES:
		root: Path = clones / getattr(source, attribute)
		if not root.is_dir():
			continue
		for path in root.rglob("*"):
			if path.is_file():
				relative: str = path.relative_to(root).as_posix()
				collisions.add(relative) if relative in seen else seen.add(relative)
	return len(collisions)


def main() -> int:
	""" Merge into the destination and write the manifest the worker serves at GET /textures.

	Returns:
		int: 0 unless the merged folder came out larger than the image budget.
	"""
	if len(sys.argv) != 3:
		print("usage: merge_assets.py <clones directory> <destination directory>")
		return 2

	clones: Path = Path(sys.argv[1])
	destination: Path = Path(sys.argv[2])

	print("Textures:")
	textures: dict[str, str] = merge(clones, destination / "textures", "textures")
	print(f"  {report(clones, 'textures')} name(s) provided by more than one source, highest precedence kept")

	print("Renders:")
	merge(clones, destination / "iso_renders", "renders")
	print(f"  {report(clones, 'renders')} name(s) provided by more than one source, highest precedence kept")

	# What a visitor can reference by name, which the playground lists next to the editor.
	manifest: list[dict[str, str]] = [
		{"name": Path(relative).stem, "source": owner}
		for relative, owner in sorted(textures.items())
		if relative.endswith(".png")
	]
	(destination / "textures.json").write_text(json.dumps(manifest, indent=1), encoding="utf-8", newline="\n")

	total: int = sum(path.stat().st_size for path in destination.rglob("*") if path.is_file())
	print(f"Merged {len(manifest)} textures, {total / 1024 / 1024:.1f} MB total")
	if total > MAX_TOTAL_BYTES:
		print(f"FAILED: {total / 1024 / 1024:.1f} MB exceeds the {MAX_TOTAL_BYTES / 1024 / 1024:.0f} MB budget")
		return 1
	return 0


if __name__ == "__main__":
	sys.exit(main())
