
# Lazy imports (PEP 810), ignored before Python 3.15
from stouputils.lazy import ALWAYS_LAZY

__lazy_modules__ = ALWAYS_LAZY

# Imports
from beet.core.utils import split_version

from ..__memory__ import Mem
from ..constants import LATEST_MC_VERSION


# Functions
def minecraft_version_at_least(version: tuple[int, ...]) -> bool:
	""" Whether the project targets the given Minecraft version or a later one.

	Projects without a "minecraft" field in their config target the latest version.

	>>> minecraft_version_at_least((1, 21)), minecraft_version_at_least((9999,))
	(True, False)
	"""
	return split_version(Mem.ctx.minecraft_version or LATEST_MC_VERSION) >= version

