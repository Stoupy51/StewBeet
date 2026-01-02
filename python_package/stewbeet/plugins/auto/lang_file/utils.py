
# Imports
import re

import stouputils as stp
from beet import Context, TextFileBase

# Prepare lang dictionary and lang_format function
lang: dict[str, str] = {}

# Regex pattern for text extraction
TEXT_RE: re.Pattern[str] = re.compile(
	r'''
	(?P<key_quote>["'])?text(?(key_quote)(?P=key_quote))  # Match "text", 'text', or text
	\s*:\s*                                       # Match the colon and spaces
	(?P<quote>["'])                               # Opening quote for value
	(?P<value>(?:\\.|[^\\])*?)                    # The value, handling escapes
	(?P=quote)                                    # Closing quote
	''', re.VERBOSE
)


# Functions
def extract_texts(content: str) -> list[tuple[str, int, int, str, str | None]]:
	""" Extract all text values from content using regex patterns.

	Args:
		content (str): The content to extract text from.

	Returns:
		list[tuple[str, int, int, str, str | None]]: List of tuples containing (text, start_pos, end_pos, value_quote_char, key_quote_char)

	Examples:
		>>> matches = extract_texts('{"text":"Hello World"}')
		>>> len(matches)
		1
		>>> matches[0][0]  # Extract the text value
		'Hello World'
		>>> matches[0][3]  # Extract the value quote character
		'"'
		>>> matches[0][4]  # Extract the key quote character
		'"'

		>>> matches = extract_texts('{text:"Hey dude!!!!"}')
		>>> matches[0][0]
		'Hey dude!!!!'
		>>> matches[0][4] is None  # No quotes around 'text' key
		True

		>>> matches = extract_texts("{'text':'Single quotes'}")
		>>> matches[0][0]
		'Single quotes'
		>>> matches[0][3]
		"'"
	"""
	matches: list[tuple[str, int, int, str, str | None]] = []
	for match in TEXT_RE.finditer(content):
		start, end = match.span()
		value: str = match.group("value")
		quote: str = match.group("quote")
		key_quote: str | None = match.group("key_quote")
		matches.append((value, start, end, quote, key_quote))
	return matches


@stp.simple_cache
def lang_format(ctx: Context, text: str) -> tuple[str, str]:
	""" Format text into a valid lang key.

	Args:
		text (str): The text to format.

	Returns:
		tuple[str, str]: The formatted key and a simplified version of it.

	Examples:
		>>> from typing import NamedTuple
		>>> FakeContext = NamedTuple('FakeContext', [('project_id', str)])
		>>> ctx = FakeContext(project_id='my_project')
		>>> key, simplified = lang_format(ctx, 'Hello World')
		>>> key
		'my_project.hello_world'
		>>> simplified
		'helloworld'

		>>> key, simplified = lang_format(ctx, 'Test/Path:Name')
		>>> key
		'my_project.test_path_name'

		>>> key, simplified = lang_format(ctx, 'Special!@#$%Characters')
		>>> key
		'my_project.specialcharacters'

		>>> key, simplified = lang_format(ctx, 'a' * 100)  # Test truncation
		>>> len(simplified) <= 64
		True
	"""
	text = re.sub(r"[./:]", "_", text)   # Clean up all unwanted chars
	text = re.sub(r"[^a-zA-Z0-9 _-]", "", text).lower()
	alpha_num: str = re.sub(r"[ _-]+", "_", text).strip("_")[:64]
	key: str = f"{ctx.project_id}.{alpha_num}" if not alpha_num.startswith(ctx.project_id) else alpha_num
	return key, re.sub(r"[._]", "", alpha_num)


def handle_file(ctx: Context, content: TextFileBase[str] | None) -> None:
	""" Process a file to extract and replace text with lang keys.

	Args:
		ctx      (Context):      The context containing project information.
		content  (TextFileBase): The content of the file to process.

	Returns:
		None: The function modifies the content in place.
	"""
	# Read content from supported beet types
	#	Function, LootTable, ItemModifier or Advancement
	if isinstance(content, TextFileBase):
		string: str = str(content.text)
	else:
		raise ValueError(f"Unsupported content type: {type(content)}")

	# Extract all text matches, str | None]] = extract_texts(string)
	matches: list[tuple[str, int, int, str, str | None]] = extract_texts(string)

	# Process matches in reverse to avoid position shifting
	for text, start, end, quote, key_quote in reversed(matches):
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

		# Replace whole "text": "value" with "translate": "key" (preserving quote style)
		translate_key = f'{key_quote}translate{key_quote}' if key_quote else 'translate'
		new_fragment: str = f'{translate_key}: {quote}{key_for_lang}{quote}'
		string = string[:start] + new_fragment + string[end:]

	# Update the content
	if string != str(content.text):
		content.text = string

