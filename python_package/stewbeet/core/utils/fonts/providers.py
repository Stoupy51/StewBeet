""" Writing bitmap font providers into the resource pack.

Minecraft fonts are additive: several generators may contribute providers to the same font file, so
every write merges into whatever is already there instead of replacing it.
"""
# Imports
from collections.abc import Iterator

import stouputils as stp
from beet import Font
from beet.core.utils import TextComponent
from stouputils.typing import JsonDict

from ...__memory__ import Mem
from .allocator import GlyphAllocator

# Constants
FONT_MAX_LEVEL: int = 2
""" Indentation depth of a generated font file: one line per provider, which stays readable in a diff. """


# Functions
def iter_fonts(component: TextComponent) -> Iterator[str]:
	""" Yield every font id a text component references, its nested lists and parts included.

	Args:
		component	(TextComponent):	Text component to inspect.
	Returns:
		Iterator[str]: Each ``"namespace:font"`` found, in reading order, duplicates included.

	Examples:
		>>> list(iter_fonts([{"text": "a"}, [{"text": "b", "font": "mypack:tooltip"}]]))
		['mypack:tooltip']
		>>> list(iter_fonts({"text": "a", "extra": [{"text": "b", "font": "mypack:glyphs"}]}))
		['mypack:glyphs']
		>>> list(iter_fonts("plain string"))
		[]
	"""
	if isinstance(component, list):
		for part in component:
			yield from iter_fonts(part)
	elif isinstance(component, dict):
		# "in" rather than .get(): beet hands out Box objects built with default_box=True, where
		# reading a missing key without a default inserts it. Inspecting a component would then
		# write '"font": {}' into it, which is not something Minecraft accepts.
		if "font" in component and isinstance(component["font"], str):
			yield component["font"]
		for key in ("extra", "with"):
			if key in component:
				yield from iter_fonts(component[key])


def uses_font(component: TextComponent, font: str) -> bool:
	""" Recursively check whether a text component (or any of its parts) renders with ``font``.

	Args:
		component	(TextComponent):	Text component to inspect.
		font		(str):				Fully qualified font id, e.g. ``"mypack:tooltip"``.
	Returns:
		bool: True when at least one part of the component uses that font.

	Examples:
		>>> uses_font([{"text": "a"}, {"text": "b", "font": "mypack:tooltip"}], "mypack:tooltip")
		True
		>>> uses_font({"text": "a", "extra": [{"text": "b", "font": "mypack:tooltip"}]}, "mypack:tooltip")
		True
		>>> uses_font("plain string", "mypack:tooltip")
		False
	"""
	return any(referenced == font for referenced in iter_fonts(component))


def merge_font_providers(namespace: str, font_name: str, providers: list[JsonDict]) -> Font:
	""" Append ``providers`` to the ``<namespace>:<font_name>`` font, creating it when missing.

	Args:
		namespace	(str):				Resource pack namespace holding the font.
		font_name	(str):				Font file name, without the namespace, e.g. ``"tooltip"``.
		providers	(list[JsonDict]):	Providers to append to the existing ones.
	Returns:
		Font: The font object stored in the resource pack.
	"""
	font: Font = Mem.ctx.assets[namespace].fonts.setdefault(font_name, Font({"providers": []}))
	font.encoder = lambda x: stp.json_dump(x, max_level=FONT_MAX_LEVEL)
	font.data["providers"].extend(providers)
	return font


def write_font_from_allocator(namespace: str, font_name: str, allocator: GlyphAllocator) -> Font:
	""" Merge every provider an allocator collected into the ``<namespace>:<font_name>`` font.

	Args:
		namespace	(str):				Resource pack namespace holding the font.
		font_name	(str):				Font file name, without the namespace, e.g. ``"manual"``.
		allocator	(GlyphAllocator):	Allocator whose providers should be written.
	Returns:
		Font: The font object stored in the resource pack.
	"""
	return merge_font_providers(namespace, font_name, allocator.providers)


def validate_font_providers(namespace: str, providers: list[JsonDict]) -> None:
	""" Error out if any provider references a missing texture or maps no character.

	Args:
		namespace	(str):				Resource pack namespace the textures live in.
		providers	(list[JsonDict]):	Providers to check.
	"""
	for provider in providers:
		if "file" not in provider:
			continue
		path: str = provider["file"].split(":", 1)[-1].removesuffix(".png")
		if not Mem.ctx.assets[namespace].textures.get(path):
			stp.error(f"Missing font provider at '{path}' for {provider}")
		chars: list[str] = provider["chars"]
		if len(chars) < 1 or (len(chars) == 1 and not chars[0]):
			stp.error(f"Font provider '{path}' has no chars")

