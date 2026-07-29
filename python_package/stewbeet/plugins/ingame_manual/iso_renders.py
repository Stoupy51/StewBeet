"""Isometric item renders + vanilla texture download.

Ported from v1 ``iso_renders`` with the cache flag taken from :class:`~.config.ManualConfig`
(``cache_assets``) instead of reading meta directly. This is an *asset* cache (skip
already-generated PNGs because 3D rendering is expensive), unrelated to the removed v1
page-content cache.
"""

# Imports
import os
import shutil
import threading
from typing import TYPE_CHECKING, cast

import stouputils as stp
from beet import Model
from PIL import Image
from stouputils.typing import JsonDict

from ...core.__memory__ import Mem
from ...core.cls.item import Item
from ...core.constants import (
	DOWNLOAD_VANILLA_ASSETS_RAW,
	DOWNLOAD_VANILLA_ASSETS_SOURCE,
	DOWNLOAD_VANILLA_ASSETS_SPECIAL_RAW,
)
from .config import ManualConfig

if TYPE_CHECKING:
	import requests

# Thread-local requests session: reuses HTTP connections (TLS handshakes dominate
# the texture download time otherwise, since each item tries up to 6 URLs).
_thread_locals = threading.local()

def _get_session() -> requests.Session:
	""" `requests` is imported here rather than at module level: this module is reachable from the
	top-level ``stewbeet`` package, and paying a fifth of a second of HTTP stack on every single
	build only to download textures the manual may never ask for is not worth it.
	"""
	import requests

	session: requests.Session | None = getattr(_thread_locals, "session", None)
	if session is None:
		session = requests.Session()
		_thread_locals.session = session
	return session


def download_item(path: str, item: str, cache_assets: bool, destination: str = "") -> None:
	""" Download a single vanilla item texture from the wiki. """
	if not destination:
		destination = f"{path}/minecraft/{item}.png"
	if os.path.exists(destination) and cache_assets:
		return
	session: requests.Session = _get_session()
	for base_link in (DOWNLOAD_VANILLA_ASSETS_SPECIAL_RAW, DOWNLOAD_VANILLA_ASSETS_RAW):
		for folder in ["item", "block", "items"]:
			link: str = f"{base_link}/{folder}/{item}.png"
			response = session.get(link)
			if response.status_code == 200:
				with stp.super_open(destination, "wb") as file:
					file.write(response.content)
				return
	stp.warning(f"Failed to download texture for '{item}', please add it manually to '{destination}'")
	stp.warning(f"Suggestion link: '{DOWNLOAD_VANILLA_ASSETS_SOURCE}'")


def build_model_resolver_queue(path: str, ns: str, cache_assets: bool) -> dict[str, str]:
	""" Build the queue of items that need iso renders generated. """
	for_model_resolver: dict[str, str] = {}
	for item in Mem.definitions.keys():
		obj = Item.from_id(item)
		if not obj.components.get("item_model"):
			continue
		if os.path.exists(f"{path}/{ns}/{item}.png") and cache_assets:
			continue
		rp_path = obj.model
		model: Model | None = rp_path.get()
		dst_path = f"{path}/{ns}/{item}.png"
		if model is not None and model.get_content().get("textures", None) is not None:  # type: ignore
			for_model_resolver[rp_path] = dst_path
	return for_model_resolver


def run_model_resolver(for_model_resolver: dict[str, str]) -> None:
	""" Run the model resolver to generate iso renders for the given items. """
	any_atlas_used: bool = "before_format_73" in Mem.ctx.assets.overlays._wrapped.keys()  # type: ignore
	if any_atlas_used:
		Mem.ctx.assets["minecraft"].atlases["temporary_stewbeet"] = Mem.ctx.assets.overlays["before_format_73"]["minecraft"].atlases["blocks"]

	stp.debug(f"Generating iso renders for {len(for_model_resolver)} items, this may take a while...")
	with stp.MeasureTime(message="Generated iso renders for all items"):
		from model_resolver.render import Render as ModelResolverRender

		class FastPaletteRender(ModelResolverRender):
			""" Same rendering as model_resolver, but with a fast ``apply_palette``.

			The upstream implementation scans the whole palette per texture pixel with
			``Image.getpixel`` (O(width*height*palette_size) Python calls); this one builds
			the color mapping once (same column-major first-match semantics) and remaps
			all pixels in a single pass, producing pixel-identical output.
			"""

			def apply_palette(self, texture: Image.Image, palette: Image.Image, color_palette: Image.Image) -> Image.Image:
				texture = texture.convert("RGBA")
				palette = palette.convert("RGB")
				color_palette = color_palette.convert("RGB")
				pal_width: int = palette.width
				pal_pixels: list[tuple[int, int, int]] = list(palette.getdata())  # pyright: ignore[reportArgumentType, reportUnknownVariableType]
				col_pixels: list[tuple[int, int, int]] = list(color_palette.getdata())  # pyright: ignore[reportArgumentType, reportUnknownVariableType]
				mapping: dict[tuple[int, int, int], tuple[int, int, int]] = {}
				for i in range(pal_width):  # column-major like upstream, first match wins
					for j in range(palette.height):
						src: tuple[int, int, int] = pal_pixels[j * pal_width + i]
						if src not in mapping:
							mapping[src] = col_pixels[j * color_palette.width + i]
				tex_pixels: list[tuple[int, int, int, int]] = list(texture.getdata())  # pyright: ignore[reportArgumentType, reportUnknownVariableType]
				new_image = Image.new("RGBA", texture.size)
				new_image.putdata([
					(*new_color, pixel[3]) if (new_color := mapping.get(pixel[:3])) is not None else pixel
					for pixel in tex_pixels
				])
				return new_image

		render = FastPaletteRender(Mem.ctx)  # pyright: ignore[reportCallIssue]
		for rp_path, dst_path in for_model_resolver.items():
			render.add_model_task(rp_path, path_save=dst_path, animation_mode="one_file")
		render.run()

	if any_atlas_used:
		del Mem.ctx.assets["minecraft"].atlases["temporary_stewbeet"]


def collect_used_vanilla_items() -> set[str]:
	""" Collect all vanilla items referenced in recipes across all definitions. """
	used_vanilla_items: set[str] = set()
	for item in Mem.definitions.keys():
		obj = Item.from_id(item)
		for recipe in obj.recipes:
			ingredients = []
			if recipe.get("ingredients"):
				ingredients = recipe["ingredients"]
				if isinstance(ingredients, dict):
					ingredients = cast(list[JsonDict], ingredients.values())
			elif recipe.get("ingredient"):
				ingredients = [recipe["ingredient"]]
			for ingredient in ingredients:
				if "item" in ingredient:
					used_vanilla_items.add(ingredient["item"].split(":")[1])
			if recipe.get("result") and recipe["result"].get("item"):
				used_vanilla_items.add(recipe["result"]["item"].split(":")[1])
	return used_vanilla_items


def download_vanilla_textures(path: str, used_vanilla_items: set[str], cache_assets: bool) -> None:
	""" Download vanilla item textures from the wiki using multithreading. """
	if not used_vanilla_items:
		return
	args = [(path, item, cache_assets) for item in used_vanilla_items]
	stp.multithreading(download_item, args, use_starmap=True, max_workers=min(32, len(used_vanilla_items)))


def copy_painting_textures(path: str, ns: str, cache_assets: bool) -> None:
	""" Download and copy painting textures for custom painting items. """
	last_painting_path: str = ""
	for item, data in Mem.definitions.items():
		if data["id"] == "minecraft:painting" and not data.get("item_model"):
			if not last_painting_path:
				last_painting_path = f"{path}/{ns}/{item}.png"
				download_item(path, "painting", cache_assets, last_painting_path)
			else:
				shutil.copy(last_painting_path, f"{path}/{ns}/{item}.png")


def generate_all_iso_renders(
	config: ManualConfig,
	override_cache_path: str | None = None,
	ignore_vanilla: bool = False,
	ignore_painting: bool = False,
) -> None:
	""" Generate iso renders for every item plus download referenced vanilla textures. """
	ns: str = config.project_id
	path = override_cache_path or (config.cache_path + "/items")
	os.makedirs(f"{path}/{ns}", exist_ok=True)
	cache_assets: bool = config.cache_assets

	for_model_resolver = build_model_resolver_queue(path, ns, cache_assets)
	if for_model_resolver:
		run_model_resolver(for_model_resolver)

	if not ignore_vanilla:
		download_vanilla_textures(path, collect_used_vanilla_items(), cache_assets)

	if not ignore_painting:
		copy_painting_textures(path, ns, cache_assets)

