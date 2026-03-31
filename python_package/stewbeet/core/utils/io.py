
# Imports
import os
from typing import Any, TypeVar, cast, Callable

import stouputils as stp
from beet import Advancement, Function, JsonFile, NamespaceContainer, NamespaceProxy, TagFile, Texture
from beet.core.utils import JsonDict

from ..__memory__ import Mem

# Constants
JsonFileT = TypeVar("JsonFileT", bound=JsonFile)

# Advancements
def write_advancement(
	path: str,
	advancement: Advancement | JsonDict,
	overwrite: bool = False,
	max_level: int = -1,
	condition: Callable[[JsonDict], bool] = lambda existing_data: True,
) -> None:
	""" Write an advancement at the given path.

	Args:
		path        (str):  The path to the advancement (ex: "namespace:folder/advancement_name")
		advancement (Advancement | JsonDict): The advancement to write
		overwrite   (bool): If the file should be overwritten (default: Merge with existing content using super_merge_dict)
		max_level   (int):  The maximum level of the JSON dump, -1 for default behavior (default: -1)
		condition   (Callable[[JsonDict], bool]): A function that takes the existing advancement data and returns whether the new advancement should be written (default: always write)
	"""
	if path.endswith(".json"):
		path = path[:-len(".json")]

	# Get existing advancement or create empty one
	existing: Advancement = Mem.ctx.data.advancements.setdefault(path)
	existing_data: JsonDict = existing.data
	# Check condition with existing data
	if not condition(existing_data): return

	# Convert to dict if it's an Advancement object
	new_data: JsonDict = advancement.data if isinstance(advancement, Advancement) else advancement

	if overwrite:
		Mem.ctx.data.advancements[path] = set_json_encoder(Advancement(new_data), max_level=max_level)
	else:
		# Merge the new data with existing data
		merged_data: JsonDict = super_merge_dict(existing_data, new_data)
		Mem.ctx.data.advancements[path] = set_json_encoder(Advancement(merged_data), max_level=max_level)

# Functions
def write_tag(
	path: str,
	tag_type: NamespaceProxy[Any] | NamespaceContainer[Any],
	values: list[Any] | None = None,
	prepend: bool = False,
	max_level: int | None = None,
	condition: Callable[[list[Any]], bool] = lambda existing_values: True,
) -> None:
	""" Write a function tag at the given path.

	Args:
		path        (str):  The path to the function tag (ex: "namespace:something" for 'data/namespace/tags/function/something.json')
		tag_type    (NamespaceProxy[TagFile]): The tag type to write to (ex: ctx.data.function_tags)
		values      (list[Any] | None): The values to add to the tag
		prepend     (bool): If the values should be prepended instead of appended
		max_level   (int | None):  The maximum level of the JSON dump, None for default behavior (default: None)
		condition   (Callable[[list[Any]], bool]): A function that takes the existing values and returns whether the new values should be written (default: always write)
	"""
	if path.endswith(".json"):
		path = path[:-len(".json")]
	tag: TagFile = tag_type.setdefault(path)
	data: JsonDict = tag.data

	# Check condition with existing values
	existing_values: list[Any] = data.get("values")
	if not condition([] if existing_values is None else existing_values): return

	if not existing_values:
		data["values"] = values or []

	if prepend:
		data["values"] = (values or []) + data["values"]
	else:
		data["values"].extend(values or [])
	data["values"] = stp.unique_list(data["values"])
	if max_level is None:
		tag.encoder = stp.json_dump
	else:
		tag.encoder = lambda x: stp.json_dump(x, max_level=max_level)

def write_function_tag(
	path: str,
	functions: list[Any] | None = None,
	prepend: bool = False,
	max_level: int | None = None,
	condition: Callable[[list[Any]], bool] = lambda existing_values: True,
) -> None:
	""" Write a function tag at the given path.

	Args:
		path        (str):  The path to the function tag (ex: "namespace:something" for 'data/namespace/tags/function/something.json')
		functions   (list[Any] | None): The functions to add to the tag
		prepend     (bool): If the functions should be prepended instead of appended
		max_level   (int | None):  The maximum level of the JSON dump, None for default behavior (default: None)
		condition   (Callable[[list[Any]], bool]): A function that takes the existing functions and returns whether the new functions should be written (default: always write)
	"""
	return write_tag(path, Mem.ctx.data.function_tags, functions, prepend, max_level, condition)


def read_function(path: str) -> str:
	""" Read the content of a function at the given path.

	Args:
		path (str): The path to the function (ex: "namespace:folder/function_name")

	Returns:
		str: The content of the function, or an empty string if the function does not exist
	"""
	if path.endswith(".mcfunction"):
		path = path[:-len(".mcfunction")]
	return Mem.ctx.data.functions[path].text if path in Mem.ctx.data.functions else ""


def write_function(
	path: str,
	content: str,
	overwrite: bool = False,
	prepend: bool = False,
	tags: list[str] | None = None,
	condition: Callable[[str], bool] | None = None,
) -> None:
	""" Write the content to the function at the given path.

	Args:
		path            (str):  The path to the function (ex: "namespace:folder/function_name")
		content         (str):  The content to write
		overwrite       (bool): If the file should be overwritten (default: Append the content)
		prepend         (bool): If the content should be prepended instead of appended (not used if overwrite is True)
		tags            (list[str] | None): The function tags to add to the function (ex: ["namespace:something"] for 'data/namespace/tags/function/something.json')
		condition       (Callable[[str], bool]): A function that takes the existing content and returns whether the new content should be written (default: always write)
	"""
	if path.endswith(".mcfunction"):
		path = path[:-len(".mcfunction")]

	# Check condition with existing content
	if condition is not None:
		existing_content: str = read_function(path)
		if not condition(existing_content): return

	if overwrite:
		Mem.ctx.data.functions[path] = Function(content)
	else:
		if prepend:
			Mem.ctx.data.functions.setdefault(path).prepend(content)
		else:
			Mem.ctx.data.functions.setdefault(path).append(content)
	if tags:
		for tag in tags:
			write_function_tag(tag, [path], prepend)


def write_versioned_function(
	path: str,
	content: str,
	overwrite: bool = False,
	prepend: bool = False,
	tags: list[str] | None = None,
	condition: Callable[[str], bool] | None = None,
) -> None:
	""" Write the content to a versioned function at the given path.

	Args:
		path            (str):  The path to the function (ex: "folder/function_name")
		content         (str):  The content to write
		overwrite       (bool): If the file should be overwritten (default: Append the content)
		prepend         (bool): If the content should be prepended instead of appended (not used if overwrite is True)
		tags            (list[str] | None): The function tags to add to the function (ex: ["namespace:something"] for 'data/namespace/tags/function/something.json')
		condition       (Callable[[str], bool]): A function that takes the existing content and returns whether the new content should be written (default: always write)
	"""
	return write_function(f"{Mem.ctx.project_id}:v{Mem.ctx.project_version}/{path}", content, overwrite, prepend, tags, condition)


def write_load_file(
	content: str,
	overwrite: bool = False,
	prepend: bool = False,
	tags: list[str] | None = None,
	condition: Callable[[str], bool] | None = None,
) -> None:
	""" Write the content to the load file

	Args:
		content     (str):  The content to write
		overwrite   (bool): If the file should be overwritten (default: Append the content)
		prepend     (bool): If the content should be prepended instead of appended (not used if overwrite is True)
		tags        (list[str] | None): The function tags to add to the function (ex: ["namespace:something"] for 'data/namespace/tags/function/something.json')
		condition   (Callable[[str], bool]): A function that takes the existing content and returns whether the new content should be written (default: always write)
	"""
	return write_versioned_function("load/confirm_load", content, overwrite, prepend, tags, condition)


def write_tick_file(
	content: str,
	overwrite: bool = False,
	prepend: bool = False,
	tags: list[str] | None = None,
	condition: Callable[[str], bool] | None = None,
) -> None:
	""" Write the content to the tick file

	Args:
		content     (str):  The content to write
		overwrite   (bool): If the file should be overwritten (default: Append the content)
		prepend     (bool): If the content should be prepended instead of appended (not used if overwrite is True)
		tags        (list[str] | None): The function tags to add to the function (ex: ["namespace:something"] for 'data/namespace/tags/function/something.json')
		condition   (Callable[[str], bool]): A function that takes the existing content and returns whether the new content should be written (default: always write)
	"""
	return write_versioned_function("tick", content, overwrite, prepend, tags, condition)


def write_scheduled_function(
	duration: int | str,
	content: str,
	unit: str = "t",
	path: str | None = None,
	overwrite: bool = False,
	prepend: bool = False,
	condition: Callable[[str], bool] = lambda existing_content: True,
) -> None:
	""" Write a self-rescheduling function and schedule it on load.

	Args:
		duration	(int | str):	Delay before re-execution. If it's a digit-only string, it is converted to int.
		content		(str):			Function content to execute.
		unit		(str):			Time unit used only when duration is int (default: "t").
		path		(str | None):	Target function path. Defaults to "{project_id}:scheduled/{duration}".
		overwrite	(bool):			If True, overwrite target files instead of appending.
		prepend		(bool):			If True, prepend content instead of appending (ignored when overwrite is True).
		condition	(Callable[[str], bool]): A function that takes the existing content and returns whether the new content should be written (default: always write)
	"""
	# Normalize duration: keep custom string delays (e.g. "5s"), coerce numeric strings to int.
	parsed_duration: int | str = duration.strip() if isinstance(duration, str) else duration
	if isinstance(parsed_duration, str) and parsed_duration.isdigit():
		parsed_duration = int(parsed_duration)

	# Build schedule command and target paths.
	schedule_delay: str = f"{parsed_duration}{unit}" if isinstance(parsed_duration, int) else parsed_duration
	resolved_path: str = path or f"{Mem.ctx.project_id}:scheduled/{schedule_delay}"
	schedule_command: str = f"schedule function {resolved_path} {schedule_delay}"
	content_stripped: str = content.strip("\n")

	# Read existing contents for condition check and idempotent writes
	existing_scheduled_content: str = read_function(resolved_path) if resolved_path in Mem.ctx.data.functions else ""
	if not condition(existing_scheduled_content): return

	# Overwrite mode always refreshes both scheduled function and load registration.
	if overwrite:
		body: str = f"# Wait for {schedule_delay}\n{schedule_command}"
		if content_stripped:
			body = f"{body}\n\n{content_stripped}"
		write_load_file(f"# Schedule function for {schedule_delay}\n{schedule_command} replace", overwrite=True, prepend=prepend)
		return write_function(path=resolved_path, content=body, overwrite=True, prepend=prepend)

	write_load_file(f"# Schedule function for {schedule_delay}\n{schedule_command} replace", overwrite=False, prepend=prepend, condition=lambda existing: schedule_command not in existing)

	# Append/prepend mode: avoid duplicating schedule lines and duplicate content blocks.
	if schedule_command not in existing_scheduled_content:
		body = f"# Wait for {schedule_delay}\n{schedule_command}"
		if content_stripped:
			body = f"{body}\n\n{content_stripped}"
		return write_function(path=resolved_path, content=body, overwrite=False, prepend=prepend)
	elif content_stripped and content_stripped not in existing_scheduled_content:
		return write_function(path=resolved_path, content=content_stripped, overwrite=False, prepend=prepend)


# Merge two dict recuirsively
def super_merge_dict(dict1: JsonDict, dict2: JsonDict) -> JsonDict:
	""" Merge the two dictionnaries recursively without modifying originals
	Args:
		dict1 (dict): The first dictionnary
		dict2 (dict): The second dictionnary
	Returns:
		dict: The merged dictionnary
	"""
	# Copy first dictionnary
	new_dict: JsonDict = {}
	for key, value in dict1.items():
		new_dict[key] = value

	# For each key of the second dictionnary,
	for key, value in dict2.items():

		# If key exists in dict1, and both values are also dict, merge recursively
		if key in dict1 and isinstance(dict1[key], dict) and isinstance(value, dict):
			new_dict[key] = super_merge_dict(dict1[key], cast(JsonDict, value))

		# Else if it's a list, merge it
		elif key in dict1 and isinstance(dict1[key], list) and isinstance(value, list):
			new_dict[key] = dict1[key] + value
			if not any(isinstance(x, dict) for x in new_dict[key]):
				new_dict[key] = stp.unique_list(new_dict[key])

		# Else, just overwrite or add value
		else:
			new_dict[key] = value

	# Return the new dict
	return new_dict


# Set the JSON encoder to json_dump for a JsonFile object
def set_json_encoder[JsonFileT: JsonFile](
	obj: JsonFileT, max_level: int | None = None, indent: str | int = '\t'
) -> JsonFileT:
	""" Set the encoder of the given object to json_dump

	Args:
		obj			(JsonFile):		The object to set the encoder for
		max_level	(int | None):	The maximum level of the JSON dump, or None for default behavior
		indent		(str | int):	The indentation character (default: '\t')
	Returns:
		JsonFile: The object with the encoder set
	"""
	if max_level is None:
		obj.encoder = lambda x: stp.json_dump(x, indent=indent)
	else:
		obj.encoder = lambda x: stp.json_dump(x, max_level=max_level, indent=indent)
	return obj


# Convert objects with to_dict() to JSON-serializable forms
def convert_to_serializable(obj: Any) -> Any:
	""" Recursively convert objects to JSON-serializable forms.

	Objects with a `to_dict()` method are converted to their dictionary representation.
	Dictionaries and lists are recursively processed.

	Args:
		obj (Any): The object to convert
	Returns:
		Any: The JSON-serializable version of the object
	"""
	if hasattr(obj, 'to_dict'):
		return obj.to_dict()
	elif isinstance(obj, dict):
		return {k: convert_to_serializable(v) for k, v in obj.items()} # type: ignore
	elif isinstance(obj, list):
		return [convert_to_serializable(item) for item in obj] # type: ignore
	else:
		return obj


# Create a texture object with mcmeta if found
def texture_mcmeta(source_path: str) -> Texture:
	""" Create a Texture object with mcmeta if found

	Args:
		source_path (str): The path to the texture (ex: "assets/textures/texture_name.png")
	Returns:
		Texture: The texture object
	"""
	mcmeta_path: str = f"{source_path}.mcmeta"
	if os.path.exists(mcmeta_path):
		return Texture(source_path=source_path, mcmeta=stp.json_load(mcmeta_path))
	return Texture(source_path=source_path)

