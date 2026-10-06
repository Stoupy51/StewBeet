""" 🧱 Helpers filling item definitions: missing components, equipments, materials, records, ores and SimplEnergy items. """
# Lazy imports (PEP 810), ignored before Python 3.15
from stouputils.lazy import ALWAYS_LAZY

__lazy_modules__ = ALWAYS_LAZY

# Imports
from .completion import (
	add_item_model_component as add_item_model_component,
	add_item_name_and_lore_if_missing as add_item_name_and_lore_if_missing,
	add_private_custom_data_for_namespace as add_private_custom_data_for_namespace,
	add_smithed_ignore_vanilla_behaviours_convention as add_smithed_ignore_vanilla_behaviours_convention,
	export_all_definitions_to_json as export_all_definitions_to_json,
	set_manual_components as set_manual_components,
)
from .equipments import (
	INVERSE_SLOTS as INVERSE_SLOTS,
	SLOTS as SLOTS,
	UNIQUE_SLOTS_VALUES as UNIQUE_SLOTS_VALUES,
	DefaultOre as DefaultOre,
	EquipmentsConfig as EquipmentsConfig,
	VanillaEquipments as VanillaEquipments,
	format_attributes as format_attributes,
)
from .materials import (
	ARMOR as ARMOR,
	ARMOR_MATERIALS as ARMOR_MATERIALS,
	TOOLS as TOOLS,
	Gear as Gear,
	Material as Material,
	add_recipes_for_all_dusts as add_recipes_for_all_dusts,
	add_recipes_for_dust as add_recipes_for_dust,
	copy_armor_layer as copy_armor_layer,
	dust_recipes as dust_recipes,
	generate_everything_about_these_materials as generate_everything_about_these_materials,
	generate_everything_about_this_material as generate_everything_about_this_material,
	ingredient_recipes as ingredient_recipes,
	refined_recipes as refined_recipes,
	write_armor as write_armor,
	write_equipment_asset as write_equipment_asset,
	write_ingredient as write_ingredient,
	write_placeable as write_placeable,
	write_tool as write_tool,
)
from .records import (
	clean_record_name as clean_record_name,
	generate_custom_records as generate_custom_records,
	records_to_generate as records_to_generate,
	register_record_song as register_record_song,
)
from .simplenergy import (
	add_energy_lore_to_definitions as add_energy_lore_to_definitions,
	create_energy_lore as create_energy_lore,
	format_energy_number as format_energy_number,
)
from .smart_ore_generation import (
	CustomOreGeneration as CustomOreGeneration,
)
from .text import (
	create_gradient_text as create_gradient_text,
	gradient_text_to_string as gradient_text_to_string,
	rainbow_gradient_text as rainbow_gradient_text,
)

