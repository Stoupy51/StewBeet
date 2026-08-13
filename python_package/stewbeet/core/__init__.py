
# Lazy imports (PEP 810), ignored before Python 3.15
from stouputils.lazy import ALWAYS_LAZY

__lazy_modules__ = ALWAYS_LAZY

# Imports
# JsonDict and the two classes below live outside the blocks sync_api.py owns, since a star import
# only ever reached them by accident. They stay listed here so the flat namespace keeps exposing them.
from stouputils.typing import JsonDict as JsonDict

from .__memory__ import (
	Mem as Mem,
)
from .cls._recipe_list import RecipeList as RecipeList
from .cls._utils import StMapping as StMapping
from .cls.block import (
	VANILLA_BLOCK_FOR_ORES as VANILLA_BLOCK_FOR_ORES,
	Block as Block,
	BlockAlternative as BlockAlternative,
	BlockHead as BlockHead,
	GrowingSeed as GrowingSeed,
	GrowingSeedLoot as GrowingSeedLoot,
	NoSilkTouchDrop as NoSilkTouchDrop,
	VanillaBlock as VanillaBlock,
)
from .cls.block_functions import (
	BlockFunctions as BlockFunctions,
)
from .cls.external_item import (
	ExternalItem as ExternalItem,
)
from .cls.ingredients import (
	ALL_RECIPES_TYPES as ALL_RECIPES_TYPES,
	CRAFTING_RECIPES_TYPES as CRAFTING_RECIPES_TYPES,
	FURNACES_RECIPES_TYPES as FURNACES_RECIPES_TYPES,
	OTHER_RECIPES_TYPES as OTHER_RECIPES_TYPES,
	SPECIAL_RECIPES_TYPES as SPECIAL_RECIPES_TYPES,
	UNUSED_RECIPES_TYPES as UNUSED_RECIPES_TYPES,
	Ingr as Ingr,
	Ingredient as Ingredient,
	IngrRepr as IngrRepr,
)
from .cls.item import (
	Item as Item,
)
from .cls.painting import (
	Painting as Painting,
	PaintingData as PaintingData,
)
from .cls.recipe import (
	AwakenedForgeRecipe as AwakenedForgeRecipe,
	BlastingRecipe as BlastingRecipe,
	CampfireCookingRecipe as CampfireCookingRecipe,
	CraftingShapedRecipe as CraftingShapedRecipe,
	CraftingShapelessRecipe as CraftingShapelessRecipe,
	HardcodedRecipe as HardcodedRecipe,
	PulverizingRecipe as PulverizingRecipe,
	Recipe as Recipe,
	RecipeBase as RecipeBase,
	SmeltingRecipe as SmeltingRecipe,
	SmithingTransformRecipe as SmithingTransformRecipe,
	SmithingTrimRecipe as SmithingTrimRecipe,
	SmokingRecipe as SmokingRecipe,
	StonecuttingRecipe as StonecuttingRecipe,
)
from .cls.resource import (
	Resource as Resource,
	existing_container as existing_container,
	resolve_pack as resolve_pack,
)
from .cls.resource_folder import (
	ResourceFolder as ResourceFolder,
)
from .cls.wiki_button import (
	WikiButton as WikiButton,
)
from .constants import (
	BLOCKS_WITH_INTERFACES as BLOCKS_WITH_INTERFACES,
	CATEGORY as CATEGORY,
	COMMON_SIGNAL as COMMON_SIGNAL,
	COMMON_SIGNAL_HIDDEN as COMMON_SIGNAL_HIDDEN,
	CUSTOM_BLOCK_ALTERNATIVE as CUSTOM_BLOCK_ALTERNATIVE,
	CUSTOM_BLOCK_HEAD as CUSTOM_BLOCK_HEAD,
	CUSTOM_BLOCK_HEAD_CUBE_RADIUS as CUSTOM_BLOCK_HEAD_CUBE_RADIUS,
	CUSTOM_BLOCK_VANILLA as CUSTOM_BLOCK_VANILLA,
	CUSTOM_BLOCKS_FOLDER as CUSTOM_BLOCKS_FOLDER,
	CUSTOM_ITEM_VANILLA as CUSTOM_ITEM_VANILLA,
	DOWNLOAD_VANILLA_ASSETS_RAW as DOWNLOAD_VANILLA_ASSETS_RAW,
	DOWNLOAD_VANILLA_ASSETS_SOURCE as DOWNLOAD_VANILLA_ASSETS_SOURCE,
	DOWNLOAD_VANILLA_ASSETS_SPECIAL_RAW as DOWNLOAD_VANILLA_ASSETS_SPECIAL_RAW,
	EXTERNAL_RECIPES_FOLDER as EXTERNAL_RECIPES_FOLDER,
	FACES as FACES,
	GROWING_SEED as GROWING_SEED,
	ITEMS_LOOT_FOLDER as ITEMS_LOOT_FOLDER,
	LATEST_MC_VERSION as LATEST_MC_VERSION,
	MORE_ASSETS_PACK_FORMATS as MORE_ASSETS_PACK_FORMATS,
	MORE_DATA_PACK_FORMATS as MORE_DATA_PACK_FORMATS,
	MORE_DATA_VERSIONS as MORE_DATA_VERSIONS,
	NO_SILK_TOUCH_DROP as NO_SILK_TOUCH_DROP,
	NOT_COMPONENTS as NOT_COMPONENTS,
	OVERRIDE_MODEL as OVERRIDE_MODEL,
	PAINTING_DATA as PAINTING_DATA,
	PLAYER_HEAD_FOLDER as PLAYER_HEAD_FOLDER,
	RESULT_OF_CRAFTING as RESULT_OF_CRAFTING,
	SEEDS_FOLDER as SEEDS_FOLDER,
	SIDES as SIDES,
	SMITHED_CRAFTER_COMMAND as SMITHED_CRAFTER_COMMAND,
	USED_FOR_CRAFTING as USED_FOR_CRAFTING,
	VANILLA_BLOCK as VANILLA_BLOCK,
	WIKI_COMPONENT as WIKI_COMPONENT,
	Conventions as Conventions,
	ConventionTags as ConventionTags,
)
from .definitions_helper import (
	INVERSE_SLOTS as INVERSE_SLOTS,
	SLOTS as SLOTS,
	UNIQUE_SLOTS_VALUES as UNIQUE_SLOTS_VALUES,
	CustomOreGeneration as CustomOreGeneration,
	DefaultOre as DefaultOre,
	EquipmentsConfig as EquipmentsConfig,
	VanillaEquipments as VanillaEquipments,
	add_energy_lore_to_definitions as add_energy_lore_to_definitions,
	add_item_model_component as add_item_model_component,
	add_item_name_and_lore_if_missing as add_item_name_and_lore_if_missing,
	add_private_custom_data_for_namespace as add_private_custom_data_for_namespace,
	add_recipes_for_all_dusts as add_recipes_for_all_dusts,
	add_recipes_for_dust as add_recipes_for_dust,
	add_smithed_ignore_vanilla_behaviours_convention as add_smithed_ignore_vanilla_behaviours_convention,
	clean_record_name as clean_record_name,
	create_energy_lore as create_energy_lore,
	create_gradient_text as create_gradient_text,
	export_all_definitions_to_json as export_all_definitions_to_json,
	format_attributes as format_attributes,
	format_energy_number as format_energy_number,
	generate_custom_records as generate_custom_records,
	generate_everything_about_these_materials as generate_everything_about_these_materials,
	generate_everything_about_this_material as generate_everything_about_this_material,
	gradient_text_to_string as gradient_text_to_string,
	rainbow_gradient_text as rainbow_gradient_text,
	set_manual_components as set_manual_components,
)
from .placeholder_context import (
	PLACEHOLDER_CTX as PLACEHOLDER_CTX,
	create_placeholder_context as create_placeholder_context,
)
from .utils.equation import (
	MACRO_RE as MACRO_RE,
	AnyOperator as AnyOperator,
	BaseEquation as BaseEquation,
	ScoreboardEquation as ScoreboardEquation,
	StorageEquation as StorageEquation,
	get_comment_token as get_comment_token,
	get_scoreboard_operation as get_scoreboard_operation,
	get_scoreboard_set as get_scoreboard_set,
	is_macro_argument as is_macro_argument,
)
from .utils.fonts import (
	DEFAULT_ISO_RENDERS_PATH as DEFAULT_ISO_RENDERS_PATH,
	FONT_MAX_LEVEL as FONT_MAX_LEVEL,
	HUE_BUCKETS as HUE_BUCKETS,
	MAX_GLYPH_SIZE as MAX_GLYPH_SIZE,
	MIN_SATURATION as MIN_SATURATION,
	MIN_VALUE as MIN_VALUE,
	NO_RECOLOR_VALUES as NO_RECOLOR_VALUES,
	GlyphAllocator as GlyphAllocator,
	Pixel as Pixel,
	SpliceLayout as SpliceLayout,
	SpliceTile as SpliceTile,
	add_border as add_border,
	build_model_resolver_queue as build_model_resolver_queue,
	careful_resize as careful_resize,
	collect_used_vanilla_items as collect_used_vanilla_items,
	copy_painting_textures as copy_painting_textures,
	download_item as download_item,
	download_vanilla_textures as download_vanilla_textures,
	ensure_item_images as ensure_item_images,
	ensure_rgba_color as ensure_rgba_color,
	generate_all_iso_renders as generate_all_iso_renders,
	get_dominant_color as get_dominant_color,
	get_font as get_font,
	get_pixels as get_pixels,
	glyph_advance as glyph_advance,
	iso_renders_path as iso_renders_path,
	item_image_path as item_image_path,
	iter_fonts as iter_fonts,
	lighten_color as lighten_color,
	merge_font_providers as merge_font_providers,
	opaque_width as opaque_width,
	parse_color as parse_color,
	plan_splice as plan_splice,
	recolor_image as recolor_image,
	resolve_item_image as resolve_item_image,
	run_model_resolver as run_model_resolver,
	uses_font as uses_font,
	validate_font_providers as validate_font_providers,
	write_font_from_allocator as write_font_from_allocator,
)
from .utils.io import (
	EXACT_JSON_TYPES as EXACT_JSON_TYPES,
	MODEL_CACHE_MAX_AGE as MODEL_CACHE_MAX_AGE,
	MODEL_CACHE_MIN_SIZE as MODEL_CACHE_MIN_SIZE,
	MODEL_CACHE_NAME as MODEL_CACHE_NAME,
	JsonFileT as JsonFileT,
	McFunction as McFunction,
	ModelSerializationCache as ModelSerializationCache,
	active_model_cache as active_model_cache,
	convert_to_serializable as convert_to_serializable,
	read_function as read_function,
	set_json_encoder as set_json_encoder,
	set_model_encoder as set_model_encoder,
	setup_model_cache as setup_model_cache,
	super_merge_dict as super_merge_dict,
	texture_mcmeta as texture_mcmeta,
	to_plain_builtin as to_plain_builtin,
	write_advancement as write_advancement,
	write_function as write_function,
	write_function_tag as write_function_tag,
	write_load_file as write_load_file,
	write_scheduled_function as write_scheduled_function,
	write_tag as write_tag,
	write_tick_file as write_tick_file,
	write_unload_file as write_unload_file,
	write_versioned_function as write_versioned_function,
)
from .utils.loot_table import (
	result_count_to_suffix as result_count_to_suffix,
)
from .utils.sounds import (
	add_sound as add_sound,
)
from .utils.text_component import (
	CLOSERS as CLOSERS,
	Replacement as Replacement,
	TextComponent as TextComponent,
	apply_replacements as apply_replacements,
	find_enclosing_object as find_enclosing_object,
	item_id_to_name as item_id_to_name,
	item_id_to_text_component as item_id_to_text_component,
	iter_data_text_files as iter_data_text_files,
	text_component_to_str as text_component_to_str,
)

