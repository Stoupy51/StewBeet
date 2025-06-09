
# Imports
from typing import Any

from beet import Function, FunctionTag
from beet.core.utils import JsonDict
from stouputils.collections import unique_list
from stouputils.io import super_json_dump

from ..__memory__ import Mem


# Functions
def write_function_tag(path: str, functions: list[Any] | None = None, prepend: bool = False) -> None:
    """ Write a function tag at the given path.

    Args:
        path        (str):  The path to the function tag (ex: "namespace:something" for 'data/namespace/tags/function/something.json')
        functions   (list[Any] | None): The functions to add to the tag
        prepend     (bool): If the functions should be prepended instead of appended
    """
    tag: FunctionTag = Mem.ctx.data.function_tags.setdefault(path)
    data: JsonDict = tag.data
    if not data.get("values"):
        data["values"] = functions or []

    if prepend:
        data["values"] = functions + data["values"]
    else:
        data["values"].extend(functions or [])
    data["values"] = unique_list(data["values"])
    tag.encoder = super_json_dump


def read_function(path: str) -> str:
    """ Read the content of a function at the given path.

    Args:
        path (str): The path to the function (ex: "namespace:folder/function_name")

    Returns:
        str: The content of the function
    """
    return Mem.ctx.data.functions[path].text


def write_function(path: str, content: str, overwrite: bool = False, prepend: bool = False, tags: list[str] | None = None) -> None:
    """ Write the content to the function at the given path.

    Args:
        path            (str):  The path to the function (ex: "namespace:folder/function_name")
        content         (str):  The content to write
        overwrite       (bool): If the file should be overwritten (default: Append the content)
        prepend         (bool): If the content should be prepended instead of appended (not used if overwrite is True)
        tags            (list[str] | None): The function tags to add to the function (ex: ["namespace:something"] for 'data/namespace/tags/function/something.json')
    """
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


def write_load_file(content: str, overwrite: bool = False, prepend: bool = False) -> None:
    """ Write the content to the load file

    Args:
        content     (str):  The content to write
        overwrite   (bool): If the file should be overwritten (default: Append the content)
        prepend     (bool): If the content should be prepended instead of appended (not used if overwrite is True)
    """
    write_function(f"{Mem.ctx.project_id}:v{Mem.ctx.project_version}/load/confirm_load", content, overwrite, prepend)


def write_tick_file(content: str, overwrite: bool = False, prepend: bool = False) -> None:
    """ Write the content to the tick file

    Args:
        content     (str):  The content to write
        overwrite   (bool): If the file should be overwritten (default: Append the content)
        prepend     (bool): If the content should be prepended instead of appended (not used if overwrite is True)
    """
    write_function(f"{Mem.ctx.project_id}:v{Mem.ctx.project_version}/tick", content, overwrite, prepend)


def write_versioned_function(path: str, content: str, overwrite: bool = False, prepend: bool = False) -> None:
    """ Write the content to a versioned function at the given path.

    Args:
        path            (str):  The path to the function (ex: "folder/function_name")
        content         (str):  The content to write
        overwrite       (bool): If the file should be overwritten (default: Append the content)
        prepend         (bool): If the content should be prepended instead of appended (not used if overwrite is True)
    """
    write_function(f"{Mem.ctx.project_id}:v{Mem.ctx.project_version}/{path}", content, overwrite, prepend)


# Merge two dict recuirsively
def super_merge_dict(dict1: dict, dict2: dict) -> dict:
	""" Merge the two dictionnaries recursively without modifying originals
	Args:
		dict1 (dict): The first dictionnary
		dict2 (dict): The second dictionnary
	Returns:
		dict: The merged dictionnary
	"""
	# Copy first dictionnary
	new_dict = {}
	for key, value in dict1.items():
		new_dict[key] = value

	# For each key of the second dictionnary,
	for key, value in dict2.items():

		# If key exists in dict1, and both values are also dict, merge recursively
		if key in dict1 and isinstance(dict1[key], dict) and isinstance(value, dict):
			new_dict[key] = super_merge_dict(dict1[key], value)

		# Else if it's a list, merge it
		elif key in dict1 and isinstance(dict1[key], list) and isinstance(value, list):
			new_dict[key] = dict1[key] + value
			if not any(isinstance(x, dict) for x in new_dict[key]):
				new_dict[key] = unique_list(new_dict[key])

		# Else, just overwrite or add value
		else:
			new_dict[key] = value

	# Return the new dict
	return new_dict

