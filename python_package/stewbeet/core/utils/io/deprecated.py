
# Imports
from collections.abc import Callable
from typing import Any

import stouputils as stp
from beet import TagFile

from ...__memory__ import Mem
from .functions import write_tag


# Deprecated functions
@stp.deprecated(message="convert_to_serializable is deprecated, prefer using stp.convert_to_serializable from stouputils", version="v3.1.3")
def convert_to_serializable(obj: Any) -> Any:
	return stp.convert_to_serializable(obj)


@stp.deprecated(message="write_function_tag is deprecated, prefer using write_tag or `tags` argument of write_function instead", version="v3.1.3")
def write_function_tag(
	path: str,
	functions: list[Any] | None = None,
	prepend: bool = False,
	max_level: int | None = None,
	condition: Callable[[list[Any]], bool] = lambda existing_values: True, # pyright: ignore[reportUnknownLambdaType]
) -> TagFile | None:
	""" write_function_tag is deprecated, prefer using write_tag or `tags` argument of write_function instead """
	return write_tag(path, Mem.ctx.data.function_tags, functions, prepend, max_level, condition)

