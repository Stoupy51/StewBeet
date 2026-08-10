""" Shared building blocks for the custom bitmap fonts StewBeet generates.

Imports are explicit rather than star imports: this package is re-exported all the way up to the
top-level ``stewbeet`` namespace, and star importing would leak ``PIL.Image`` and friends into it.
"""
# Imports
from .allocator import GlyphAllocator, get_font
from .colors import (
	HUE_BUCKETS,
	MIN_SATURATION,
	MIN_VALUE,
	NO_RECOLOR_VALUES,
	Pixel,
	get_dominant_color,
	get_pixels,
	parse_color,
	recolor_image,
)
from .image_utils import add_border, careful_resize, ensure_rgba_color, lighten_color
from .item_images import (
	DEFAULT_ISO_RENDERS_PATH,
	build_model_resolver_queue,
	collect_used_vanilla_items,
	copy_painting_textures,
	download_item,
	download_vanilla_textures,
	ensure_item_images,
	generate_all_iso_renders,
	iso_renders_path,
	item_image_path,
	resolve_item_image,
	run_model_resolver,
)
from .providers import merge_font_providers, uses_font, validate_font_providers, write_font_from_allocator

__all__ = [
	"DEFAULT_ISO_RENDERS_PATH",
	"HUE_BUCKETS",
	"MIN_SATURATION",
	"MIN_VALUE",
	"NO_RECOLOR_VALUES",
	"GlyphAllocator",
	"Pixel",
	"add_border",
	"build_model_resolver_queue",
	"careful_resize",
	"collect_used_vanilla_items",
	"copy_painting_textures",
	"download_item",
	"download_vanilla_textures",
	"ensure_item_images",
	"ensure_rgba_color",
	"generate_all_iso_renders",
	"get_dominant_color",
	"get_font",
	"get_pixels",
	"iso_renders_path",
	"item_image_path",
	"lighten_color",
	"merge_font_providers",
	"parse_color",
	"recolor_image",
	"resolve_item_image",
	"run_model_resolver",
	"uses_font",
	"validate_font_providers",
	"write_font_from_allocator",
]
