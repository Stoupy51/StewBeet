
# Imports
import stouputils as stp

# Main
if __name__ == "__main__":

	# Increment version
	ROOT: str = stp.get_root_path(__file__, go_up=1)
	stp.increment_version_from_pyproject(f"{ROOT}/pyproject.toml")

