# A command no vanilla tree has, added to mecha's the way a plugin like bolt_compute adds its own.

# Imports
from beet import Context
from mecha import Mecha


# Main entry point
def beet_default(ctx: Context) -> None:
	ctx.inject(Mecha).spec.add_commands({
		"type": "root",
		"children": {"say": {"type": "literal", "children": {"loudly": {"type": "literal", "children": {
			"message": {"type": "argument", "parser": "minecraft:message", "executable": True},
		}}}}},
	})

