# Lazy imports (PEP 810), ignored before Python 3.15
from stouputils.lazy import ALWAYS_LAZY

__lazy_modules__ = ALWAYS_LAZY

# Imports
from uuid import NAMESPACE_URL, uuid5

from ..__memory__ import Mem
from ..constants import FORCELOAD_BLOCK
from .io import write_load_file


# Functions
def persistent_item_display(name: str) -> str:
	""" Have the load function summon an item_display that stays in the forceloaded chunk, and give its UUID.

	Target it with `execute as <uuid>` instead of summoning and killing a temporary entity every call:
	a UUID selector is a direct lookup, and the entity is never created twice. The UUID depends only on
	the project id and the name, and the unload function kills the entity.

	Args:
		name: Unique within the project, ex: "pulverizer_recipe".
	Returns:
		The UUID in its hyphenated form, usable as a selector.
	"""
	uuid = uuid5(NAMESPACE_URL, f"{Mem.ctx.project_id}:{name}")
	x, z = FORCELOAD_BLOCK
	forceload: str = f"forceload add {x} {z}"
	summon: str = (
		f"execute unless entity {uuid} run summon minecraft:item_display {x} 0 {z} "
		f'{{UUID:uuid("{uuid}"),Tags:["smithed.entity","smithed.strict"],view_range:0f}}'
	)
	write_load_file(f"\n# Chunk of the persistent utility entities\n{forceload}\n", condition=lambda load: forceload not in load)
	write_load_file(f"\n# Persistent item_display '{name}'\n{summon}\n", condition=lambda load: summon not in load)
	return str(uuid)

