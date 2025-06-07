
# Get start time & Enable colors in Windows 10 console
import os
import stouputils as stp
os.system("color")

@stp.measure_time(message="Optimized textures")
def main():

	# For each texture in the textures folder, optimize it without loosing any quality
	from PIL import Image
	for root, _, files in os.walk("./"):
		for file in files:
			if not file.endswith(".png"):
				continue
			filepath = f"{root}/{file}"

			# Load image
			image = Image.open(filepath)
			image = image.convert("RGBA")
			pixels = image.load()
			width, height = image.size

			# Optimize image
			for x in range(width):
				for y in range(height):
					r, g, b, a = pixels[x, y]
					if a == 0:
						pixels[x, y] = (0, 0, 0, 0)
			
			# Save image
			image.save(filepath)
			stp.info(f"Optimized '{file}'")

if __name__ == "__main__":
	main()

