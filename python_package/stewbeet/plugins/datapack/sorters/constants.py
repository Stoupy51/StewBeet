
# Imports
from typing import Any, ClassVar, Literal, TypeAlias

from beet import FileDeserialize, JsonFileBase, NamespaceFileScope
from pydantic.v1 import BaseModel

# Constants
MACRO: str = "storage sorter:temp args"

# Type aliases
SorterAlgorithm: TypeAlias = Literal[
	"quick_sort",
	"selection_sort"
]

# Classes
class Sorter(BaseModel):
	""" Configuration model for sorting operations.

	This class defines the parameters required to generate datapack functions
	that can sort lists stored in storage using various algorithms.

	Example:
	```
		{
			"algorithm": "selection_sort",
			"functions_location": "switch:stats/minigame/sort_leaderboard",
			"to_sort": {
				"storage": "switch:stats",
				"target": "all.modes.sheepwars.played"
			},
			"key": "count",
			"scale": 100
		}
	```
	"""
	algorithm: SorterAlgorithm = "selection_sort"
	""" Algorithm used to sort the elements, defaults to `selection_sort`. """
	functions_location: str
	""" Namespaced id where the sorting functions are generated. """
	to_sort: dict[str, str]
	""" Location of the list to sort. """
	key: str
	""" The key to the number getting compared. """
	scale: int = 1
	""" (Option) By how many the number should be scaled before getting rounded. """
	limit: int | None = None
	""" (Option) Limit of how many elements to sort, if not specified all elements will be sorted.
	(Only compatible with `selection_sort` algorithm.) """


class SorterFile(JsonFileBase[Sorter]):
	""" JSON file handler for sorter configurations.

	This class handles the serialization and deserialization of sorter
	configuration files within the datapack namespace.
	"""
	model: type[Any] = Sorter
	scope: ClassVar[NamespaceFileScope] = ("sorter",)
	extension: ClassVar[str] = ".json"
	data: ClassVar[FileDeserialize[Sorter]] = FileDeserialize()

