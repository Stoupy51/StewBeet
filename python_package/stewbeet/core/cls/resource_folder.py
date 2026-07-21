
# Imports
from __future__ import annotations

from collections.abc import Iterator

from beet import NamespaceContainer, NamespaceFile

from ..__memory__ import Mem
from .resource import Resource, existing_container


# Class
class ResourceFolder[FileT: NamespaceFile]:
    """ A lazy accessor over a folder of resources sharing the same beet file type.

    >>> from beet import Function
    >>> folder = ResourceFolder(Function, "custom_blocks/machine_block")
    >>> folder.folder
    'your_namespace:custom_blocks/machine_block'
    >>> folder["place_main"]
    'your_namespace:custom_blocks/machine_block/place_main'
    >>> folder
    ResourceFolder('your_namespace:custom_blocks/machine_block/*')
    """
    __slots__ = ("_folder", "file_type", "namespace")

    def __init__(self, file_type: type[FileT], folder: str, namespace: str | None = None) -> None:
        """ Build a resource folder accessor.

        Args:
            file_type	(type[FileT]):	The beet file type, ex: Function
            folder		(str):			The folder path inside the namespace, ex: "custom_blocks/machine_block"
            namespace	(str|None):		The namespace, defaults to the current project namespace
        """
        self.file_type: type[FileT] = file_type
        self._folder: str = str(folder).strip("/")
        self.namespace: str = Mem.ctx.project_id if namespace is None else str(namespace)

    def __getitem__(self, name: str) -> Resource[FileT]:
        """ Get any resource of this folder, ex: folder["place_main"]. """
        return Resource(self.file_type, f"{self._folder}/{name}", self.namespace)

    @property
    def folder(self) -> Resource[FileT]:
        """ The folder itself, as a resource location (no trailing slash). """
        return Resource(self.file_type, self._folder, self.namespace)

    def __iter__(self) -> Iterator[Resource[FileT]]:
        """ Iterate over the resources of this folder that already exist in the pack (sorted). """
        container: NamespaceContainer[FileT] | None = existing_container(self.file_type, self.namespace)
        if container is None:
            return
        prefix: str = f"{self._folder}/"
        for key in sorted(container):
            if key.startswith(prefix):
                yield Resource(self.file_type, key, self.namespace)

    def __repr__(self) -> str:
        return f"{type(self).__name__}('{self.namespace}:{self._folder}/*')"

