""" The :class:`Manual` orchestrator.

Owns the ordered list of pages, the glyph allocator, the image builder and the recipe
renderer, plus the developer hook registry. ``build()`` runs the pipeline:

	discover -> prepare -> order -> render -> resolve -> optimize -> emit

firing the matching :class:`Phase` hooks after each step. Cross-page links are emitted as
:class:`~.refs.PageRef` during ``render`` and substituted once in ``resolve`` (after the
order is final), so inserting/reordering pages never needs page-number bookkeeping.
"""

# Imports
import enum
import os
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any, cast

import stouputils as stp
from beet.core.utils import TextComponent
from PIL import Image

from ...core.__memory__ import Mem
from ...core.cls.item import Item
from .config import ManualConfig
from .glyphs import HEAVY_WORKBENCH_CATEGORY, GlyphAllocator
from .images import GlyphImageBuilder
from .optimizer import optimize_element

# Page imports
from .pages.base import Page
from .pages.browser_page import CategoryBrowserPage
from .pages.category_page import CategoryPage
from .pages.intro_page import IntroPage
from .pages.item_page import ItemPage
from .recipes import RecipeRenderer
from .refs import PageRef


class Phase(enum.Enum):
	""" Points in the build pipeline at which developer hooks run. """
	DISCOVERED = "discovered"
	PREPARED = "prepared"
	ORDERED = "ordered"
	RENDERED = "rendered"
	RESOLVED = "resolved"
	BEFORE_EMIT = "before_emit"


@dataclass(eq=False)
class Manual:
	""" Orchestrates manual generation and exposes the public extension API.

	Construct with ``Manual(config)``; every other field is derived. ``eq=False`` keeps
	identity semantics: the manual and its collaborators (:class:`~.recipes.RecipeRenderer`)
	reference each other, so field-based equality would recurse.

	>>> manual = Manual(ManualConfig(project_id="demo", project_name="Demo", project_author="me", cache_path="cache"))
	>>> manual.recipes.manual is manual
	True
	>>> _ = manual.add_page(Page(anchor="later"))
	>>> len(manual.pages), len(manual.pending_ops)  # deferred until discover() builds the defaults
	(0, 1)
	"""

	config: ManualConfig
	""" The typed manual configuration (the only constructor argument). """

	# Collaborators (created from ``config`` in __post_init__)
	glyphs: GlyphAllocator = field(init=False, repr=False)
	""" Dynamic glyph counter + bitmap font-provider registry. """
	images: GlyphImageBuilder = field(init=False, repr=False)
	""" Builder for every manual texture (icons, templates, page backgrounds). """
	recipes: RecipeRenderer = field(init=False, repr=False)
	""" Dispatcher rendering each recipe through its registered :class:`~.recipes.CraftRenderer`. """

	# Page registry + developer hooks
	pages: list[Page] = field(init=False, default_factory=list[Page])
	""" The ordered pages; 1-based page numbers follow this order. """
	by_anchor: dict[str, Page] = field(init=False, default_factory=dict[str, Page])
	""" Anchor -> page lookup (rebuilt by :meth:`order`). """
	hooks: dict[Phase, list[Callable[[Manual], None]]] = field(init=False, repr=False)
	""" Per-:class:`Phase` developer hooks (see :meth:`on` / :meth:`register`). """
	item_page_hooks: list[Callable[[ItemPage, Manual], None]] = field(init=False, default_factory=list[Callable[[ItemPage, "Manual"], None]], repr=False)
	""" Hooks run on every :class:`~.pages.item_page.ItemPage` during preparation. """

	# Page operations requested before discover() runs are deferred and replayed once the
	# default pages exist (so setup code can reference default anchors like "intro").
	discovered: bool = field(init=False, default=False)
	""" True once :meth:`discover` built the default pages. """
	pending_ops: list[Callable[[], None]] = field(init=False, default_factory=list[Callable[[], None]], repr=False)
	""" Page operations deferred until after :meth:`discover`. """

	# Computed during the pipeline
	definitions_as_objects: dict[str, Item] = field(init=False, default_factory=dict[str, Item], repr=False)
	""" Item id -> :class:`Item` cache built at discover time. """
	categories: dict[str, list[str]] = field(init=False, default_factory=dict[str, list[str]])
	""" Category name -> item ids (insertion order preserved). """
	has_forge_3x3: bool = field(init=False, default=False)
	""" Whether any recipe needs the 3x3 awakened forge assets. """
	has_forge_3x4: bool = field(init=False, default=False)
	""" Whether any recipe needs the 3x4 awakened forge assets. """
	pages_content: list[list[TextComponent]] = field(init=False, default_factory=list[list[TextComponent]], repr=False)
	""" Rendered dialog bodies, one list of components per page. """
	item_index: dict[str, int] = field(init=False, default_factory=dict[str, int], repr=False)
	""" Item id -> 1-based page index (computed by :meth:`order`). """
	anchor_index: dict[str, int] = field(init=False, default_factory=dict[str, int], repr=False)
	""" Anchor -> 1-based page index (computed by :meth:`order`). """
	cached_simple_case: Image.Image | None = field(init=False, default=None, repr=False)
	""" Cache for :attr:`simple_case`. """
	texture_cache: dict[str, Image.Image] = field(init=False, default_factory=dict[str, Image.Image], repr=False)
	""" Item id -> loaded texture cache (see :meth:`load_item_texture`). """

	def __post_init__(self) -> None:
		self.glyphs = GlyphAllocator(self.config.project_id)
		self.images = GlyphImageBuilder(self.config, self.glyphs)
		self.recipes = RecipeRenderer(self)
		self.hooks = {p: [] for p in Phase}

	# --- shared lazy resources ---
	@property
	def simple_case(self) -> Image.Image:
		""" The case background image (cached), widened in high-res mode. """
		if self.cached_simple_case is None:
			self.cached_simple_case = self.images.load_simple_case_no_border(self.config.high_resolution)
		return self.cached_simple_case

	def object_for(self, item_id: str | None) -> Item | None:
		""" Return the cached :class:`Item` for an internal id, or None. """
		if not item_id:
			return None
		obj = self.definitions_as_objects.get(item_id)
		if obj is None and item_id in Mem.definitions:
			obj = Item.from_id(item_id)
			self.definitions_as_objects[item_id] = obj
		return obj

	def load_item_texture(self, item: str) -> Image.Image:
		""" Open an item's cached iso-render texture (placeholder if missing). """
		if item in self.texture_cache:
			return self.texture_cache[item]
		path = f"{self.config.cache_path}/items/{self.config.project_id}/{item}.png"
		if os.path.exists(path):
			img = Image.open(path)
		else:
			stp.warning(f"Missing texture at '{path}', using empty texture")
			img = Image.new("RGBA", (1, 1), (0, 0, 0, 0))
		self.texture_cache[item] = img
		return img

	# --- page management API (public) ---
	# Each method applies immediately once the default pages exist (during build), or is
	# deferred and replayed right after discover() when called from setup code.
	def add_page(self, page: Page) -> Page:
		""" Append a page to the end of the manual. """
		if not self.discovered:
			self.pending_ops.append(lambda: self.apply_add(page))
		else:
			self.apply_add(page)
		return page

	def insert_page(self, page: Page, *, before: str | None = None, after: str | None = None, index: int | None = None) -> Page:
		""" Insert a page before/after an anchor, or at an explicit index. """
		if not self.discovered:
			self.pending_ops.append(lambda: self.apply_insert(page, before, after, index))
		else:
			self.apply_insert(page, before, after, index)
		return page

	def replace_page(self, anchor: str, page: Page) -> Page:
		""" Replace the page at ``anchor`` with ``page``. """
		if not self.discovered:
			self.pending_ops.append(lambda: self.apply_replace(anchor, page))
		else:
			self.apply_replace(anchor, page)
		return page

	def remove_page(self, anchor: str) -> None:
		""" Remove the page identified by ``anchor``. """
		if not self.discovered:
			self.pending_ops.append(lambda: self.apply_remove(anchor))
		else:
			self.apply_remove(anchor)

	def move_page(self, anchor: str, *, before: str | None = None, after: str | None = None, index: int | None = None) -> None:
		""" Move an existing page to a new position. """
		if not self.discovered:
			self.pending_ops.append(lambda: self.apply_move(anchor, before, after, index))
		else:
			self.apply_move(anchor, before, after, index)

	def apply_add(self, page: Page) -> None:
		""" Immediate (non-deferred) implementation of :meth:`add_page`. """
		self.pages.append(page)
		self.by_anchor[page.anchor] = page

	def apply_insert(self, page: Page, before: str | None, after: str | None, index: int | None) -> None:
		""" Immediate (non-deferred) implementation of :meth:`insert_page`. """
		if index is None:
			if before is not None:
				index = self.index_of_anchor(before)
			elif after is not None:
				index = self.index_of_anchor(after) + 1
			else:
				index = len(self.pages)
		self.pages.insert(index, page)
		self.by_anchor[page.anchor] = page

	def apply_replace(self, anchor: str, page: Page) -> None:
		""" Immediate (non-deferred) implementation of :meth:`replace_page`. """
		idx = self.index_of_anchor(anchor)
		old = self.pages[idx]
		self.pages[idx] = page
		del self.by_anchor[old.anchor]
		self.by_anchor[page.anchor] = page

	def apply_remove(self, anchor: str) -> None:
		""" Immediate (non-deferred) implementation of :meth:`remove_page`. """
		idx = self.index_of_anchor(anchor)
		page = self.pages.pop(idx)
		self.by_anchor.pop(page.anchor, None)

	def apply_move(self, anchor: str, before: str | None, after: str | None, index: int | None) -> None:
		""" Immediate (non-deferred) implementation of :meth:`move_page`. """
		idx = self.index_of_anchor(anchor)
		page = self.pages.pop(idx)
		self.by_anchor.pop(page.anchor, None)
		self.apply_insert(page, before, after, index)

	def get_page(self, anchor: str) -> Page:
		""" Return the page registered under ``anchor``. """
		return self.by_anchor[anchor]

	def get_page_for_item(self, item_id: str) -> ItemPage | None:
		""" Return the :class:`ItemPage` for an item id, if present. """
		for page in self.pages:
			if isinstance(page, ItemPage) and page.item_id == item_id:
				return page
		return None

	def index_of_anchor(self, anchor: str) -> int:
		""" Return the 0-based list index of the page with ``anchor`` (KeyError if absent). """
		for i, page in enumerate(self.pages):
			if page.anchor == anchor:
				return i
		raise KeyError(f"No manual page with anchor '{anchor}'")

	# --- hook API (public) ---
	def register(self, phase: Phase, fn: Callable[[Manual], None]) -> Callable[[Manual], None]:
		""" Register ``fn`` to run after ``phase``. Returns ``fn`` (usable as a decorator). """
		self.hooks[phase].append(fn)
		return fn

	def on(self, phase: Phase) -> Callable[[Callable[[Manual], None]], Callable[[Manual], None]]:
		""" Decorator form of :meth:`register`. """
		def deco(fn: Callable[[Manual], None]) -> Callable[[Manual], None]:
			return self.register(phase, fn)
		return deco

	def on_item_page(self, fn: Callable[[ItemPage, Manual], None]) -> Callable[[ItemPage, Manual], None]:
		""" Register ``fn(page, manual)`` to run on every item page during preparation. """
		self.item_page_hooks.append(fn)
		return fn

	def run_hooks(self, phase: Phase) -> None:
		""" Fire all hooks registered for ``phase``. """
		for fn in self.hooks[phase]:
			fn(self)

	# --- link resolution (public) ---
	def page_index_of(self, ref: PageRef) -> int:
		""" Resolve a :class:`PageRef` to a 1-based page index (-1 if unknown). """
		if ref.page is not None:
			return ref.page
		if ref.item is not None:
			return self.item_index.get(ref.item, -1)
		if ref.anchor is not None:
			return self.anchor_index.get(ref.anchor, -1)
		return -1

	# --- pipeline ---
	def build(self) -> None:
		""" Run the full generation pipeline, firing hooks between steps. """
		self.discover()
		self.run_hooks(Phase.DISCOVERED)
		self.prepare()
		self.run_hooks(Phase.PREPARED)
		self.order()
		self.run_hooks(Phase.ORDERED)
		self.render()
		self.run_hooks(Phase.RENDERED)
		self.normalize()
		self.resolve()
		self.run_hooks(Phase.RESOLVED)
		self.optimize()
		self.run_hooks(Phase.BEFORE_EMIT)
		self.emit()

	def discover(self) -> None:
		""" Create the default page set (intro, browser, categories, items, special). """
		from .pages.raw_page import RawPage  # local to avoid cycle at import time
		from .special import build_stardust_forge_page

		# From here on, page operations apply immediately (defaults now being built).
		self.discovered = True
		self.definitions_as_objects = {item: Item.from_id(item) for item in Mem.definitions.keys()}

		# Detect awakened-forge sizes
		for obj in self.definitions_as_objects.values():
			for recipe in obj.recipes:
				if recipe.get("type") == "stardust_awakened_forge":
					if len(recipe["ingredients"]) <= 9:
						self.has_forge_3x3 = True
					else:
						self.has_forge_3x4 = True

		# Build categories (insertion order preserved)
		self.categories = {}
		for item, obj in self.definitions_as_objects.items():
			if not obj.manual_category:
				stp.suggestion(f"Item '{item}' has no category key. Skipping.")
				continue
			self.categories.setdefault(obj.manual_category, []).append(item)
		if len(self.categories) > self.config.max_items_per_page:
			stp.error(f"Too many categories ({len(self.categories)}). Maximum is {self.config.max_items_per_page}.")

		# Split categories into pages
		category_pages: list[CategoryPage] = []
		for cat, items in self.categories.items():
			if cat == HEAVY_WORKBENCH_CATEGORY:
				continue
			i = 0
			while i < len(items):
				page_name = cat.title()
				if len(items) > self.config.max_items_per_page:
					page_name += f" #{i // self.config.max_items_per_page + 1}"
				chunk = items[i:i + self.config.max_items_per_page]
				category_pages.append(CategoryPage(anchor=f"category:{page_name}", title=page_name, items=chunk))
				i += self.config.max_items_per_page

		# Item pages, sorted by category order
		category_list = list(self.categories.keys())
		items_with_category = [(item, obj) for item, obj in self.definitions_as_objects.items() if obj.manual_category]
		items_with_category.sort(key=lambda x: category_list.index(x[1].manual_category or ""))
		item_pages: list[ItemPage] = [ItemPage.for_item(item) for item, _ in items_with_category]

		# Assemble base order: intro, browser, categories, items
		self.pages = []
		self.by_anchor = {}
		self.add_page(IntroPage(anchor="intro", title=self.config.name))
		self.add_page(CategoryBrowserPage(anchor="category_browser", title="Category browser"))
		for cp in category_pages:
			self.add_page(cp)
		for ip in item_pages:
			self.add_page(ip)

		# Special pages inserted right after the intro, via the public API
		if self.has_forge_3x3 or self.has_forge_3x4:
			self.insert_page(RawPage(anchor="stardust_forge", title="Awakened Forge", content=build_stardust_forge_page(), optimize=False), index=1)
		if "heavy_workbench" in Mem.definitions:
			self.move_page("item:heavy_workbench", index=1)

		# Replay any page operations a developer requested during setup (now that defaults exist).
		for op in self.pending_ops:
			op()
		self.pending_ops = []

	def prepare(self) -> None:
		""" Run per-page preparation and the on_item_page hooks. """
		for page in stp.progress_bar(self.pages, desc="Preparing manual pages"):
			page.prepare(self)
			if isinstance(page, ItemPage):
				for fn in self.item_page_hooks:
					fn(page, self)

	def order(self) -> None:
		""" Finalize the order and compute the anchor/item -> index maps (1-based). """
		self.by_anchor = {p.anchor: p for p in self.pages}
		self.anchor_index = {p.anchor: i + 1 for i, p in enumerate(self.pages)}
		self.item_index = {p.item_id: i + 1 for i, p in enumerate(self.pages) if p.item_id is not None}

	def render(self) -> None:
		""" Render every page to text components (links left as PageRef). """
		self.pages_content = []
		for page in stp.progress_bar(self.pages, desc="Rendering manual pages"):
			self.pages_content.append(page.render(self))

	def normalize(self) -> None:
		""" Convert the rendered tree to plain dict/list/str (preserving :class:`PageRef`).

		Item components copied from definitions (and meta-derived components like
		``first_page_text``) are beet ``Box`` objects with default-box behavior: accessing a
		missing key auto-creates an empty ``{}`` entry, which corrupts the output (Minecraft:
		"Not a string: {}"). Flattening to plain Python types up front makes every later pass
		(resolve/optimize/dialog) safe.
		"""
		def to_plain(node: Any) -> Any:
			if isinstance(node, PageRef):
				return node
			if isinstance(node, dict):
				return {k: to_plain(v) for k, v in cast(dict[Any, Any], node).items()}
			if isinstance(node, (list, tuple)):
				return [to_plain(v) for v in cast("list[Any]", node)]
			return node
		self.pages_content = to_plain(self.pages_content)

	def resolve(self) -> None:
		""" Turn every ``change_page`` click event into a ``show_dialog`` to the target page.

		A :class:`PageRef` is resolved to its 1-based index first; a literal int page is used
		as-is (covers author-provided WikiButton links). Unresolvable links are dropped.
		Iterative (no recursion limit) and bounded: such links only live in ``click_event``,
		so we never descend into ``hover_event`` subtrees (which hold deep item-component data).
		"""
		ns = self.config.project_id
		stack: list[Any] = [self.pages_content]
		seen: set[int] = set()
		while stack:
			node = stack.pop()
			if isinstance(node, dict):
				node_d = cast("dict[str, Any]", node)
				if id(node_d) in seen:
					continue
				seen.add(id(node_d))
				ce = node_d.get("click_event")
				if isinstance(ce, dict):
					ce_d = cast("dict[str, Any]", ce)
					if ce_d.get("action") == "change_page":
						page_val = ce_d.get("page")
						idx = self.page_index_of(page_val) if isinstance(page_val, PageRef) else (page_val if isinstance(page_val, int) else -1)
						if idx != -1:
							ce_d.clear()
							ce_d["action"] = "show_dialog"
							ce_d["dialog"] = f"{ns}:manual/page_{idx}"
						else:
							del node_d["click_event"]
				for key, value in node_d.items():
					if key in ("hover_event", "click_event"):
						continue  # no PageRefs live here; avoids deep/Box traversal
					if isinstance(value, (dict, list)):
						stack.append(value)
			elif isinstance(node, list):
				for value in cast("list[Any]", node):
					if isinstance(value, (dict, list)):
						stack.append(value)

	def optimize(self) -> None:
		""" Merge adjacent compounds per page (skipping pages that opt out). """
		self.pages_content = [
			cast(list[TextComponent], optimize_element(page)) if self.pages[i].optimize else page
			for i, page in enumerate(self.pages_content)
		]

	def emit(self) -> None:
		""" Write fonts/textures, dialogs, the manual item, showcase, and clean up. """
		from . import manual_emit
		from .dialog import DialogEmitter
		from .showcase import generate_showcase_images

		manual_emit.register_static_assets(self)
		manual_emit.register_book_overrides(self)
		manual_emit.write_font(self)
		manual_emit.copy_generated_textures(self)
		manual_emit.validate_providers(self)

		# Optional debug dump
		if self.config.json_dump_path:
			with stp.super_open(self.config.json_dump_path, "w") as f:
				f.write(stp.json_dump(self.pages_content))
			stp.debug(f"Debug pages_content at '{stp.relative_path(self.config.json_dump_path)}'")

		# Showcase
		if self.config.showcase_image > 0:
			generate_showcase_images(self.config.showcase_image, self.categories, self.simple_case, self.config.cache_path)

		# Dialogs (always, dialog-first)
		DialogEmitter(self).emit()

		# Manual item
		manual_emit.create_manual_item(self)

		# Cleanup heavy workbench temp item
		from ...dependencies.official_libs import OFFICIAL_LIBS
		if OFFICIAL_LIBS["smithed.crafter"]["is_used"] and "heavy_workbench" in Mem.definitions:
			del Mem.definitions["heavy_workbench"]
			ns = self.config.project_id
			Mem.ctx.assets[ns].textures.pop("item/heavy_workbench", None)
			Mem.ctx.assets[ns].models.pop("item/heavy_workbench", None)
			Mem.ctx.assets[ns].item_models.pop("heavy_workbench", None)


