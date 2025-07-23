""" Quick Sort Algorithm for Minecraft Storage Lists

This algorithm is less efficient than the Selection Sort algorithm for Minecraft due to the cost of macro calls.
It is recommended to use Selection Sort.

Author: Darukshock
"""

# Imports
from beet import Context

from ....core import Mem, write_function
from .constants import MACRO


# Functions
def generate_quick_sort(ctx: Context, sorter: dict) -> None:
	""" Generate quick_sort algorithm functions for sorting storage lists.

	This function creates a set of minecraft functions that implement the quick_sort
	algorithm to sort lists stored in minecraft storage. The algorithm is implemented
	using recursive function calls with macro parameters.

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

	# Main sort entry point function
	write_function(f"{functions_location}/sort", f"""
# Create a scoreboard objective and storage for temporary values
scoreboard objectives add sorter.val dummy
data modify storage sorter:temp inInt set value [0]

# Count the number of elements to sort and prepare the macro
execute store result score high sorter.val run data get {to_sort}
execute store result {MACRO}.high int 1 run scoreboard players remove high sorter.val 1
data modify {MACRO}.low set value 0

# Start the quick_sort process
function {functions_location}/quick_sort with {MACRO}
""")

	# Quicksort recursive function
	write_function(f"{functions_location}/quick_sort", f"""
$execute if predicate {{"condition": "value_check","range": {{"min": -8,"max": $(low)}},"value": $(high)}} run return 0
$execute store result score pi sorter.val run function {functions_location}/partition_main {{low:$(low),high:$(high)}}
data modify storage sorter:temp inInt append value 0
execute store result storage sorter:temp inInt[-1] int 1 store result {MACRO}.high int 1 run scoreboard players remove pi sorter.val 1
function {functions_location}/quick_sort with {MACRO}
execute store result score pi sorter.val run data get storage sorter:temp inInt[-1]
execute store result {MACRO}.low int 1 run scoreboard players add pi sorter.val 2
$data modify {MACRO}.high set value $(high)
function {functions_location}/quick_sort with {MACRO}
""")

	# Partition function - finds pivot position
	write_function(f"{functions_location}/partition_main", f"""
$execute store result score pivot sorter.val run data get {to_sort}[$(high)].{key} {scale}
$scoreboard players set i sorter.val $(low)
scoreboard players remove i sorter.val 1
$execute store result {MACRO}.j int 1 run scoreboard players set j sorter.val $(low)
$function {functions_location}/partition_loop {{high:$(high),low:$(low),j:$(low)}}
execute store result {MACRO}.i int 1 run scoreboard players add i sorter.val 1
$data modify {MACRO}.j set value $(high)
function {functions_location}/partition_swap with {MACRO}
return run scoreboard players get i sorter.val
""")

	# Partition loop - iterates through elements to partition
	write_function(f"{functions_location}/partition_loop", f"""
$execute if score j sorter.val matches $(high).. run return 0
$execute store result score test sorter.val run data get {to_sort}[$(j)].{key} {scale}
execute if score test sorter.val < pivot sorter.val run function {functions_location}/partition_loop_swap with {MACRO}
execute store result {MACRO}.j int 1 run scoreboard players add j sorter.val 1
function {functions_location}/partition_loop with {MACRO}
""")

	# Partition swap - swaps elements during partitioning
	write_function(f"{functions_location}/partition_swap", f"""
$data modify storage sorter:temp element set from {to_sort}[$(i)]
$data modify {to_sort}[$(i)] set from {to_sort}[$(j)]
$data modify {to_sort}[$(j)] set from storage sorter:temp element
""")

	# Partition loop swap - continues partitioning after swap
	write_function(f"{functions_location}/partition_loop_swap", f"""
execute store result {MACRO}.i int 1 run scoreboard players add i sorter.val 1
function {functions_location}/partition_swap with {MACRO}
""")

	# Reset the context to the original one
	Mem.ctx = old_ctx

