
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

# Regex pattern for text extraction, starting with a literal so the engine jumps from one "text" to the next.
# The opening quote of a quoted key comes before that literal, `extract_texts` checks it against the closing one.
TEXT_RE: re.Pattern[str] = re.compile(
	r'''
	text(?P<key_quote>["']?)\s*:\s*                                   # Match text, closing quote of the key, colon
	(?:"(?P<double>(?:[^"\\]|\\.)*)"|'(?P<single>(?:[^'\\]|\\.)*)')  # The value up to its first unescaped closing quote
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

	prefix, core, suffix = absorb_prefix_openers(text[:match.start()], match.group(), text[match.end():])
	core, consumed = absorb_core_closers(core, suffix)
	suffix_was_consumed: bool = len(consumed) < len(suffix)
	suffix = consumed

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


def unmatched(text: str, opener: str, closer: str) -> int:
	""" How many openers of text are left open. A quote opens and closes with the same character, so parity decides for it.

	>>> unmatched("((a)", "(", ")"), unmatched("'a'' ", "'", "'")
	(1, 1)
	"""
	return text.count(opener) % 2 if opener == closer else text.count(opener) - text.count(closer)


def absorb_prefix_openers(prefix: str, core: str, suffix: str) -> tuple[str, str, str]:
	""" Fold into the core each opener of the prefix left open, with its closer when the suffix still holds it. """
	for opener, closer in CLOSERS.items():
		for _ in range(unmatched(prefix, opener, closer)):
			closed_in_core: bool = closer in core
			if not closed_in_core and closer not in suffix:
				break
			idx_open: int = prefix.rindex(opener)
			core, prefix = prefix[idx_open:] + core, prefix[:idx_open]
			if not closed_in_core:
				idx_close: int = suffix.index(closer)
				core, suffix = core + suffix[:idx_close + 1], suffix[idx_close + 1:]
	return prefix, core, suffix


def absorb_core_closers(core: str, suffix: str) -> tuple[str, str]:
	""" Let each opener of the core left open take its closer from the suffix. """
	for opener, closer in CLOSERS.items():
		for _ in range(unmatched(core, opener, closer)):
			if closer not in suffix:
				break
			idx: int = suffix.index(closer)
			core, suffix = core + suffix[:idx + 1], suffix[idx + 1:]
	return core, suffix


@stp.simple_cache
def lang_parts(clean_text: str) -> tuple[str, str, str]:
	""" `split_text_content`, with the core's leading and trailing newlines moved out of the translation and its key.

	>>> lang_parts("\\nHello\\n\\n")
	('\\n', 'Hello', '\\n\\n')
	"""
	prefix, core, suffix = split_text_content(clean_text)
	left: str = core.lstrip("\n")
	right: str = left.rstrip("\n")
	return prefix + "\n" * (len(core) - len(left)), right, "\n" * (len(left) - len(right)) + suffix


def extract_texts(content: str) -> list[tuple[str, int, int, str, str | None]]:
	""" Every "text" value of content, as (value, start, end, value_quote, key_quote) with key_quote None for a bare key.

	>>> extract_texts('{"text":"Hello World"}')
	[('Hello World', 1, 21, '"', '"')]
	>>> extract_texts("{text:'Hey'}")
	[('Hey', 1, 11, "'", None)]
	"""
	matches: list[tuple[str, int, int, str, str | None]] = []
	last_end: int = 0
	position: int = 0
	while (match := TEXT_RE.search(content, position)) is not None:
		start, end = match.span()

		# A quoted key needs the same quote right before it, outside the previous match
		key_quote: str = match.group("key_quote")
		if key_quote:
			if start - 1 < last_end or content[start - 1] != key_quote:
				position = start + 1
				continue
			start -= 1

		double: str | None = match.group("double")
		value, quote = (double, '"') if double is not None else (match.group("single"), "'")
		matches.append((value, start, end, quote, key_quote or None))
		last_end = position = end
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


def translated(
	string: str, text: str, start: int, end: int, quote: str, key_quote: str | None, ctx: Context | None,
) -> Replacement | None:
	""" The replacement turning one "text" value of string into a lang key, registered in `lang`, or None for a value not worth one.

	Args:
		text: Raw matched value, as `extract_texts` found it at start to end.
		ctx:  Passed to `lang_format`, None for Mem.ctx.
	"""
	clean_text: str = text.replace("\\n", "\n").replace("\\", "")
	if not ALNUM_RE.search(clean_text):
		return None
	prefix, core, suffix = lang_parts(clean_text)
	key_for_lang, verif = lang_format(core, ctx)
	if len(verif) < 3 or not verif.isalnum() or "\\u" in text or "$" in clean_text:
		return None
	key_for_lang = resolve_lang_key(key_for_lang, core)
	lang[key_for_lang] = core
	new_fragment, replace_start, replace_end = build_replacement(
		string, text, clean_text, start, end, quote, key_quote, key_for_lang, prefix, suffix,
	)
	return Replacement(replace_start, replace_end, new_fragment)


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
		replacement: Replacement | None = translated(string, text, start, end, quote, key_quote, None if Mem.ctx == ctx else ctx)
		if replacement is None:
			continue
		# A replacement of the enclosing object drops those nested in it, whose overlapping ranges would corrupt the JSON
		replacements = [r for r in replacements if not (replacement.start <= r.start and r.end <= replacement.end)]
		replacements.append(replacement)

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

