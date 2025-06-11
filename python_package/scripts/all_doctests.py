
# Imports
import sys

# Import stouputils
from stouputils import get_root_path, info, launch_tests, measure_time


# Main
@measure_time(info, message="All doctests finished")
def main() -> None:
	FOLDER_TO_TEST: str = get_root_path(__file__, 1)
	if launch_tests(f"{FOLDER_TO_TEST}/stewbeet") > 0:
		sys.exit(1)

if __name__ == "__main__":
	main()

