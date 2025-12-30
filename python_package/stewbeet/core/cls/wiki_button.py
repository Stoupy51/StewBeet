
# Imports
from typing import Any

from beet.core.utils import TextComponent


# Class
class WikiButton:
    """ Represents a button in the ingame manual that provides additional information about an item.

    >>> content = [{"text": "Hello", "color": "yellow"}]
    >>> button = WikiButton(content)
    >>> button.content
    [{'text': 'Hello', 'color': 'yellow'}]
    >>> button.content[0]
    {'text': 'Hello', 'color': 'yellow'}
    >>> WikiButton(button.content[0]).content["text"]
    'Hello'
    """
    __slots__ = ('content',)

    def __init__(self, content: TextComponent) -> None:
        self.content = content

    def __repr__(self) -> str:
        return f"WikiButton({self.content!r})"

    def to_dict(self) -> str | list[Any] | dict[str, Any]:
        """ Convert to JSON-serializable format (returns the underlying TextComponent). """
        return self.content

