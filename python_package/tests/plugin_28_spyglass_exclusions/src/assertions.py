# Assertions for: stewbeet.plugins.spyglass
#
# Listed first, so its setup seeds the starting state and its teardown runs after the plugin's.

# Imports
import json
import os
from collections.abc import Iterator

from beet import Context

# Constants
CONFIG: str = ".spyglassrc.json"
""" The config the plugin creates when a project has none of the names Spyglass looks for. """

CACHE_NAME: str = "stewbeet_spyglass"
""" Where the plugin remembers which patterns are its own. """

AUTHORS_OWN: str = "build/**"
""" An exclusion the author wrote. It is in nobody's ownership list and must survive untouched. """

STALE: str = "src/data/tns/function/gone.mcfunction"
""" An exclusion an earlier build added for a file that no longer holds bolt. """

BOLTED: str = "src/data/tns/function/bolted.mcfunction"
NESTED: str = "src/data/tns/function/nested.mcfunction"
PLAIN: str = "src/data/tns/function/plain.mcfunction"


# Main entry point
def beet_default(ctx: Context) -> Iterator[None]:
    # Start from a config that already holds one of the author's own patterns and one this plugin
    # added last time, so both halves of the contract are exercised in a single build.
    with open(CONFIG, "w", encoding="utf-8") as file:
        json.dump({"env": {"dependencies": ["@vanilla-mcdoc"], "exclude": [AUTHORS_OWN, STALE]}}, file, indent=2)
    ctx.cache[CACHE_NAME].json["excluded"] = [STALE]

    yield

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
