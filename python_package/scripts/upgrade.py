
# Imports
import stouputils.continuous_delivery as cd
from stouputils.io import get_root_path

# Main
if __name__ == "__main__":

	# Increment version
	ROOT: str = get_root_path(__file__, go_up=1)
	cd.increment_version_from_pyproject(f"{ROOT}/pyproject.toml")

