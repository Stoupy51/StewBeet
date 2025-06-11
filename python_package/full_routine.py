
# Imports
import os
import sys

import stouputils as stp

# Constants
ROOT: str = stp.get_root_path(__file__)

# Main
if __name__ == "__main__":

	# Increment version in pyproject.toml
	stp.increment_version_from_pyproject(f"{ROOT}/pyproject.toml")

	# PyPI full routine
	os.system(f"{sys.executable} {ROOT}/scripts/pypi_full_routine.py")

