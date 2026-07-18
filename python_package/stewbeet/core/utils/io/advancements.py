
# Imports
from collections.abc import Callable

from beet import Advancement
from stouputils.typing import JsonDict

from ...__memory__ import Mem
from .dicts import super_merge_dict
from .files import set_json_encoder


# Advancements
def write_advancement(
	path: str,
	advancement: Advancement | JsonDict,
	overwrite: bool = False,
	max_level: int = -1,
	condition: Callable[[JsonDict], bool] = lambda existing_data: True, # pyright: ignore[reportUnknownLambdaType]
) -> Advancement | None:
	""" Write an advancement at the given path.

	Args:
		path        (str):                         The path to the advancement (ex: "namespace:folder/advancement_name")
		advancement (Advancement | JsonDict):      The advancement to write
		overwrite   (bool):                        If the file should be overwritten (default: Merge with existing content using super_merge_dict)
		max_level   (int):                         The maximum level of the JSON dump, -1 for default behavior (default: -1)
		condition   (Callable[[JsonDict], bool]):  A function that takes the existing advancement data
			and returns whether the new advancement should be written (default: always write)
	Returns:
		Advancement | None: The written advancement, or None if the condition was not met
	"""
	path = path.removesuffix(".json")  # Remove .json extension if present

	# Get existing advancement or create empty one, and check condition with its data
	existing_data: JsonDict = Mem.ctx.data.advancements.get(path, Advancement()).data
	if not condition(existing_data):
		return None

	# Convert to dict if it's an Advancement object
	new_data: JsonDict = advancement.data if isinstance(advancement, Advancement) else advancement

	if overwrite or not existing_data:
		adv: Advancement = set_json_encoder(Advancement(new_data), max_level=max_level)
	else:
		# Merge the new data with existing data
		merged_data: JsonDict = super_merge_dict(existing_data, new_data)
		adv: Advancement = set_json_encoder(Advancement(merged_data), max_level=max_level)

	# Write the advancement to memory and return it
	Mem.ctx.data.advancements[path] = adv
	return adv

