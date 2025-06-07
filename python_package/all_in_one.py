
import os
import sys

commands = [
	f"{sys.executable} upgrade.py",				# Upgrade the version in pyproject.toml
	f"{sys.executable} build_all_in_one.py",	# Build the package and upload it
]

for command in commands:
	if os.system(command) != 0:
		print(f"Error while executing '{command}'")
		exit(1)

