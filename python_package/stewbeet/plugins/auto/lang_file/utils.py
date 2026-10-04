
# Lazy imports (PEP 810), ignored before Python 3.15
from stouputils.lazy import ALWAYS_LAZY

__lazy_modules__ = ALWAYS_LAZY

# Imports
import re
from typing import NamedTuple

import stouputils as stp
from beet import Context, TextFileBase

from ....core.__memory__ import Mem
from ....core.utils.text_component import CLOSERS, Replacement, apply_replacements, find_enclosing_object

# Prepare lang dictionary and lang_format function
lang: dict[str, str] = {}

# Pre-compiled regex patterns
ALNUM_RE: re.Pattern[str] = re.compile(r'[a-zA-Z0-9]')
LETTER_RE: re.Pattern[str] = re.compile(r'[a-zA-Z].*[a-zA-Z]|[a-zA-Z]', re.DOTALL)
SENTENCE_PUNCT_RE: re.Pattern[str] = re.compile(r'^[\s:.,!?]*$')

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

# Fake context for doctests
class FakeContext(NamedTuple):
	project_id: str


# Functions
def split_text_content(text: str, max_words: int = 5) -> tuple[str, str, str]:
	""" Split text into (prefix, core, suffix), the core spanning from the first to the last letter.

	The core then expands to close the brackets and quotes opened within it.
	When it holds more than max_words words, the text is not split and comes back whole as the core.

	>>> split_text_content(" attacks | ")
	(' ', 'attacks', ' | ')
	"""
	match = LETTER_RE.search(text)
	if not match or len(match.group().split()) > max_words:
		return ('', text, '')

	prefix, core, suffix = text[:match.start()], match.group(), text[match.end():]

	# Unmatched openers of the prefix whose closers are already in the core get folded into the core.
	# Quotes open and close with the same character, so their count difference is always 0 and parity is used instead.
	for opener, closer in CLOSERS.items():
		unmatched_in_prefix = prefix.count(opener) % 2 if opener == closer else prefix.count(opener) - prefix.count(closer)
		while unmatched_in_prefix > 0:
			if closer in core:
				# Closer already absorbed into core: just pull the opener in too
				idx_open = prefix.rindex(opener)
				core = prefix[idx_open:] + core
				prefix = prefix[:idx_open]
			elif closer in suffix:
				# Closer still in suffix: pull opener from prefix and closer from suffix
				idx_open = prefix.rindex(opener)
				core = prefix[idx_open:] + core
				prefix = prefix[:idx_open]
				idx_close = suffix.index(closer)
				core += suffix[:idx_close + 1]
				suffix = suffix[idx_close + 1:]
			else:
				break
			unmatched_in_prefix -= 1

	# Unmatched openers of the core consume their closers from the suffix, with the same parity rule for quotes.
	# Whether anything was consumed decides how much of the remaining suffix the punctuation sweep absorbs.
	suffix_was_consumed: bool = False
	for opener, closer in CLOSERS.items():
		unmatched = core.count(opener) % 2 if opener == closer else core.count(opener) - core.count(closer)
		while unmatched > 0 and closer in suffix:
			idx = suffix.index(closer)
			core += suffix[:idx + 1]
			suffix = suffix[idx + 1:]
			unmatched -= 1
			suffix_was_consumed = True

	# Absorb back a suffix that is purely sentence-ending punctuation (: . , ! ?).
	# After closers were taken from the suffix, only strong terminators (! ? .) are, so a ": " spacer after a bracket stays apart.
	if suffix_was_consumed:
		if re.match(r'^[!?.]+$', suffix):
			core += suffix
			suffix = ''
	elif SENTENCE_PUNCT_RE.match(suffix):
		core += suffix
		suffix = ''

	return prefix, core, suffix


def extract_texts(content: str) -> list[tuple[str, int, int, str, str | None]]:
	""" Every "text" value of content, as (value, start, end, value_quote, key_quote) with key_quote None for a bare key.

	>>> extract_texts('{"text":"Hello World"}')
	[('Hello World', 1, 21, '"', '"')]
	>>> extract_texts("{text:'Hey'}")
	[('Hey', 1, 11, "'", None)]
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
def lang_format(text: str, ctx: Context | None = None) -> tuple[str, str]:
	""" Format text into a lang key, returned with its simplified form used for length and alphanumeric checks.

	Path separators become underscores, other non-alphanumeric characters go, whitespace and dashes collapse,
	and the result is lowercased, truncated to 64 characters and prefixed with the project_id.

	Args:
		ctx: The beet context providing project_id, None for Mem.ctx

	>>> lang_format('BOMB PLANTED!', FakeContext(project_id='mgs'))
	('mgs.bomb_planted', 'bombplanted')
	"""
	if ctx is None:
		ctx = Mem.ctx
	text = re.sub(r"[./:]", "_", text)
	text = re.sub(r"[^a-zA-Z0-9 _-]", "", text).lower()
	alpha_num: str = re.sub(r"[ _-]+", "_", text).strip("_")[:64]
	key: str = f"{ctx.project_id}.{alpha_num}" if not alpha_num.startswith(ctx.project_id) else alpha_num
	return key, re.sub(r"[._]", "", alpha_num)


def resolve_lang_key(base_key: str, value: str) -> str:
	""" Return a lang key for value, base_key itself when it is free or already holds value.

	Otherwise _2, _3, ... are tried until a free slot or a slot already holding value is found.
	"""
	if base_key not in lang or lang[base_key] == value:
		return base_key
	counter: int = 2
	candidate: str = f"{base_key}_{counter}"
	while candidate in lang and lang[candidate] != value:
		counter += 1
		candidate = f"{base_key}_{counter}"
	return candidate


def build_replacement(
	string: str,
	text: str,
	clean_text: str,
	start: int,
	end: int,
	quote: str,
	key_quote: str | None,
	key_for_lang: str,
	prefix: str,
	suffix: str,
) -> tuple[str, int, int]:
	r""" Build the replacement fragment, with the start and end positions in string it overwrites.

	Without prefix or suffix, only the matched key:value fragment is replaced. Otherwise the enclosing JSON object
	is wrapped into a list, [prefix_obj?, {translate: key}, "suffix"?], or replaced in place when it cannot be located.

	Args:
		text:       Raw matched value, as it appears in source with escapes.
		clean_text: Decoded version of text (\\n -> newline, etc.).
		start:      Start position of the matched key:value fragment.
		quote:      Quote character used around the value, single or double.
		key_quote:  Quote character used around the "text" key, or None.
		prefix:     Non-alphanumeric prefix stripped from clean_text.
	"""
	translate_key: str = f'{key_quote}translate{key_quote}' if key_quote else 'translate'

	if not prefix and not suffix:
		# Simple case: swap text key/value in-place, preserving original colon spacing
		src_kv = re.search(r'(?:["\'])?text(?:["\'])?\s*(:\s*)', string[max(0, start-20):end])
		colon_str = src_kv.group(1) if src_kv else ': '
		new_fragment = f'{translate_key}{colon_str}{quote}{key_for_lang}{quote}'
		return new_fragment, start, end

	# Try to locate and wrap the enclosing JSON object
	bounds = find_enclosing_object(string, start, end)
	if bounds is None:
		# Fallback: plain replacement, store full text so value is correct
		lang[key_for_lang] = clean_text
		return f'{translate_key}: {quote}{key_for_lang}{quote}', start, end

	obj_start, obj_end = bounds
	obj_content = string[obj_start:obj_end]

	old_kv = re.search(
		r'(?:["\'])?text(?:["\'])?\s*:\s*["\']' + re.escape(text) + r'["\']',
		obj_content
	)
	if old_kv is None:
		# Fallback: can't locate the key/value inside object
		lang[key_for_lang] = clean_text
		return f'{translate_key}: {quote}{key_for_lang}{quote}', start, end

	parts: list[str] = []

	if prefix:
		prefix_escaped = prefix.replace('"', '\\"').replace('\n', '\\n')
		prefix_obj = re.sub(
			r'(?:["\'])?text(?:["\'])?\s*:\s*["\']' + re.escape(text) + r'["\']',
			lambda m: m.group(0)[:m.group(0).index(':')+1] + f'"{prefix_escaped}"',
			obj_content
		)
		parts.append(prefix_obj)
		# Core: bare translate only: styling already on prefix obj, inherited from parent
		colon_spacing = re.search(r'(?:["\'])?text(?:["\'])?\s*(\s*:\s*)', obj_content)
		colon_str = colon_spacing.group(1) if colon_spacing else ': '
		parts.append(f'{{{translate_key}{colon_str}{quote}{key_for_lang}{quote}}}')
	else:
		# No prefix: keep all original styling on the translate component
		core_obj = re.sub(
			r'(?:["\'])?text(?:["\'])?\s*:\s*["\']' + re.escape(text) + r'["\']',
			lambda m: m.group(0)[:m.group(0).index(':')+1] + f'"{key_for_lang}"',
			obj_content
		).replace('"text"', f'{translate_key}', 1).replace("'text'", f'{translate_key}', 1)
		# Handle unquoted text key
		core_obj = re.sub(r'\btext\b', translate_key.strip('"\''), core_obj, count=1)
		parts.append(core_obj)

	if suffix:
		suffix_escaped = suffix.replace('"', '\\"').replace('\n', '\\n')
		parts.append(f'"{suffix_escaped}"')

	new_fragment = '[' + ', '.join(parts) + ']'
	return new_fragment, obj_start, obj_end


def handle_file(content: TextFileBase[str] | None, ctx: Context | None = None) -> None:
	""" Replace in place every useful {"text": "..."} component of a file with a lang key.

	Strings without alphanumeric characters, too short or holding macros are skipped.
	A non-alphanumeric prefix or suffix is stripped to derive a stable key, wrapping the enclosing JSON object into a list,
	so components sharing the same alphanumeric content share their key.
	Numeric suffixes (_2, _3, ...) are the fallback when the object cannot be wrapped.

	Args:
		ctx: The context containing project information, None for Mem.ctx
	"""
	if ctx is None:
		ctx = Mem.ctx
	if isinstance(content, TextFileBase):
		string: str = str(content.text)
	else:
		raise ValueError(f"Unsupported content type: {type(content)}")

	# Fast path: TEXT_RE requires a literal "text" key, so skip the regex machinery entirely
	if "text" not in string:
		return

	matches: list[tuple[str, int, int, str, str | None]] = extract_texts(string)

	# Collect the slices to overwrite, then splice them all in a single pass
	replacements: list[Replacement] = []

	for text, start, end, quote, key_quote in reversed(matches):
		clean_text: str = text.replace("\\n", "\n").replace("\\", "")
		if not ALNUM_RE.search(clean_text):
			continue

		prefix, core, suffix = split_text_content(clean_text)

		# Redistribute leading/trailing \n from core into prefix/suffix so they are
		# not stored in the translation value and don't inflate the lang key.
		while core.startswith('\n'):
			prefix += '\n'
			core = core[1:]
		while core.endswith('\n'):
			suffix = '\n' + suffix
			core = core[:-1]

		key_for_lang, verif = lang_format(core, None if Mem.ctx == ctx else ctx)
		if len(verif) < 3 or not verif.isalnum() or "\\u" in text or "$" in clean_text:
			continue

		key_for_lang = resolve_lang_key(key_for_lang, core)
		lang[key_for_lang] = core

		new_fragment, replace_start, replace_end = build_replacement(
			string, text, clean_text, start, end, quote, key_quote,
			key_for_lang, prefix, suffix,
		)
		# Drop any nested replacements fully contained in this broader enclosing-object
		# replacement to prevent overlapping ranges that corrupt the output JSON.
		replacements = [r for r in replacements if not (replace_start <= r.start and r.end <= replace_end)]
		replacements.append(Replacement(replace_start, replace_end, new_fragment))

	new_string: str = apply_replacements(string, replacements)
	if new_string != string:
		content.text = new_string


__test__: dict[str, str] = {
	"build_replacement": r"""
	>>> # Simple case: no prefix/suffix
	>>> s = '{"text":"Hello World"}'
	>>> frag, rs, re_ = build_replacement(s, 'Hello World', 'Hello World', 1, 21, '"', '"', 'mgs.hello_world', '', '')
	>>> s[:rs] + frag + s[re_:]
	'{"translate":"mgs.hello_world"}'
	>>> # Prefix+suffix: wraps object into list, core gets bare translate
	>>> s = '{"text":" attacks | ","color":"white"}'
	>>> frag, rs, re_ = build_replacement(s, ' attacks | ', ' attacks | ', 1, 36, '"', '"', 'mgs.attacks', ' ', ' | ')
	>>> result = s[:rs] + frag + s[re_:]
	>>> result
	'[{"text":" ","color":"white"}, {"translate":"mgs.attacks"}, " | "]'
	>>> # Suffix only: translate keeps all original styling
	>>> s = '{"text":"attacks!","color":"green"}'
	>>> frag, rs, re_ = build_replacement(s, 'attacks!', 'attacks!', 1, 33, '"', '"', 'mgs.attacks', '', '!')
	>>> result = s[:rs] + frag + s[re_:]
	>>> result
	'[{"translate":"mgs.attacks","color":"green"}, "!"]'
	>>> # Suffix only with color: color stays on translate component
	>>> s = '{"text":"Exited map editor (changes discarded).","color":"red"}'
	>>> frag, rs, re_ = build_replacement(
	...		s, 'Exited map editor (changes discarded).', 'Exited map editor (changes discarded).', 1, 62,
	...		'"', '"', 'mgs.exited_map_editor_changes_discarded', '', '.'
	...	)
	>>> result = s[:rs] + frag + s[re_:]
	>>> result
	'[{"translate":"mgs.exited_map_editor_changes_discarded","color":"red"}, "."]'
	>>> # No object bounds fallback
	>>> s = 'text: "hello world"'
	>>> frag, rs, re_ = build_replacement(s, 'hello world', 'hello world', 0, 19, '"', None, 'mgs.hello_world', '', '...')
	>>> s[:rs] + frag + s[re_:]
	'translate: "mgs.hello_world"'
	>>> # Prefix with newline: newline in prefix must be re-escaped back to \\n
	>>> s = '{"text":"\\nNo secondary magazines","color":"gray"}'
	>>> frag, rs, re_ = build_replacement(
	...     s, '\\nNo secondary magazines', '\nNo secondary magazines', 1, 48, '"', '"', 'mgs.no_secondary_magazines', '\n', ''
	... )
	>>> s[:rs] + frag + s[re_:]
	'[{"text":"\\n","color":"gray"}, {"translate":"mgs.no_secondary_magazines"}]'
	""",
	"extract_texts": """
	>>> matches = extract_texts('{"text":"Hello World"}')
	>>> len(matches)
	1
	>>> matches[0][0]
	'Hello World'
	>>> matches[0][3]
	'"'
	>>> matches[0][4]
	'"'
	>>> matches = extract_texts('{text:"Hey dude!!!!"}')
	>>> matches[0][0]
	'Hey dude!!!!'
	>>> matches[0][4] is None
	True
	>>> matches = extract_texts("{'text':'Single quotes'}")
	>>> matches[0][0]
	'Single quotes'
	>>> matches[0][3]
	"'"
	>>> matches = extract_texts('{"text":"first"} and {"text":"second"}')
	>>> len(matches)
	2
	>>> matches[0][0]
	'first'
	>>> matches[1][0]
	'second'
	>>> extract_texts('{"color":"red"}')
	[]
	""",
	"handle_file": """
	>>> from unittest.mock import MagicMock
	>>> def make_content(text):
	...     m = MagicMock()
	...     m.text = text
	...     m.__class__ = TextFileBase
	...     return m
	>>> ctx = FakeContext(project_id='mgs')
	>>> # Simple replacement
	>>> lang.clear()
	>>> c = make_content('{"text":"Hello World"}')
	>>> handle_file(c, ctx)
	>>> c.text
	'{"translate":"mgs.hello_world"}'
	>>> lang['mgs.hello_world']
	'Hello World'
	>>> # Prefix/suffix wrapping: attacks with pipe vs attacks with exclamation
	>>> lang.clear()
	>>> c1 = make_content('{"text":" attacks | ","color":"white"}')
	>>> c2 = make_content('{"text":"attacks!","color":"green"}')
	>>> handle_file(c1, ctx)
	>>> handle_file(c2, ctx)
	>>> c1.text
	'[{"text":" ","color":"white"}, {"translate":"mgs.attacks"}, " | "]'
	>>> c2.text
	'{"translate":"mgs.attacks_2","color":"green"}'
	>>> lang['mgs.attacks']
	'attacks'
	>>> lang['mgs.attacks_2']
	'attacks!'
	>>> # Styling is stripped from core translate component
	>>> lang.clear()
	>>> c = make_content('{"text":" MC Guns System","italic":true,"color":"blue"}')
	>>> handle_file(c, ctx)
	>>> c.text
	'[{"text":" ","italic":true,"color":"blue"}, {"translate":"mgs.mc_guns_system"}]'
	>>> # No-op: unchanged content is not written back
	>>> lang.clear()
	>>> c = make_content('{"color":"red"}')
	>>> handle_file(c, ctx)
	>>> c.text  # setter never called
	'{"color":"red"}'
	""",
	"lang_format": """
	>>> ctx = FakeContext(project_id='my_project')
	>>> lang_format('Hello World', ctx)
	('my_project.hello_world', 'helloworld')
	>>> lang_format('Test/Path:Name', ctx)
	('my_project.test_path_name', 'testpathname')
	>>> lang_format('Special!@#$%Characters', ctx)
	('my_project.specialcharacters', 'specialcharacters')
	>>> key, simplified = lang_format('a' * 100, ctx)
	>>> len(simplified) <= 64
	True
	>>> lang_format('BOMB PLANTED!', ctx)
	('my_project.bomb_planted', 'bombplanted')
	>>> lang_format(' attacks | ', ctx)
	('my_project.attacks', 'attacks')
	""",
	"resolve_lang_key": """
	>>> _orig = lang.copy(); lang.clear()
	>>> resolve_lang_key('mgs.attacks', 'attacks')
	'mgs.attacks'
	>>> lang['mgs.attacks'] = 'attacks'
	>>> resolve_lang_key('mgs.attacks', 'attacks')
	'mgs.attacks'
	>>> resolve_lang_key('mgs.attacks', 'attacks!')
	'mgs.attacks_2'
	>>> lang['mgs.attacks_2'] = 'attacks!'
	>>> resolve_lang_key('mgs.attacks', 'attacks?')
	'mgs.attacks_3'
	>>> lang.clear(); lang.update(_orig)  # restore
	""",
	"split_text_content": """
	>>> split_text_content("attacks!")
	('', 'attacks!', '')
	>>> split_text_content("Hello World")
	('', 'Hello World', '')
	>>> split_text_content("\\n- Total 'Vb Contents Frame': \\n")
	('\\n- ', "Total 'Vb Contents Frame'", ': \\n')
	>>> split_text_content("💣 BOMB PLANTED!")
	('💣 ', 'BOMB PLANTED!', '')
	>>> split_text_content("  !pure!  ")
	('  !', 'pure!  ', '')
	>>> split_text_content("no change needed")
	('', 'no change needed', '')
	>>> split_text_content("missing\\nplease download more")
	('', 'missing\\nplease download more', '')
	>>> split_text_content("💣 BOMB!\\nRun away!")
	('💣 ', 'BOMB!\\nRun away!', '')
	>>> split_text_content(" MC Guns System")
	(' ', 'MC Guns System', '')
	>>> split_text_content("Round ")
	('', 'Round ', '')
	>>> split_text_content("!!!!")
	('', '!!!!', '')
	>>> split_text_content("Chest [10/11]")
	('', 'Chest', ' [10/11]')
	>>> split_text_content("950 points")
	('950 ', 'points', '')
	>>> split_text_content("/100")
	('', '/100', '')
	>>> split_text_content("Create Loadout - Scope (Secondary)")
	('', 'Create Loadout - Scope (Secondary)', '')
	>>> split_text_content("Click [here] for more!")
	('', 'Click [here] for more!', '')
	>>> split_text_content("💣 Bomb (timed)!")
	('💣 ', 'Bomb (timed)!', '')
	>>> split_text_content(" (Defenders) win the round!")
	(' ', '(Defenders) win the round!', '')
	>>> split_text_content(" (Attackers) win the round!")
	(' ', '(Attackers) win the round!', '')
	>>> split_text_content("Run this command to create a new map:")
	('', 'Run this command to create a new map:', '')
	>>> split_text_content("Score: ")
	('', 'Score: ', '')
	>>> split_text_content("Ability: ")
	('', 'Ability: ', '')
	>>> split_text_content("💣 This is a six word sentence!", max_words=5)
	('', '💣 This is a six word sentence!', '')
	>>> split_text_content("💣 Yes Five words exactly here!", max_words=5)
	('💣 ', 'Yes Five words exactly here!', '')
	""",
}

