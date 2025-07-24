
# Imports
from beet import Context
from stouputils.decorators import measure_time
from stouputils.print import progress

from ....core.__memory__ import Mem
from ....core.utils.io import read_function, write_function
from .object import Header
from .function_analyzer import FunctionAnalyzer
from .context_analyzer import ContextAnalyzer


# Main entry point
@measure_time(progress, message="Execution time of 'stewbeet.plugins.auto.headers'")
def beet_default(ctx: Context):
    """ Main entry point for the headers plugin.

    Args:
        ctx (Context): The beet context.
    """
    if Mem.ctx is None:
        Mem.ctx = ctx

    # Get all mcfunctions paths and create Header objects
    mcfunctions: dict[str, Header] = {}
    for path in ctx.data.functions:
        # Create a Header object from the function content
        content: str = read_function(path)
        mcfunctions[path] = Header.from_content(path, content)

    # Analyze function relationships
    function_analyzer = FunctionAnalyzer(ctx, mcfunctions)
    function_analyzer.analyze_all_relationships()

    # Analyze execution contexts
    context_analyzer = ContextAnalyzer(mcfunctions)
    context_analyzer.analyze_all_contexts()

    # Write updated headers to all mcfunction files
    for path, header in mcfunctions.items():
        write_function(path, header.to_str(), overwrite=True)

