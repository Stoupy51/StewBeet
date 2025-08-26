
# Imports
from typing import cast

from beet.core.utils import JsonDict, TextComponent


# Page optimizer
def optimize_element(content: TextComponent) -> TextComponent:
	""" Optimize the page content by merging compounds when possible
	Args:
		content (TextComponent): The page content
	Returns:
		TextComponent: The optimized page content
	"""
	# If dict, optimize the values
	if isinstance(content, dict):
		if not any(x in content for x in ["text", "translate", "contents"]):	# If not a text, translate or contents, just return
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
		if isinstance(compound, list) or i == 0:
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

				# If the previous compound is a text, merge the text
				if isinstance(new_content[-1], str):
					new_content[-1] += str(compound)

				# If the previous compound is a dict, merge the dict
				elif isinstance(new_content[-1], dict):
					new_content[-1]["text"] += cast(JsonDict, compound)["text"]

			# Always add break lines to the previous part (if the text is a string containing only break lines)
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

	# Return
	return new_content

# Remove events recursively
EVENTS: list[str] = ["hover_event", "click_event"]
def remove_events(compound: TextComponent) -> None:
	""" Remove events from a compound recursively
	Args:
		compound (dict): The compound
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

# Function
def optimize_book(book_content: TextComponent) -> TextComponent:
	""" Optimize the book content by associating compounds when possible
	Args:
		book_content (TextComponent): The book content
	Returns:
		TextComponent: The optimized book content
	"""
	if not isinstance(book_content, list):
		book_content = [book_content]

	# For each page, remove events if useless (in an item Lore for example)
	for page in book_content:
		for compound in page:
			if isinstance(compound, list):
				compound_list = cast(list[TextComponent], compound)
			else:
				compound_list = [compound]
			for e in compound_list:
				if isinstance(e, dict):
					e = cast(JsonDict, e)
					for event_type in EVENTS:
						if e.get(event_type):
							remove_events(e[event_type])  # Remove all events below the first event

	# For each page, optimize the array
	return optimize_element(book_content)

