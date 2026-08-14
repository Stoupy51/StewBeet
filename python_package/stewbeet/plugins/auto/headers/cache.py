""" Reuse of the previous build's header analysis.

Building the @within graph and inferring macro argument types walks every function body, then walks the
callers of every macro function recursively. The answer is a pure function of the function contents plus
the tags, advancements and dialogs that can reference them, so a build whose inputs are all unchanged can
restore the previous answer instead of computing it again. Anything at all changing in those inputs
invalidates the whole record, which is what keeps a cross-referencing analysis honest: a single edited
body can change the header of a function on the other side of the pack.
"""

# Lazy imports (PEP 810), ignored before Python 3.15
from stouputils.lazy import ALWAYS_LAZY

__lazy_modules__ = ALWAYS_LAZY

# Imports
import hashlib
import json
from typing import Any

from beet import Cache, Context

from .object import Header

# Constants
CACHE_NAME: str = "auto_headers"
""" Beet cache slot holding the analysis of the previous build. """
CACHE_KEY: str = "analysis"
""" Key of the file inside that slot, resolved through the cache so the path stays beet's business. """


# Functions
def analysis_signature(ctx: Context, contents: dict[str, str]) -> str:
    """ Hash everything the analyzers read, so any change to any of it invalidates the stored analysis.

    Only the fields the analyzers actually consume are hashed. Reading more would mean deserializing pack
    files that this plugin deliberately never touches, which would re-encode them on output.

    Args:
        ctx (Context): The beet context.
        contents (dict[str, str]): The raw content of every function, keyed by path.
    Returns:
        str: Hexadecimal digest covering every input of the analysis.
    """
    digest = hashlib.sha1()
    for path, content in sorted(contents.items()):
        digest.update(f"function\0{path}\0{content}\0".encode())
    for tag_path, tag in sorted(ctx.data.function_tags.items()):
        digest.update(f"tag\0{tag_path}\0{tag.data.get('values')}\0".encode())
    for adv_path, adv in sorted(ctx.data.advancements.items()):
        digest.update(f"advancement\0{adv_path}\0{adv.data.get('rewards', {}).get('function')}\0".encode())
    for dialog_path, dialog in sorted(ctx.data.dialogs.items()):
        digest.update(f"dialog\0{dialog_path}\0{dialog.text}\0".encode())
    return digest.hexdigest()


def restore_analysis(cache: Cache, signature: str, mcfunctions: dict[str, Header]) -> list[str] | None:
    """ Put the previous build's analysis back into the headers, when it still applies.

    Everything is parsed and validated before a single header is touched: the analyzers append to
    `within` rather than replacing it, so a half applied record would silently duplicate entries.

    Args:
        cache (Cache): The beet cache slot holding the record.
        signature (str): Signature the inputs must still match.
        mcfunctions (dict[str, Header]): Headers to fill in, keyed by function path.
    Returns:
        list[str] | None: The warnings the skipped analysis had emitted, or None when nothing was restored.
    """
    try:
        stored: Any = json.loads(cache.get_path(CACHE_KEY).read_text("utf-8"))
        if stored.get("signature") != signature:
            return None
        entries: dict[str, Any] = stored["headers"]
        parsed: dict[str, tuple[list[str], str, dict[str, tuple[str, list[str]]]]] = {
            path: (
                [str(caller) for caller in entry["within"]],
                str(entry["executed"]),
                {str(name): (str(value[0]), [str(line) for line in value[1]]) for name, value in entry["args"].items()},
            )
            for path, entry in entries.items()
        }
        warnings: list[str] = [str(warning) for warning in stored["warnings"]]
    except (OSError, ValueError, TypeError, KeyError, IndexError, AttributeError):
        return None

    if parsed.keys() != mcfunctions.keys():
        return None
    for path, (within, executed, args) in parsed.items():
        header: Header = mcfunctions[path]
        header.within = within
        header.executed = executed
        header.args = args
    return warnings


def store_analysis(cache: Cache, signature: str, mcfunctions: dict[str, Header], warnings: list[str]) -> None:
    """ Record the analysis so the next build with the same inputs can skip it.

    Args:
        cache (Cache): The beet cache slot to write to.
        signature (str): Signature of the inputs this analysis was computed from.
        mcfunctions (dict[str, Header]): The analyzed headers, keyed by function path.
        warnings (list[str]): Warnings emitted while analyzing, replayed on every restore.
    """
    path = cache.get_path(CACHE_KEY)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({
        "signature": signature,
        "warnings": warnings,
        "headers": {
            func_path: {"within": header.within, "executed": header.executed, "args": header.args}
            for func_path, header in mcfunctions.items()
        },
    }), "utf-8")

