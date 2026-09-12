# Lazy imports (PEP 810), ignored before Python 3.15
from stouputils.lazy import ALWAYS_LAZY

__lazy_modules__ = ALWAYS_LAZY

# Imports
import stouputils as stp
from beet import Context


# Silent mode entry point
def beet_default(ctx: Context) -> None:
	from .__init__ import apply_exclusions, queue_at_end
	queue_at_end(ctx, stp.silent(apply_exclusions))

