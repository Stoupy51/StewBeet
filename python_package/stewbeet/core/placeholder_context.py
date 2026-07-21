
# Imports
from pathlib import Path
from tempfile import gettempdir

from beet import Context
from beet.toolchain.context import ProjectCache
from beet.toolchain.template import TemplateManager
from beet.toolchain.worker import WorkerPoolHandle


# Placeholder context
def create_placeholder_context() -> Context:
    """ Build a lightweight stand-in Context so code touching Mem.ctx works out of a build (doctests, scripts).

    Its packs are empty and every path points to a scratch directory that is never created:
    nothing on disk is read or written unless a real build replaces the context.

    Returns:
        Context: A placeholder context with project_id "your_namespace" and empty packs.

    Examples:
        >>> from stewbeet.core.placeholder_context import create_placeholder_context
        >>> ctx = create_placeholder_context()
        >>> ctx.project_id, ctx.project_name
        ('your_namespace', 'Your Namespace')
        >>> bool(ctx.data), bool(ctx.assets)  # Both packs are empty
        (False, False)
    """
    scratch: Path = Path(gettempdir()) / "stewbeet_placeholder_context"
    return Context(
        project_id="your_namespace",
        project_name="Your Namespace",
        project_description="",
        project_author="",
        project_version="0.0.0",
        project_root=False,
        minecraft_version="",
        directory=scratch,
        output_directory=None,
        meta={},
        cache=ProjectCache(scratch / "cache", scratch / "generated"),
        worker=WorkerPoolHandle(None),
        template=TemplateManager([], scratch),
    )

PLACEHOLDER_CTX: Context = create_placeholder_context()
""" The placeholder context Mem.ctx defaults to. Compare with `Mem.ctx is PLACEHOLDER_CTX` to detect "not in a build". """

