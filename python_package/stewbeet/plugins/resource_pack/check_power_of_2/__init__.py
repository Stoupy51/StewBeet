""" 📐 Checks that every texture of the resource pack has a power of 2 resolution. """
# Lazy imports (PEP 810), ignored before Python 3.15
from stouputils.lazy import ALWAYS_LAZY

__lazy_modules__ = ALWAYS_LAZY

# Imports
import stouputils as stp
from beet import Context, Texture


# Main entry point
@stp.measure_time(message="Execution time of 'stewbeet.plugins.resource_pack.check_power_of_2'")
def beet_default(ctx: Context) -> None:
	""" Check if all textures in the resource pack are in power of 2 resolution.

	Args:
		ctx: The beet context.
	"""
	# Get all textures in the resource pack folder
	wrongs: list[tuple[str, int, int]] = []

	for namespaced in ctx.assets.textures.match("*item/*", "*block/*"):
		texture: Texture = ctx.assets.textures[namespaced]

		# Check if the texture is in power of 2 resolution
		width, height = texture.image.size
		not_power_of_2: bool = bin(width).count("1") != 1 or bin(height).count("1") != 1
		# A height that is a multiple of the width is probably a GUI or animation texture
		if not_power_of_2 and (height % width != 0 or height == width):
			wrongs.append((namespaced, width, height))

	# Print all wrong textures
	if wrongs:
		text: str = "The following textures are not in power of 2 resolution (2x2, 4x4, 8x8, 16x16, ...):\n"
		for file_path, width, height in wrongs:
			text += f"- {file_path}\t({width}x{height})\n"
		stp.warning(text)

