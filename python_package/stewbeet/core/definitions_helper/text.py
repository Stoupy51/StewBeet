
# Imports
from typing import Any

from stouputils.print import warning


# Functions
def create_gradient_text(text: str, start_hex: str = "c24a17", end_hex: str = "c77e36", text_length: int | None = None) -> list[dict[str, Any]]:
	""" Create a gradient text effect by interpolating colors between start and end hex.

	Args:
		text        (str): The text to apply the gradient to.
		start_hex   (str): Starting color in hex format (e.g. 'c24a17').
		end_hex     (str): Ending color in hex format (e.g. 'c77e36').
		text_length (int | None): Optional length override for the text. If provided, uses this instead of len(text).

	Returns:
		list[dict[str, Any]]: List of text components, each with a letter and its color.
	"""
	# Convert hex to RGB
	start_r: int = int(start_hex[0:2], 16)
	start_g: int = int(start_hex[2:4], 16)
	start_b: int = int(start_hex[4:6], 16)

	end_r: int = int(end_hex[0:2], 16)
	end_g: int = int(end_hex[2:4], 16)
	end_b: int = int(end_hex[4:6], 16)

	result: list[dict[str, Any]] = []
	len_text: int = text_length if text_length is not None else len(text)

	# For each letter, calculate its color
	for i, char in enumerate(text):
		# Calculate progress (0 to 1)
		progress: float = i / (len_text - 1) if len_text > 1 else 0

		# Interpolate each color component
		r: int = int(start_r + (end_r - start_r) * progress)
		g: int = int(start_g + (end_g - start_g) * progress)
		b: int = int(start_b + (end_b - start_b) * progress)

		# Convert to hex
		color: str = f"{r:02x}{g:02x}{b:02x}"

		# Add text component
		result.append({"text": char, "color": f"#{color}"})
		if i == 0:
			result[-1]["italic"] = False

	return result


def gradient_text_to_string(gradient_text: list[dict[str, Any]], color_pos: int = 0) -> dict[str, str]:
	""" Convert a gradient text back to a string, optionally getting the color at a specific position.

	Args:
		gradient_text (list[dict[str, Any]]):  The gradient text to convert back to a string.
		color_pos     (int):                   The position to get the color from.

	Returns:
		dict[str, str]: A dictionary containing the concatenated text and its color at the specified position.
	"""
	# Concatenate all text components into a single string
	text: str = "".join(item["text"] for item in gradient_text)

	# Check if the requested color position is valid
	if -len(gradient_text) <= color_pos < len(gradient_text):
		return {"text": text, "color": gradient_text[color_pos]["color"]}

	# If position is invalid, warn and use first color
	warning(f"Color position {color_pos} is out of range for gradient text of length {len(gradient_text)}. Using first color instead.")
	return {"text": text, "color": gradient_text[0]["color"]}
