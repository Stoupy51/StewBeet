""" ⚡ Support for SimplEnergy's energy library: cables, batteries, servo mechanisms, wrench and energy balancing. """
# Lazy imports (PEP 810), ignored before Python 3.15
from stouputils.lazy import ALWAYS_LAZY

__lazy_modules__ = ALWAYS_LAZY

# Imports
from beet import Context  # pyright: ignore[reportUnusedImport] # noqa: F401

# Mem is core's, but every pack built on this contrib reaches for it right beside the helpers below
from ...core import Mem as Mem
from .balancing import (
	setup_energy_balancing as setup_energy_balancing,
)
from .batteries import (
	keep_energy_for_batteries as keep_energy_for_batteries,
)
from .cables import (
	ENERGY_CABLE_SIDES as ENERGY_CABLE_SIDES,
	ENERGY_CABLE_TILES as ENERGY_CABLE_TILES,
	ITEM_CABLE_SIDES as ITEM_CABLE_SIDES,
	ITEM_CABLE_TEXTURES as ITEM_CABLE_TEXTURES,
	EnergyCableSide as EnergyCableSide,
	copy_block_texture as copy_block_texture,
	energy_cable_centre_face as energy_cable_centre_face,
	energy_cable_elements as energy_cable_elements,
	energy_cable_variant as energy_cable_variant,
	energy_cables_models as energy_cables_models,
	item_cables_models as item_cables_models,
	model_dispatch as model_dispatch,
	register_servo_models as register_servo_models,
	register_servo_textures as register_servo_textures,
	servo_mechanisms_models as servo_mechanisms_models,
	servo_toggle as servo_toggle,
	write_cable_update as write_cable_update,
	write_item_cable_variant as write_item_cable_variant,
	write_servo_functions as write_servo_functions,
)
from .energy_lib_calls import (
	ENERGY_DIRECTIONS as ENERGY_DIRECTIONS,
	HORIZONTAL_FACINGS as HORIZONTAL_FACINGS,
	RELATIVE_FACES as RELATIVE_FACES,
	cable_refusals as cable_refusals,
	insert_lib_calls as insert_lib_calls,
	write_energy_calls as write_energy_calls,
)
from .gui import (
	GuiTranslation as GuiTranslation,
	setup_gui_in_resource_packs as setup_gui_in_resource_packs,
)
from .wrench import (
	setup_wrench as setup_wrench,
)

