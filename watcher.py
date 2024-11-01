# Install required packages
import sys
import os
try:
	from python_datapack import check_config_format
except ImportError:
	os.system(f"{sys.executable} -m pip install python_datapack watchdog")
	print("\nRequired modules have been installed.\nPlease restart the watcher script")
	sys.exit(-1)

# Import configuration and watcher
from config import configuration, ROOT
from python_datapack.utils.print import error
from python_datapack.watcher import watcher


# Main
if __name__ == "__main__":
	if not check_config_format(configuration):
		error("Invalid config format, please check the documentation")

	# Setup and start file watcher
	configs_to_get: list[str] = ["merge_folder", "assets_folder", "libs_folder"]
	to_watch: list[str] = [configuration[x] + '/' for x in configs_to_get if configuration.get(x, None) is not None]
	to_watch += [
		f"{ROOT}/user/",
		f"{ROOT}/config.py",
	]
	to_ignore: list[str] = [
		"__pycache__/",
		".git/",
		".venv/",
	]
	
	# Start the watcher
	watcher(to_watch, to_ignore, f"{ROOT}/build.py")

