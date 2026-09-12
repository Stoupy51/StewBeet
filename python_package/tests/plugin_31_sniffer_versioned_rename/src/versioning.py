# The smithed versioning refactor, reduced to the two beet plugins it is built out of.

# Imports
from collections.abc import Iterator

from beet import Context
from beet.contrib.find_replace import find_replace
from beet.contrib.rename_files import rename_files


# Main entry point
def beet_default(ctx: Context) -> Iterator[None]:
    # After the yield, so the functions move once mecha has already compiled them.
    yield

    ctx.require(find_replace(data_pack={"match": "tns:*"}, substitute={"find": "tns:impl/", "replace": "tns:v1.0.0/"}))
    ctx.require(rename_files(data_pack={"match": "tns:*", "find": "tns:impl/", "replace": "tns:v1.0.0/"}))

