
# Lazy imports (PEP 810), ignored before Python 3.15
from stouputils.lazy import ALWAYS_LAZY

__lazy_modules__ = ALWAYS_LAZY

# Imports
from beet.core.utils import TextComponent

from ..__memory__ import Mem


def format_energy_number(number: int) -> str:
	""" Formats a number into a string with appropriate unit suffix (k, M, G, T).

	Args:
		number (int): The number to format
	Returns:
		str: Formatted string with unit suffix, ex: 12000 -> "12 M", 1200 -> "1200 k"
	"""
	if number < 9999:
		return f"{number} k"
	elif number < 9999999:
		return f"{number/1000:.0f} M"
	elif number < 9999999999:
		return f"{number/1000000:.0f} G"
	else:
		return f"{number/1000000000:.0f} T"

def create_energy_lore(energy_data: dict[str, int]) -> TextComponent:
	""" Creates lore entries for energy-related blocks based on their energy data.

	Args:
		energy_data (dict): Dictionary containing energy configuration values
	Returns:
		TextComponent: Formatted text component with energy lore
	"""
	# Determine if this is a battery (no usage/generation) or a cable (only transfer)
	is_battery: bool = "max_storage" in energy_data and "usage" not in energy_data and "generation" not in energy_data
	is_cable: bool = "transfer" in energy_data and "max_storage" not in energy_data

	# Create the lore config
	lore_config: dict[str, tuple[str, str]] = {
		"generation": ("Energy Generation", "W"),
		"usage": ("Power Usage", "W"),
		"max_storage": ("Energy Storage" if is_battery else "Energy Buffer", "J"),
		"transfer": ("Transfer Speed" if is_cable else "Energy Transfer", "W")
	}

	# Create the lore entries
	lore: TextComponent = []
	for key, (label, unit) in lore_config.items():
		if key in energy_data:
			lore.append({
				"text": f"[{label}: {format_energy_number(energy_data[key])}{unit}]",
				"italic": False,
				"color": "gray"
			})

	return lore

def add_energy_lore_to_definitions():
	""" Adds energy-related lore to definitions based on their custom data. """
	for data in Mem.definitions.values():
		data = data.components
		if "energy" in data.get("custom_data", {}):
			data["lore"] = data.get("lore", []) + create_energy_lore(data["custom_data"]["energy"])

