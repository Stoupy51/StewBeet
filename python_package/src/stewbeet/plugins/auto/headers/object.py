
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
    def __init__(self, path: str, within: list[str] | None = None, other: list[str] | None = None, content: str = ""):
        self.path = path
        self.within = within or []
        self.other = other or []
        self.content = content

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
        """
        # Initialize empty lists
        within: list[str] = []
        other: list[str] = []
        actual_content: str = content.strip()

        # If the content has a header, parse it
        if content.strip().startswith("#> "):
            # Split the content into lines
            lines: list[str] = content.strip().split("\n")

            # Skip the first line (#> path) and the second line (#)
            i: int = 2

            # Parse within section
            while i < len(lines) and lines[i].strip().startswith("# @within"):
                within_line: str = lines[i].strip()
                if within_line != "# @within":
                    # Extract the function name after @within
                    func_name: str = within_line.split("@within")[1].strip()
                    within.append(func_name)
                i += 1

            # Skip empty lines
            while i < len(lines) and lines[i].strip() == "#":
                i += 1

            # Parse other information
            while i < len(lines) and lines[i].strip().startswith("# "):
                other_line: str = lines[i].strip()
                if other_line != "#":
                    # Remove the # prefix and add to other
                    other.append(other_line[2:].strip())
                i += 1

            # Skip empty lines
            while i < len(lines) and lines[i].strip() == "#":
                i += 1

            # The remaining lines are the actual content
            actual_content = "\n".join(lines[i:]).strip()

        return cls(path, within, other, actual_content)

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

