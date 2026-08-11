""" One-time confirmation before a build starts baking renders too big for a single glyph.

Splicing a picture into a grid of glyphs is cheap to write and expensive to ship: a 1000x370 logo
becomes eight textures the resource pack has to carry. The question is asked in the terminal the
first time a project runs into it, and the answer is remembered in ``.beet_cache`` so later builds
stay quiet. ``meta.stewbeet.text_renders.allow_oversized`` answers it up front and skips the prompt.
"""
# Imports
import sys

import stouputils as stp

from ....core.__memory__ import Mem
from ....core.utils.fonts import MAX_GLYPH_SIZE

# Constants
CACHE_NAME: str = "stewbeet_text_renders"
""" beet cache holding the remembered answer, next to the rest of the project cache. """

CACHE_KEY: str = "allow_oversized"
""" Key the answer is stored under inside that cache. """


# Functions
def prompt() -> bool | None:
	""" The answer typed in the terminal, or None when there is nobody to answer.

	A build driven by a script, a CI job or an editor has no terminal to read from, and blocking one
	forever on a question is worse than the pack size it was meant to save.

	Returns:
		bool | None: True to cut the render into glyphs, False to shrink it, None when unanswered.
	"""
	if sys.stdin is None or not sys.stdin.isatty():
		return None
	try:
		return not input("Cut it into glyphs? [Y/n] ").strip().lower().startswith("n")
	except EOFError:
		return None


def ask_oversized(item_id: str, stored: tuple[int, int], tiles: int) -> bool:
	""" Ask once whether renders bigger than a font atlas may be baked, and remember the answer.

	Answering no shrinks the render down to a single glyph instead, which keeps the pack small at the
	cost of sharpness. Outside a terminal (a CI build, a watch loop) there is nobody to answer, so
	the render is baked and the reason is printed rather than silently changing what gets built.

	Args:
		item_id	(str):				Render that ran into the limit.
		stored	(tuple[int, int]):	Pixel size its texture would be stored at.
		tiles	(int):				Number of glyph textures it would be cut into.
	Returns:
		bool: True to splice the render, False to shrink it to a single glyph.
	"""
	cache = Mem.ctx.cache[CACHE_NAME]
	remembered = cache.json.get(CACHE_KEY)
	if isinstance(remembered, bool):
		if not remembered:
			stp.warning(f"'{item_id}' is shrunk down to {MAX_GLYPH_SIZE}px, as answered earlier (see 'allow_oversized')")
		return remembered

	stp.warning(
		f"'{item_id}' renders at {stored[0]}x{stored[1]} pixels, more than the {MAX_GLYPH_SIZE}x{MAX_GLYPH_SIZE} "
		f"Minecraft fits in one glyph. It can be cut into {tiles} glyphs stitched back together with negative "
		f"spacing, which costs {tiles} textures in the resource pack. Answering no shrinks it to a single glyph."
	)

	typed: bool | None = prompt()
	if typed is None:
		stp.warning("Nobody to answer, so it is cut. Set 'meta.stewbeet.text_renders.allow_oversized' to decide up front.")
		return True

	# Only an answer somebody actually gave is remembered: a build with no terminal must not decide
	# for the author, it just keeps printing the warning until one of them does.
	cache.json[CACHE_KEY] = typed
	return typed

