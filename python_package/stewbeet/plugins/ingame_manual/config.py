"""Typed configuration for the manual, read from ``ctx.meta["stewbeet"]["manual"]``.

Replaces the scattered ``manual_config.get(...)`` calls and the config-ish fields of the
old ``SharedMemory``. v2 is dialog-first: ``use_dialog`` is validated to be 1 or 2 (0 is
coerced to 1 with a warning). The old caching keys (``cache_pages``) are intentionally not
read; ``json_dump_path`` survives only as an optional debug dump.
"""

# Imports
from dataclasses import dataclass, field

import stouputils as stp
from beet import Context
from beet.core.utils import TextComponent
from stouputils.typing import JsonDict

from ...core.__memory__ import Mem
from ...core.utils.fonts import iso_renders_path
from .button_layout import ButtonLayout

# Beet cache holding the generated glyph PNGs and the copied templates (lives in .beet_cache).
FONT_CACHE_NAME: str = "stewbeet_manual"

# Default item components shown when hovering an item in the manual (target of set_manual_components).
DEFAULT_COMPONENTS_TO_INCLUDE: list[str] = ["item_name", "lore", "custom_name", "damage", "max_damage"]

# Backward-compat hook: set_manual_components() writes here so a later from_meta() picks it up,
# even when called before the Manual exists.
COMPONENTS_OVERRIDE: list[str] | None = None


@dataclass(kw_only=True, slots=True)
class ManualConfig:
	""" Typed mirror of the ``manual`` stewbeet config block.

	Build one with :meth:`from_meta`. All fields are public.

	>>> config = ManualConfig(project_id="mypack", project_name="My Pack", project_author="me", max_items_per_row=9)
	>>> config.max_items_per_row  # clamped like v1 (max 6 per row)
	6
	>>> config.font
	'mypack:manual'
	>>> config.name  # defaults to "<project_name> Manual"
	'My Pack Manual'
	"""
	# Project info (copied from ctx for convenience)
	project_id: str
	project_name: str
	project_author: str

	# Paths
	iso_renders_path: str = ""
	""" Folder holding the per-item PNG renders, shared with auto.text_renders. Resolved lazily when empty. """
	font_cache_path: str = ""
	""" Throwaway folder for the generated glyph PNGs, inside beet's own cache. Resolved lazily when empty. """
	manual_overrides: str = ""
	json_dump_path: str = ""  # Debug dump only (NOT a cache)

	# Rendering
	high_resolution: bool = True
	use_dialog: int = 1  # 1 = dialog + manual item, 2 = dialog only (0 coerced to 1)
	debug_mode: bool = False
	cache_assets: bool = True  # Skip re-rendering/re-downloading item textures that already exist
	max_items_per_row: int = 5
	max_rows_per_page: int = 5
	showcase_image: int = 3

	# Content
	name: str = ""
	first_page_text: TextComponent = ""
	components_to_include: list[str] = field(default_factory=lambda: list(DEFAULT_COMPONENTS_TO_INCLUDE))
	button_layout: ButtonLayout = field(default_factory=lambda: ButtonLayout(columns=6, max_buttons=42))

	def __post_init__(self) -> None:
		# Clamp grid like v1 (max 6 per row, 7 rows)
		self.max_items_per_row = min(6, self.max_items_per_row)
		self.max_rows_per_page = min(7, self.max_rows_per_page)

		# Dialog-first: drop mode 0
		if self.use_dialog not in (1, 2):
			if self.use_dialog == 0:
				stp.warning("manual.use_dialog=0 (book-only) is removed in ingame_manual; using dialog mode 1.")
			self.use_dialog = 1

		# Resolve manual name + length check
		if not self.name:
			self.name = f"{self.project_name} Manual"
		if len(self.name) >= 32:
			stp.error(f"Manual name '{self.name}' is too long (max 32 characters), Minecraft does not support it.")

		# Resolve the two cache folders: the item renders are a project artifact, the glyph PNGs are throwaway
		if not self.iso_renders_path:
			self.iso_renders_path = iso_renders_path()
		if not self.font_cache_path:
			self.font_cache_path = stp.clean_path(str(Mem.ctx.cache[FONT_CACHE_NAME].directory))

	# Derived properties
	@property
	def max_items_per_page(self) -> int:
		""" Item capacity of a category page (rows x columns). """
		return self.max_items_per_row * self.max_rows_per_page

	@property
	def left_padding(self) -> int:
		""" Category grid left padding: higher items-per-row -> lower padding. """
		return 6 - self.max_items_per_row

	@property
	def font(self) -> str:
		""" Fully-qualified font id, e.g. ``mynamespace:manual``. """
		return f"{self.project_id}:manual"

	@classmethod
	def from_meta(cls, ctx: Context) -> ManualConfig:
		""" Build a :class:`ManualConfig` from the beet context meta. """
		assert ctx.project_id, "Project ID is not set."
		assert ctx.project_name, "Project name is not set."
		assert ctx.project_author, "Project author is not set."
		stewbeet: JsonDict = ctx.meta.get("stewbeet", {})
		assert stewbeet, "stewbeet configuration is not set."
		assert stewbeet.get("textures_folder"), "Textures folder is not set."
		raw: JsonDict = stewbeet.get("manual", {})
		assert raw, "Manual configuration is not set."

		components = list(COMPONENTS_OVERRIDE) if COMPONENTS_OVERRIDE else list(DEFAULT_COMPONENTS_TO_INCLUDE)

		return cls(
			components_to_include=components,
			project_id=ctx.project_id,
			project_name=ctx.project_name,
			project_author=ctx.project_author,
			manual_overrides=raw.get("manual_overrides", ""),
			json_dump_path=raw.get("json_dump_path", ""),
			high_resolution=raw.get("high_resolution", True),
			use_dialog=raw.get("use_dialog", 1),
			debug_mode=raw.get("debug_mode", False),
			cache_assets=raw.get("cache_assets", True),
			max_items_per_row=raw.get("max_items_per_row", 5),
			max_rows_per_page=raw.get("max_rows_per_page", 5),
			showcase_image=raw.get("showcase_image", 3),
			name=raw.get("name", ""),
			first_page_text=raw.get("first_page_text", ""),
		)

