
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
		ctx (Context): The beet context.
	"""
	# Get all textures in the resource pack folder
	wrongs: list[tuple[str, int, int]] = []

	for namespaced in ctx.assets.textures.match("*item/*", "*block/*"):
		texture: Texture = ctx.assets.textures[namespaced]

		# Check if the texture is in power of 2 resolution
		width, height = texture.image.size
		if bin(width).count("1") != 1 or bin(height).count("1") != 1:  # At least one of them is not a power of 2
			# If width can't divide height, add it to the wrongs list (else it's probably a GUI or animation texture)
			if height % width != 0 or height == width:
				wrongs.append((namespaced, width, height))

	# Print all wrong textures
	if wrongs:
		text: str = "The following textures are not in power of 2 resolution (2x2, 4x4, 8x8, 16x16, ...):\n"
		for file_path, width, height in wrongs:
			text += f"- {file_path}\t({width}x{height})\n"
		stp.warning(text)

