""" Displays following a host state that changes after placement, as the corner a stairs host makes or a furnace burning. """
# Lazy imports (PEP 810), ignored before Python 3.15
from stouputils.lazy import ALWAYS_LAZY

__lazy_modules__ = ALWAYS_LAZY

# Imports
from ....core.cls.items.block import Block
from ....core.utils.io import write_function


# Functions
def write_host_state(block: Block) -> None:
	""" Keep the custom_model_data string of the block's display on the state of `VanillaBlock.host_states` its host is in.

	It is set on placement and checked every second, the items definition showing the model copy of that state,
	and only for a block whose resource pack has such a copy.
	"""
	vanilla = block.vanilla_block
	if vanilla is None or not any(block.model.suffixed(suffix).exists() for suffix in vanilla.host_states.values() if suffix):
		return
	follow: str = block.functions["follow_host"]
	write_function(follow, "".join(
		f'execute if block ~ ~ ~ {vanilla.base_id}[{state}] '
		f'unless items entity @s contents *[custom_model_data={{strings:["{state}"]}}] '
		f'run data modify entity @s item.components."minecraft:custom_model_data" set value {{strings:["{state}"]}}\n'
		for state in vanilla.host_states
	))
	write_function(block.functions.place_secondary, f"\n# Show the model of the state the host is in\nfunction {follow}\n")
	write_function(block.functions.second, f"function {follow}\n")

