
# Assertions for: the bolt sources stewbeet.plugins.sniffer marks under a versioning refactor

# Imports
import json
from collections.abc import Iterator

from beet import Context, TextFile


# Main entry point
def beet_default(ctx: Context) -> Iterator[None]:
	# Listed first and yielding, so these checks run after the emitter and after mecha.
	yield

	moved: list[str] = [path for path in ctx.data.functions if path.startswith("tns:impl/")]
	assert not moved, f"the refactor should have moved every implementation function, {moved} stayed"

	assert bolt_of(ctx, "bolted") == [0], "a file bolt generated Python for is bolt"
	assert bolt_of(ctx, "nested") == [0], "a file mecha split into two functions is bolt"
	assert bolt_of(ctx, "plain") is None, "plain.mcfunction is vanilla"

	print("plugin_33: bolt sources found through a versioning refactor")


# Functions
def bolt_of(ctx: Context, name: str) -> object:
	""" The `x_stewbeet_bolt` entry of a moved function's map, None when the map has none. """
	extra = ctx.data.extra.get(f"data/tns/function/v1.0.0/{name}.mcfunction.map")
	assert isinstance(extra, TextFile), f"{name} must be mapped"
	return json.loads(extra.text).get("x_stewbeet_bolt")

