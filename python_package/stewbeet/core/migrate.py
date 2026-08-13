
# Lazy imports (PEP 810), ignored before Python 3.15
from stouputils.lazy import ALWAYS_LAZY

__lazy_modules__ = ALWAYS_LAZY

# Imports
import io
import os
import shutil
import zipfile
from typing import Any

import requests
import stouputils as stp

from ..utils import get_project_config


def migrate_command() -> None:
    """ Handle the 'migrate' command to migrate an existing datapack/resource pack to StewBeet structure.

    This command will:

    1. Check if there's no existing beet configuration
    2. Search for datapack (data/ folder) and resource pack (assets/ folder)
    3. Download and extract the basic template
    4. Migrate existing files to the src/ folder structure

    Ex: `stewbeet migrate`
    """
    # Capture the working directory BEFORE any config check (which might change cwd)
    working_dir = stp.clean_path(os.getcwd())

    # Check if beet configuration already exists
    try:
        get_project_config()
        stp.error("A beet configuration file already exists. Migration is only for projects not using StewBeet or beet yet.")
        return
    except (AssertionError, FileNotFoundError):
        # No config found, continue with migration
        pass

    stp.info("Searching for datapack and resource pack structures...")

    # Search for datapack and resource pack structures
    datapack_info = _find_pack_structure("data", working_dir)
    resource_pack_info = _find_pack_structure("assets", working_dir)

    if not datapack_info and not resource_pack_info:
        stp.error("No datapack or resource pack structure found. Migration requires at least a 'data/' or 'assets/' folder.")
        return

    # Display what was found
    if datapack_info:
        stp.info(f"✓ Found datapack: {stp.relative_path(datapack_info['path'])}")
    if resource_pack_info:
        stp.info(f"✓ Found resource pack: {stp.relative_path(resource_pack_info['path'])}")

    # Ask user confirmation
    stp.warning("This will download the 'basic' template and migrate your existing files to the StewBeet structure.")
    stp.warning("It's recommended to backup your project before proceeding.")
    stp.info("Do you want to continue? (y/n):", end=" ")
    choice = input().strip().lower()
    if choice not in ("y", "yes"):
        stp.info("Migration cancelled.")
        return

    # Download the basic template
    stp.info("Downloading basic template...")
    from importlib.metadata import version
    template_url = f"https://raw.githubusercontent.com/Stoupy51/StewBeet/refs/tags/v{version('stewbeet')}/templates/basic_template.zip"

    try:
        response = requests.get(template_url)
        if response.status_code != 200:
            stp.error(f"Failed to download template. HTTP status code: {response.status_code}")
            return
    except Exception as e:
        stp.error(f"Failed to download template: {e}")
        return

    # Extract the template
    stp.info("Extracting template...")
    try:
        with zipfile.ZipFile(io.BytesIO(response.content)) as zip_file:
            zip_file.extractall(working_dir)
    except Exception as e:
        stp.error(f"Failed to extract template: {e}")
        return

    # Migrate datapack if found
    if datapack_info:
        _migrate_pack(datapack_info, "data", "datapack", working_dir)

    # Migrate resource pack if found
    if resource_pack_info:
        _migrate_pack(resource_pack_info, "assets", "resource pack", working_dir)

    stp.info("✓ Migration completed successfully!")
    stp.info("Next steps:")
    stp.info("  1. Edit beet.yml to configure your project (id, name, author, etc.)")
    stp.info("  2. Run 'stewbeet build' to build your project")


def _find_pack_structure(folder_name: str, search_dir: str | None = None) -> dict[str, Any] | None:
    """ Find a pack structure (data/ or assets/) in the current directory or subdirectories.

    Args:
        folder_name: The folder to search for ('data' or 'assets')
        search_dir: Directory to search in (defaults to current working directory)

    Returns:
        A dict with 'path' (str to the folder), 'parent' (parent directory), and 'has_pack_mcmeta' (bool)
        Returns None if not found or if pack.mcmeta doesn't exist alongside
    """
    current_dir = search_dir if search_dir else os.getcwd()

    # Check if folder exists at root level
    folder_path = f"{current_dir}/{folder_name}"
    if os.path.isdir(folder_path):
        pack_mcmeta_path = f"{current_dir}/pack.mcmeta"
        has_pack_mcmeta = os.path.exists(pack_mcmeta_path)
        if has_pack_mcmeta:
            return {
                "path": folder_path,
                "parent": current_dir,
                "has_pack_mcmeta": has_pack_mcmeta
            }

    # Check in subdirectories (up to two levels deep)
    for subdir_name in os.listdir(current_dir):
        subdir = f"{current_dir}/{subdir_name}"
        if os.path.isdir(subdir):
            # Check one level deep
            pack_folder = f"{subdir}/{folder_name}"
            if os.path.isdir(pack_folder):
                pack_mcmeta_path = f"{subdir}/pack.mcmeta"
                has_pack_mcmeta = os.path.exists(pack_mcmeta_path)
                if has_pack_mcmeta:
                    return {
                        "path": pack_folder,
                        "parent": subdir,
                        "has_pack_mcmeta": has_pack_mcmeta
                    }

            # Check two levels deep
            for subsubdir_name in os.listdir(subdir):
                subsubdir = f"{subdir}/{subsubdir_name}"
                if os.path.isdir(subsubdir):
                    pack_folder = f"{subsubdir}/{folder_name}"
                    if os.path.isdir(pack_folder):
                        pack_mcmeta_path = f"{subsubdir}/pack.mcmeta"
                        has_pack_mcmeta = os.path.exists(pack_mcmeta_path)
                        if has_pack_mcmeta:
                            return {
                                "path": pack_folder,
                                "parent": subsubdir,
                                "has_pack_mcmeta": has_pack_mcmeta
                            }

    return None


def _migrate_pack(pack_info: dict[str, str | bool], folder_name: str, pack_type: str, working_dir: str) -> None:
    """ Migrate a pack (datapack or resource pack) to the StewBeet structure.

    Args:
        pack_info: Dict containing pack information from _find_pack_structure
        folder_name: 'data' or 'assets'
        pack_type: 'datapack' or 'resource pack' (for logging)
        working_dir: The working directory where migration is happening
    """
    stp.info(f"Migrating {pack_type}...")

    # Remove the template's src folder for this pack type if it exists
    template_src_folder = f"{working_dir}/src/{folder_name}"
    if os.path.exists(template_src_folder):
        stp.debug(f"  Removing template's {stp.relative_path(template_src_folder)}...")
        shutil.rmtree(template_src_folder)

    # Create src directory if it doesn't exist
    src_dir = f"{working_dir}/src"
    os.makedirs(src_dir, exist_ok=True)

    # Move the pack folder to src/
    source_path: str = pack_info["path"]  # type: ignore
    dest_path = f"{src_dir}/{folder_name}"

    stp.info(f"  Moving {stp.relative_path(source_path)} to {stp.relative_path(dest_path)}...")
    try:
        shutil.move(source_path, dest_path)
    except Exception as e:
        stp.error(f"Failed to move {folder_name}: {e}")
        return

    # If pack.mcmeta exists in the parent directory and we're in a subdirectory, move it too
    parent_path: str = pack_info["parent"]  # type: ignore
    has_pack_mcmeta: bool = pack_info["has_pack_mcmeta"]  # type: ignore
    if has_pack_mcmeta and parent_path != working_dir:
        pack_mcmeta_src = f"{parent_path}/pack.mcmeta"
        pack_mcmeta_dest = f"{src_dir}/pack.mcmeta"
        if os.path.exists(pack_mcmeta_src) and not os.path.exists(pack_mcmeta_dest):
            stp.debug(f"  Moving pack.mcmeta to {stp.relative_path(pack_mcmeta_dest)}...")
            shutil.move(pack_mcmeta_src, pack_mcmeta_dest)

        # Also move pack.png if it exists (goes to assets/ folder at root)
        pack_png_src = f"{parent_path}/pack.png"
        assets_dir = f"{working_dir}/assets"
        os.makedirs(assets_dir, exist_ok=True)
        pack_png_dest = f"{assets_dir}/pack.png"
        if os.path.exists(pack_png_src) and not os.path.exists(pack_png_dest):
            stp.debug(f"  Moving pack.png to {stp.relative_path(pack_png_dest)}...")
            shutil.move(pack_png_src, pack_png_dest)

    # Clean up empty parent directory if it was a subdirectory
    if parent_path != working_dir:
        try:
            # Check if directory is empty
            if not os.listdir(parent_path):
                stp.debug(f"  Removing empty directory {stp.relative_path(parent_path)}...")
                os.rmdir(parent_path)
        except Exception:
            pass  # Ignore errors when cleaning up

    stp.info(f"  ✓ {pack_type.capitalize()} migrated successfully")
