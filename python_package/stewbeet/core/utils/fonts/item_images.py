""" Per-item PNG renders, the image source behind every item glyph.

Three kinds of item ids resolve differently: project items are rasterized from their resource pack
model with ``model_resolver``, ``minecraft:`` items are downloaded from the wiki, and items belonging
to any other pack are read from disk (the project is expected to drop them there itself).

The resulting folder is shared by every consumer, so an item is only ever rendered once per build.
"""
# Imports
import os
import shutil
import threading
from collections.abc import Iterable
from typing import TYPE_CHECKING, cast

import stouputils as stp
from beet import Model
from PIL import Image
from stouputils.typing import JsonDict

from ...__memory__ import Mem
from ...cls.item import Item
from ...constants import (
	DOWNLOAD_VANILLA_ASSETS_RAW,
	DOWNLOAD_VANILLA_ASSETS_SOURCE,
	DOWNLOAD_VANILLA_ASSETS_SPECIAL_RAW,
)

if TYPE_CHECKING:
	import requests

# Constants
DEFAULT_ISO_RENDERS_PATH: str = "manual_cache/items"
""" Folder used when neither 'iso_renders_path' nor the deprecated 'manual.cache_path' is configured. """

# Thread-local requests session: reuses HTTP connections (TLS handshakes dominate
# the texture download time otherwise, since each item tries up to 6 URLs).
THREAD_LOCALS = threading.local()


# Path resolution
def iso_renders_path() -> str:
	""" Folder holding the per-item PNG renders.

	Reads ``meta.stewbeet.iso_renders_path``, falling back to the deprecated
	``meta.stewbeet.manual.cache_path`` suffixed with ``/items`` so existing projects keep their folder.

	Returns:
		str: Path to the renders folder, e.g. ``"manual_cache/items"``.
	"""
	stewbeet: JsonDict = Mem.ctx.meta.get("stewbeet", {})
	explicit: str = stewbeet.get("iso_renders_path", "")
	if explicit:
		return stp.clean_path(explicit)

	legacy: str = stewbeet.get("manual", {}).get("cache_path", "")
	if legacy:
		stp.warning(
			"'meta.stewbeet.manual.cache_path' is deprecated, use 'meta.stewbeet.iso_renders_path' instead "
			f"(currently falling back to '{legacy}/items'). Everything else the manual cached now lives in '.beet_cache'."
		)
		return stp.clean_path(f"{legacy}/items")
	return DEFAULT_ISO_RENDERS_PATH


def item_image_path(item_id: str) -> str:
	""" Path of the PNG backing an item id, whether it exists yet or not.

	Args:
		item_id (str): Fully qualified item id, e.g. ``"minecraft:stone"``.
	Returns:
		str: Path inside the renders folder, e.g. ``"manual_cache/items/minecraft/stone.png"``.
	"""
	namespace, name = item_id.split(":", 1)
	return f"{iso_renders_path()}/{namespace}/{name}.png"


# Vanilla texture download
def get_session() -> requests.Session:
	""" `requests` is imported here rather than at module level: this module is reachable from the
	top-level ``stewbeet`` package, and paying a fifth of a second of HTTP stack on every single
	build only to download textures the caller may never ask for is not worth it.
	"""
	import requests

	session: requests.Session | None = getattr(THREAD_LOCALS, "session", None)
	if session is None:
		session = requests.Session()
		THREAD_LOCALS.session = session
	return session


def download_item(path: str, item: str, cache_assets: bool, destination: str = "") -> None:
	""" Download a single vanilla item texture from the wiki. """
	if not destination:
		destination = f"{path}/minecraft/{item}.png"
	if os.path.exists(destination) and cache_assets:
		return
	session: requests.Session = get_session()
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


def download_vanilla_textures(path: str, used_vanilla_items: set[str], cache_assets: bool) -> None:
	""" Download vanilla item textures from the wiki using multithreading. """
	if not used_vanilla_items:
		return
	args = [(path, item, cache_assets) for item in used_vanilla_items]
	stp.multithreading(download_item, args, use_starmap=True, max_workers=min(32, len(used_vanilla_items)))


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


# Project item rendering
def build_model_resolver_queue(path: str, ns: str, cache_assets: bool, only: Iterable[str] | None = None) -> dict[str, str]:
	""" Build the queue of items that need iso renders generated.

	Args:
		path			(str):					Renders folder.
		ns				(str):					Project namespace.
		cache_assets	(bool):					Skip items whose PNG already exists.
		only			(Iterable[str] | None):	Restrict to these item ids, or None for every definition.
	Returns:
		dict[str, str]: Mapping of resource pack model path to destination PNG path.
	"""
	for_model_resolver: dict[str, str] = {}
	for item in (Mem.definitions.keys() if only is None else only):
		if item not in Mem.definitions:
			continue
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
	renders_path: str = "",
	project_id: str = "",
	cache_assets: bool = True,
	ignore_vanilla: bool = False,
	ignore_painting: bool = False,
) -> None:
	""" Generate iso renders for every item plus download referenced vanilla textures.

	Args:
		renders_path	(str):	Renders folder, defaults to :func:`iso_renders_path`.
		project_id		(str):	Project namespace, defaults to the context one.
		cache_assets	(bool):	Skip items whose PNG already exists.
		ignore_vanilla	(bool):	Skip downloading the vanilla textures used by recipes.
		ignore_painting	(bool):	Skip copying the painting textures.
	"""
	ns: str = project_id or Mem.ctx.project_id
	path: str = renders_path or iso_renders_path()
	os.makedirs(f"{path}/{ns}", exist_ok=True)

	for_model_resolver = build_model_resolver_queue(path, ns, cache_assets)
	if for_model_resolver:
		run_model_resolver(for_model_resolver)

	if not ignore_vanilla:
		download_vanilla_textures(path, collect_used_vanilla_items(), cache_assets)

	if not ignore_painting:
		copy_painting_textures(path, ns, cache_assets)


# Resolution for arbitrary item ids
def ensure_item_images(item_ids: Iterable[str], cache_assets: bool = True) -> dict[str, str]:
	""" Make sure a PNG exists for every given item id, generating or downloading what is missing.

	The three namespace kinds are batched: project items go through a single ``model_resolver`` run,
	``minecraft:`` items through a single multithreaded download, and any other namespace is expected
	to already be on disk (see the ``iso_renders_path`` documentation).

	Args:
		item_ids		(Iterable[str]):	Item ids, namespaced or bare (bare means the project namespace).
		cache_assets	(bool):				Reuse the PNGs that already exist instead of regenerating them.
	Returns:
		dict[str, str]: Mapping of fully qualified item id to PNG path, missing ones left out.
	"""
	ns: str = Mem.ctx.project_id
	path: str = iso_renders_path()
	qualified: list[str] = sorted({item if ":" in item else f"{ns}:{item}" for item in item_ids})

	# Project items: one model_resolver run for the whole batch
	own: list[str] = [item.split(":", 1)[1] for item in qualified if item.startswith(f"{ns}:")]
	if own:
		os.makedirs(f"{path}/{ns}", exist_ok=True)
		queue: dict[str, str] = build_model_resolver_queue(path, ns, cache_assets, only=own)
		if queue:
			run_model_resolver(queue)

	# Vanilla items: one multithreaded download for the whole batch
	vanilla: set[str] = {item.split(":", 1)[1] for item in qualified if item.startswith("minecraft:")}
	if vanilla:
		os.makedirs(f"{path}/minecraft", exist_ok=True)
		download_vanilla_textures(path, vanilla, cache_assets)

	# Everything else must already be on disk
	resolved: dict[str, str] = {}
	for item in qualified:
		image_path: str = item_image_path(item)
		if os.path.exists(image_path):
			resolved[item] = image_path
		else:
			stp.warning(f"No image found for '{item}', expected it at '{stp.relative_path(image_path)}'")
	return resolved


def resolve_item_image(item_id: str, cache_assets: bool = True) -> str | None:
	""" Path of the PNG for a single item id, generating or downloading it when needed.

	Args:
		item_id			(str):	Item id, namespaced or bare (bare means the project namespace).
		cache_assets	(bool):	Reuse the PNG if it already exists instead of regenerating it.
	Returns:
		str | None: Path to the PNG, or None when it could not be resolved.
	"""
	qualified: str = item_id if ":" in item_id else f"{Mem.ctx.project_id}:{item_id}"
	return ensure_item_images([qualified], cache_assets).get(qualified)

