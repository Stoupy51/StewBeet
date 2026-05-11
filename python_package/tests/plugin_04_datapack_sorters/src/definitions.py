
# Imports
import json

from beet import Context
from stewbeet import *  # type: ignore
from stewbeet.plugins.datapack.sorters.constants import SorterFile


# Main entry point
def beet_default(ctx: Context):
    ns: str = ctx.project_id

    # Add a selection_sort configuration to the data pack namespace.
    # The sorters plugin will pick it up and generate the sorting functions.
    sorter_config: dict = {
        "algorithm": "selection_sort",
        "functions_location": f"{ns}:utils/sort_scores",
        "to_sort": {
            "storage": f"{ns}:data",
            "target": "all.players",
        },
        "key": "score",
        "scale": 100,
        "limit": 10,
    }
    ctx.data[ns][SorterFile]["my_sort"] = SorterFile(json.dumps(sorter_config))
