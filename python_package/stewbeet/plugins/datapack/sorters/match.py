
# Imports
from beet import Context

from .quick_sort import generate_quick_sort
from .selection_sort import generate_selection_sort


# Functions
def generate_sorter(ctx: Context, sorter: dict):
	""" Generate sorting functions based on the specified algorithm.

	Currently an abstraction layer in case more algorithms are added in the future.
	Routes to the appropriate algorithm-specific generator function.

	Args:
		ctx (Context): The beet context for generating functions.
		sorter (dict): Configuration dictionary containing sorting parameters.
	"""
	# Assertions to validate sorter configuration
	assert isinstance(sorter.get("functions_location"), str), "'functions_location' must be a string, e.g. 'switch:stats/minigame/sort_leaderboard'."
	assert isinstance(sorter.get("key"), str), "'key' must be a string, e.g. 'count' if you list is looking like [{'id':'...', count:54}, ...]."
	assert isinstance(sorter.get("to_sort"), dict), "'to_sort' must be a dictionary."
	assert isinstance(sorter["to_sort"].get("storage"), str), "'to_sort.storage' must be a string, e.g. 'switch:stats'"
	assert isinstance(sorter["to_sort"].get("target"), str), "'to_sort.target' must be a string, e.g. 'all.modes.sheepwars.played'."

	# Switch case
	match(sorter["algorithm"]):
		case "selection_sort":
			generate_selection_sort(ctx, sorter)
		case "quick_sort":
			generate_quick_sort(ctx, sorter)

