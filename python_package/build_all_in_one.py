
import os
import sys

commands = [
	f"{sys.executable} 1_upgrades.py",
	f"{sys.executable} 2_build.py",
	f"{sys.executable} 3_upload.py",
]

for command in commands:
	if os.system(command) != 0:
		print(f"Error while executing '{command}'")
		exit(1)

