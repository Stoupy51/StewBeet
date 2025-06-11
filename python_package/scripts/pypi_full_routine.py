
# Imports
import stouputils.continuous_delivery as cd
from stouputils.io import get_root_path

# Constants
ROOT: str = get_root_path(__file__, go_up=1)
REPOSITORY: str = "stewbeet"
DIST_DIRECTORY: str = f"{ROOT}/dist"
LAST_FILES: int = 1
ENDSWITH: str = ".tar.gz"

if __name__ == "__main__":

	cd.pypi_full_routine(
		repository=REPOSITORY,
		dist_directory=DIST_DIRECTORY,
		last_files=LAST_FILES,
		endswith=ENDSWITH,
	)

