
# Imports
import re

import stouputils as stp

from ..utils.io import FILES_TO_WRITE

# Regex pattern for text extraction
TEXT_RE: re.Pattern = re.compile(
	r'''
	(?P<prefix>["']?text["']?\s*:\s*)             # Match the "text": part
	(?P<quote>["'])                               # Opening quote for value
	(?P<value>(?:\\.|[^\\])*?)                    # The value, handling escapes
	(?P=quote)                                    # Closing quote
	''', re.VERBOSE
)


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


# Main function
def main(config: dict):
	# Prepare lang dictionary and lang_format function
	lang: dict[str, str] = {}

	@stp.simple_cache()
	def lang_format(text: str) -> tuple[str, str]:
		""" Format text into a valid lang key.

		Args:
			text (str): The text to format.

		Returns:
			tuple[str, str]: The formatted key and a simplified version of it.
		"""
		text = re.sub(r"[./:]", "_", text)   # Clean up all unwanted chars
		text = re.sub(r"[^a-zA-Z0-9 _-]", "", text).lower()
		alpha_num: str = re.sub(r"[ _-]+", "_", text).strip("_")[:64]
		namespace: str = config['namespace']
		key: str = f"{namespace}.{alpha_num}" if not alpha_num.startswith(namespace) else alpha_num
		return key, re.sub(r"[._]", "", alpha_num)

	def handle_file(file: str, content: str):
		# Extract all text matches
		matches: list[tuple[str, int, int, str]] = extract_texts(content)

		# Process matches in reverse to avoid position shifting
		for text, start, end, quote in reversed(matches):
			# Clean text and skip if not useful
			clean_text: str = text.replace("\\n", "\n").replace("\\", "")
			if not any(c.isalnum() for c in clean_text):
				continue

			key_for_lang, verif = lang_format(clean_text)
			if len(verif) < 3 or not verif.isalnum() or "\\u" in text or "$(" in text:
				continue

			if key_for_lang not in lang:
				lang[key_for_lang] = clean_text
			elif lang[key_for_lang] != clean_text:
				continue

			# Replace whole "text": "value" with "translate": "key"
			new_fragment: str = f'{quote}translate{quote}: {quote}{key_for_lang}{quote}'
			content = content[:start] + new_fragment + content[end:]

		# Write the new content to the file
		FILES_TO_WRITE[file] = content

	# Show progress of the handle_file function
	stp.multithreading(handle_file, FILES_TO_WRITE.items(), use_starmap=True, desc="Generating lang file", max_workers=min(32, len(FILES_TO_WRITE)))

	# Sort the lang dictionary (by value)
	lang = dict(sorted(lang.items(), key=lambda x: x[1]))

	# Write the lang file
	path: str = f"{config['build_resource_pack']}/assets/minecraft/lang/en_us.json"
	FILES_TO_WRITE[path] = stp.super_json_dump(lang)

