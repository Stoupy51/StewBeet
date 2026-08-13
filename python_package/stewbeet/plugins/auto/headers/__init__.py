
# Lazy imports (PEP 810), ignored before Python 3.15
from stouputils.lazy import ALWAYS_LAZY

__lazy_modules__ = ALWAYS_LAZY

# Imports
import stouputils as stp
from beet import Context

from ....core.__memory__ import Mem
from ....core.utils.io import read_function, write_function
from .context_analyzer import ContextAnalyzer
from .function_analyzer import FunctionAnalyzer
from .macro_analyzer import MacroAnalyzer
from .object import Header


# Main entry point
@stp.measure_time(message="Execution time of 'stewbeet.plugins.auto.headers'")
def beet_default(ctx: Context):
    """ Main entry point for the headers plugin.

    Args:
        ctx (Context): The beet context.
    """
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

    # Analyze macro arguments
    macro_analyzer = MacroAnalyzer(mcfunctions)
    macro_analyzer.analyze_all_macros()

    # Write updated headers to all mcfunction files
    for path, header in mcfunctions.items():
        write_function(path, header.to_str(), overwrite=True)

