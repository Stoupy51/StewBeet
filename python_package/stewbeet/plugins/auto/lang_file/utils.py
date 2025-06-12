
# Imports
import re

from beet import Advancement, Context, Function, ItemModifier, LootTable
from stouputils.decorators import simple_cache

# Prepare lang dictionary and lang_format function
lang: dict[str, str] = {}

# Regex pattern for text extraction
TEXT_RE: re.Pattern = re.compile(
	r'''
	(?P<prefix>["']?text["']?\s*:\s*)             # Match the "text": part
	(?P<quote>["'])                               # Opening quote for value
	(?P<value>(?:\\.|[^\\])*?)                    # The value, handling escapes
	(?P=quote)                                    # Closing quote
	''', re.VERBOSE
)


# Functions
def extract_texts(content: str) -> list[tuple[str, int, int, str]]:
	""" Extract all text values from content using regex patterns.

	Args:
		content (str): The content to extract text from.

	Returns:
		list[tuple[str, int, int, str]]: List of tuples containing (text, start_pos, end_pos, quote_char)
	"""
	matches: list[tuple[str, int, int, str]] = []
	for match in TEXT_RE.finditer(content):
		start, end = match.span()
		value: str = match.group("value")
		quote: str = match.group("quote")
		matches.append((value, start, end, quote))
	return matches


@simple_cache
def lang_format(ctx: Context, text: str) -> tuple[str, str]:
	""" Format text into a valid lang key.

	Args:
		text (str): The text to format.

	Returns:
		tuple[str, str]: The formatted key and a simplified version of it.
	"""
	text = re.sub(r"[./:]", "_", text)   # Clean up all unwanted chars
	text = re.sub(r"[^a-zA-Z0-9 _-]", "", text).lower()
	alpha_num: str = re.sub(r"[ _-]+", "_", text).strip("_")[:64]
	key: str = f"{ctx.project_id}.{alpha_num}" if not alpha_num.startswith(ctx.project_id) else alpha_num
	return key, re.sub(r"[._]", "", alpha_num)


def handle_file(ctx: Context, file: str, content: Function | LootTable | ItemModifier | Advancement) -> None:
	""" Process a file to extract and replace text with lang keys.

	Args:
		ctx      (Context):              The context containing project information.
		file     (str):                  The path to the file being processed.
		content  (Function | LootTable): The content of the file to process.

	Returns:
		None: The function modifies the content in place.
	"""
	# Read content from supported beet types
	#	Function, LootTable, ItemModifier or Advancement
	if isinstance(content, Function) or isinstance(content, LootTable) \
		or isinstance(content, ItemModifier) or isinstance(content, Advancement):
		string: str = content.text
	else:
		raise ValueError(f"Unsupported content type: {type(content)}")

	# Extract all text matches
	matches: list[tuple[str, int, int, str]] = extract_texts(string)

	# Process matches in reverse to avoid position shifting
	for text, start, end, quote in reversed(matches):
		# Clean text and skip if not useful
		clean_text: str = text.replace("\\n", "\n").replace("\\", "")
		if not any(c.isalnum() for c in clean_text):
			continue

		key_for_lang, verif = lang_format(ctx, clean_text)
		if len(verif) < 3 or not verif.isalnum() or "\\u" in text or "$(" in text:
			continue

		if key_for_lang not in lang:
			lang[key_for_lang] = clean_text
		elif lang[key_for_lang] != clean_text:
			continue

		# Replace whole "text": "value" with "translate": "key"
		new_fragment: str = f'{quote}translate{quote}: {quote}{key_for_lang}{quote}'
		string = string[:start] + new_fragment + string[end:]

	# Write the new content back to the appropriate context data
	if isinstance(content, Function):
		ctx.data.functions[file] = Function(string)
	elif isinstance(content, LootTable):
		ctx.data.loot_tables[file] = LootTable(string)
	elif isinstance(content, ItemModifier):
		ctx.data.item_modifiers[file] = ItemModifier(string)
	elif isinstance(content, Advancement):
		ctx.data.advancements[file] = Advancement(string)

