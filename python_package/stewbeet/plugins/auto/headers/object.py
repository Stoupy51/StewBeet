
# Imports
from __future__ import annotations

# Lazy imports (PEP 810), ignored before Python 3.15
from stouputils.lazy import ALWAYS_LAZY

__lazy_modules__ = ALWAYS_LAZY


# Header class
class Header:
    """ A class representing a function header.

    Examples:
        >>> header = Header("test:function", ["other:function"], ["Some info"], "say Hello")
        >>> header.path
        'test:function'
        >>> header.within
        ['other:function']
        >>> header.other
        ['Some info']
        >>> header.content
        'say Hello'
    """
    __slots__ = {
        "args": "Dictionary mapping macro argument names to (type, description_lines), "
                "where description_lines is a list of strings (empty list if no description)",
        "content": "The content of the function",
        "executed": "The execution context (ex: \"as the player & at current position\")",
        "other": "List of other information about the function",
        "path": "The path to the function (ex: \"namespace:folder/function_name\")",
        "within": "List of functions that call this function",
    }

    def __init__(
        self,
        path: str,
        within: list[str] | None = None,
        other: list[str] | None = None,
        content: str = "",
        executed: str | None = None,
        args: dict[str, tuple[str, list[str]]] | None = None
    ):
        self.path = path
        self.within = within or []
        self.other = other or []
        self.content = content
        self.executed = executed or ""
        self.args = args or {}

    @classmethod
    def from_content(cls, path: str, content: str) -> Header:
        """ Create a Header object from a function's content.

        Args:
            path (str): The path to the function
            content (str): The content of the function

        Returns:
            Header: A new Header object

        Examples:
            Basic function without args:
            >>> content = '''
            ... #> test:function
            ... #
            ... # @within    other:function
            ... # Some info
            ... #
            ... say Hello'''
            >>> header = Header.from_content("test:function", content)
            >>> header.path
            'test:function'
            >>> header.within
            ['other:function']
            >>> header.other
            ['Some info']
            >>> header.content
            'say Hello'

            Macro function with args (like StardustFragment teleport_to):
            >>> tp_header = Header("stardust:dimensions/teleport_to",
            ...                    ["stardust:dimensions/teleport_home with storage stardust:main world_spawn"],
            ...                    [],
            ...                    "$execute in $(dimension) run tp @s $(x) $(y) $(z)",
            ...                    "in stardust:cavern",
            ...                    {'dimension': ('string', []), 'x': ('int', []), 'y': ('int', []), 'z': ('int', [])})
            >>> tp_header.executed
            'in stardust:cavern'
            >>> tp_header.args['dimension']
            ('string', [])
            >>> tp_header.args['x']
            ('int', [])
            >>> len(tp_header.args)
            4

            Macro function with args and descriptions (like SimplEnergy update_energy_lore):
            >>> lore_header = Header("simplenergy:calls/update_energy_lore/macro",
            ...                      ["simplenergy:calls/update_energy_lore/main with storage simplenergy:temp macro"],
            ...                      [],
            ...                      "$data modify storage energy:temp list[0] set value $(part_1)",
            ...                      "",
            ...                      {'part_1': ('int', ['first part of energy value']),
            ...                       'part_2': ('int', ['second part of energy value']),
            ...                       'scale': ('string', ['energy scale suffix'])})
            >>> lore_header.args['part_1']
            ('int', ['first part of energy value'])
            >>> lore_header.args['part_2']
            ('int', ['second part of energy value'])
            >>> lore_header.args['scale']
            ('string', ['energy scale suffix'])

            Function with compound type and multi-line description:
            >>> comp_header = Header("test:compound_func",
            ...                      [],
            ...                      [],
            ...                      "function content",
            ...                      "",
            ...                      {'config': ('compound', ['configuration object',
            ...                                                '- duration : int - how long in ticks',
            ...                                                '- power : float - effect strength'])})
            >>> comp_header.args['config']
            ('compound', ['configuration object', '- duration : int - how long in ticks', '- power : float - effect strength'])
        """
        # Initialize empty lists
        within: list[str] = []
        other: list[str] = []
        executed: str = ""
        args: dict[str, tuple[str, list[str]]] = {}
        actual_content: str = content.strip()

        # If the content has a header, parse it
        if content.strip().startswith("#> "):
            # Split the content into lines
            lines: list[str] = content.strip().split("\n")

            # Skip the first line (#> path) and the second line (#)
            i: int = 2

            # Parse executed section
            if i < len(lines) and lines[i].strip().startswith("# @executed"):
                executed_line: str = lines[i].strip()
                if executed_line != "# @executed":
                    # Extract the execution context after @executed
                    executed = executed_line.split("@executed")[1].strip()
                i += 1

            # Skip empty comment lines
            while i < len(lines) and lines[i].strip() == "#":
                i += 1

            # Parse args section
            if i < len(lines) and lines[i].strip().startswith("# @args"):
                args_line: str = lines[i].strip()
                current_arg: str | None = None
                current_type: str = ""
                current_description: list[str] = []

                # Check if there's an argument on the same line as @args
                import re
                # Remove "# @args" and any tabs/spaces after it
                args_content: str = re.sub(r'^#\s*@args\s+', '', args_line)
                if args_content:
                    # There's an argument on the same line
                    # Try to match with description
                    match: re.Match[str] | None = re.match(r'(\w+)\s*\((\w+)\)\s*:\s*(.+)', args_content)
                    if match:
                        current_arg, current_type, desc = match.groups()
                        current_description = [desc]
                    else:
                        # Try to match without description
                        match = re.match(r'(\w+)\s*\((\w+)\)', args_content)
                        if match:
                            current_arg, current_type = match.groups()
                            current_description = []

                i += 1  # Move to next line
                # Parse argument lines until we hit a non-indented comment or empty line

                while i < len(lines) and lines[i].strip().startswith("#"):
                    arg_line: str = lines[i].strip()

                    # Check if it's an indented argument line (starts with # followed by whitespace)
                    if arg_line.startswith("#") and len(arg_line) > 1 and arg_line[1].isspace():
                        arg_content: str = arg_line[1:].strip()

                        # Check if it's a sub-description line (starts with -)
                        if arg_content.startswith("-"):
                            # This is a description line for compound type
                            if current_arg:
                                current_description.append(arg_content)
                        else:
                            # Save previous argument if exists
                            if current_arg:
                                args[current_arg] = (current_type, current_description[:])

                            # Parse new argument (format: "arg_name (type): description" or "arg_name (type)")
                            # Try to match with description
                            match = re.match(r'(\w+)\s*\((\w+)\)\s*:\s*(.+)', arg_content)
                            if match:
                                current_arg, current_type, desc = match.groups()
                                current_description = [desc]
                            else:
                                # Try to match without description
                                match = re.match(r'(\w+)\s*\((\w+)\)', arg_content)
                                if match:
                                    current_arg, current_type = match.groups()
                                    current_description = []
                                else:
                                    current_arg = None
                    elif arg_line == "#":
                        # Empty comment line might end args section or be part of description
                        # We'll treat it as end of args section
                        break
                    else:
                        # Non-indented line ends args section
                        break
                    i += 1

                # Save the last argument if exists
                if current_arg:
                    args[current_arg] = (current_type, current_description[:])

            # Skip empty comment lines
            while i < len(lines) and lines[i].strip() == "#":
                i += 1

            # Parse within section
            while i < len(lines) and lines[i].strip().startswith("# @within"):
                within_line: str = lines[i].strip()
                if within_line != "# @within":
                    # Extract the function name after @within
                    func_name: str = within_line.split("@within")[1].strip()
                    within.append(func_name)
                i += 1

            # Skip empty comment lines
            while i < len(lines) and lines[i].strip() == "#":
                i += 1

            # Parse other information (without # prefix)
            while i < len(lines) and lines[i].strip().startswith("#"):
                other_line: str = lines[i].strip()
                other.append(other_line[2:])
                i += 1

            # Skip any remaining empty comment lines
            while i < len(lines) and lines[i].strip() == "#":
                i += 1

            # The remaining lines are the actual content
            actual_content = "\n".join(lines[i:]).strip()

        if other and other[-1] == "":
            # Remove the last empty line if it exists
            other.pop()

        return cls(path, within, other, actual_content, executed, args)

    def to_str(self) -> str:
        """ Convert the Header object to a string.

        Returns:
            str: The function content with the header

        Examples:
            >>> content = '''
            ... #> test:function
            ... #
            ... # @within\\tother:function
            ... #
            ... # Some info
            ... #
            ...
            ... say Hello\\n\\n'''
            >>> header = Header("test:function", ["other:function"], ["Some info"], "say Hello")
            >>> content.strip() == header.to_str().strip()
            True
            >>> content_lines = content.splitlines()
            >>> header_lines = header.to_str().splitlines()
            >>> for i, (c, h) in enumerate(zip(content_lines, header_lines)):
            ...     if c != h:
            ...         print(f"Difference at line {i}:")
            ...         print(f"Content:  {c}")
            ...         print(f"Header:   {h}")
            ...         break
        """
        # Start with the path
        header: str = f"\n#> {self.path}\n#\n"

        # Add the executed context (only if known)
        if self.executed:
            executed: str = self.executed.strip()
            executed: str = "".join(
                x for i, x in enumerate(executed)
                if x != " " or (i > 0 and executed[i - 1] not in ":,")
            )
            header += f"# @executed\t{executed}\n#\n"

        # Add the within list
        if self.within:
            header += "# @within\t" + "\n#\t\t\t".join(self.within) + "\n#\n"
        else:
            header += "# @within\t???\n#\n"

        # Add the args section (only if there are arguments)
        if self.args:
            header += "# @args\t\t"
            # Preserve insertion order of args (first-introduced order).
            arg_lines: list[str] = []
            for arg_name, (arg_type, description_lines) in self.args.items():
                # First line: arg_name (type): description (or just arg_name (type) if no description)
                if description_lines:
                    # First description line goes on same line as arg
                    first_line: str = f"{arg_name} ({arg_type}): {description_lines[0]}"
                    arg_lines.append(first_line)
                    # Additional description lines (for compound types)
                    for desc_line in description_lines[1:]:
                        arg_lines.append(f"\t\t\t\t{desc_line}")
                else:
                    # No description
                    arg_lines.append(f"{arg_name} ({arg_type})")

            header += "\n#\t\t\t".join(arg_lines) + "\n#\n"

        # Add other information
        for line in self.other:
            header += f"# {line}\n"

        # Add final empty line and content
        if not header.endswith("#\n"):
            header += "#\n"
        return (header + "\n" + self.content.strip() + "\n\n").replace("\n\n\n", "\n\n")

if __name__ == "__main__":
    # Example usage
    example_content = """
#> alt_launch
#
# @executed			as the player & at current position
#
# @args				target (string): target selector for position and rotation source
#					time (int): time in ticks
#					with (compound): additional arguments (optional)
#						- yaw : float - yaw rotation (will override target rotation)
#						- pitch : float - pitch rotation (will override target rotation)
#						- go_side : float - how far to go side (0 = don't go side)
#						- add_y : float - additional y position (default: 20.0)
#						- particle : int - particle effect (0 = none, 1 = glow)
#						- interpolation : int - teleport duration (default: 1)
#						- delay : int - delay in ticks before starting (default: 0)
#
# @description		Launch a cinematic that moves the player to the position and rotation of a target entity
#
# @example			/execute as @s positioned 0 69 0 rotated -55 10 run function switch:cinematic/alt_launch {target:"@s",time:60,with:{go_side:1,add_y:20.0,particle:1,interpolation:1,delay:20}}
#

# Fonction content here
"""
    header = Header.from_content("alt_launch", example_content)
    print(header.to_str())
