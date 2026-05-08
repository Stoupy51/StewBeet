
# Imports
import os
import sys
import zipfile

import stouputils as stp

from ..utils import get_project_config


def dump_command() -> None:
    """ Handle the 'dump' command to create a zip archive of the project.
    Excludes build outputs, cache directories, and other temporary files.

    Ex: `stewbeet dump [output_name.zip]`
    """
    # Get the project configuration
    cfg = get_project_config()

    # Determine output zip filename
    output_name: str = sys.argv[2] if len(sys.argv) >= 3 else "project_dump.zip"
    if not output_name.endswith(".zip"):
        output_name += ".zip"

    # Get paths to exclude from the archive
    exclude_paths: set[str] = {
        ".beet_cache",
        "__pycache__",
        ".git",
        ".vscode",
        ".idea",
        "*.pyc",
        ".DS_Store",
        "Thumbs.db",
    }

    # Add patterns from .gitignore if it exists
    if os.path.exists(".gitignore"):
        with stp.super_open(".gitignore", "r") as f:
            for line in f.readlines():
                line: str = line.strip()
                # Skip empty lines and comments
                if line and not line.startswith("#"):
                    exclude_paths.add(line)

    # Add output directory from config
    if cfg.output:
        exclude_paths.add(stp.relative_path(str(cfg.output)))

    # Add manual cache path from config
    manual_config = cfg.meta.get("stewbeet", {}).get("manual", {})
    cache_path: str = manual_config.get("cache_path", "")
    if cache_path:
        exclude_paths.add(stp.relative_path(cache_path))

    # Add definitions_debug if specified
    definitions_debug: str = cfg.meta.get("stewbeet", {}).get("definitions_debug", "")
    if definitions_debug:
        exclude_paths.add(stp.relative_path(definitions_debug))

    # Add files from ignore list in config
    ignore_patterns: list[str] = cfg.ignore or []
    exclude_paths.update(ignore_patterns)

    stp.debug(f"Creating project archive: '{output_name}'")
    stp.debug(f"Excluding: {', '.join(sorted(exclude_paths))}")

    # Create the zip file
    files_added = 0

    try:
        with zipfile.ZipFile(output_name, "w", zipfile.ZIP_DEFLATED, strict_timestamps=False) as zip_file:
            # Walk through all files in the current directory
            for root, dirs, files in os.walk("."):
                # Get relative path
                root = stp.relative_path(root)

                # Check if this directory should be excluded
                should_exclude = False
                for exclude in exclude_paths:
                    # Check if the current path matches any exclude pattern
                    if exclude in root.split("/"):
                        should_exclude = True
                        break
                    # Check if the path starts with the exclude pattern
                    if root.startswith(exclude.rstrip("*")):
                        should_exclude = True
                        break

                if should_exclude:
                    # Remove excluded directories from dirs list to prevent os.walk from traversing them
                    dirs[:] = []
                    continue

                # Filter out excluded directories from dirs list
                dirs[:] = [
                    d for d in dirs
                    if not any(
                        d == excl or d.startswith(excl.rstrip("*"))
                        for excl in exclude_paths
                    )
                ]

                # Add files from this directory
                for file in files:
                    file_path = f"{root}/{file}" if root != "." else file

                    # Check if this specific file should be excluded
                    should_exclude_file = False
                    for exclude in exclude_paths:
                        if exclude.startswith("*") and file_path.endswith(exclude[1:]):
                            should_exclude_file = True
                            break
                        if file_path == exclude or file_path.startswith(exclude):
                            should_exclude_file = True
                            break

                    # Don't include the output zip file itself
                    if file_path == output_name:
                        should_exclude_file = True

                    if not should_exclude_file:
                        zip_file.write(file_path, file_path)
                        files_added += 1

        stp.info(f"✓ Successfully created archive with {files_added} files: '{output_name}'")

    except Exception as e:
        stp.error(f"Failed to create archive: {e}")
        # Remove partially created zip file
        if os.path.exists(output_name):
            os.remove(output_name)
        raise

