""" ↪️ Runs stewbeet.plugins.check_unused_textures, with a deprecation warning asking to require it by that path. """
# Lazy imports (PEP 810), ignored before Python 3.15
from stouputils.lazy import ALWAYS_LAZY

__lazy_modules__ = ALWAYS_LAZY

# Imports
import stouputils as stp
from beet import Context

# Constants
MOVED_MESSAGE: str = (
	"'stewbeet.plugins.finalyze.check_unused_textures' is now 'stewbeet.plugins.check_unused_textures'. "
	"Require it by that path, after every plugin that adds textures (such as auto.text_renders)."
)


# Main entry point
@stp.deprecated(message=MOVED_MESSAGE, version="3.11.0")
def beet_default(ctx: Context) -> None:
	ctx.require("stewbeet.plugins.check_unused_textures")

