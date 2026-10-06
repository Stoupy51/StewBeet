"""Text-component optimization (merge adjacent compounds, strip nested events)."""

# Lazy imports (PEP 810), ignored before Python 3.15
from stouputils.lazy import ALWAYS_LAZY

__lazy_modules__ = ALWAYS_LAZY

# Imports
from typing import cast

from beet.core.utils import TextComponent
from stouputils.typing import JsonDict


def optimize_element(content: TextComponent) -> TextComponent:
	""" Optimize the page content by merging compounds when possible.

	>>> optimize_element(["","",{"text": "A", "color": "red", "bold": True, "shadow_color": [0,0,0,0]}])
	['', {'text': 'A', 'color': 'red', 'bold': True, 'shadow_color': [0, 0, 0, 0]}]
	"""
	if isinstance(content, dict):
		if not any(x in content for x in ["text", "translate", "contents"]):
			return content
		return {key: optimize_element(value) for key, value in content.items()}
	if not isinstance(content, list):
		return content
	if len(content) == 1:
		return content[0]

	new_content: list[TextComponent] = []
	for i, compound in enumerate(content):
		compound = cast(TextComponent, compound)
		if isinstance(compound, int):
			new_content.append(compound)
		elif isinstance(compound, list) or i == 0:
			new_content.append(optimize_element(compound))
		else:
			merge_into(new_content, compound)
	return new_content


def merge_into(new_content: list[TextComponent], compound: TextComponent) -> None:
	""" Append a compound, merged into the last one when both differ only by their text, or when it is only line breaks.

	A string merges into a string. A compound merging into one that is neither a string nor a dict is dropped.
	"""
	# A dict holding nothing but its text is that text
	if isinstance(compound, dict) and len(compound) == 1 and "text" in compound:
		compound = cast(TextComponent, compound["text"])
	previous: TextComponent = new_content[-1]
	if same_style(compound, previous):
		if isinstance(previous, str):
			new_content[-1] = previous + str(compound)
		elif isinstance(previous, dict):
			previous["text"] += cast(JsonDict, compound)["text"]
	elif isinstance(compound, str) and all(c == "\n" for c in compound):
		if isinstance(previous, str):
			new_content[-1] = previous + compound
		elif isinstance(previous, dict):
			previous["text"] += compound
	elif isinstance(compound, str) and isinstance(previous, str):
		new_content[-1] = previous + compound
	else:
		new_content.append(optimize_element(compound))


def same_style(compound: TextComponent, previous: TextComponent) -> bool:
	""" Whether two compounds are the same apart from their text, two dicts being compared without it. """
	compound_without_text = cast(JsonDict, compound.copy() if isinstance(compound, dict) else compound)
	previous_without_text = cast(JsonDict, previous.copy() if isinstance(previous, dict) else previous)
	if isinstance(compound, dict) and isinstance(previous, dict):
		compound_without_text.pop("text", None)
		previous_without_text.pop("text", None)
	return str(compound_without_text) == str(previous_without_text)


# Remove events recursively
EVENTS: list[str] = ["hover_event", "click_event"]


def remove_events(compound: TextComponent) -> None:
	""" Remove hover/click events from a compound recursively (in place).

	>>> component = {"text": "a", "click_event": {"action": "open_url"}, "extra": [{"text": "b", "hover_event": {}}]}
	>>> remove_events(component)
	>>> component
	{'text': 'a', 'extra': [{'text': 'b'}]}
	"""
	if not isinstance(compound, dict):
		if isinstance(compound, list):
			for element in compound:
				remove_events(element)
		return
	for key in EVENTS:
		if key in compound:
			del compound[key]
	for value in compound.values():
		remove_events(value)

