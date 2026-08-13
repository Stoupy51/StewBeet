
# Lazy imports (PEP 810), ignored before Python 3.15
from stouputils.lazy import ALWAYS_LAZY

__lazy_modules__ = ALWAYS_LAZY

# Imports
from typing import cast

import stouputils as stp
from stouputils.typing import JsonDict


# Merge two dict recursively
def super_merge_dict(dict1: JsonDict, dict2: JsonDict) -> JsonDict:
	""" Merge the two dictionaries recursively without modifying originals

	Args:
		dict1 (dict): The first dictionary
		dict2 (dict): The second dictionary
	Returns:
		dict: The merged dictionary

	Examples:
		>>> super_merge_dict({"a": 1}, {"b": 2})
		{'a': 1, 'b': 2}
		>>> super_merge_dict({"a": 1}, {"a": 99})
		{'a': 99}
		>>> super_merge_dict({"nested": {"x": 1, "y": 2}}, {"nested": {"y": 99, "z": 3}})
		{'nested': {'x': 1, 'y': 99, 'z': 3}}
		>>> super_merge_dict({"tags": ["a", "b"]}, {"tags": ["b", "c"]})
		{'tags': ['a', 'b', 'c']}
		>>> result = super_merge_dict({"items": [{"id": 1}]}, {"items": [{"id": 2}]})
		>>> result["items"]
		[{'id': 1}, {'id': 2}]
	"""
	# Copy first dictionary
	new_dict: JsonDict = {}
	for key, value in dict1.items():
		new_dict[key] = value

	# For each key of the second dictionnary,
	for key, value in dict2.items():

		# If key exists in dict1, and both values are also dict, merge recursively
		if key in dict1 and isinstance(dict1[key], dict) and isinstance(value, dict):
			new_dict[key] = super_merge_dict(dict1[key], cast(JsonDict, value))

		# Else if it's a list, merge it
		elif key in dict1 and isinstance(dict1[key], list) and isinstance(value, list):
			new_dict[key] = dict1[key] + value
			if not any(isinstance(x, dict) for x in new_dict[key]):
				new_dict[key] = stp.unique_list(new_dict[key])

		# Else, just overwrite or add value
		else:
			new_dict[key] = value

	# Return the new dict
	return new_dict
