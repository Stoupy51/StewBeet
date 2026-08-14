
# Lazy imports (PEP 810), ignored before Python 3.15
from stouputils.lazy import ALWAYS_LAZY

__lazy_modules__ = ALWAYS_LAZY

# Imports
import stouputils as stp
from beet import Cache, Context

from ....core.__memory__ import Mem
from ....core.utils.io import read_function, write_function
from .cache import CACHE_NAME, analysis_signature, restore_analysis, store_analysis
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
    contents: dict[str, str] = {path: read_function(path) for path in ctx.data.functions}
    mcfunctions: dict[str, Header] = {path: Header.from_content(path, content) for path, content in contents.items()}

    # The analysis is cross-referencing, so it is reused as a whole or recomputed as a whole
    cache: Cache = ctx.cache[CACHE_NAME]
    signature: str = analysis_signature(ctx, contents)
    restored: list[str] | None = restore_analysis(cache, signature, mcfunctions)

    if restored is None:
        # Analyze function relationships
        function_analyzer = FunctionAnalyzer(ctx, mcfunctions)
        function_analyzer.analyze_all_relationships()

        # Analyze execution contexts
        context_analyzer = ContextAnalyzer(mcfunctions)
        context_analyzer.analyze_all_contexts()

        # Analyze macro arguments
        macro_analyzer = MacroAnalyzer(mcfunctions)
        macro_analyzer.analyze_all_macros()

        store_analysis(cache, signature, mcfunctions, macro_analyzer.warnings)
    else:
        # Replay what the skipped analysis would have reported
        for warning in restored:
            stp.warning(warning)

    # Write updated headers to all mcfunction files
    for path, header in mcfunctions.items():
        write_function(path, header.to_str(), overwrite=True)

