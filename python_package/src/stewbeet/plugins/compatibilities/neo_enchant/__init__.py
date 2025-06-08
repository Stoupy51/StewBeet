
# Imports
from beet import BlockTag, Context
from beet.core.utils import JsonDict
from stouputils.decorators import measure_time
from stouputils.io import super_json_dump
from stouputils.print import progress

from ....core.__memory__ import Mem
from ....core.constants import VANILLA_BLOCK, VANILLA_BLOCK_FOR_ORES


# Main entry point
@measure_time(progress, message="Execution time of 'stewbeet.plugins.compatibilities.neo_enchant'")
def beet_default(ctx: Context):
	""" Main entry point for the NeoEnchant compatibility plugin.
	This plugin sets up NeoEnchant's Veinminer compatibility.

	Args:
		ctx (Context): The beet context.
	"""
	if Mem.ctx is None:
		Mem.ctx = ctx

	# If any block use the vanilla block for ores, add the compatibility
	if any(VANILLA_BLOCK_FOR_ORES == data.get(VANILLA_BLOCK) for data in Mem.database.values()):

		# Add the block to veinminer tag
		tag_content: JsonDict = {"values": [VANILLA_BLOCK_FOR_ORES["id"]]}
		Mem.ctx.data["enchantplus"].block_tags["veinminer"] = BlockTag(super_json_dump(tag_content))

