
# Lazy imports (PEP 810), ignored before Python 3.15
from stouputils.lazy import ALWAYS_LAZY

__lazy_modules__ = ALWAYS_LAZY

# Imports
import os
import sys
import zipfile

import stouputils as stp
from beet import ProjectConfig

from ..utils import get_project_config


def dump_command() -> None:
	""" Handle the 'dump' command to create a zip archive of the project.
	Excludes build outputs, cache directories, and other temporary files.

	Ex: `stewbeet dump [output_name.zip]`
	"""
	cfg = get_project_config()
	output_name: str = sys.argv[2] if len(sys.argv) >= 3 else "project_dump.zip"
	if not output_name.endswith(".zip"):
		output_name += ".zip"
	exclude_paths: set[str] = dump_exclusions(cfg)
	stp.debug(f"Creating project archive: '{output_name}'")
	stp.debug(f"Excluding: {', '.join(sorted(exclude_paths))}")
	try:
		files_added: int = write_archive(output_name, exclude_paths)
		stp.info(f"✓ Successfully created archive with {files_added} files: '{output_name}'")
	except Exception as e:
		stp.error(f"Failed to create archive: {e}")
		# Remove partially created zip file
		if os.path.exists(output_name):
			os.remove(output_name)
		raise


def dump_exclusions(cfg: ProjectConfig) -> set[str]:
	""" What the archive leaves out: caches, editor and VCS folders, .gitignore patterns, the build output and generated files. """
	exclude_paths: set[str] = {
		".beet_cache",
		"__pycache__",
		".git",
		".github",
		".vscode",
		".idea",
		".venv",
		"*.pyc",
		".DS_Store",
		"Thumbs.db",
		"docs",
	}
	if os.path.exists(".gitignore"):
		with stp.super_open(".gitignore", "r") as f:
			exclude_paths.update(line.strip() for line in f.readlines() if line.strip() and not line.strip().startswith("#"))
	if cfg.output:
		exclude_paths.add(stp.relative_path(str(cfg.output)))

	# The item renders folder, under its older `manual.cache_path` key when the new one is unset
	stewbeet_meta = cfg.meta.get("stewbeet", {})
	renders_path: str = stewbeet_meta.get("iso_renders_path", "") or stewbeet_meta.get("manual", {}).get("cache_path", "")
	if renders_path:
		exclude_paths.add(stp.relative_path(renders_path))
	definitions_debug: str = stewbeet_meta.get("definitions_debug", "")
	if definitions_debug:
		exclude_paths.add(stp.relative_path(definitions_debug))
	exclude_paths.update(cfg.ignore or [])
	return exclude_paths


def write_archive(output_name: str, exclude_paths: set[str]) -> int:
	""" Zip every file of the current directory not excluded, and return how many went in. """
	files_added: int = 0
	with zipfile.ZipFile(output_name, "w", zipfile.ZIP_DEFLATED, strict_timestamps=False) as zip_file:
		for root, dirs, files in os.walk("."):
			root = stp.relative_path(root)
			if directory_excluded(root, exclude_paths):
				# Stop os.walk from going any deeper
				dirs[:] = []
				continue
			dirs[:] = [d for d in dirs if not any(d == excl or d.startswith(excl.rstrip("*")) for excl in exclude_paths)]
			for file in files:
				file_path: str = f"{root}/{file}" if root != "." else file
				if file_path != output_name and not file_excluded(file_path, exclude_paths):
					zip_file.write(file_path, file_path)
					files_added += 1
	return files_added


def directory_excluded(root: str, exclude_paths: set[str]) -> bool:
	""" Whether a directory is excluded: one of its path parts is a pattern, or it starts with one, a trailing `*` dropped.

	>>> directory_excluded("src/__pycache__", {"__pycache__"}), directory_excluded("src", {"build"})
	(True, False)
	"""
	return any(exclude in root.split("/") or root.startswith(exclude.rstrip("*")) for exclude in exclude_paths)


def file_excluded(file_path: str, exclude_paths: set[str]) -> bool:
	""" Whether a file is excluded: a `*.ext` pattern matches its end, or the path starts with a pattern.

	>>> file_excluded("a/b.pyc", {"*.pyc"}), file_excluded("notes.txt", {"build"})
	(True, False)
	"""
	return any(
		(exclude.startswith("*") and file_path.endswith(exclude[1:])) or file_path.startswith(exclude)
		for exclude in exclude_paths
	)

