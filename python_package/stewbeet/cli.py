
# Imports
import importlib
import os
import shutil
import subprocess
import sys

from beet import ProjectConfig
from box import Box
from stouputils.decorators import LogLevels, handle_error
from stouputils.print import info

from .utils import get_project_config


@handle_error(message="Error while running 'stewbeet'")
def main():
    second_arg: str = sys.argv[1] if len(sys.argv) == 2 else ""

    # Try to find and load the beet configuration file
    cfg: ProjectConfig | None = get_project_config()

    # Check if the command is "clean" or "rebuild"
    if second_arg in ["clean", "rebuild"]:
        info("Cleaning project and caches...")

        # Remove the beet cache directory
        subprocess.run(["beet", "cache", "-c"], check=False, capture_output=True)
        if os.path.exists(".beet_cache"):
            shutil.rmtree(".beet_cache", ignore_errors=True)

        # Remove the output directory specified in the config
        shutil.rmtree(cfg.output, ignore_errors=True)

        # Remove all __pycache__ folders
        for root, dirs, _ in os.walk("."):
            if "__pycache__" in dirs:
                cache_dir: str = os.path.join(root, "__pycache__")
                shutil.rmtree(cache_dir, ignore_errors=True)

        # Load metadata from config into a Box
        meta: Box = Box(cfg.meta, default_box=True, default_box_attr={})

        # Remove manual cache directory if specified in metadata
        cache_path: str = meta.stewbeet.manual.cache_path
        if cache_path and os.path.exists(cache_path):
            shutil.rmtree(cache_path, ignore_errors=True)

        # Remove debug definitions file if it exists
        definitions_debug: str = meta.stewbeet.definitions_debug
        if definitions_debug and os.path.exists(definitions_debug):
            os.remove(definitions_debug)
        info("Cleaning done!")

    if second_arg != "clean":
        # Add current directory to Python path
        current_dir: str = os.getcwd()
        if current_dir not in sys.path:
            sys.path.insert(0, current_dir)

        # Try to import all pipeline
        for plugin in cfg.pipeline:
            handle_error(importlib.import_module, error_log=LogLevels.ERROR_TRACEBACK)(plugin)

        # Run beet with all remaining arguments
        subprocess.run(["beet"] + [x for x in sys.argv[1:] if x != "rebuild"], check=False)


if __name__ == "__main__":
    main()
