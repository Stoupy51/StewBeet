
# Imports
from __future__ import annotations

import stouputils as stp
from beet.core.utils import JsonDict


# Utility function to convert result_count to string suffix
@stp.simple_cache
def result_count_to_suffix(result_count: int | JsonDict) -> str:
	""" Convert a result count to a string suffix for loot table paths

	Args:
		result_count (int | JsonDict): The count of the result item, can be an int or a dict for random counts
			ex: 1
			ex: {"type": "minecraft:uniform","min": 4,"max": 6}
	Returns:
		str: The suffix string, ex: "" or "_x5" or "_x4to6"
	"""
	if isinstance(result_count, int):
		if result_count > 1:
			return f"_x{result_count}"
		return ""
	elif hasattr(result_count, "get"):
		minimum = result_count.get("min", 1)
		maximum = result_count.get("max", 1)
		if maximum > 1:
			return f"_x{minimum}to{maximum}"
		elif minimum > 1:
			return f"_x{minimum}"
	return ""

