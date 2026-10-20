""" The tool a block needs to drop its item: enforced by vanilla through a host of the right level, or checked by StewBeet. """
# Lazy imports (PEP 810), ignored before Python 3.15
from stouputils.lazy import ALWAYS_LAZY

__lazy_modules__ = ALWAYS_LAZY

# Imports
from beet import ItemTag

from ....core.cls.items.block import Block
from ....core.cls.items.features import VANILLA_BLOCK_FOR_ORES, Mining, VanillaBlock
from ....core.utils.io import set_json_encoder, write_function


# Functions
def resolve_mining_hosts(blocks: list[Block]) -> None:
	""" Give a block with `mining` and no host the default host of its level, and refuse a host that would not enforce it.

	An ore keeps `VANILLA_BLOCK_FOR_ORES`, and an interaction host checks the tool itself, so both may need any tool.

	Raises:
		ValueError: When no vanilla host enforces the tool, or the host given is not one of `Mining.hosts`.
	"""
	for block in blocks:
		mining: Mining | None = block.mining
		host: VanillaBlock | None = block.vanilla_block
		if mining is None or (host and (host.interaction or host == VANILLA_BLOCK_FOR_ORES)):
			continue

		if not mining.hosts:
			raise ValueError(f"Block '{block.id}': no vanilla host requires {mining}, give it an Interaction host to check the tool.")
		if host is None or not host.id:
			block.vanilla_block = VanillaBlock(id=mining.hosts[0])
		elif host.base_id not in mining.hosts:
			raise ValueError(f"Block '{block.id}': host '{host.id}' does not require {mining}, use one of {mining.hosts}.")


def write_mining(blocks: list[Block]) -> None:
	""" The item tag of the tools each `Mining` allows, and the check making an ore's item vanish when mined with a weaker one.

	An ore's host breaks with any pickaxe, so its drop is checked against the tool of the nearest survival player within 8 blocks.
	"""
	for mining in {block.mining for block in blocks if block.mining}:
		mining.item_tag.write(set_json_encoder(ItemTag({"values": mining.tools})))
	for block in blocks:
		if block.mining and block.mining.level != "wood" and block.vanilla_block == VANILLA_BLOCK_FOR_ORES:
			miner: str = "@p[distance=..8,gamemode=!creative,gamemode=!spectator]"
			write_function(block.functions.replace_item, f"""
# Mined with a tool too weak
execute if entity {miner} unless items entity {miner} weapon.mainhand #{block.mining.item_tag} run return run kill @s
""", prepend=True)

