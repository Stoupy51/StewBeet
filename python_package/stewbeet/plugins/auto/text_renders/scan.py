""" Finding ``render`` nodes inside already-generated files.

Everything here works on fragments of text rather than parsed JSON: by the time this plugin runs,
text components live inside mcfunction commands and SNBT payloads where keys may be unquoted and
strings single-quoted, so ``json.loads`` is not an option. Only the ``render``, ``height``, ``ascent``
and ``resolution`` fragments of a node are touched; every other key is left exactly as written.
"""
# Imports
import re
from dataclasses import dataclass

import stouputils as stp

from ....core.utils.text_component import find_enclosing_object
from .config import default_ascent

# Pre-compiled regex patterns
RENDER_RE: re.Pattern[str] = re.compile(
	r'''
	(?P<key_quote>["'])?render(?(key_quote)(?P=key_quote))  # Match "render", 'render', or render
	\s*:\s*                                                 # Match the colon and spaces
	(?P<quote>["'])                                         # Opening quote for value
	(?P<value>(?:\\.|[^\\])*?)                              # The value, handling escapes
	(?P=quote)                                              # Closing quote
	''', re.VERBOSE
)
""" Matches the ``"render": "<item id>"`` fragment of a text component. """

HEIGHT_RE: re.Pattern[str] = re.compile(r'''(?:["']?height["']?)\s*:\s*(\d+)''')
""" Matches a sibling ``"height": <int>`` fragment. """

ASCENT_RE: re.Pattern[str] = re.compile(r'''(?:["']?ascent["']?)\s*:\s*(-?\d+)''')
""" Matches a sibling ``"ascent": <int>`` fragment. """

RESOLUTION_RE: re.Pattern[str] = re.compile(r'''(?:["']?resolution["']?)\s*:\s*(\d+)''')
""" Matches a sibling ``"resolution": <int>`` fragment. """

TEXT_KEY_RE: re.Pattern[str] = re.compile(r'''(?:["']?text["']?)\s*:''')
""" Matches a sibling ``"text":`` key, which a render node must not carry. """


# Classes
@dataclass(frozen=True, slots=True)
class RenderRequest:
	""" One ``render`` node found in a file, and everything needed to rewrite it.

	>>> request = RenderRequest(item_id="mypack:steel_ingot", height=16, ascent=7, resolution=64, start=0, end=10, drops=())
	>>> request.glyph_key
	('mypack:steel_ingot', 16, 7, 64)
	"""
	item_id: str
	""" Fully qualified item id, or the reserved ``ICON``. """
	height: int
	""" On-screen glyph height in pixels. """
	ascent: int
	""" Baseline offset of the glyph. """
	resolution: int
	""" Texture height in pixels, or 0 to follow the displayed height. """
	start: int
	""" Index of the ``render`` fragment in the file text. """
	end: int
	""" Index just past the ``render`` fragment. """
	drops: tuple[tuple[int, int], ...]
	""" Spans of the consumed sibling keys, each including one separating comma. """

	@property
	def glyph_key(self) -> tuple[str, int, int, int]:
		""" Identity of the glyph this request needs; equal keys share one provider. """
		return (self.item_id, self.height, self.ascent, self.resolution)


# Functions
def top_level_search(node: str, pattern: re.Pattern[str]) -> re.Match[str] | None:
	""" Search ``pattern`` in a serialized object, ignoring matches nested in a sub-object.

	``node`` starts at its own opening brace, so a match belongs to the node itself only when the
	brace depth at that point is exactly 1. Braces inside quoted strings are skipped.

	Examples:
		>>> import re
		>>> height = re.compile(r'"height"\\s*:\\s*(\\d+)')
		>>> top_level_search('{"render":"a","height":8}', height).group(1)
		'8'
		>>> top_level_search('{"render":"a","hover":{"height":8}}', height) is None
		True
		>>> top_level_search('{"render":"a{","height":4}', height).group(1)
		'4'
	"""
	depth: int = 0
	quote: str | None = None
	index: int = 0
	while index < len(node):
		char: str = node[index]

		# Inside a string: nothing counts until it closes
		if quote is not None:
			if char == "\\":
				index += 2
				continue
			if char == quote:
				quote = None
			index += 1
			continue

		# The match is attempted before the quote handling, since a key starts with one
		if depth == 1 and (match := pattern.match(node, index)) is not None:
			return match
		if char in "\"'":
			quote = char
		elif char == "{":
			depth += 1
		elif char == "}":
			depth -= 1
		index += 1
	return None


def widen_to_comma(string: str, start: int, end: int) -> tuple[int, int]:
	""" Grow a key:value span to swallow one neighbouring comma, so removing it keeps valid syntax.

	The comma after the fragment is preferred; the one before is used when the fragment is last.

	Examples:
		>>> widen_to_comma('{"a":1,"b":2}', 7, 12)  # trailing fragment: eats the comma before it
		(6, 12)
		>>> widen_to_comma('{"a":1,"b":2}', 1, 6)   # leading fragment: eats the comma after it
		(1, 7)
	"""
	after: int = end
	while after < len(string) and string[after].isspace():
		after += 1
	if after < len(string) and string[after] == ",":
		return (start, after + 1)

	before: int = start
	while before > 0 and string[before - 1].isspace():
		before -= 1
	if before > 0 and string[before - 1] == ",":
		return (before - 1, end)
	return (start, end)


def merge_spans(string: str, spans: list[tuple[int, int]]) -> tuple[tuple[int, int], ...]:
	""" Group the consumed siblings into spans that can be removed without breaking the syntax.

	Neighbouring siblings are joined first (they are separated by a single comma, which goes away
	with them), and only the resulting group claims one outer comma. Widening each sibling before
	joining would instead strand the comma sitting in front of the group.

	Examples:
		>>> merge_spans('{"a":1,"b":2,"c":3}', [(7, 12), (13, 18)])  # two neighbours: one group
		((6, 18),)
		>>> merge_spans('{"a":1,"b":2,"c":3}', [(7, 12)])            # a single sibling in the middle
		((7, 13),)
		>>> merge_spans('{"a":1}', [])
		()
	"""
	# Join siblings separated by nothing but whitespace and their own comma
	joined: list[tuple[int, int]] = []
	for start, end in sorted(spans):
		if joined and string[joined[-1][1]:start].strip() in ("", ","):
			joined[-1] = (joined[-1][0], max(joined[-1][1], end))
		else:
			joined.append((start, end))
	return tuple(widen_to_comma(string, start, end) for start, end in joined)


def qualify(item_id: str, project_id: str, icon_id: str) -> str:
	""" Namespace a bare render id with the project namespace, leaving the reserved icon alone.

	>>> qualify("steel_ingot", "mypack", "ICON")
	'mypack:steel_ingot'
	>>> qualify("minecraft:stone", "mypack", "ICON")
	'minecraft:stone'
	>>> qualify("mechanization:tin_ore", "mypack", "ICON")
	'mechanization:tin_ore'
	>>> qualify("ICON", "mypack", "ICON")
	'ICON'
	"""
	if item_id == icon_id or ":" in item_id:
		return item_id
	return f"{project_id}:{item_id}"


def find_requests(string: str, project_id: str, default_height: int, icon_id: str, default_resolution: int = 0) -> list[RenderRequest]:
	""" Collect every ``render`` node of a file's text.

	Args:
		string				(str):	Full file text.
		project_id			(str):	Namespace bare ids belong to.
		default_height		(int):	Displayed height used when a node omits its own.
		icon_id				(str):	Reserved id standing for the project logo.
		default_resolution	(int):	Texture height used when a node omits its own.
	Returns:
		list[RenderRequest]: One request per node, in file order.

	Examples:
		>>> requests = find_requests('tellraw @a {"render":"steel_ingot","height":8}', "mypack", 16, "ICON")
		>>> requests[0].item_id, requests[0].height, requests[0].ascent
		('mypack:steel_ingot', 8, 7)
		>>> find_requests('tellraw @a {"render":"minecraft:stone"}', "mypack", 16, "ICON")[0].glyph_key
		('minecraft:stone', 16, 11, 0)
		>>> find_requests('tellraw @a {"render":"a","height":10,"resolution":64}', "mypack", 16, "ICON")[0].glyph_key
		('mypack:a', 10, 8, 64)
	"""
	requests: list[RenderRequest] = []
	for match in RENDER_RE.finditer(string):
		start, end = match.span()
		item_id: str = qualify(match.group("value"), project_id, icon_id)

		# The node's own braces bound the search for the height/ascent/resolution siblings
		bounds: tuple[int, int] | None = find_enclosing_object(string, start, end)
		height: int = default_height
		ascent: int | None = None
		resolution: int = default_resolution
		spans: list[tuple[int, int]] = []
		if bounds is not None:
			node: str = string[bounds[0]:bounds[1]]
			if top_level_search(node, TEXT_KEY_RE) is not None:
				stp.warning(f"A render node also carries a 'text' key, which the glyph replaces: {node}")
			if (height_match := top_level_search(node, HEIGHT_RE)) is not None:
				height = int(height_match.group(1))
				spans.append((bounds[0] + height_match.start(), bounds[0] + height_match.end()))
			if (ascent_match := top_level_search(node, ASCENT_RE)) is not None:
				ascent = int(ascent_match.group(1))
				spans.append((bounds[0] + ascent_match.start(), bounds[0] + ascent_match.end()))
			if (resolution_match := top_level_search(node, RESOLUTION_RE)) is not None:
				resolution = int(resolution_match.group(1))
				spans.append((bounds[0] + resolution_match.start(), bounds[0] + resolution_match.end()))

		requests.append(RenderRequest(
			item_id=item_id,
			height=height,
			ascent=ascent if ascent is not None else default_ascent(height),
			resolution=resolution,
			start=start,
			end=end,
			drops=merge_spans(string, spans),
		))
	return requests

