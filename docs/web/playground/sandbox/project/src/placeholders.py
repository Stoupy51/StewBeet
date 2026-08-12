""" Give every defined item a texture and a render, so the playground never needs a GPU or a name it does not have.

Two failures this prevents, both of which a visitor hits within a minute of editing:

resource_pack.item_models raises `Texture '<id>.png' not found in source textures` for an item with
no matching file, and stouputils turns that into sys.exit(1). Locally that is right: you forgot a
texture and you want to know. Here it means renaming steel_ingot to something of your own kills the
build over an asset you were never going to have.

auto.text_renders reaches model_resolver for any item with no cached render, through
emit.source_images -> ensure_item_images -> run_model_resolver, which imports OpenGL. That is the
one thing this container cannot do. build_model_resolver_queue skips an item whose PNG already
exists when cache_assets is true, so seeding the cache is what keeps the queue empty and the whole
render path unreachable.

An item's render here is just its texture rather than an isometric view. For a flat item that is
what the render would have looked like anyway, and for a block it is honest enough: it shows the
right texture, drawn flat.
"""
# Imports
import shutil
from pathlib import Path

import stouputils as stp
from beet import Context
from PIL import Image

from stewbeet import Mem

# Constants
SIZE: int = 16
""" One Minecraft texture tile. """

COLORS: tuple[tuple[int, int, int, int], tuple[int, int, int, int]] = ((248, 0, 248, 255), (0, 0, 0, 255))
""" Magenta and black: what a Minecraft player already reads as a missing texture. """


# Functions
def placeholder() -> Image.Image:
	""" Draw the missing-texture checkerboard.

	Returns:
		Image.Image: A 16x16 RGBA image of four alternating quarters.
	"""
	image: Image.Image = Image.new("RGBA", (SIZE, SIZE))
	half: int = SIZE // 2
	for x in range(SIZE):
		for y in range(SIZE):
			image.putpixel((x, y), COLORS[(x < half) == (y < half)])
	return image


def fill_textures(folder: Path) -> list[str]:
	""" Write a checkerboard for every definition the bundled packs do not cover.

	Args:
		folder (Path): The writable texture folder.
	Returns:
		list[str]: Ids that got a placeholder.
	"""
	existing: set[str] = {path.name for path in folder.rglob("*.png")}
	missing: list[str] = sorted(item for item in Mem.definitions if f"{item}.png" not in existing)
	if missing:
		image: Image.Image = placeholder()
		for item in missing:
			image.save(folder / f"{item}.png")
	return missing


def fill_renders(folder: Path, textures: Path, namespace: str) -> None:
	""" Seed the render cache so build_model_resolver_queue comes back empty.

	Args:
		folder    (Path): The writable renders folder.
		textures  (Path): The texture folder, already filled by fill_textures.
		namespace (str):  Project namespace, which is the subfolder renders are looked up in.
	"""
	destination: Path = folder / namespace
	destination.mkdir(parents=True, exist_ok=True)
	for item in Mem.definitions:
		render: Path = destination / f"{item}.png"
		texture: Path = textures / f"{item}.png"
		if not render.exists() and texture.exists():
			shutil.copyfile(texture, render)


def beet_default(ctx: Context) -> None:
	""" Fill both caches, between the submitted module and the plugins that read them.

	Args:
		ctx (Context): The beet context, read for the project namespace.
	"""
	stewbeet: dict[str, str] = dict(Mem.ctx.meta.get("stewbeet", {}))
	textures: Path = Path(stewbeet.get("textures_folder", ""))
	renders: Path = Path(stewbeet.get("iso_renders_path", ""))
	if not textures.is_dir():
		return

	missing: list[str] = fill_textures(textures)
	fill_renders(renders, textures, str(ctx.project_id))

	if missing:
		stp.warning(
			f"No bundled texture for {', '.join(missing)}: using the missing-texture checkerboard. "
			f"The playground ships the textures of SimplEnergy, Stardust Fragment and the extensive template, "
			f"and any other name gets this placeholder."
		)
