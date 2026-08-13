
# Imports
from __future__ import annotations

# Lazy imports (PEP 810), ignored before Python 3.15
from stouputils.lazy import ALWAYS_LAZY

__lazy_modules__ = ALWAYS_LAZY

from beet import Function

from ..constants import CUSTOM_BLOCKS_FOLDER
from .resource import Resource
from .resource_folder import ResourceFolder


# Class
class BlockFunctions(ResourceFolder[Function]):
    """ The mcfunctions generated for one custom block, under "{ns}:custom_blocks/{id}/".

    >>> funcs = BlockFunctions("machine_block")
    >>> funcs.place_main
    'your_namespace:custom_blocks/machine_block/place_main'
    >>> funcs.place_secondary
    'your_namespace:custom_blocks/machine_block/place_secondary'
    >>> funcs.destroy
    'your_namespace:custom_blocks/machine_block/destroy'
    >>> funcs.second
    'your_namespace:custom_blocks/machine_block/second'
    >>> funcs["any_custom_function"]
    'your_namespace:custom_blocks/machine_block/any_custom_function'
    >>> funcs.folder
    'your_namespace:custom_blocks/machine_block'
    """
    __slots__ = ()

    def __init__(self, block_id: str, namespace: str | None = None) -> None:
        """ Build the function accessor of a custom block.

        Args:
            block_id	(str):		The custom block ID, ex: "machine_block"
            namespace	(str|None):	The namespace, defaults to the current project namespace
        """
        super().__init__(Function, f"{CUSTOM_BLOCKS_FOLDER}/{block_id}", namespace)

    # Placement
    @property
    def place_main(self) -> Resource[Function]:
        """ Ran at the block position when the custom block is placed. """
        return self["place_main"]

    @property
    def place_secondary(self) -> Resource[Function]:
        """ Ran as the summoned item_display/item_frame (this is where Block.on_place is appended). """
        return self["place_secondary"]

    @property
    def place_check(self) -> Resource[Function]:
        """ Checks that the placed block is really this custom block before calling place_main. """
        return self["place_check"]

    @property
    def search(self) -> Resource[Function]:
        """ Searches the placed entity for item frame based custom blocks. """
        return self["search"]

    @property
    def get_facing(self) -> Resource[Function]:
        """ Computes the facing of the custom block from the player orientation. """
        return self["get_facing"]

    # Destruction
    @property
    def destroy(self) -> Resource[Function]:
        """ Ran when the custom block is destroyed. """
        return self["destroy"]

    @property
    def replace_item(self) -> Resource[Function]:
        """ Replaces the dropped item with the custom block item. """
        return self["replace_item"]

    # Growing seeds
    @property
    def update_seed_model(self) -> Resource[Function]:
        """ Updates the item model of a growing seed to match its current stage. """
        return self["update_seed_model"]

    @property
    def is_fully_grown(self) -> Resource[Function]:
        """ Ran when a growing seed reaches its last stage. """
        return self["is_fully_grown"]

    # Ticking (discovered by plugins.finalyze.custom_blocks_ticking)
    @property
    def tick(self) -> Resource[Function]:
        """ Ran every tick as the custom block entity. """
        return self["tick"]

    @property
    def tick_2(self) -> Resource[Function]:
        """ Ran every 2 ticks as the custom block entity. """
        return self["tick_2"]

    @property
    def second(self) -> Resource[Function]:
        """ Ran every second as the custom block entity. """
        return self["second"]

    @property
    def second_5(self) -> Resource[Function]:
        """ Ran every 5 seconds as the custom block entity. """
        return self["second_5"]

    @property
    def minute(self) -> Resource[Function]:
        """ Ran every minute as the custom block entity. """
        return self["minute"]

