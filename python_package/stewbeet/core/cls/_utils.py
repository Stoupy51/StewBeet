
# Imports
from collections.abc import Mapping
from typing import Any, Self

from beet.core.utils import JsonDict


# Class for mapping behavior
class StMapping(Mapping[str, Any]):
    def __getitem__(self, key: str) -> Any:
        return getattr(self, key)

    @classmethod
    def from_dict(cls, data: JsonDict) -> Self:
        if isinstance(data, cls):
            return data
        return cls(**data)

