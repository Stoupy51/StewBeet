
# Imports
from __future__ import annotations

from typing import Any, Self, cast

from beet import (
    DataPack,
    DataPackNamespace,
    NamespaceContainer,
    NamespaceFile,
    NamespaceProxy,
    ResourcePack,
    ResourcePackNamespace,
)

from ..__memory__ import Mem


# Helpers
def resolve_pack(file_type: type[NamespaceFile]) -> DataPack | ResourcePack:
    """ Get the pack (Mem.ctx.data or Mem.ctx.assets) owning the given file type.

    Args:
        file_type (type[NamespaceFile]): The beet file type, ex: LootTable, Function, Model
    Returns:
        DataPack | ResourcePack: The pack owning that file type
    Raises:
        KeyError: If the file type belongs to neither pack.
    """
    if file_type in DataPackNamespace.field_map or file_type in Mem.ctx.data.extend_namespace:
        return Mem.ctx.data
    if file_type in ResourcePackNamespace.field_map or file_type in Mem.ctx.assets.extend_namespace:
        return Mem.ctx.assets
    raise KeyError(f"File type '{file_type.__name__}' belongs to neither ctx.data nor ctx.assets")

def existing_container[FileT: NamespaceFile](file_type: type[FileT], namespace: str) -> NamespaceContainer[FileT] | None:
    """ Get the container holding that file type in that namespace, or None if the namespace is absent.

    Read-only counterpart of `Resource.container`: it never creates anything, and resolves the pack
    only once (going through `Resource.pack` then `Resource.container` resolves it twice).

    Note: the namespace is looked up by iterating the pack, because both `namespace in pack` and
    `pack.get(namespace)` route through Pack.missing(), which *creates* the namespace.

    Args:
        file_type	(type[FileT]):	The beet file type, ex: LootTable, Function, Model
        namespace	(str):			The namespace to look up, ex: "your_namespace"
    Returns:
        NamespaceContainer[FileT] | None: The container, or None if the namespace isn't in the pack
    """
    pack: DataPack | ResourcePack = resolve_pack(file_type)
    if namespace not in list(pack):
        return None
    # beet types Namespace as Container[type[NamespaceFile], NamespaceContainer[NamespaceFile]],
    # so the file type parameter cannot be carried through the lookup.
    return cast(NamespaceContainer[FileT], pack[namespace][file_type])


# Classes
class Resource[FileT: NamespaceFile](str):
    """ A Minecraft resource location ("namespace:relative/path") that knows its beet file type.

    A Resource **is** a str holding the full resource location, so it compares equal to the plain
    string, hashes the same, works as a dict key, formats in f-strings, and can be passed to every
    writer (write_function, write_tag, write_advancement, ctx.data[...], ...) without conversion.
    On top of that, it gives access to the underlying beet file through `.obj`, `.get()`, ...

    Building resource locations
    >>> from beet import Function, LootTable
    >>> res = Resource(LootTable, "i/multimeter")
    >>> res
    'your_namespace:i/multimeter'
    >>> res.namespace, res.relative_path
    ('your_namespace', 'i/multimeter')
    >>> res.file_type is LootTable
    True

    It behaves exactly like a str
    >>> res == "your_namespace:i/multimeter"
    True
    >>> isinstance(res, str)
    True
    >>> f"loot spawn ~ ~ ~ loot {res}"
    'loot spawn ~ ~ ~ loot your_namespace:i/multimeter'
    >>> {res: 1}["your_namespace:i/multimeter"]
    1

    The file extension is stripped
    >>> Resource(Function, "custom_blocks/machine_block/place_main.mcfunction")
    'your_namespace:custom_blocks/machine_block/place_main'

    A foreign namespace can be given either way, and a location already carrying one wins
    >>> Resource(LootTable, "base/tin_raw", namespace="mechanization")
    'mechanization:base/tin_raw'
    >>> Resource(LootTable, "mechanization:base/tin_raw").namespace
    'mechanization'
    >>> Resource(LootTable, "mechanization:base/tin_raw", namespace="ignored").namespace
    'mechanization'

    Copies survive (mandatory: components dicts get deep-copied during serialization)
    >>> import copy
    >>> copied = copy.deepcopy(res)
    >>> copied == res and copied.file_type is LootTable
    True

    Out of a build, pack accessors run against an empty placeholder context
    >>> res.exists()
    False
    >>> res.get() is None
    True
    """
    namespace: str
    """ The namespace of the resource, e.g. "stewbeet.core.cls.resource". """
    relative_path: str
    """ The path inside the namespace (the beet NamespaceContainer key), ex: "i/multimeter". """
    file_type: type[FileT]
    """ The beet file type this resource points to, ex: LootTable. """

    def __new__(cls, file_type: type[FileT], location: str, namespace: str | None = None) -> Self:
        """ Build a resource location.

        Args:
            file_type	(type[FileT]):	The beet file type, ex: LootTable, Function, Model
            location	(str):			Either a path inside the namespace ("i/multimeter") or a full
                resource location ("mechanization:base/tin_raw"), whose namespace then wins
            namespace	(str|None):		The namespace to use when `location` doesn't carry one,
                defaults to the current project namespace
        """
        # Split the namespace out of the location, falling back to the given one then to the project
        ns, separator, path = str(location).partition(":")
        if not separator:
            ns, path = (Mem.ctx.project_id if namespace is None else str(namespace)), ns

        # Clean up the path
        path = path.strip("/").removesuffix(file_type.extension)

        # Build the resource
        self = super().__new__(cls, f"{ns}:{path}")

        # Store the namespace, path, and file type
        self.namespace = ns
        self.relative_path = path
        self.file_type = file_type
        return self

    # Pickle/copy support: str subclasses with a custom __new__ break deepcopy without this
    def __reduce__(self) -> tuple[Any, ...]:
        return (type(self), (self.file_type, self.relative_path, self.namespace))

    # Accessors
    @property
    def pack(self) -> DataPack | ResourcePack:
        """ The pack owning this resource (Mem.ctx.data or Mem.ctx.assets). """
        return resolve_pack(self.file_type)

    @property
    def proxy(self) -> NamespaceProxy[FileT]:
        """ The beet NamespaceProxy for this file type (keys are full "namespace:path" locations). """
        return self.pack[self.file_type]

    @property
    def container(self) -> NamespaceContainer[FileT]:
        """ The beet NamespaceContainer for this namespace (keys are relative paths). """
        # beet types Namespace as Container[type[NamespaceFile], NamespaceContainer[NamespaceFile]],
        # so the file type parameter cannot be carried through the lookup.
        return cast(NamespaceContainer[FileT], self.pack[self.namespace][self.file_type])

    # File access
    @property
    def obj(self) -> FileT:
        """ The beet file at this location.

        Returns:
            FileT: The beet file, ex: a LootTable, a Functio, or whatever
        Raises:
            KeyError: If the file is not in the pack yet (use .get() to get None instead).

        >>> from stewbeet import Function
        >>> res = Resource(Function, "custom_blocks/machine_block/place_main")
        >>> res.get() is None
        True
        >>> res.obj = Function("say Hello")
        >>> res.obj
        Function('say Hello')
        >>> res.obj is Function("say Hello")
        False
        >>> res.obj == Function("say Hello")
        True
        """
        try:
            return self.proxy[str(self)]
        except KeyError:
            raise KeyError(str(self)) from None

    @obj.setter
    def obj(self, value: FileT) -> None:
        self.proxy[str(self)] = value

    def get(self, default: FileT | None = None) -> FileT | None:
        """ Get the beet file at this location, or `default` when it doesn't exist yet.

        Args:
            default (FileT|None): The value to return when the file doesn't exist
        Returns:
            FileT | None: The beet file, or `default`
        """
        container: NamespaceContainer[FileT] | None = existing_container(self.file_type, self.namespace)
        return default if container is None else container.get(self.relative_path, default)

    def exists(self) -> bool:
        """ Whether the file already exists in the pack.

        Returns:
            bool: True if the file exists
        """
        container: NamespaceContainer[FileT] | None = existing_container(self.file_type, self.namespace)
        return container is not None and self.relative_path in container

    def setdefault(self, default: FileT | None = None) -> FileT:
        """ Get the existing beet file, or insert and return `default` (or a new empty file).

        Args:
            default (FileT|None): The file to insert when nothing exists yet
        Returns:
            FileT: The existing or newly inserted beet file
        """
        return self.proxy.setdefault(str(self), default)

    def write(self, value: FileT) -> FileT:
        """ Write the beet file at this location, overwriting anything already there.

        Args:
            value (FileT): The beet file to write, ex: LootTable({...})
        Returns:
            FileT: The written file
        """
        self.proxy[str(self)] = value
        return value

    def delete(self) -> None:
        """ Remove the file from the pack if it exists (no-op otherwise). """
        container: NamespaceContainer[FileT] | None = existing_container(self.file_type, self.namespace)
        if container is not None and self.relative_path in container:
            del container[self.relative_path]

    # Derivation
    def child(self, name: str) -> Resource[FileT]:
        """ Get a resource nested under this one.

        Args:
            name (str): The child name, ex: "place_main"
        Returns:
            Resource[FileT]: The nested resource

        Examples:
            >>> from beet import Function
            >>> Resource(Function, "custom_blocks/machine_block").child("place_main")
            'your_namespace:custom_blocks/machine_block/place_main'
        """
        return Resource(self.file_type, f"{self.relative_path}/{name}", self.namespace)

    def suffixed(self, suffix: str) -> Resource[FileT]:
        """ Get a resource with a suffix appended to its path, ex: the "_on" variant of a model.

        Args:
            suffix (str): The suffix to append, ex: "_on"
        Returns:
            Resource[FileT]: The suffixed resource

        Examples:
            >>> from beet import Model
            >>> Resource(Model, "item/battery").suffixed("_on")
            'your_namespace:item/battery_on'
            >>> Resource(Model, "item/battery").suffixed("")
            'your_namespace:item/battery'
        """
        return Resource(self.file_type, f"{self.relative_path}{suffix}", self.namespace)

    def sibling(self, name: str) -> Resource[FileT]:
        """ Get a resource in the same folder as this one.

        Args:
            name (str): The sibling name, ex: "destroy"
        Returns:
            Resource[FileT]: The sibling resource

        Examples:
            >>> from beet import Function
            >>> Resource(Function, "custom_blocks/machine_block/place_main").sibling("destroy")
            'your_namespace:custom_blocks/machine_block/destroy'
        """
        parent: str = self.relative_path.rpartition("/")[0]
        return Resource(self.file_type, f"{parent}/{name}" if parent else name, self.namespace)

