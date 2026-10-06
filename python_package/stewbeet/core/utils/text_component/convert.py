
# Lazy imports (PEP 810), ignored before Python 3.15
from stouputils.lazy import ALWAYS_LAZY

__lazy_modules__ = ALWAYS_LAZY

# Imports
import stouputils as stp
from beet.core.utils import TextComponent
from stouputils.typing import JsonDict

from ...__memory__ import Mem


# Utility functions
@stp.simple_cache(method="str")
def text_component_to_str(tc: TextComponent) -> str:
	""" Convert a TextComponent to the plain string it displays.

	>>> text_component_to_str("hello")
	'hello'
	>>> text_component_to_str(["hello", " ", "world"])
	'hello world'
	>>> text_component_to_str({"text": "Hello"})
	'Hello'
	>>> text_component_to_str({"text": "Hello", "extra": [{"text": " World"}]})
	'Hello World'
	>>> text_component_to_str({"text": "A", "extra": ["B", {"text": "C"}]})
	'ABC'
	>>> text_component_to_str({"color": "red"})
	''
	"""
	if isinstance(tc, str):
		return tc
	if isinstance(tc, list):
		result: str = ""
		for part in tc:
			result += text_component_to_str(part)
		return result
	result: str = ""
	if tc.get("text"):
		result += tc["text"]
	if tc.get("extra"):
		for extra in tc["extra"]:
			result += text_component_to_str(extra)
	return result

def item_id_to_text_component(item_id: str, use_default: bool = True) -> TextComponent:
	""" Get the TextComponent from an item id

	Args:
		item_id:     The item id, ex: "minecraft:stick" or "iyc:adamantium_ingot"
		use_default: Whether to use the default prettified string if no TextComponent is found
	Returns:
		str: The TextComponent of the item, ex: "Stick" or {"text":"Adamantium Ingot"}
	"""
	if ":" not in item_id:
		item_id = f"{Mem.ctx.project_id}:{item_id}"

	# The project's own definition first, then an external one
	ns, id = item_id.split(":")
	from ...cls.item import Item
	sources: list[str] = [id] if ns == Mem.ctx.project_id and id in Mem.definitions else []
	sources += [item_id] if item_id in Mem.external_definitions else []
	for source in sources:
		if name := components_name(Item.from_id(source).components):
			return name

	# Default: prettify the id
	if use_default:
		return id.replace("_", " ").title()
	return ""


def components_name(components: JsonDict) -> TextComponent:
	""" The name an item's components give it, a music disc's record name first, "" when they give none. """
	if "jukebox_playable" in components:
		smithed_record: JsonDict = components.get("custom_data", {}).get("smithed", {}).get("dict", {}).get("record", {})
		if smithed_record.get("item_name"):
			return smithed_record["item_name"]
	return next((components[component] for component in ("item_name", "custom_name") if components.get(component)), "")

def item_id_to_name(item_id: str) -> str:
	""" Get the name from an item id

	Args:
		item_id: The item id, ex: "minecraft:stick" or "iyc:adamantium_ingot"
	Returns:
		str: The name of the item, ex: "Stick" or "Adamantium Ingot"
	"""
	return text_component_to_str(item_id_to_text_component(item_id))

