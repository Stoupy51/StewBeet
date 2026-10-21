
# Lazy imports (PEP 810), ignored before Python 3.15
from stouputils.lazy import ALWAYS_LAZY

__lazy_modules__ = ALWAYS_LAZY

# Imports
import stouputils as stp
from beet import Context

from . import MOVED_MESSAGE


# Silent mode entry point, the deprecation warning still shows
@stp.deprecated(message=MOVED_MESSAGE, version="3.11.0")
def beet_default(ctx: Context) -> None:
	ctx.require("stewbeet.plugins.check_unused_textures.silent")

