
# Imports
from config import configuration
import shutil
import os

# Delete build folder
if configuration.get("build_folder") is not None:
	shutil.rmtree(configuration["build_folder"], ignore_errors = True)
	print(f"Deleted build folder '{configuration['build_folder']}'")

# Delete manual folder
if configuration.get("manual_path") is not None:
	shutil.rmtree(configuration["manual_path"], ignore_errors = True)
	print(f"Deleted manual folder '{configuration['manual_path']}'")

# Delete database_debug, debug_manual, and cmd_cache json files
for x in ["database_debug", "manual_debug", "cmd_cache"]:
	if configuration.get(x) is not None:
		if os.path.exists(configuration[x]):
			os.remove(configuration[x])
			print(f"Deleted {x} file '{configuration[x]}'")

