
# Lazy imports (PEP 810), ignored before Python 3.15
from stouputils.lazy import ALWAYS_LAZY

__lazy_modules__ = ALWAYS_LAZY

# Imports
# Star imports keep this package a drop-in replacement for the former io.py module: every name it
# used to expose, including the ones it merely imported, stays reachable from `core.utils.io`.
from .advancements import (
	write_advancement as write_advancement,
)
from .deprecated import (
	convert_to_serializable as convert_to_serializable,
	write_function_tag as write_function_tag,
)
from .dicts import (
	super_merge_dict as super_merge_dict,
)
from .files import (
	JsonFileT as JsonFileT,
	set_json_encoder as set_json_encoder,
	texture_mcmeta as texture_mcmeta,
)
from .functions import (
	McFunction as McFunction,
	read_function as read_function,
	write_function as write_function,
	write_load_file as write_load_file,
	write_scheduled_function as write_scheduled_function,
	write_tag as write_tag,
	write_tick_file as write_tick_file,
	write_unload_file as write_unload_file,
	write_versioned_function as write_versioned_function,
)
from .model_cache import (
	EXACT_JSON_TYPES as EXACT_JSON_TYPES,
	MODEL_CACHE_MAX_AGE as MODEL_CACHE_MAX_AGE,
	MODEL_CACHE_MIN_SIZE as MODEL_CACHE_MIN_SIZE,
	MODEL_CACHE_NAME as MODEL_CACHE_NAME,
	ModelSerializationCache as ModelSerializationCache,
	active_model_cache as active_model_cache,
	set_model_encoder as set_model_encoder,
	setup_model_cache as setup_model_cache,
	to_plain_builtin as to_plain_builtin,
)
