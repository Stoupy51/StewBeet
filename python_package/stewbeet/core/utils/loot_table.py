
# Imports
from __future__ import annotations

import stouputils as stp
from stouputils.typing import JsonDict


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

	Examples:
		Count of 1 returns empty suffix:
		>>> result_count_to_suffix(1)
		''

		Count greater than 1 returns _xN suffix:
		>>> result_count_to_suffix(5)
		'_x5'

		Random range with max > 1 returns _xMINtoMAX:
		>>> result_count_to_suffix({"min": 4, "max": 6})
		'_x4to6'

		Range where min > max (degenerate range: only _xMIN suffix emitted since max <= 1):
		>>> result_count_to_suffix({"min": 3, "max": 1})
		'_x3'

		Empty dict (no min/max keys) returns empty suffix:
		>>> result_count_to_suffix({})
		''

		Range with both min and max equal to 1 returns empty suffix:
		>>> result_count_to_suffix({"min": 1, "max": 1})
		''
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

