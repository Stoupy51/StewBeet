
# Imports
import stouputils as stp
from beet import Context


# Silent mode entry point
def beet_default(ctx: Context) -> None:
	from . import beet_default
	return stp.silent(beet_default)(ctx)

