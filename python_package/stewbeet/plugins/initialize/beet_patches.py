""" Monkey patches applied to beet at the very start of every build.

These live here instead of in a beet fork so upstream stays pullable. Each patch keeps the exact
behaviour of what it replaces and is applied once per process, never re-wrapping on the second build
of a `stewbeet watch` session.
"""
# Lazy imports (PEP 810), ignored before Python 3.15
from stouputils.lazy import ALWAYS_LAZY

__lazy_modules__ = ALWAYS_LAZY

# Imports
import os
from collections.abc import Callable, Iterator
from pathlib import Path
from typing import Any

import beet.library.utils
import stouputils as stp
from beet import Pack, PngFile
from beet.core.utils import FileSystemPath
from PIL import Image

# Variables
patches_applied: bool = False
""" Whether `apply_beet_patches` already ran in this process. """


# Functions
def fast_list_files(directory: FileSystemPath) -> Iterator[Path]:
	""" Drop-in replacement for `beet.library.utils.list_files`, yielding every file below a directory relative to it.

	Upstream builds a `Path` out of every walked file and then re-parses it through
	`relative_to(directory)`, which is about five times slower than slicing the prefix off the string
	`os.walk` already hands over.
	Files come in sorted order, so a pack loads the same way on every file system.

	>>> import tempfile
	>>> with tempfile.TemporaryDirectory() as tmp:
	...     Path(tmp, "sub").mkdir()
	...     _ = Path(tmp, "sub", "a.txt").write_text("a")
	...     sorted(path.as_posix() for path in fast_list_files(tmp))
	['sub/a.txt']
	"""
	base: str = os.fspath(directory)
	prefix_length: int = len(base) + (0 if base.endswith(("/", os.sep)) else 1)
	for root, dirs, files in os.walk(base):
		dirs.sort()
		relative_root: str = root[prefix_length:]
		for filename in sorted(files):
			yield Path(relative_root, filename)


def same_pixels(left: Image.Image, right: Image.Image) -> bool:
	""" Tell whether two images hold exactly the same pixels, mode and palette included.

	>>> red = Image.new("RGBA", (2, 2), "red")
	>>> same_pixels(red, Image.new("RGBA", (2, 2), "red"))
	True
	>>> same_pixels(red, Image.new("RGBA", (2, 2), "blue"))
	False
	>>> same_pixels(red, Image.new("RGB", (2, 2), "red"))
	False
	"""
	return (
		left.mode == right.mode
		and left.size == right.size
		and left.getpalette() == right.getpalette()
		and left.tobytes() == right.tobytes()
	)


def reuse_unchanged_pngs(pack: Pack[Any], directory: FileSystemPath) -> None:
	""" Give the in-memory images of a pack the bytes saved in `directory` by the previous build, when their pixels are unchanged.

	>>> import tempfile
	>>> from beet import ResourcePack, Texture
	>>> with tempfile.TemporaryDirectory() as tmp:
	...     saved = Texture(Image.new("RGBA", (4, 4), "red")).ensure_serialized() + b"previous encoding"
	...     Path(tmp, "assets/demo/textures").mkdir(parents=True)
	...     _ = Path(tmp, "assets/demo/textures/red.png").write_bytes(saved)
	...     pack = ResourcePack()
	...     pack.textures["demo:red"] = Texture(Image.new("RGBA", (4, 4), "red"))
	...     reuse_unchanged_pngs(pack, tmp)
	...     pack.textures["demo:red"].ensure_serialized() == saved
	True
	"""
	# Pillow's zlib compresses differently on each platform, so a build on another machine would otherwise rewrite them all.
	# Files loaded from disk or already serialized are copied byte for byte by beet, only encoded images can differ.
	files: list[tuple[str, PngFile]] = [
		(relative_path, file)
		for part in (pack, *pack.overlays.values())
		for relative_path, file in part.list_files(extend=PngFile)
		if isinstance(file.get_content(), Image.Image)
	]

	for relative_path, file in files:
		existing: Path = Path(directory, relative_path)
		if not existing.is_file():
			continue

		saved: bytes = existing.read_bytes()
		try:
			unchanged: bool = same_pixels(PngFile(saved).image, file.image)
		except (OSError, SyntaxError, ValueError):
			continue  # Unreadable file on disk, beet overwrites it
		if unchanged:
			file.set_content(saved)


def stable_png_save(save: Callable[..., Path]) -> Callable[..., Path]:
	""" Wrap `Pack.save` so a pack saved as a folder over a previous build keeps the bytes of its unchanged images. """
	def wrapper(
		self: Pack[Any], directory: FileSystemPath | None = None, path: FileSystemPath | None = None,
		zipped: bool | None = None, *args: Any, **kwargs: Any
	) -> Path:
		# Same output location as upstream computes it
		output: Path | None = Path(path) if path else None
		is_zipped: bool = output.suffix == ".zip" if output else bool(self.zipped if zipped is None else zipped)
		if output is None and self.name:
			output = Path(directory or self.path or Path.cwd(), self.name)

		if not is_zipped and output is not None and output.is_dir():
			reuse_unchanged_pngs(self, output)
		return save(self, directory, path, zipped, *args, **kwargs)
	return wrapper


def apply_beet_patches() -> None:
	""" Install every beet monkey patch, once per process. """
	global patches_applied
	if patches_applied:
		return
	patches_applied = True

	# Rebind the module global: `list_origin` is beet's only caller and resolves it at call time
	beet.library.utils.list_files = fast_list_files

	# Retry saving when another program (vscode, Minecraft, ...) holds a file locked for a moment
	Pack.save = stp.retry(Pack.save, exceptions=PermissionError, max_attempts=10, delay=1.0, backoff=2.0)  # pyright: ignore[reportUnknownArgumentType, reportUnknownMemberType]

	# Keep the previous bytes of generated images whose pixels did not change (see reuse_unchanged_pngs)
	Pack.save = stable_png_save(Pack.save)  # pyright: ignore[reportUnknownArgumentType, reportUnknownMemberType]

