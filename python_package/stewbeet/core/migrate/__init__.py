""" `stewbeet migrate [minimal|basic] [--dry-run] [--yes]`: turn an existing datapack or resource pack into a StewBeet project. """
# Lazy imports (PEP 810), ignored before Python 3.15
from stouputils.lazy import ALWAYS_LAZY

__lazy_modules__ = ALWAYS_LAZY

# Imports
import io
import sys
import zipfile
from pathlib import Path

import requests
import stouputils as stp
from beet import locate_config

from ..template import TEMPLATES_URL
from .packs import SEARCH_DEPTH, FoundPack, find_packs
from .plan import MigrationPlan, build_plan

# Constants
MIGRATION_TEMPLATES: tuple[str, ...] = ("minimal", "basic")
""" Templates a pack can be migrated onto. The extensive one ships example content that would mix with the pack's. """

FLAGS: frozenset[str] = frozenset({"--dry-run", "--yes", "-y"})


# Functions
def migrate_command() -> None:
	""" Parse the command line, then migrate the packs found in the working directory. """
	arguments: list[str] = sys.argv[2:]
	names: list[str] = [argument.lower() for argument in arguments if not argument.startswith("-")]
	if unknown := [argument for argument in arguments if argument.startswith("-") and argument not in FLAGS]:
		stp.error(f"Unknown option {', '.join(unknown)}. Usage: stewbeet migrate [minimal|basic] [--dry-run] [--yes]")
		return
	assume_yes: bool = "--yes" in arguments or "-y" in arguments

	working_dir: Path = Path.cwd()
	if locate_config(working_dir, parents=False):
		stp.error("This folder already has a beet configuration. Migration is for packs that do not use beet or StewBeet yet.")
		return
	if not (packs := select_packs(working_dir)):
		return

	template_name: str | None = names[0] if names else ("minimal" if assume_yes else ask_template())
	if template_name not in MIGRATION_TEMPLATES:
		stp.error(f"Migration supports the {' and '.join(MIGRATION_TEMPLATES)} templates, not '{template_name}'.")
		return
	if not (archive := download_template(template_name)):
		return
	with zipfile.ZipFile(io.BytesIO(archive)) as template:
		run_migration(working_dir, template, *packs, dry_run="--dry-run" in arguments, assume_yes=assume_yes)


def select_packs(working_dir: Path) -> tuple[FoundPack | None, FoundPack | None] | None:
	""" The datapack and the resource pack to migrate, or None after telling the user why there is nothing to migrate. """
	packs: list[FoundPack] = find_packs(working_dir)
	datapacks: list[FoundPack] = [pack for pack in packs if pack.has_data]
	resource_packs: list[FoundPack] = [pack for pack in packs if pack.has_assets]
	if not packs:
		stp.error(f"No pack found: migration looks for a pack.mcmeta next to a data/ or assets/ folder, up to {SEARCH_DEPTH} folders deep.")
		return None
	for kind, found in (("datapacks", datapacks), ("resource packs", resource_packs)):
		if len(found) > 1:
			listing: str = "".join(f"\n  - {pack.root.relative_to(working_dir).as_posix()}" for pack in found)
			stp.error(f"Found {len(found)} {kind}, migration takes one of each. Run it from the folder of the one to migrate:{listing}")
			return None
	for pack in packs:
		stp.info(f"Found {pack.kind} in {pack.root.relative_to(working_dir).as_posix()}")
	return (datapacks[0] if datapacks else None, resource_packs[0] if resource_packs else None)


def ask_template() -> str:
	stp.info("Template to migrate onto: 'minimal' (beet with one StewBeet plugin) or 'basic' (every plugin configured). Press Enter for minimal:", end=" ")
	return input().strip().lower() or "minimal"


def download_template(template_name: str) -> bytes | None:
	""" The template archive matching the installed StewBeet version, or None after reporting why it could not be fetched. """
	from importlib.metadata import version
	url: str = TEMPLATES_URL[template_name]["url"].replace("__VERSION__", f"v{version('stewbeet')}")
	try:
		response: requests.Response = requests.get(url, timeout=30)
	except requests.RequestException as error:
		stp.error(f"Could not download the '{template_name}' template: {error}")
		return None
	if response.status_code != 200:
		stp.error(f"Could not download the '{template_name}' template from {url}: HTTP {response.status_code}")
		return None
	return response.content


def run_migration(working_dir: Path, template: zipfile.ZipFile, datapack: FoundPack | None, resource_pack: FoundPack | None, *, dry_run: bool, assume_yes: bool) -> MigrationPlan | None:
	""" Show the plan, then apply it unless this is a dry run or the user declines.

	Returns:
		The plan when it could run (applied, unless `dry_run`), None when it was refused or cancelled.
	"""
	plan: MigrationPlan = build_plan(working_dir, template, datapack, resource_pack)
	stp.info("Migration plan:\n" + "\n".join(f"  {line}" for line in plan.describe()))
	for warning in plan.warnings:
		stp.warning(warning)
	if conflicts := plan.conflicts():
		stp.error("Nothing was changed, because:" + "".join(f"\n  - {conflict}" for conflict in conflicts))
		return None
	if dry_run:
		stp.info("Dry run: nothing was changed. Run the same command without --dry-run to apply this plan.")
		return plan
	if not assume_yes:
		stp.warning("Files are moved, not copied. Commit or back up the folder first.")
		stp.info("Apply this plan? (y/n):", end=" ")
		if input().strip().lower() not in ("y", "yes"):
			stp.info("Migration cancelled, nothing was changed.")
			return None

	plan.apply(template)
	stp.info("Migration done. Next: check beet.yml, then run 'stewbeet build'.")
	return plan

