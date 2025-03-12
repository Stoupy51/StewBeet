
# Install required package
import sys
import os
try:
	from python_datapack import build_process
except ImportError as e:
	import traceback
	traceback.print_exc()

	print("\npython_datapack package not found, installing it...")
	os.system(f"{sys.executable} -m pip install python_datapack")
	print("\npython_datapack package has been installed.\nPlease restart the build script!")
	sys.exit(-1)

# Setup config
from config import configuration

# Import my code
from user.setup_database import main as setup_database_main
from user.setup_external_database import main as setup_external_database_main
from user.link import main as link_main	# Called near the end of the build process

# Run build process
if __name__ == "__main__":
	build_process(configuration, setup_database_main, setup_external_database_main, link_main)

