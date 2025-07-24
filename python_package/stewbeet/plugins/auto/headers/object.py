
# Imports
from __future__ import annotations


# Header class
class Header:
    """ A class representing a function header.

    Attributes:
        path (str): The path to the function (ex: "namespace:folder/function_name")
        within (list[str]): List of functions that call this function
        other (list[str]): List of other information about the function
        content (str): The content of the function
        executed (str): The execution context (ex: "as the player & at current position")

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
    def __init__(self, path: str, within: list[str] | None = None, other: list[str] | None = None, content: str = "", executed: str | None = None):
        self.path = path
        self.within = within or []
        self.other = other or []
        self.content = content
        self.executed = executed or ""

    @classmethod
    def from_content(cls, path: str, content: str) -> Header:
        """ Create a Header object from a function's content.

        Args:
            path (str): The path to the function
            content (str): The content of the function

        Returns:
            Header: A new Header object

        Examples:
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

            >>> alt_launch_content = '''
            ... #> alt_launch
            ... #
            ... # @executed			as the player & at current position
            ... #
            ... # @input macro		target : string - target selector for position and rotation source
            ... # @input macro		time : int - time in ticks
            ... # @input macro		with : compound - additional arguments (optional)
            ... #						- yaw : float - yaw rotation (will override target rotation)
            ... #						- pitch : float - pitch rotation (will override target rotation)
            ... #						- go_side : float - how far to go side (0 = don't go side)
            ... #						- add_y : float - additional y position (default: 20.0)
            ... #						- particle : int - particle effect (0 = none, 1 = glow)
            ... #						- interpolation : int - teleport duration (default: 1)
            ... #						- delay : int - delay in ticks before starting (default: 0)
            ... #
            ... # @description		Launch a cinematic that moves the player to the position and rotation of a target entity
            ... #
            ... # @example			/execute as @s positioned 0 69 0 rotated -55 10 run function switch:cinematic/alt_launch
            ... #					{target:"@s",time:60,with:{go_side:1,add_y:20.0,particle:1,interpolation:1,delay:20}}
            ... #
            ...
            ... function content here'''
            >>> alt_header = Header.from_content("alt_launch", alt_launch_content)
            >>> len(alt_header.other) > 10  # Should capture all the @executed, @input, @description, @example lines
            True
        """
        # Initialize empty lists
        within: list[str] = []
        other: list[str] = []
        executed: str = ""
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

        return cls(path, within, other, actual_content, executed)

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
        header = f"\n#> {self.path}\n#\n"

        # Add the executed context (only if known)
        if self.executed:
            header += f"# @executed\t{self.executed.strip()}\n#\n"

        # Add the within list
        if self.within:
            header += "# @within\t" + "\n#\t\t\t".join(self.within) + "\n#\n"
        else:
            header += "# @within\t???\n#\n"

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
# @input macro		target : string - target selector for position and rotation source
# @input macro		time : int - time in ticks
# @input macro		with : compound - additional arguments (optional)
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
