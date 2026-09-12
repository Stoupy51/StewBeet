# The smithed versioning refactor, run the way `simple_item_plugin` runs it: before mecha parses.

# Imports
from beet import Context
from beet.contrib.find_replace import find_replace
from beet.contrib.rename_files import rename_files


# Main entry point
def beet_default(ctx: Context) -> None:
    ctx.require(find_replace(data_pack={"match": "tns:*"}, substitute={"find": "tns:impl/", "replace": "tns:v1.0.0/"}))
    ctx.require(rename_files(data_pack={"match": "tns:*", "find": "tns:impl/", "replace": "tns:v1.0.0/"}))

