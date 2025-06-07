
# Imports
from beet import Context
from stouputils.decorators import measure_time

from ....core.utils.io import read_function, write_function
from .object import Header


# Main entry point
@measure_time(message="Executing")
def beet_default(ctx: Context):
    """ Main entry point for the lang file plugin.

    Args:
        ctx (Context): The beet context.
    """
    # Get all mcfunctions paths
    mcfunctions: dict[str, Header] = {}
    for path in ctx.data.functions:
        # Create a Header object from the function content
        content: str = read_function(path)
        mcfunctions[path] = Header.from_content(path, content)


    # For each function tag, get the functions that it calls
    for tag_path, tag in ctx.data.function_tags.items():
        # Get string that is used for calling the function (ex: "#namespace:my_function")
        to_be_called: str = f"#{tag_path}"

        # Loop through the functions in the tag
        for function_path in tag.data["values"]:
            if isinstance(function_path, str):
                if function_path in mcfunctions:
                    mcfunctions[function_path].within.append(to_be_called)
            elif isinstance(function_path, dict):
                function_path: str = function_path.get("id", "")
                if function_path in mcfunctions:
                    mcfunctions[function_path].within.append(to_be_called)


    # For each advancement, get the functions that it calls
    for adv_path, adv in ctx.data.advancements.items():
        # Get string that is used for calling the function (ex: "advancement namespace:my_function")
        to_be_called: str = f"advancement {adv_path}"

        # Check if the advancement has a function reward
        if adv.data.get("rewards", {}).get("function"):
            function_path: str = adv.data["rewards"]["function"]
            if function_path in mcfunctions:
                mcfunctions[function_path].within.append(to_be_called)


    # For each mcfunction file, look at each line
    for path, header in mcfunctions.items():
        for line in header.content.split("\n"):

            # If the line calls a function
            if "function " in line:
                # Get the called function
                splitted: list[str] = line.split("function ", 1)[1].replace("\n", "").split(" ")
                calling: str = splitted[0].replace('"', '').replace("'", "")

                # Get additional text like macros, ex: function iyc:function {id:"51"}
                more: str = ""
                if len(splitted) > 1:
                    more = " " + " ".join(splitted[1:])  # Add Macros or schedule time

                # If the called function is registered, append the name of this file as well as the additional text
                if calling in mcfunctions and (path + more) not in mcfunctions[calling].within:
                    mcfunctions[calling].within.append(path + more)


    # For each mcfunction file, write the header
    for path, header in mcfunctions.items():
        write_function(path, header.to_str(), overwrite=True)

