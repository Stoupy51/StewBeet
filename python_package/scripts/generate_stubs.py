
# Imports
import stouputils.continuous_delivery as cd
from stouputils.io import get_root_path

# Constants
ROOT: str = get_root_path(__file__, go_up=1)
PACKAGE_NAME: str = "stouputils"
CLEAN_BEFORE: bool = True

if __name__ == "__main__":

	cd.stubs_full_routine(
		package_name=PACKAGE_NAME,
		output_directory=ROOT,	# Merge stubs into the package directory
		clean_before=CLEAN_BEFORE,
	)

