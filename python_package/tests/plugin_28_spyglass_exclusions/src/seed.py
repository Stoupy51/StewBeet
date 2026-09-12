# Starting state for: stewbeet.plugins.spyglass
#
# A config that already holds one of the author's own patterns and one an earlier build added, so
# both halves of the contract are exercised in a single build.

# Imports
import json

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


# Main entry point
def beet_default(ctx: Context) -> None:
    with open(CONFIG, "w", encoding="utf-8") as file:
        json.dump({"env": {"dependencies": ["@vanilla-mcdoc"], "exclude": [AUTHORS_OWN, STALE]}}, file, indent=2)
    ctx.cache[CACHE_NAME].json["excluded"] = [STALE]

