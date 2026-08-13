""" auto.text_renders: replace every ``render`` key of a text component with a font glyph.

``{"render": "steel_ingot"}`` anywhere a text component can appear (item lore, source lore, a
``tellraw``, a manual dialog) becomes a bitmap glyph showing that item, so packs can put pictures in
chat and tooltips without hand-managing a font.

The pass runs on the generated files rather than on the definitions: by that point every item
component has already been serialised into loot tables, ``give`` commands and dialogs, so one scan
covers all of them at once.
"""
# Lazy imports (PEP 810), ignored before Python 3.15
from stouputils.lazy import ALWAYS_LAZY

__lazy_modules__ = ALWAYS_LAZY

# Imports
import stouputils as stp
from beet import Context, TextFileBase
from beet.core.utils import TextComponent

from ....core.__memory__ import Mem
from ....core.utils.text_component import Replacement, apply_replacements, iter_data_text_files
from .config import ICON_ID, TextRendersConfig, default_ascent
from .emit import GlyphEmitter, GlyphKey
from .scan import RenderRequest, find_requests, qualify

# Constants
RENDER_KEY: str = "render"
""" Text component key this plugin consumes. """

CONSUMED_KEYS: tuple[str, ...] = (RENDER_KEY, "height", "ascent", "resolution")
""" Keys a render node owns; every other key is carried over onto the glyph component. """


# Functions
def get_emitter(config: TextRendersConfig | None = None) -> GlyphEmitter:
	""" The emitter owning this build's glyphs, created on first use.

	Held on :class:`Mem` (and reset by ``plugins.initialize``) so the build pass and
	:func:`resolve_renders` draw glyph characters from the same allocator.

	Args:
		config (TextRendersConfig | None): Configuration, read from the context when omitted.
	Returns:
		GlyphEmitter: The emitter for the current build.
	"""
	if Mem.text_renders is None:
		Mem.text_renders = GlyphEmitter(config=config or TextRendersConfig.from_meta(Mem.ctx))
	return Mem.text_renders


def build_replacements(requests: list[RenderRequest], glyphs: dict[GlyphKey, str], font: str) -> list[Replacement]:
	""" Turn resolved requests into the slices rewriting a file's text.

	Args:
		requests	(list[RenderRequest]):	Requests found in one file.
		glyphs		(dict):					Glyph key -> glyph character.
		font		(str):					Fully qualified font id to attach to each glyph.
	Returns:
		list[Replacement]: Slices to overwrite; requests whose image could not be resolved are left untouched.
	"""
	replacements: list[Replacement] = []
	for request in requests:
		glyph: str | None = glyphs.get(request.glyph_key)
		if glyph is None:
			continue
		fragment: str = stp.json_dump({"text": glyph, "font": font}, max_level=0).strip().removeprefix("{").removesuffix("}")
		replacements.append(Replacement(request.start, request.end, fragment))
		replacements.extend(Replacement(start, end, "") for start, end in request.drops)
	return replacements


def resolve_renders(component: TextComponent, config: TextRendersConfig | None = None) -> TextComponent:
	""" Replace every ``render`` node of an in-memory text component with its glyph.

	The build-wide pass already covers everything written to a file, so this is only needed when the
	glyph string itself is wanted right away, for instance to measure a line.

	Args:
		component	(TextComponent):			Component to convert (never mutated).
		config		(TextRendersConfig | None):	Configuration, read from the context when omitted.
	Returns:
		TextComponent: A copy where every render node became a glyph component.
	"""
	emitter: GlyphEmitter = get_emitter(config)
	if isinstance(component, list):
		return [resolve_renders(part, emitter.config) for part in component]
	if not isinstance(component, dict):
		return component
	if RENDER_KEY not in component:
		return {key: resolve_renders(value, emitter.config) if key in ("extra", "with") else value for key, value in component.items()}

	height: int = component.get("height", emitter.config.default_height)
	ascent: int = component.get("ascent", default_ascent(height))
	resolution: int = component.get("resolution", emitter.config.default_resolution)
	item_id: str = qualify(str(component[RENDER_KEY]), emitter.config.project_id, ICON_ID)

	request = RenderRequest(item_id=item_id, height=height, ascent=ascent, resolution=resolution, start=0, end=0, drops=())
	glyphs = emitter.emit([request])
	rest = {key: value for key, value in component.items() if key not in (*CONSUMED_KEYS, "text")}
	glyph: str | None = glyphs.get(request.glyph_key)
	if glyph is None:
		return rest
	return {"text": glyph, "font": emitter.config.font, **rest}


# Main entry point
@stp.measure_time(message="Execution time of 'stewbeet.plugins.auto.text_renders'")
def beet_default(ctx: Context) -> None:
	""" Main entry point for the text renders plugin.

	Scans every generated datapack file for ``render`` keys, generates one glyph per distinct
	``(item id, height, ascent, resolution)`` combination, then rewrites the files to use them.

	Args:
		ctx (Context): The beet context.
	"""
	Mem.ctx = ctx
	config = TextRendersConfig.from_meta(ctx)

	# First pass: collect every request of the build so images are rendered/downloaded in one batch
	pending: list[tuple[TextFileBase[str], str, list[RenderRequest]]] = []
	for content in iter_data_text_files(ctx):
		string: str = str(content.text)
		if RENDER_KEY not in string:
			continue
		requests: list[RenderRequest] = find_requests(string, config.project_id, config.default_height, ICON_ID, config.default_resolution)
		if requests:
			pending.append((content, string, requests))
	if not pending:
		return

	# Second pass: generate the glyphs, then rewrite the files that asked for them
	emitter: GlyphEmitter = get_emitter(config)
	glyphs = emitter.emit([request for _, _, requests in pending for request in requests])
	rewritten: int = 0
	for content, string, requests in pending:
		new_string: str = apply_replacements(string, build_replacements(requests, glyphs, config.font))
		if new_string != string:
			content.text = new_string
			rewritten += 1

	total: int = sum(len(requests) for _, _, requests in pending)
	stp.debug(f"Resolved {total} render(s) into {len(glyphs)} glyph(s) across {rewritten} file(s)")
