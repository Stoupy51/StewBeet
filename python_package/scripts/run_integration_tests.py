
# Imports
import os
import subprocess
import sys
from pathlib import Path

import stouputils as stp

# Constants
ROOT: str = stp.get_root_path(__file__, go_up=1)
TESTS_FOLDER: str = f"{ROOT}/tests"


# Main
@stp.measure_time(printer=stp.info, message="All integration tests finished")
def main() -> None:
	tests_dir: Path = Path(TESTS_FOLDER)
	test_folders: list[Path] = sorted(p.parent for p in tests_dir.glob("*/beet.yml"))

	if not test_folders:
		stp.error(f"No test folders found in '{stp.relative_path(str(tests_dir))}'")
		sys.exit(1)

	stp.info(f"Found {len(test_folders)} integration test(s) in '{stp.relative_path(str(tests_dir))}'")

	failures: list[str] = [test_dir.name for test_dir in test_folders if not run_test(test_dir)]
	if failures:
		stp.error(f"\n{len(failures)} integration test(s) failed:")
		for name in failures:
			stp.error(f"  - {name}")
		sys.exit(1)
	else:
		stp.info(f"\nAll {len(test_folders)} integration test(s) passed!")


def run_test(test_dir: Path) -> bool:
	""" Build one test project with stewbeet under the same interpreter, printing its output when it fails. """
	stp.info(f"Running: {test_dir.name}")
	result: subprocess.CompletedProcess[str] = subprocess.run(
		[sys.executable, "-m", "stewbeet"],
		cwd=test_dir,
		capture_output=True,
		encoding="utf-8",
		errors="replace",
		env=os.environ | {"PYTHONIOENCODING": "utf-8", "STEWBEET_TELEMETRY": "0"},
		timeout=300,
	)
	if result.returncode == 0:
		stp.info(f"PASSED: {test_dir.name}")
		return True
	stp.error(f"FAILED: {test_dir.name}")
	for output in (result.stdout.strip(), result.stderr.strip()):
		if output:
			stp.error(output)
	return False


if __name__ == "__main__":
	main()

