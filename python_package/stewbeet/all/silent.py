
# Lazy imports (PEP 810), ignored before Python 3.15
from stouputils.lazy import ALWAYS_LAZY

__lazy_modules__ = ALWAYS_LAZY

# Imports
from collections.abc import Generator

from beet import Context


# Silent mode entry point
def beet_default(ctx: Context) -> Generator[None]:
	from .__init__ import beet_default
	return beet_default(ctx, silent=True)

