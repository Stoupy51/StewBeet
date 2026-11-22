
# Lazy imports (PEP 810), ignored before Python 3.15
from stouputils.lazy import ALWAYS_LAZY

__lazy_modules__ = ALWAYS_LAZY

# Imports
import stouputils as stp


# Functions
@stp.deprecated(
	message="insert_lib_calls is deprecated: the custom_blocks plugin registers energy blocks on its own, remove the call",
	version="3.15.2",
)
def insert_lib_calls() -> None:
	""" Does nothing: the custom blocks plugin registers the blocks with energy settings. """

