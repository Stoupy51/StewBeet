
# Lazy imports (PEP 810), ignored before Python 3.15
from stouputils.lazy import ALWAYS_LAZY

__lazy_modules__ = ALWAYS_LAZY

# Imports
import re

import pyperclip
import stouputils as stp
from stouputils.typing import CallableAny, JsonDict


# Configuration
def validate_config(pmc_config: dict[str, str]) -> str:
	""" Validate PlanetMinecraft configuration

	Args:
		pmc_config (dict[str, str]): Configuration for the PlanetMinecraft project
	Returns:
		str: Project url on PlanetMinecraft
	"""
	required_keys = ["project_url", "version"]
	error_messages = {
		"project_url": "url of the project on PlanetMinecraft",
		"version": "version of the project",
	}

	for key in required_keys:
		if key not in pmc_config:
			raise ValueError(f"The pmc_config dictionary must contain a '{key}' key, which is the {error_messages[key]}")

	return pmc_config["project_url"]

def table_to_bbcode(match: re.Match[str]) -> str:
	""" Convert a markdown table match to BBCode format

	Args:
		match (re.Match[str]): Regex match object containing a markdown table block

	Returns:
		str: BBCode table string
	"""
	rows: list[str] = match.group(0).split("\n")
	result: str = "[table][tbody]"
	for row in rows:
		if not row.strip():
			continue
		cells = [c.strip() for c in row.strip().strip("|").split("|")]
		# Skip separator row (cells like ---, :---, ---:)
		if cells and all(re.match(r"^[-:]+$", c) for c in cells if c.strip()):
			continue
		result += "[tr]" + "".join(f"[td]{c}[/td]" for c in cells) + "[/tr]"
	result += "[/tbody][/table]"
	return result

def _is_unordered(line: str) -> bool:
	s = line.lstrip()
	return s.startswith("- ") or s.startswith("* ")

def _ordered_type(line: str) -> str | None:
	s = line.lstrip()
	if re.match(r'^\d+\.\s', s):
		return "1"
	if re.match(r'^[a-z]\.\s', s):
		return "a"
	return None

def _is_ordered(line: str) -> bool:
	return _ordered_type(line) is not None

def _collect_block(text_lines: list[str], start: int, predicate: CallableAny) -> tuple[list[str], int]:
	""" Collect consecutive matching lines from text_lines, skipping blank lines within a block"""
	block: list[str] = []
	j: int = start
	while j < len(text_lines):
		if predicate(text_lines[j]):
			block.append(text_lines[j])
			j += 1
		elif text_lines[j].strip() == "":
			k: int = j + 1
			while k < len(text_lines) and text_lines[k].strip() == "":
				k += 1
			if k < len(text_lines) and predicate(text_lines[k]):
				j = k
			else:
				break
		else:
			break
	return block, j

def convert_list_block(block_lines: list[str], list_type: str = "") -> str:
	""" Convert a block of markdown list lines (with possible nesting) to BBCode

	Args:
		block_lines (list[str]): Lines of the list block
		list_type   (str):       BBCode list type: '' for unordered, '1' for numbered, 'a' for alphabetical

	Returns:
		str: BBCode list string
	"""
	open_tag: str = f"[list={list_type}]" if list_type else "[list]"
	result: list[str] = []
	level_stack: list[int] = []

	for line in block_lines:
		stripped = line.lstrip()
		indent = len(line) - len(stripped)
		item_text = re.sub(r'^(?:[a-zA-Z0-9]+\.|-|\*)\s+', '', stripped).strip()

		if not level_stack:
			level_stack.append(indent)
			result.append(open_tag)
		elif indent > level_stack[-1]:
			level_stack.append(indent)
			if result and result[-1].endswith("[/*]"):
				result[-1] = result[-1][:-4] + open_tag
			else:
				result.append(open_tag)
		elif indent < level_stack[-1]:
			while len(level_stack) > 1 and level_stack[-1] > indent:
				level_stack.pop()
				result.append("[/list][/*]")

		result.append(f"[*]{item_text}[/*]")

	while level_stack:
		level_stack.pop()
		result.append("[/list][/*]" if level_stack else "[/list]")

	return "\n".join(result)

def convert_markdown_to_bbcode(markdown: str, verbose: bool = True) -> str:
	""" Convert markdown to bbcode for PlanetMinecraft

	Args:
		markdown (str): Markdown text
		verbose (bool): If True, print the conversion comparison

	Returns:
		str: BBcode text

	Examples:
		>>> markdown_text = '''
		... [![Discord](https://img.shields.io/discord/1216400498488377467?label=Discord&logo=discord)](https://discord.gg/anxzu6rA9F)
		... ![Discord](https://img.shields.io/discord/1216400498488377467?label=Discord&logo=discord)
		... ## Changelog
		...
		... ### Build System
		... - 🚀 Bump version to v1.2.3 ([2111fd2](https://github.com/Stoupy51/LifeSteal/commit/2111fd2f390b80a3aab77a4e7bcbb24b93845e5a))
		...
		...
		...
		... ### Features
		... - ✨ Added new configuration for dropping heart (non pvp) ([cde8749](https://github.com/Stoupy51/LifeSteal/commit/cde8749aa9e447302481f50b9887a0b3a846c7fe))
		...
		... - 🔧 Another feature with multiple newlines before
		...
		... **Full Changelog**: https://github.com/Stoupy51/LifeSteal/compare/v1.2.2...v1.2.3
		... '''
		>>> bbcode = convert_markdown_to_bbcode(markdown_text, verbose=False)
		>>> print(bbcode.strip())
		[url=https://discord.gg/anxzu6rA9F][img]https://img.shields.io/discord/1216400498488377467?label=Discord&logo=discord[/img][/url] [img]https://img.shields.io/discord/1216400498488377467?label=Discord&logo=discord[/img]
		[h2]Changelog[/h2][h4]Build System[/h4][list]
		[*]🚀 Bump version to v1.2.3 ([url=https://github.com/Stoupy51/LifeSteal/commit/2111fd2f390b80a3aab77a4e7bcbb24b93845e5a]2111fd2[/url])[/*]
		[/list][h4]Features[/h4][list]
		[*]✨ Added new configuration for dropping heart (non pvp) ([url=https://github.com/Stoupy51/LifeSteal/commit/cde8749aa9e447302481f50b9887a0b3a846c7fe]cde8749[/url])[/*]
		[*]🔧 Another feature with multiple newlines before[/*]
		[/list]
		[b]Full Changelog[/b]: [url]https://github.com/Stoupy51/LifeSteal/compare/v1.2.2...v1.2.3[/url]
		>>> spoiler_md = '<details>\\n<summary>Preview</summary>\\n![screenshot](https://example.com/img.png)\\n</details>'
		>>> print(convert_markdown_to_bbcode(spoiler_md, verbose=False))
		[spoiler=Preview][img]https://example.com/img.png[/img][/spoiler]
		>>> print(convert_markdown_to_bbcode('Line 1<br>Line 2<br/>Line 3<br />Line 4', verbose=False))
		Line 1
		Line 2
		Line 3
		Line 4
		>>> table_md = '| A | B |\\n|---|---|\\n| 1 | 2 |\\n| 3 | 4 |'
		>>> print(convert_markdown_to_bbcode(table_md, verbose=False))
		[table][tbody][tr][td]A[/td][td]B[/td][/tr][tr][td]1[/td][td]2[/td][/tr][tr][td]3[/td][td]4[/td][/tr][/tbody][/table]
		>>> print(convert_markdown_to_bbcode('```\\ncode block\\n```', verbose=False))
		[code]code block[/code]
		>>> print(convert_markdown_to_bbcode('`inline code`', verbose=False))
		[color=#34495e]inline code[/color]
		>>> print(convert_markdown_to_bbcode('[`Smithed Crafter`](https://wiki.smithed.dev/libraries/crafter/)', verbose=False))
		[url=https://wiki.smithed.dev/libraries/crafter/][color=#34495e]Smithed Crafter[/color][/url]
		>>> badges_md = '[![YouTube](https://img.shields.io/youtube/views/zkcQn23DRaw?style=flat&logo=youtube&logoColor=red&label=YouTube)](https://www.youtube.com/watch?v=zkcQn23DRaw)\\n[![GitHub](https://img.shields.io/github/v/release/Stoupy51/stewbeet?logo=github&label=GitHub)](https://github.com/Stoupy51/stewbeet/releases/latest)'
		>>> print(convert_markdown_to_bbcode(badges_md, verbose=False))
		[url=https://www.youtube.com/watch?v=zkcQn23DRaw][img]https://img.shields.io/youtube/views/zkcQn23DRaw?style=flat&logo=youtube&logoColor=red&label=YouTube[/img][/url] [url=https://github.com/Stoupy51/stewbeet/releases/latest][img]https://img.shields.io/github/v/release/Stoupy51/stewbeet?logo=github&label=GitHub[/img][/url]
		>>> print(convert_markdown_to_bbcode('~~strikethrough~~', verbose=False))
		[s]strikethrough[/s]
		>>> print(convert_markdown_to_bbcode('*italic* and _also italic_', verbose=False))
		[i]italic[/i] and [i]also italic[/i]
		>>> print(convert_markdown_to_bbcode('<u>underline</u>', verbose=False))
		[u]underline[/u]
		>>> print(convert_markdown_to_bbcode('> blockquote', verbose=False))
		[quote]blockquote[/quote]
		>>> nested_list_md = '- item 1\\n  - sub item 1\\n  - sub item 2\\n- item 2'
		>>> print(convert_markdown_to_bbcode(nested_list_md, verbose=False))
		[list]
		[*]item 1[list]
		[*]sub item 1[/*]
		[*]sub item 2[/*]
		[/list][/*]
		[*]item 2[/*]
		[/list]
		>>> nested_list_urls = '- Actual projects:\\n  - https://github.com/Paralya/Switch\\n  - https://github.com/Stoupy51/LifeSteal'
		>>> print(convert_markdown_to_bbcode(nested_list_urls, verbose=False))
		[list]
		[*]Actual projects:[list]
		[*][url]https://github.com/Paralya/Switch[/url][/*]
		[*][url]https://github.com/Stoupy51/LifeSteal[/url][/*]
		[/list][/*]
		[/list]
		>>> print(convert_markdown_to_bbcode('---', verbose=False))
		[hr]
		>>> print(convert_markdown_to_bbcode('* item 1\\n* item 2', verbose=False))
		[list]
		[*]item 1[/*]
		[*]item 2[/*]
		[/list]
		>>> print(convert_markdown_to_bbcode('1. item 1\\n2. item 2', verbose=False))
		[list=1]
		[*]item 1[/*]
		[*]item 2[/*]
		[/list]
		>>> print(convert_markdown_to_bbcode('a. item 1\\nb. item 2', verbose=False))
		[list=a]
		[*]item 1[/*]
		[*]item 2[/*]
		[/list]
	"""
	# Make a copy of the original markdown text
	bbcode: str = markdown

	# Step 0: Convert <br> tags to newlines
	bbcode = re.sub(r"<br\s*/>", "\n", bbcode)
	bbcode = bbcode.replace("<br>", "\n")

	# Step 1: Convert headers (# -> [h1], (## -> [h2], ### -> [h4])
	bbcode = re.sub(r"^# ([^\n]+)", r"[h1]\1[/h1]", bbcode, flags=re.MULTILINE)
	bbcode = re.sub(r"^## ([^\n]+)", r"[h2]\1[/h2]", bbcode, flags=re.MULTILINE)
	bbcode = re.sub(r"^### ([^\n]+)", r"[h4]\1[/h4]", bbcode, flags=re.MULTILINE)
	bbcode = re.sub(r"^#### ([^\n]+)", r"[h5]\1[/h5]", bbcode, flags=re.MULTILINE)

	# Step 1b: Convert markdown tables to BBCode tables
	bbcode = re.sub(r"^[ \t]*\|[^\n]*(?:\n[ \t]*\|[^\n]*)*", table_to_bbcode, bbcode, flags=re.MULTILINE)

	# Step 2-3: Process lists with nested support using line-by-line traversal
	text_lines: list[str] = bbcode.split("\n")
	result_lines: list[str] = []
	i: int = 0
	while i < len(text_lines):
		line = text_lines[i]
		if _is_unordered(line):
			block_lines, i = _collect_block(text_lines, i, _is_unordered)
			result_lines.append(convert_list_block(block_lines))
		elif (otype := _ordered_type(line)) is not None:
			block_lines, i = _collect_block(text_lines, i, _is_ordered)
			result_lines.append(convert_list_block(block_lines, otype))
		else:
			result_lines.append(line)
			i += 1
	bbcode = "\n".join(result_lines)

	# Step 3b: Convert spoiler/details blocks
	# Format: <details><summary>X</summary>content</details> -> [spoiler=X]content[/spoiler]
	bbcode = re.sub(
		r"<details>\s*<summary>([^<]+)</summary>(.*?)</details>",
		lambda m: f"[spoiler={m.group(1).strip()}]{m.group(2).strip()}[/spoiler]",
		bbcode,
		flags=re.DOTALL
	)

	# Step 3c: Convert fenced code blocks
	# Format: ```\ncode\n``` -> [code]code[/code]
	bbcode = re.sub(r"```[^\n]*\n(.*?)```", lambda m: f"[code]{m.group(1).rstrip()}[/code]", bbcode, flags=re.DOTALL)

	# Step 3e: Convert blockquotes (group consecutive > lines)
	# Format: > text -> [quote]text[/quote]
	bbcode = re.sub(
		r"(?:^> ?[^\n]*(?:\n> ?[^\n]*)*)",
		lambda m: "[quote]" + re.sub(r"^> ?", "", m.group(0), flags=re.MULTILINE) + "[/quote]",
		bbcode,
		flags=re.MULTILINE
	)

	# Step 3f: Convert horizontal rules
	# Format: --- or *** (alone on a line) -> [hr]
	bbcode = re.sub(r"^[-*]{3,}$", "[hr]", bbcode, flags=re.MULTILINE)

	# Step 4: Convert clickable images (must be done before regular links and images)
	# Format: [![alt](img_url)](link_url) -> [url=link_url][img]img_url[/img][/url]
	bbcode = re.sub(r"\[!\[([^\]]*)\]\(([^)]+)\)\]\(([^)]+)\)", r"[url=\3][img]\2[/img][/url]", bbcode)

	# Step 5: Convert regular images
	# Format: ![alt](img_url) -> [img]img_url[/img]
	bbcode = re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", r"[img]\2[/img]", bbcode)

	# Step 6: Convert markdown links to BBCode links
	# Format: [text](url) -> [url=url]text[/url]
	bbcode = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"[url=\2]\1[/url]", bbcode)

	# Step 6b: Join consecutive images on the same line (separated by only a single newline)
	img_bb_pattern = r'((?:\[url=[^\]]+\])?\[img\][^\n]+\[/img\](?:\[/url\])?)\n((?:\[url=[^\]]+\])?\[img\])'
	while re.search(img_bb_pattern, bbcode):
		bbcode = re.sub(img_bb_pattern, r'\1 \2', bbcode)

	# Step 6c: Convert inline code (after links so backtick-wrapped link text is handled correctly)
	# Format: `code` -> [color=#34495e]code[/color]
	bbcode = re.sub(r"`([^`\n]+)`", r"[color=#34495e]\1[/color]", bbcode)

	# Step 7: Convert bold text
	# Format: **text** -> [b]text[/b]
	bbcode = re.sub(r"\*\*([^*]+)\*\*", r"[b]\1[/b]", bbcode)

	# Step 7b: Convert strikethrough text
	# Format: ~~text~~ -> [s]text[/s]
	bbcode = re.sub(r"~~([^~]+)~~", r"[s]\1[/s]", bbcode)

	# Step 7c: Convert underline tags
	# Format: <u>text</u> -> [u]text[/u]
	bbcode = re.sub(r"<u>(.*?)</u>", r"[u]\1[/u]", bbcode, flags=re.DOTALL)

	# Step 7d: Convert italic text (single * or _)
	# Format: *text* or _text_ -> [i]text[/i]
	# Exclude [*] and [/*] list tags by checking for [ and / before *
	bbcode = re.sub(r"(?<![\[/])\*(?![*\]])([^*\n]+)(?<![\[/])\*(?![*\]])", r"[i]\1[/i]", bbcode)
	bbcode = re.sub(r"(?<![_\w\[])_([^_\n]+)_(?![_\w\]])", r"[i]\1[/i]", bbcode)

	# Step 8: Convert plain URLs (not already in BBCode)
	# Look for URLs not already inside [url] or [img] tags
	# Note: [^\s\[\]]+ excludes '[' to avoid consuming BBCode list tags like [/*]
	url_pattern = r"(?<!\[url=|\[url\]|\[img\])(https?://[^\s\[\]]+)(?!\[/url\]|\[/img\])"
	bbcode = re.sub(url_pattern, r"[url]\1[/url]", bbcode)

	# Step 9: Remove blank lines between sections to create compact format
	bbcode = re.sub(r"\n{3,}", "\n\n", bbcode)  # Collapse 3+ newlines to 2 (i.e. one blank line max)
	bbcode = re.sub(r"\[/h2]\n+\[h4]", r"[/h2][h4]", bbcode)
	bbcode = re.sub(r"(\[/h4])\n+(\[list(?:=[^\]]+)?])", r"\1\2", bbcode)
	bbcode = re.sub(r"(\[/list])\n+(\[h4])", r"\1\2", bbcode)
	bbcode = re.sub(r"(\[/list])\n+(\[b])", r"\1\n\2", bbcode)
	bbcode = re.sub(r":\n\n(\[list(?:=[^\]]+)?])", r":\n\1", bbcode)  # Remove blank line between colon and list

	# Print the conversion comparison if verbose is True
	if verbose:
		print("Original Markdown:")
		print("-" * 40)
		print(markdown)
		print("-" * 40)
		print("\nConverted BBCode:")
		print("-" * 40)
		print(bbcode)
		print("-" * 40)

	return bbcode

def upload_version(project_url: str, changelog: str) -> None:
	""" Upload new version by opening the project url with the browser

	Args:
		project_url		(str):	Url of the project on PlanetMinecraft to open
		changelog		(str):	Changelog text
	"""
	# Open the project url in the browser
	import subprocess
	subprocess.run(["start", project_url], shell=True)

	# Copy the changelog text to the clipboard
	pyperclip.copy(convert_markdown_to_bbcode(changelog))
	stp.info("Changelog text copied to the clipboard!")


@stp.measure_time(message="Uploading to PlanetMinecraft took")
@stp.handle_error
def upload_to_pmc(pmc_config: JsonDict, changelog: str = "") -> None:
	""" Upload the project to PlanetMinecraft using the configuration

	Disclaimer:
		There is no API for PlanetMinecraft, so everything is done manually.

	Args:
		pmc_config		(dict):		Configuration for the PlanetMinecraft project
		changelog		(str):		Changelog text for the release
	"""
	project_url: str = validate_config(pmc_config)
	upload_version(project_url, changelog)


if __name__ == "__main__":
	import doctest
	doctest.testmod()

