
# Imports
import importlib
import os
import shutil
import subprocess
import sys
from importlib.metadata import version

from beet import ProjectConfig
from stouputils.decorators import LogLevels, handle_error
from stouputils.print import GREEN, RED, RESET, info

from .utils import get_project_config


@handle_error(message="Error while running 'stewbeet'")
def main():
    second_arg: str = sys.argv[1] if len(sys.argv) == 2 else ""
    if second_arg == "" and len(sys.argv) == 1:
        sys.argv.append("build")

    # Print the version of stewbeet, beet, bolt, mecha, and stouputils
    if second_arg == "--version":
        for pkg in ["stewbeet", "beet", "bolt", "mecha", "smithed", "model_resolver", "stouputils"]:
            v: str = version(pkg).split("version: ")[-1]
            print(f"{RED}{pkg} {GREEN}v{v}{RESET}")
        return

    # Try to find and load the beet configuration file
    cfg: ProjectConfig = get_project_config()

    # Check if the command is "clean" or "rebuild"
    if second_arg in ["clean", "rebuild"]:
        info("Cleaning project and caches...")

        # Remove the beet cache directory
        subprocess.run([sys.executable, "-m", "beet", "cache", "-c"], check=False, capture_output=True)
        if os.path.exists(".beet_cache"):
            shutil.rmtree(".beet_cache", ignore_errors=True)

        # Remove the output directory specified in the config
        shutil.rmtree(str(cfg.output), ignore_errors=True)

        # Remove all __pycache__ folders
        for root, dirs, _ in os.walk("."):
            if "__pycache__" in dirs:
                cache_dir: str = os.path.join(root, "__pycache__")
                shutil.rmtree(cache_dir, ignore_errors=True)

        # Remove manual cache directory if specified in metadata
        cache_path: str = cfg.meta.get("stewbeet", {}).get("manual", {}).get("cache_path", "")
        if cache_path and os.path.exists(cache_path):
            shutil.rmtree(cache_path, ignore_errors=True)

        # Remove debug definitions file if it exists
        definitions_debug: str = cfg.meta.get("stewbeet", {}).get("definitions_debug", "")
        if definitions_debug and os.path.exists(definitions_debug):
            os.remove(definitions_debug)
        info("Cleaning done!")

        # Replace "rebuild" by "build" to continue the process
        if second_arg == "rebuild":
            sys.argv[1] = "build"

    # Handle all other commands except "clean"
    if second_arg != "clean":
        # Add current directory to Python path
        current_dir: str = os.getcwd()
        if current_dir not in sys.path:
            sys.path.insert(0, current_dir)

        # Try to import all pipeline
        for plugin in cfg.pipeline:
            handle_error(importlib.import_module, error_log=LogLevels.ERROR_TRACEBACK)(plugin)

        # Run beet with all remaining arguments
        subprocess.run([sys.executable, "-m", "beet"] + [x for x in sys.argv[1:] if x != "rebuild"], check=False)


if __name__ == "__main__":
    main()

