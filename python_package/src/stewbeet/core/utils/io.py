
# Imports
from beet import Function

from ..__memory__ import Mem


# Functions
def read_function(path: str) -> str:
    """ Read the content of a function at the given path.

    Args:
        path (str): The path to the function (ex: "namespace:folder/function_name")

    Returns:
        str: The content of the function
    """
    f: Function = Mem.ctx.data.functions[path]
    return f.to_str(f.lines)


def write_function(path: str, content: str, overwrite: bool = False, prepend: bool = False) -> None:
    """ Write the content to the function at the given path.

    Args:
        path            (str):  The path to the function (ex: "namespace:folder/function_name")
        content         (str):  The content to write
        overwrite       (bool): If the file should be overwritten (default: Append the content)
        prepend         (bool): If the content should be prepended instead of appended (not used if overwrite is True)
    """
    if overwrite:
        Mem.ctx.data.functions[path] = Function(content)
    else:
        if prepend:
            Mem.ctx.data.functions.setdefault(path).prepend(content)
        else:
            Mem.ctx.data.functions.setdefault(path).append(content)


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

