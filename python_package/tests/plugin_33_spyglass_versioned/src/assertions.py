# Assertions for: stewbeet.plugins.spyglass under a versioning refactor
#
# Queued the same way the plugin queues itself, one entry further down the pipeline, so these run
# after it: a task inserted at the front of beet's list pops last, and the later insert pops later.

# Imports
import json

from beet import Context

from stewbeet.plugins.spyglass import queue_at_end

# Constants
CONFIG: str = ".spyglassrc.json"
""" The config the plugin writes, in the project root. """

BOLTED: str = "src/data/tns/function/impl/bolted.mcfunction"
NESTED: str = "src/data/tns/function/impl/nested.mcfunction"
PLAIN: str = "src/data/tns/function/impl/plain.mcfunction"


# Main entry point
def beet_default(ctx: Context) -> None:
    queue_at_end(ctx, check)


# Functions
def check(ctx: Context) -> None:
    # The refactor moved every function, which is what makes the names hard to recover.
    moved: list[str] = [path for path in ctx.data.functions if path.startswith("tns:impl/")]
    assert not moved, f"the refactor should have moved every implementation function, {moved} stayed"

    with open(CONFIG, encoding="utf-8") as file:
        exclude: list[str] = json.load(file)["env"]["exclude"]

    assert BOLTED in exclude, f"a file bolt generated Python for must be excluded, got {exclude}"
    assert NESTED in exclude, f"a file mecha split into two functions must be excluded, got {exclude}"
    assert PLAIN not in exclude, f"{PLAIN} is vanilla and excluding it costs it Spyglass for nothing"

    print(f"plugin_33: {len(exclude)} exclusions found through a versioning refactor")

