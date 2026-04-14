
# Imports
import os
from collections.abc import Callable
from typing import Any, TypeVar, cast

import stouputils as stp
from beet import Advancement, Function, JsonFile, NamespaceContainer, NamespaceProxy, TagFile, Texture
from stouputils.typing import JsonDict

from ..__memory__ import Mem

# Constants
JsonFileT = TypeVar("JsonFileT", bound=JsonFile)

# Advancements
def write_advancement(
	path: str,
	advancement: Advancement | JsonDict,
	overwrite: bool = False,
	max_level: int = -1,
	condition: Callable[[JsonDict], bool] = lambda existing_data: True, # pyright: ignore[reportUnknownLambdaType]
) -> Advancement | None:
	""" Write an advancement at the given path.

	Args:
		path        (str):                         The path to the advancement (ex: "namespace:folder/advancement_name")
		advancement (Advancement | JsonDict):      The advancement to write
		overwrite   (bool):                        If the file should be overwritten (default: Merge with existing content using super_merge_dict)
		max_level   (int):                         The maximum level of the JSON dump, -1 for default behavior (default: -1)
		condition   (Callable[[JsonDict], bool]):  A function that takes the existing advancement data
			and returns whether the new advancement should be written (default: always write)
	Returns:
		Advancement | None: The written advancement, or None if the condition was not met
	"""
	path = path.removesuffix(".json")  # Remove .json extension if present

	# Get existing advancement or create empty one, and check condition with its data
	existing_data: JsonDict = Mem.ctx.data.advancements.get(path, Advancement()).data
	if not condition(existing_data):
		return None

	# Convert to dict if it's an Advancement object
	new_data: JsonDict = advancement.data if isinstance(advancement, Advancement) else advancement

	if overwrite or not existing_data:
		adv: Advancement = set_json_encoder(Advancement(new_data), max_level=max_level)
	else:
		# Merge the new data with existing data
		merged_data: JsonDict = super_merge_dict(existing_data, new_data)
		adv: Advancement = set_json_encoder(Advancement(merged_data), max_level=max_level)

	# Write the advancement to memory and return it
	Mem.ctx.data.advancements[path] = adv
	return adv

# Functions
def write_tag(
	path: str,
	tag_type: NamespaceProxy[Any] | NamespaceContainer[Any],
	values: list[Any] | None = None,
	prepend: bool = False,
	max_level: int | None = None,
	condition: Callable[[list[Any]], bool] = lambda existing_values: True, # pyright: ignore[reportUnknownLambdaType]
) -> TagFile | None:
	""" Write a function tag at the given path.

	Args:
		path        (str):                          The path to the function tag (ex: "namespace:something" for 'data/namespace/tags/function/something.json')
		tag_type    (NamespaceProxy[TagFile]):      The tag type to write to (ex: ctx.data.function_tags)
		values      (list[Any] | None):             The values to add to the tag
		prepend     (bool):                         If the values should be prepended instead of appended
		max_level   (int | None):                   The maximum level of the JSON dump, None for default behavior (default: None)
		condition   (Callable[[list[Any]], bool]):  A function that takes the existing values and returns whether the new values should be written (default: always write)
	Returns:
		TagFile | None: The written tag, or None if the condition was not met
	"""
	path = path.removesuffix(".json")  # Remove .json extension if present
	tag: TagFile = tag_type.get(path, TagFile())
	data: JsonDict = tag.data

	# Check condition with existing values
	existing_values: list[Any] = data.get("values", [])
	if not condition(existing_values):
		return None

	# Set empty list if there is no existing values
	if not existing_values:
		data["values"] = cast(list[Any], [])

	# Prepend = (new values) + (existing values)
	# Append = (existing values) + (new values)
	if prepend:
		data["values"] = (values or []) + data["values"]
	else:
		data["values"].extend(values or [])

	# Remove duplicates while preserving order
	data["values"] = stp.unique_list(data["values"])

	# Set encoder to json_dump with max_level if specified, else default behavior
	if max_level is None:
		tag.encoder = stp.json_dump
	else:
		tag.encoder = lambda x: stp.json_dump(x, max_level=max_level)

	# Write the tag to memory and return it
	tag_type[path] = tag
	return tag


def read_function(path: str) -> str:
	""" Read the content of a function at the given path.

	Args:
		path (str): The path to the function (ex: "namespace:folder/function_name")
	Returns:
		str: The content of the function, or an empty string if the function does not exist
	"""
	path = path.removesuffix(".mcfunction")  # Remove .mcfunction extension if present
	return Mem.ctx.data.functions.get(path, Function()).text


def write_function(
	path: str,
	content: str,
	overwrite: bool = False,
	prepend: bool = False,
	tags: list[str] | None = None,
	condition: Callable[[str], bool] | None = lambda existing_content: True, # pyright: ignore[reportUnknownLambdaType]
) -> Function | None:
	""" Write the content to the function at the given path.

	Args:
		path            (str):                    The path to the function (ex: "namespace:folder/function_name")
		content         (str):                    The content to write
		overwrite       (bool):                   If the file should be overwritten (default: Append the content)
		prepend         (bool):                   If the content should be prepended instead of appended (not used if overwrite is True)
		tags            (list[str] | None):       The function tags to add to the function (ex: ["namespace:something"] for 'data/namespace/tags/function/something.json')
		condition       (Callable[[str], bool]):  A function that takes the existing content and returns whether the new content should be written (default: always write)
	Returns:
		Function | None: The written function, or None if the condition was not met
	"""
	path = path.removesuffix(".mcfunction")

	# Check condition with existing content
	if condition is not None:
		existing_content: str = read_function(path)
		if not condition(existing_content):
			return None

	# Overwrite, prepend, or append content to the function
	if overwrite:
		func = Function(content)
		Mem.ctx.data.functions[path] = func
	else:
		if prepend:
			func = Mem.ctx.data.functions.setdefault(path, Function())
			func.prepend(content)
		else:
			func = Mem.ctx.data.functions.setdefault(path, Function())
			func.append(content)

	# Add the function to the specified tags
	if tags:
		for tag in tags:
			write_tag(tag, Mem.ctx.data.function_tags, [path], prepend)

	# Return the written function
	return func


def write_versioned_function(
	path: str,
	content: str,
	overwrite: bool = False,
	prepend: bool = False,
	tags: list[str] | None = None,
	condition: Callable[[str], bool] | None = lambda existing_content: True, # pyright: ignore[reportUnknownLambdaType]
) -> Function | None:
	""" Write the content to a versioned function at the given path.

	Args:
		path            (str):                    The path to the function (ex: "folder/function_name")
		content         (str):                    The content to write
		overwrite       (bool):                   If the file should be overwritten (default: Append the content)
		prepend         (bool):                   If the content should be prepended instead of appended (not used if overwrite is True)
		tags            (list[str] | None):       The function tags to add to the function (ex: ["namespace:something"] for 'data/namespace/tags/function/something.json')
		condition       (Callable[[str], bool]):  A function that takes the existing content and returns whether the new content should be written (default: always write)
	"""
	return write_function(f"{Mem.ctx.project_id}:v{Mem.ctx.project_version}/{path}", content, overwrite, prepend, tags, condition)


def write_load_file(
	content: str,
	overwrite: bool = False,
	prepend: bool = False,
	tags: list[str] | None = None,
	condition: Callable[[str], bool] | None = lambda existing_content: True, # pyright: ignore[reportUnknownLambdaType]
) -> Function | None:
	""" Write the content to the load file

	Args:
		content     (str):                    The content to write
		overwrite   (bool):                   If the file should be overwritten (default: Append the content)
		prepend     (bool):                   If the content should be prepended instead of appended (not used if overwrite is True)
		tags        (list[str] | None):       The function tags to add to the function (ex: ["namespace:something"] for 'data/namespace/tags/function/something.json')
		condition   (Callable[[str], bool]):  A function that takes the existing content and returns whether the new content should be written (default: always write)
	"""
	return write_versioned_function("load/confirm_load", content, overwrite, prepend, tags, condition)


def write_tick_file(
	content: str,
	overwrite: bool = False,
	prepend: bool = False,
	tags: list[str] | None = None,
	condition: Callable[[str], bool] | None = lambda existing_content: True, # pyright: ignore[reportUnknownLambdaType]
) -> Function | None:
	""" Write the content to the tick file

	Args:
		content     (str):                    The content to write
		overwrite   (bool):                   If the file should be overwritten (default: Append the content)
		prepend     (bool):                   If the content should be prepended instead of appended (not used if overwrite is True)
		tags        (list[str] | None):       The function tags to add to the function (ex: ["namespace:something"] for 'data/namespace/tags/function/something.json')
		condition   (Callable[[str], bool]):  A function that takes the existing content and returns whether the new content should be written (default: always write)
	"""
	return write_versioned_function("tick", content, overwrite, prepend, tags, condition)


def write_scheduled_function(
	duration: int | str,
	content: str,
	unit: str = "t",
	path: str | None = None,
	overwrite: bool = False,
	prepend: bool = False,
	condition: Callable[[str], bool] = lambda existing_content: True, # pyright: ignore[reportUnknownLambdaType]
) -> Function | None:
	""" Write a self-rescheduling function and schedule it on load.

	Args:
		duration	(int | str):	         Delay before re-execution. If it's a digit-only string, it is converted to int.
		content		(str):			         Function content to execute.
		unit		(str):			         Time unit used only when duration is int (default: "t").
		path		(str | None):	         Target function path. Defaults to "{project_id}:v{project_version}/scheduled/{duration}".
		overwrite	(bool):			         If True, overwrite target files instead of appending.
		prepend		(bool):			         If True, prepend content instead of appending (ignored when overwrite is True).
		condition	(Callable[[str], bool]): A function that takes the existing content and returns whether the new content should be written (default: always write)
	"""
	# Normalize duration: keep custom string delays (e.g. "5s"), coerce numeric strings to int.
	parsed_duration: int | str = duration.strip() if isinstance(duration, str) else duration
	if isinstance(parsed_duration, str) and parsed_duration.isdigit():
		parsed_duration = int(parsed_duration)

	# Build schedule command and target paths.
	schedule_delay: str = f"{parsed_duration}{unit}" if isinstance(parsed_duration, int) else parsed_duration
	resolved_path: str = path or f"{Mem.ctx.project_id}:v{Mem.ctx.project_version}/scheduled/{schedule_delay}"
	schedule_command: str = f"schedule function {resolved_path} {schedule_delay}"
	content_stripped: str = content.strip("\n")

	# 0. Read existing contents for condition check and idempotent writes
	existing_scheduled_content: str = read_function(resolved_path)
	if not condition(existing_scheduled_content):
		return

	# 1. Ensure the schedule command is in the load file while avoiding duplicates.
	def is_schedule_missing(existing: str) -> bool: return (schedule_command not in existing)
	write_load_file(
		f"# Schedule function for {schedule_delay}\n{schedule_command} replace",
		overwrite=False, prepend=prepend, condition=is_schedule_missing
	)

	# 2. Build function body: schedule self-rescheduling header + optional content
	body_with_reschedule: str = f"# Wait for {schedule_delay}\n{schedule_command}"
	if content_stripped:
		body_with_reschedule = f"{body_with_reschedule}\n\n{content_stripped}"

	# 3.1. Overwrite mode always refreshes scheduled function, but not load registration
	if overwrite:
		write_load_file(f"# Schedule function for {schedule_delay}\n{schedule_command} replace", overwrite=True, prepend=prepend)
		return write_function(path=resolved_path, content=body_with_reschedule, overwrite=True, prepend=prepend)

	# 3.2. Append/prepend mode: avoid duplicating schedule lines and duplicate content blocks.
	func = write_function(path=resolved_path, content=body_with_reschedule, overwrite=False, prepend=prepend, condition=is_schedule_missing)
	if func is None and content_stripped:
		def is_content_missing(existing: str) -> bool: return (content_stripped not in existing)
		return write_function(path=resolved_path, content=content_stripped, overwrite=False, prepend=prepend, condition=is_content_missing)

	# Return the function object
	return func


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



# Deprecated functions
@stp.deprecated(message="convert_to_serializable is deprecated, prefer using stp.convert_to_serializable from stouputils", version="v3.1.3")
def convert_to_serializable(obj: Any) -> Any:
	return stp.convert_to_serializable(obj)


@stp.deprecated(message="write_function_tag is deprecated, prefer using write_tag or `tags` argument of write_function instead", version="v3.1.3")
def write_function_tag(
	path: str,
	functions: list[Any] | None = None,
	prepend: bool = False,
	max_level: int | None = None,
	condition: Callable[[list[Any]], bool] = lambda existing_values: True, # pyright: ignore[reportUnknownLambdaType]
) -> TagFile | None:
	""" write_function_tag is deprecated, prefer using write_tag or `tags` argument of write_function instead """
	return write_tag(path, Mem.ctx.data.function_tags, functions, prepend, max_level, condition)

