# Lazy imports (PEP 810), ignored before Python 3.15
from stouputils.lazy import ALWAYS_LAZY

__lazy_modules__ = ALWAYS_LAZY

# Imports
# TextComponent is beet's, re-exported because every helper here takes or returns one
from beet.core.utils import TextComponent as TextComponent

# Every name these modules expose stays reachable from `core.utils.text_component`
from .convert import (
	item_id_to_name as item_id_to_name,
	item_id_to_text_component as item_id_to_text_component,
	text_component_to_str as text_component_to_str,
)
from .scan import (
	CLOSERS as CLOSERS,
	Replacement as Replacement,
	apply_replacements as apply_replacements,
	find_enclosing_object as find_enclosing_object,
	iter_data_text_files as iter_data_text_files,
)

