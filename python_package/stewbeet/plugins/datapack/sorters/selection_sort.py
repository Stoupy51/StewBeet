
# Imports
from beet import Context

from ....core import Mem, write_function
from .constants import MACRO


# Functions
def generate_selection_sort(ctx: Context, sorter: dict) -> None:
	""" Generate selection sort algorithm functions for sorting storage lists.

	This function creates a set of minecraft functions that implement the selection sort
	algorithm to sort lists stored in minecraft storage. The algorithm finds the minimum
	element and moves it to a new sorted array repeatedly.

	Args:
		ctx (Context): The beet context for generating functions.
		sorter (dict): Configuration dictionary containing sorting parameters.
	"""
	old_ctx: Context = Mem.ctx
	Mem.ctx = ctx  # Set the current context to the one provided

	# Extract configuration parameters
	functions_location: str = sorter["functions_location"]
	to_sort: str = f"storage {sorter['to_sort']['storage']} {sorter['to_sort']['target']}"
	key: str = sorter["key"]
	scale: int = sorter.get("scale", 1)  # Default scale is 1
	limit: int | None = sorter.get("limit")  # Optional limit for sorting

	# Main sort entry point function
	sort_function_content = f"""
# Create a scoreboard objective and storage for temporary values
scoreboard objectives add sorter.val dummy
data modify storage sorter:temp original_array set from {to_sort}
data modify storage sorter:temp sorted_array set value []
"""
	if limit is not None:
		sort_function_content += """
scoreboard players set #sorted_count sorter.val 0
"""
	sort_function_content += f"""
# Start the selection sort process
execute if data storage sorter:temp original_array[0] run function {functions_location}/selection_sort_loop
data modify {to_sort} set from storage sorter:temp sorted_array

# Cleanup temporary storage
data remove storage sorter:temp original_array
data remove storage sorter:temp copy_array
data remove storage sorter:temp sorted_array
"""
	write_function(f"{functions_location}/sort", sort_function_content)

	# Selection sort main loop
	loop_function_content = f"""
# Reset variables for finding minimum
scoreboard players set #current_index sorter.val 0
scoreboard players set #min_value sorter.val 2147483647
scoreboard players set #min_index sorter.val 0

# Copy the original array to the working copy
data modify storage sorter:temp copy_array set from storage sorter:temp original_array

# Find the minimum element
execute if data storage sorter:temp copy_array[0] run function {functions_location}/find_min

# Move the minimum element to the sorted array
execute store result {MACRO}.min_index int 1 run scoreboard players get #min_index sorter.val
function {functions_location}/move_min_element with {MACRO}
"""
	if limit is not None:
		loop_function_content += f"""
# Increment sorted count
scoreboard players add #sorted_count sorter.val 1

# Continue if limit not reached and there are more elements to sort
execute if score #sorted_count sorter.val matches ..{limit-1} if data storage sorter:temp original_array[0] run return run function {functions_location}/selection_sort_loop

# If limit reached, append remaining elements without sorting
execute if score #sorted_count sorter.val matches {limit} run function {functions_location}/append_remaining
"""
	else:
		loop_function_content += f"""
# Continue if there are more elements to sort
execute if data storage sorter:temp original_array[0] run function {functions_location}/selection_sort_loop
"""
	write_function(f"{functions_location}/selection_sort_loop", loop_function_content)

	# Find minimum element in the array
	write_function(f"{functions_location}/find_min", f"""
# Get the current element value
execute store result score #current_value sorter.val run data get storage sorter:temp copy_array[0].{key} {scale}

# Check if this is the new minimum
execute if score #current_value sorter.val < #min_value sorter.val run scoreboard players operation #min_index sorter.val = #current_index sorter.val
execute if score #current_value sorter.val < #min_value sorter.val run scoreboard players operation #min_value sorter.val = #current_value sorter.val

# Move to the next element
scoreboard players add #current_index sorter.val 1
data remove storage sorter:temp copy_array[0]

# Continue if there are more elements
execute if data storage sorter:temp copy_array[0] run function {functions_location}/find_min
""")

	# Move the minimum element from original to sorted array
	write_function(f"{functions_location}/move_min_element", """
# Add the minimum element to the sorted array
$data modify storage sorter:temp sorted_array append from storage sorter:temp original_array[$(min_index)]

# Remove the minimum element from the original array
$data remove storage sorter:temp original_array[$(min_index)]
""")

	# Generate append_remaining function only if limit is specified
	if limit is not None:
		write_function(f"{functions_location}/append_remaining", """
# Append remaining unsorted elements to the sorted array
data modify storage sorter:temp sorted_array append from storage sorter:temp original_array[]
""")

	# Reset the context to the original one
	Mem.ctx = old_ctx

