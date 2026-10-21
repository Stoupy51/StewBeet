
# Imports
import os
import runpy
import subprocess
import sys
import time
from pathlib import Path

import stouputils as stp

# Constants
ROOT: Path = Path(stp.get_root_path(__file__, go_up=1))
""" The python_package folder, ex: ".../StewBeet/python_package". """
REPOSITORY: Path = ROOT.parent
""" The StewBeet repository root, holding the templates. """
TEMPLATES_FOLDER: Path = REPOSITORY / "templates"
""" Folder holding every project template (basic, extensive, minimal, ...). """
DOWNSTREAM_NAMES: tuple[str, ...] = ("SimplEnergy", "StardustFragment", "StoupGun")
""" Sibling repositories consuming StewBeet, expected right next to the StewBeet repository. """
BUILD_TIMEOUT: int = 1800
""" Maximum seconds a single project build may take before being killed. """


# Utility
def display(path: Path) -> str:
	""" Format a path relatively to the current folder, keeping it absolute when impossible.

	Args:
		path: The path to format.
	Returns:
		str: The relative path, ex: "../templates/basic" (downstream packs sit outside the repository).
	"""
	try:
		return os.path.relpath(path).replace("\\", "/")
	except ValueError:  # Different drive on Windows
		return str(path).replace("\\", "/")


# Discovery
def find_projects(filters: list[str]) -> list[Path]:
	""" Collect every buildable project (templates first, then downstream packs).

	A project is a folder holding a "beet.yml". Templates are globbed so a newly added one is picked up automatically,
	while downstream packs live outside the repository and are only warned about when missing, since a fresh clone won't have them.

	Args:
		filters: Case-insensitive substrings; when non-empty, only matching folder names are kept.
	Returns:
		list[Path]: The project folders to build, in build order.
	"""
	projects: list[Path] = sorted(path.parent for path in TEMPLATES_FOLDER.glob("*/beet.yml"))

	for name in DOWNSTREAM_NAMES:
		project: Path = REPOSITORY.parent / name
		if (project / "beet.yml").is_file():
			projects.append(project)
		else:
			stp.warning(f"Skipping '{name}': no beet.yml found at '{display(project)}'")

	if filters:
		projects = [p for p in projects if any(f.lower() in p.name.lower() for f in filters)]
	return projects


# Build
def build_project(project: Path) -> tuple[bool, float]:
	""" Build a single project by running stewbeet inside it.

	Args:
		project: The project folder, containing a "beet.yml".
	Returns:
		tuple[bool, float]: Whether the build succeeded, and how long it took in seconds.
	"""
	start: float = time.perf_counter()
	# Not captured: on Windows, beet's prompt_toolkit output crashes without a console to write to
	result: subprocess.CompletedProcess[bytes] = subprocess.run([sys.executable, "-m", "stewbeet"], cwd=project, timeout=BUILD_TIMEOUT)
	duration: float = time.perf_counter() - start

	if result.returncode != 0:
		stp.error(f"FAILED: {project.name} ({duration:.2f}s)")
		return False, duration

	stp.info(f"PASSED: {project.name} ({duration:.2f}s)")
	return True, duration


# Main
@stp.measure_time(printer=stp.info, message="All project builds finished")
def main() -> None:
	""" Build every template and downstream pack, then zip the templates once they all built. """
	projects: list[Path] = find_projects(sys.argv[1:])
	if not projects:
		stp.error("No project to build, check the arguments and that 'templates/*/beet.yml' exist")
		sys.exit(1)

	stp.info(f"Building {len(projects)} project(s): {', '.join(p.name for p in projects)}")

	failures: list[str] = []
	for project in projects:
		stp.info(f"Building: {project.name} ('{display(project)}')")
		success, _ = build_project(project)
		if not success:
			failures.append(project.name)

	if failures:
		stp.error(f"\n{len(failures)}/{len(projects)} project(s) failed to build:")
		for name in failures:
			stp.error(f"  - {name}")
		sys.exit(1)
	stp.info(f"\nAll {len(projects)} project(s) built successfully!")
	runpy.run_path(str(REPOSITORY / "scripts" / "zip_templates.py"), run_name="__main__")


if __name__ == "__main__":
	main()

