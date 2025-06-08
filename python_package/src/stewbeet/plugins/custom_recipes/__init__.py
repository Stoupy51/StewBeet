
# Imports
from beet import Context
from stouputils.decorators import measure_time
from stouputils.print import progress

from ...core.__memory__ import Mem
from .furnace import FurnaceRecipeHandler
from .pulverizer import PulverizerRecipeHandler
from .smithed import SmithedRecipeHandler
from .vanilla import VanillaRecipeHandler


# Main entry point
@measure_time(progress, message="Execution time of 'stewbeet.plugins.custom_recipes'")
def beet_default(ctx: Context) -> None:
    """ Main entry point for the custom recipes plugin.
    This plugin handles the generation of custom recipes for the datapack.
    
    Requires a valid database in Mem.database in order to function properly.

    Args:
        ctx (Context): The beet context.
    """
    if Mem.ctx is None:
        Mem.ctx = ctx

    # Do all the things
    VanillaRecipeHandler.routine()
    SmithedRecipeHandler.routine()
    PulverizerRecipeHandler.routine()
    FurnaceRecipeHandler.routine()

