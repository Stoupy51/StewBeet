""" ⛏️ NeoEnchant compatibility, for its Veinminer enchantment. """
# Lazy imports (PEP 810), ignored before Python 3.15
from stouputils.lazy import ALWAYS_LAZY

__lazy_modules__ = ALWAYS_LAZY

# Imports
import stouputils as stp
from beet import BlockTag, Context
from stouputils.typing import JsonDict

from ....core.__memory__ import Mem
from ....core.cls.block import VANILLA_BLOCK_FOR_ORES
from ....core.constants import VANILLA_BLOCK


# Main entry point
@stp.measure_time(message="Execution time of 'stewbeet.plugins.compatibilities.neo_enchant'")
def beet_default(ctx: Context):
	""" Main entry point for the NeoEnchant compatibility plugin.
	This plugin sets up NeoEnchant's Veinminer compatibility.

	Args:
		ctx: The beet context.
	"""
	Mem.ctx = ctx

	# If any block use the vanilla block for ores, add the compatibility
	if any(data.get(VANILLA_BLOCK) == VANILLA_BLOCK_FOR_ORES for data in Mem.definitions.values()):

		# Add the block to veinminer tag
		tag_content: JsonDict = {"values": [VANILLA_BLOCK_FOR_ORES["id"]]}
		Mem.ctx.data["enchantplus"].block_tags["veinminer"] = BlockTag(stp.json_dump(tag_content))

