
# Script that compress all ogg files to 64 kbps by default
# Requires ffmpeg to be installed.

import os
import subprocess
from multiprocessing import Pool
COMPRESSION = "64k"

def compress_file(args):
	src, dst = args
	previous_size = os.path.getsize(src)
	subprocess.run(["ffmpeg", "-i", src, "-c:a", "libvorbis", "-b:a", COMPRESSION, dst], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

	# Remove original & rename temp
	file_size = os.path.getsize(dst)
	if file_size < previous_size:
		os.remove(src)
		os.rename(dst, src)
		print(f"Compressed file '{src}' from {previous_size} to {file_size} bytes")
	else:
		os.remove(dst)
		print(f"New file '{src}' is bigger than the original ({previous_size} > {file_size})")

if __name__ == "__main__":
	py_path = os.path.dirname(os.path.abspath(__file__))

	files_to_compress = []
	for root, _, files in os.walk(py_path):
		for file in files:
			if file.endswith(".ogg"):
				src = f"{root}/{file}"
				dst = src.replace(".ogg", ".temp.ogg")
				files_to_compress.append((src, dst))

	# Compress
	cpu_count = os.cpu_count() // 2 + 1
	with Pool(processes = cpu_count) as pool:
		pool.map(compress_file, files_to_compress)
	print("Compression finished!")

