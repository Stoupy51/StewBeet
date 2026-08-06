"""Text-component optimization (merge adjacent compounds, strip nested events).

Ported as-is from the v1 ``book_optimizer``: pure functions with no global state.
"""

# Imports
from typing import cast

from beet.core.utils import TextComponent
from stouputils.typing import JsonDict


def optimize_element(content: TextComponent) -> TextComponent:
	""" Optimize the page content by merging compounds when possible.

	>>> optimize_element(["","",{"text": "A", "color": "red", "bold": True, "shadow_color": [0,0,0,0]}])
	['', {'text': 'A', 'color': 'red', 'bold': True, 'shadow_color': [0, 0, 0, 0]}]
	"""
	# If dict, optimize the values
	if isinstance(content, dict):
		if not any(x in content for x in ["text", "translate", "contents"]):
			return content
		content = content.copy()
		new_component: TextComponent = {}
		for key, value in content.items():
			new_component[key] = optimize_element(value)
		return new_component

	# If not a list, just return
	if not isinstance(content, list):
		return content

	# If list with only one element, return the element
	if len(content) == 1:
		return content[0]

	# For each compound
	new_content: list[TextComponent] = []
	for i, compound in enumerate(content):
		compound = cast(TextComponent, compound)

		# Case where it's a integer => always add it
		if isinstance(compound, int):
			new_content.append(compound)

		# If it's a list or the first compound, add it
		elif isinstance(compound, list) or i == 0:
			new_content.append(optimize_element(compound))

		else:
			# If the current is a dict with only "text" key, transform it to a string
			if isinstance(compound, dict) and len(compound) == 1 and "text" in compound:
				compound = cast(TextComponent, compound["text"])

			# For checks
			compound_without_text = cast(JsonDict, compound.copy() if isinstance(compound, dict) else compound)
			previous_without_text = cast(JsonDict, new_content[-1].copy() if isinstance(new_content[-1], dict) else new_content[-1])
			if isinstance(compound, dict) and isinstance(new_content[-1], dict):
				compound_without_text.pop("text", None)
				previous_without_text.pop("text", None)

			# If the previous compound is the same as the current one, merge the text
			if str(compound_without_text) == str(previous_without_text):
				if isinstance(new_content[-1], str):
					new_content[-1] += str(compound)
				elif isinstance(new_content[-1], dict):
					new_content[-1]["text"] += cast(JsonDict, compound)["text"]

			# Always add break lines to the previous part (string of only break lines)
			elif isinstance(compound, str) and all(c == "\n" for c in compound):
				if isinstance(new_content[-1], str):
					new_content[-1] += compound
				elif isinstance(new_content[-1], dict):
					new_content[-1]["text"] += compound

			# Always merge two strings
			elif isinstance(compound, str) and isinstance(new_content[-1], str):
				new_content[-1] += compound

			# Otherwise, just add the optimized compound
			else:
				new_content.append(optimize_element(compound))

	return new_content


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
