# Assertions for: stewbeet.plugins.spyglass
#
# Queued the same way the plugin queues itself, one entry further down the pipeline, so these run
# after it: a task inserted at the front of beet's list pops last, and the later insert pops later.

# Imports
import json
import os

from beet import Context

from stewbeet.plugins.spyglass import queue_at_end

from .seed import AUTHORS_OWN, CACHE_NAME, CONFIG, STALE

# Constants
BOLTED: str = "src/data/tns/function/bolted.mcfunction"
NESTED: str = "src/data/tns/function/nested.mcfunction"
PLAIN: str = "src/data/tns/function/plain.mcfunction"


# Main entry point
def beet_default(ctx: Context) -> None:
    queue_at_end(ctx, check)


# Functions
def check(ctx: Context) -> None:
    with open(CONFIG, encoding="utf-8") as file:
        config = json.load(file)

    exclude: list[str] = config["env"]["exclude"]
    assert BOLTED in exclude, f"a file bolt generated Python for must be excluded, got {exclude}"
    assert NESTED in exclude, f"a file mecha split into two functions must be excluded, got {exclude}"
    assert PLAIN not in exclude, f"{PLAIN} is vanilla and excluding it costs it Spyglass for nothing"

    assert AUTHORS_OWN in exclude, "a pattern the author wrote is not this plugin's to remove"
    assert STALE not in exclude, "a pattern this plugin added for a file that is no longer bolt must be retracted"

    assert config["env"]["dependencies"] == ["@vanilla-mcdoc"], \
        f"everything outside env.exclude belongs to the project, got {config['env']}"

    owned: list[str] = ctx.cache[CACHE_NAME].json["excluded"]
    assert sorted(owned) == sorted([BOLTED, NESTED]), \
        f"ownership must name exactly what this plugin added, got {owned}"
    assert AUTHORS_OWN not in owned, "claiming the author's pattern would let a later build retract it"

    # The config is written where Spyglass looks, in the project root and nowhere else.
    assert os.path.isfile(CONFIG), f"{CONFIG} must sit in the project root"

    print(f"plugin_28: {len(exclude)} exclusions, one retracted, the author's own untouched")
