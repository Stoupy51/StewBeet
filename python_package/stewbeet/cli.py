
# Imports
import importlib
import os
import shutil
import subprocess
import sys

import stouputils as stp
from beet import ProjectConfig

from .core.dump import dump_command
from .core.migrate import migrate_command
from .core.template import template_command
from .utils import get_project_config


@stp.handle_error(message="Error while running 'stewbeet'", error_log=stp.LogLevels.WARNING_TRACEBACK)
def main() -> None:
    second_arg: str = sys.argv[1].lower() if len(sys.argv) >= 2 else ""
    if second_arg == "" and len(sys.argv) == 1:
        sys.argv.append("build")

    # Print help with nice formatting
    if second_arg in ("--help", "-h", "help"):
        from importlib.metadata import version
        separator: str = "─" * 60
        print(f"""
{stp.CYAN}{separator}{stp.RESET}
{stp.CYAN}StewBeet {stp.GREEN}CLI {stp.CYAN}v{version('stewbeet')}{stp.RESET}
{stp.CYAN}{separator}{stp.RESET}
{stp.CYAN}Usage:{stp.RESET} stewbeet <command> [options]

{stp.CYAN}StewBeet commands:{stp.RESET}
  {stp.GREEN}--version, -v{stp.RESET} [depth]         Show version information for stewbeet and dependencies
  {stp.GREEN}--help, -h{stp.RESET}                    Show this help message
  {stp.GREEN}init, template{stp.RESET}                Initialize a new StewBeet project from template
  {stp.GREEN}migrate{stp.RESET}                       Migrate existing datapack/resource pack to StewBeet structure
  {stp.GREEN}dump{stp.RESET}                          Create a zip archive of the project (excludes build artifacts)
  {stp.GREEN}clean{stp.RESET}                         Clean all caches and output directories
  {stp.GREEN}rebuild{stp.RESET}                       Clean and rebuild the project

{stp.CYAN}Beet commands:{stp.RESET}
  {stp.GREEN}build{stp.RESET}                         Build the current project
  {stp.GREEN}watch{stp.RESET}                         Watch the project directory and build on file changes
  {stp.GREEN}link{stp.RESET}                          Link the generated resource pack and data pack to Minecraft
  {stp.GREEN}cache{stp.RESET}                         Inspect or clear the cache
  {stp.GREEN}ast{stp.RESET}                           Inspect cached mecha ast
  {stp.GREEN}codegen{stp.RESET}                       Inspect cached bolt codegen
  {stp.GREEN}memo{stp.RESET}                          Inspect and manage bolt memo storage

{stp.CYAN}Beet options:{stp.RESET}
  {stp.GREEN}-p, --project PATH{stp.RESET}            Select project
  {stp.GREEN}-s, --set OPTION{stp.RESET}              Set config option
  {stp.GREEN}-l, --log LEVEL{stp.RESET}               Configure output verbosity
{stp.CYAN}{separator}{stp.RESET}
""".strip())
        return

    # Print the version of stewbeet, beet, bolt, mecha, and stouputils
    if second_arg in ("--version", "-v", "version"):
        return stp.show_version("stewbeet", primary_color=stp.RED, secondary_color=stp.GREEN, max_depth=int(sys.argv[-1]) if len(sys.argv) == 3 else 2)

    # Handle "init/template" command
    if second_arg in ("init", "template"):
        return template_command()

    # Handle "migrate" command
    if second_arg == "migrate":
        return migrate_command()

    # Handle "dump" command
    if second_arg == "dump":
        return dump_command()

    # Try to find and load the beet configuration file
    cfg: ProjectConfig = get_project_config()

    # Check if the command is "clean" or "rebuild"
    if second_arg in ["clean", "rebuild"]:
        stp.info("Cleaning project and caches...")

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
        stp.info("Cleaning done!")

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
            stp.handle_error(importlib.import_module, error_log=stp.LogLevels.WARNING_TRACEBACK)(plugin)

        # Run beet with all remaining arguments
        subprocess.run([sys.executable, "-m", "beet"] + [x for x in sys.argv[1:] if x != "rebuild"], check=False)
    sys.exit(0)


if __name__ == "__main__":
    main()

