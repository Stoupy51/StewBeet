
# Imports
# Lazy imports (PEP 810), ignored before Python 3.15
from stouputils.lazy import ALWAYS_LAZY

__lazy_modules__ = ALWAYS_LAZY

from dataclasses import dataclass, field
from itertools import product
from typing import TYPE_CHECKING, ClassVar

import stouputils as stp
from beet import BlockTag

from ...dependencies import official_lib_used
from ..__memory__ import Mem
from ..cls._utils import StMapping
from ..cls.block import Block
from ..cls.block_functions import BlockFunctions
from ..utils.io import set_json_encoder, write_function
from ..utils.loot_table import loot_condition
from ..utils.versions import minecraft_version_at_least

if TYPE_CHECKING:
	from ...plugins.sniffer.model import SourceOrigin


# Classes
@dataclass(kw_only=True, slots=True)
class CustomOreGeneration(StMapping):
	""" Where, how often and how large the veins of one custom ore generate, through the Smart Ore Generation library.

	The library scans 96x96 regions around players and starts each vein at a random position next to air.
	Conditions are execute subcommands starting with "if " or "unless ", all of which must hold.
	`vein_conditions` are checked once at the start of the vein and cancel all of it, which suits biomes.
	`block_conditions` are checked at every block of the vein, which suits neighbouring blocks.

	```py
	CustomOreGeneration(
		dimensions=["minecraft:overworld"],
		provider=["#minecraft:terracotta"],
		vein_conditions=["if biome ~ ~ ~ #minecraft:is_badlands"],
		block_conditions=["if block ~ ~1 ~ #minecraft:terracotta"],
	)
	```
	"""
	OVERWORLD_REPLACEABLES: ClassVar[tuple[str, ...]] = (
		"#minecraft:base_stone_overworld", "#minecraft:substrate_overworld", "#minecraft:sand", "#minecraft:terracotta",
		"#minecraft:iron_ores", "#minecraft:copper_ores", "#minecraft:snow", "minecraft:gravel", "minecraft:suspicious_gravel",
		"minecraft:sandstone", "minecraft:red_sandstone", "minecraft:calcite", "minecraft:packed_ice", "minecraft:raw_iron_block",
		"minecraft:raw_copper_block", "minecraft:cinnabar", "minecraft:sulfur", "minecraft:potent_sulfur",
	)
	""" Blocks of the #minecraft:overworld_carver_replaceables tag, which 26.3 removed. """

	NETHER_REPLACEABLES: ClassVar[tuple[str, ...]] = (
		"#minecraft:base_stone_overworld", "#minecraft:base_stone_nether", "#minecraft:substrate_overworld",
		"#minecraft:nylium", "#minecraft:wart_blocks", "minecraft:soul_sand", "minecraft:soul_soil",
	)
	""" Blocks of the #minecraft:nether_carver_replaceables tag, which 26.3 removed. """

	dimensions: list[str]
	""" Dimensions to generate in, ex: ["minecraft:overworld", "stardust:cavern"]. """
	maximum_height: int = 70
	""" Maximum height of the vein """
	minimum_height: int | None = None
	""" None starts at the bottom of the overworld. """
	veins_per_region: float = 4
	""" The decimal part is the chance of one more vein: 1.2 is one vein plus a 20% chance of a second. """
	vein_size_logic: float = 0.4
	""" Higher means larger veins: 0.0 is a single block, 0.4 a small vein, 1.0 a large one. """
	provider: str | list[str] = field(default_factory=lambda: (
		list(CustomOreGeneration.OVERWORLD_REPLACEABLES) if minecraft_version_at_least((26, 3)) else "#minecraft:overworld_carver_replaceables"
	))
	""" Blocks or block tags the ore replaces. Defaults to the blocks vanilla carvers replace in the overworld. """
	vein_conditions: list[str] = field(default_factory=list[str])
	""" Checked once at the start of the vein, ex: ["if biome ~ ~ ~ #minecraft:is_badlands"]. """
	block_conditions: list[str] = field(default_factory=list[str])
	""" Checked at every block of the vein, ex: ["if block ~ ~-1 ~ #minecraft:terracotta"]. """
	placer_command: str = ""
	""" Execute subcommands ending with "run ...", placing one ore at ~ ~ ~. Empty places the custom block of the ore. """
	origin: SourceOrigin | None = field(default=None, init=False, repr=False, compare=False, metadata={"transient": True})
	""" Where this configuration was declared, so the sniffer plugin maps the generated functions back to it. """

	def __post_init__(self) -> None:
		if Mem.sniffer_enabled:
			from ...plugins import sniffer
			self.origin = sniffer.declaration_origin()
		if self.minimum_height is not None and self.minimum_height > self.maximum_height:
			stp.error("Custom ore generation 'minimum_height' must be less or equal to 'maximum_height'")
		if self.vein_size_logic < 0:
			stp.error("Custom ore generation 'vein_size_logic' must be >= 0")
		for condition in (*self.vein_conditions, *self.block_conditions):
			if not condition.startswith(("if ", "unless ")):
				stp.error(f"Custom ore generation condition '{condition}' must start with 'if ' or 'unless '")
		if not official_lib_used("smart_ore_generation"):
			stp.debug("Found custom ore generation, adding 'smart_ore_generation' dependency")

	@staticmethod
	def all_with_config(ore_configs: dict[str | Block, list[CustomOreGeneration]]) -> None:
		""" Generate the files of every configuration, several configurations of one ore getting numbered veins.

		```py
		CustomOreGeneration.all_with_config({
			"super_iron_ore": [
				CustomOreGeneration(dimensions=["minecraft:overworld"], minimum_height=0, maximum_height=50, veins_per_region=2),
			],
			"deepslate_super_iron_ore": [
				CustomOreGeneration(dimensions=["minecraft:overworld"], maximum_height=0, veins_per_region=2),
				CustomOreGeneration(dimensions=["stardust:cavern"], maximum_height=0, veins_per_region=8, vein_size_logic=0.8),
			],
		})
		```
		"""
		for ore, config_list in ore_configs.items():
			ore_id: str = ore.id if isinstance(ore, Block) else ore
			for i, gen_config in enumerate(config_list):
				gen_config.generate_files(ore_id, i if len(config_list) > 1 else None)

	def generate_files(self, custom_ore: str, number: int | None = None) -> None:
		""" Write the functions (and block tag if needed) generating this ore.

		Args:
			custom_ore: Custom block id, ex: "adamantium_ore"
			number:     Suffix telling apart several configurations of the same ore, ex: 1 for "adamantium_ore_1"
		"""
		from ...plugins import sniffer
		beautify_ore: str = custom_ore.replace("_", " ").title()
		vein_name: str = custom_ore + ("" if number is None else f"_{number}")
		vein_path: str = f"{Mem.ctx.project_id}:calls/smart_ore_generation/veins/{vein_name}"
		with sniffer.attribute_to(self):
			self.write_main_function(beautify_ore, vein_path)
			self.write_vein_function(beautify_ore, vein_path, self.resolve_provider(vein_name), self.resolve_placer_command(custom_ore))

	def write_main_function(self, beautify_ore: str, vein_path: str) -> None:
		""" Append to the generate_ores signal the calls to the vein function, once per vein. """
		dimensions_check: str = "".join(
			f"\nexecute if dimension {dimension} run scoreboard players set #dimension smart_ore_generation.data {index}"
			for index, dimension in enumerate(self.dimensions)
		)
		op_mini: str = (
			"scoreboard players operation #min_height smart_ore_generation.data = _OVERWORLD_BOTTOM smart_ore_generation.data"
			if self.minimum_height is None
			else f"scoreboard players set #min_height smart_ore_generation.data {self.minimum_height}"
		)
		content: str = f"""
# Generate {beautify_ore} (x{self.veins_per_region})
scoreboard players set #dimension smart_ore_generation.data -1{dimensions_check}
{op_mini}
scoreboard players set #max_height smart_ore_generation.data {self.maximum_height}
"""
		int_veins_per_region: int = int(self.veins_per_region)
		remaining_veins: float = self.veins_per_region - int_veins_per_region
		content += int_veins_per_region * f"execute if score #dimension smart_ore_generation.data matches 0.. run function {vein_path}\n"
		if remaining_veins > 0:
			content += (
				"execute if score #dimension smart_ore_generation.data matches 0.. if predicate "
				f"{stp.json_dump(loot_condition('minecraft:random_chance', chance=round(remaining_veins, 5)), max_level=0).strip()} run function {vein_path}\n"
			)
		write_function(f"{Mem.ctx.project_id}:calls/smart_ore_generation/generate_ores", content)

	def write_vein_function(self, beautify_ore: str, vein_path: str, provider: str, placer_command: str) -> None:
		""" Write the function picking the start of a vein and placing the ore around it.

		Args:
			provider:       Block or block tag the ore replaces, usable in `if block`
			placer_command: Execute subcommands ending with "run ...", placing one ore at ~ ~ ~
		"""
		content: str = """
# Try to find a random position adjacent to air in the region to generate the ore
function #smart_ore_generation:v1/slots/random_position
"""
		if self.vein_conditions:
			content += "\n# Cancel the vein unless every vein condition holds at its start\n"
		for condition in self.vein_conditions:
			negated: str = f"unless {condition.removeprefix('if ')}" if condition.startswith("if ") else f"if {condition.removeprefix('unless ')}"
			content += f"execute at @s {negated} run return fail\n"

		place: str = "".join(f"{condition} " for condition in self.block_conditions) + f"if block ~ ~ ~ {provider} {placer_command}"
		content += f"\n# Placing {beautify_ore} patch\nexecute at @s {place}\n"

		# Each radius step places the ore on a 3x3x3 grid of that spacing, the decimal part setting the first one
		radius: float = self.vein_size_logic % 1
		while self.vein_size_logic > 0 and radius <= self.vein_size_logic:
			for x, y, z in product(range(-1, 2), repeat=3):
				content += f"execute at @s positioned ~{x*radius} ~{y*radius} ~{z*radius} {place}\n"
			radius += 1
		write_function(vein_path, content)

	def resolve_provider(self, vein_name: str) -> str:
		""" Block or block tag usable in `if block`, writing a block tag when the provider is a list. """
		if isinstance(self.provider, str):
			return self.provider
		provider_path: str = f"smart_ore_generation/{vein_name}_provider"
		Mem.ctx.data[Mem.ctx.project_id].block_tags[provider_path] = set_json_encoder(BlockTag({"replace": False, "values": self.provider}))
		return f"#{Mem.ctx.project_id}:{provider_path}"

	def resolve_placer_command(self, custom_ore: str) -> str:
		""" The placer command, defaulting to placing the custom block, a stone variant skipping deepslate and a deepslate variant skipping stone. """
		if self.placer_command:
			return self.placer_command
		placer: str = f"run function {BlockFunctions(custom_ore).place_main}"
		if custom_ore.startswith("deepslate_") and custom_ore.removeprefix("deepslate_") in Mem.definitions:
			return f"unless block ~ ~ ~ minecraft:stone {placer}"
		if f"deepslate_{custom_ore}" in Mem.definitions:
			return f"unless block ~ ~ ~ minecraft:deepslate {placer}"
		return placer

