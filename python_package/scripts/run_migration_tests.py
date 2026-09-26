""" Run `stewbeet migrate` on generated packs and check what it leaves on disk.

Every scenario builds a pack in a temporary folder and migrates it onto the templates of this checkout, so nothing is downloaded.
The migrated projects that should build are then built with StewBeet, which is the point of migrating.
"""
# Imports
import json
import os
import subprocess
import sys
import tempfile
import zipfile
from collections.abc import Callable
from pathlib import Path

import stouputils as stp
from PIL import Image

from stewbeet.core.migrate import run_migration, select_packs
from stewbeet.core.migrate.plan import MigrationPlan

# Constants
TEMPLATES: Path = Path(__file__).resolve().parents[2] / "templates"
""" The template archives `stewbeet migrate` would otherwise download. """

PLAIN_MCMETA: dict[str, dict[str, int | str]] = {"pack": {"pack_format": 48, "description": "My pack"}}


# Helpers
def write(path: Path, content: str) -> None:
	path.parent.mkdir(parents=True, exist_ok=True)
	path.write_text(content, encoding="utf-8")


def make_pack(
	root: Path, *, data: bool = True, assets: bool = False, mcmeta: object = PLAIN_MCMETA, icon_color: str | None = "red"
) -> None:
	""" A small pack: one function and its load tag, one lang file, and a pack.png unlike the templates' own. """
	write(root / "pack.mcmeta", json.dumps(mcmeta))
	if data:
		write(root / "data/mypack/function/hello.mcfunction", "say hello\n")
		write(root / "data/minecraft/tags/function/load.json", '{"values": ["mypack:hello"]}')
	if assets:
		write(root / "assets/mypack/lang/en_us.json", '{"item.mypack.gem": "Gem"}')
	if icon_color:
		Image.new("RGBA", (16, 16), icon_color).save(root / "pack.png")


def migrate(working_dir: Path, template_name: str, *, dry_run: bool = False) -> MigrationPlan | None:
	packs = select_packs(working_dir)
	assert packs, "select_packs found nothing to migrate"
	with zipfile.ZipFile(TEMPLATES / f"{template_name}_template.zip") as template:
		return run_migration(working_dir, template, *packs, dry_run=dry_run, assume_yes=True)


def snapshot(folder: Path) -> dict[str, bytes]:
	return {path.relative_to(folder).as_posix(): path.read_bytes() for path in folder.rglob("*") if path.is_file()}


def build(project: Path) -> None:
	result = subprocess.run(
		[sys.executable, "-m", "stewbeet", "build"],
		cwd=project, capture_output=True, encoding="utf-8", errors="replace", timeout=300,
		env=os.environ | {"PYTHONIOENCODING": "utf-8", "STEWBEET_TELEMETRY": "0"},
	)
	assert result.returncode == 0, f"the migrated project does not build:\n{result.stdout}\n{result.stderr}"
	assert (project / "build/datapack/data/mypack/function/hello.mcfunction").is_file(), "the build must contain the migrated function"


# Scenarios
def root_datapack_onto_minimal(folder: Path) -> None:
	make_pack(folder)
	icon: bytes = (folder / "pack.png").read_bytes()
	assert migrate(folder, "minimal")
	assert (folder / "src/data/mypack/function/hello.mcfunction").is_file()
	assert (folder / "src/pack.png").read_bytes() == icon, "the pack's icon must replace the template's"
	assert not any((folder / name).exists() for name in ("data", "pack.mcmeta", "pack.png")), "nothing may stay behind at the root"
	assert not (folder / "src/data/minimal").exists(), "the template's example function must not be added"
	assert 'description: "My pack"' in (folder / "beet.yml").read_text(encoding="utf-8")
	build(folder)


def nested_datapack_onto_basic(folder: Path) -> None:
	make_pack(folder / "packs/My Pack")
	icon: bytes = (folder / "packs/My Pack/pack.png").read_bytes()
	write(folder / ".gitignore", "mine\n")
	write(folder / "pyproject.toml", "# mine\n")
	assert migrate(folder, "basic")
	assert (folder / ".gitignore").read_text(encoding="utf-8") == "mine\n", "the template must not overwrite .gitignore"
	assert (folder / "pyproject.toml").read_text(encoding="utf-8") == "# mine\n", "the template must not overwrite pyproject.toml"
	assert (folder / "assets/pack.png").read_bytes() == icon, "the basic template keeps its icon in assets/"
	assert not (folder / "packs").exists(), "emptied folders must be removed, parents included"
	assert not (folder / "src/data/basic_template").exists()
	config: str = (folder / "beet.yml").read_text(encoding="utf-8")
	assert 'id: "mypack"' in config and 'name: "My Pack"' in config, "id and name must come from the pack"


def separate_packs_onto_minimal(folder: Path) -> None:
	make_pack(folder / "datapack", mcmeta={"pack": {"pack_format": 48, "description": "Data"}})
	make_pack(folder / "resourcepack", data=False, assets=True, icon_color="blue")
	plan = migrate(folder, "minimal")
	assert plan and any("left in place" in warning for warning in plan.warnings), "the second pack.png must be reported"
	assert (folder / "src/assets/mypack/lang/en_us.json").is_file()
	config: str = (folder / "beet.yml").read_text(encoding="utf-8")
	assert "resource_pack:" in config, "the minimal template must be given a resource pack"
	assert 'description: "Data"' in config
	assert not (folder / "datapack").exists()
	build(folder)


def combined_pack_with_overlays(folder: Path) -> None:
	make_pack(folder / "pack", assets=True, mcmeta={**PLAIN_MCMETA, "overlays": {"entries": []}})
	plan = migrate(folder, "basic")
	assert plan and any("kept in src/" in warning for warning in plan.warnings)
	assert json.loads((folder / "src/pack.mcmeta").read_text(encoding="utf-8"))["overlays"] == {"entries": []}
	assert (folder / "src/data").is_dir() and (folder / "src/assets").is_dir()


def two_datapacks_are_refused(folder: Path) -> None:
	make_pack(folder / "one")
	make_pack(folder / "two")
	before: dict[str, bytes] = snapshot(folder)
	assert select_packs(folder) is None
	assert snapshot(folder) == before


def dry_run_changes_nothing(folder: Path) -> None:
	make_pack(folder / "nested", assets=True)
	before: dict[str, bytes] = snapshot(folder)
	plan = migrate(folder, "basic", dry_run=True)
	assert plan and plan.steps
	assert snapshot(folder) == before


def conflict_changes_nothing(folder: Path) -> None:
	make_pack(folder / "nested")
	write(folder / "src/data/other/function/tick.mcfunction", "say tick\n")
	before: dict[str, bytes] = snapshot(folder)
	assert migrate(folder, "minimal") is None, "an existing src/data must stop the migration"
	assert snapshot(folder) == before


SCENARIOS: list[Callable[[Path], None]] = [
	root_datapack_onto_minimal,
	nested_datapack_onto_basic,
	separate_packs_onto_minimal,
	combined_pack_with_overlays,
	two_datapacks_are_refused,
	dry_run_changes_nothing,
	conflict_changes_nothing,
]


# Main
@stp.measure_time(printer=stp.info, message="All migration tests finished")
def main() -> None:
	failures: list[str] = []
	for scenario in SCENARIOS:
		with tempfile.TemporaryDirectory() as temporary:
			try:
				scenario(Path(temporary).resolve())
				stp.info(f"PASSED: {scenario.__name__}")
			except Exception as error:
				stp.error(f"FAILED: {scenario.__name__}: {error!r}")
				failures.append(scenario.__name__)
	if failures:
		stp.error(f"{len(failures)} migration test(s) failed: {', '.join(failures)}")
		sys.exit(1)
	stp.info(f"All {len(SCENARIOS)} migration tests passed!")


if __name__ == "__main__":
	main()

