# Assertions for: stewbeet.plugins.datapack.loading with items_storage disabled

# Imports
from beet import Context


# Main entry point
def beet_default(ctx: Context):
	ns: str = ctx.project_id
	version: str = ctx.project_version

	assert f"{ns}:v{version}/load/set_items_storage" not in ctx.data.functions, \
		"set_items_storage must not be written when items_storage is false"
	confirm_content: str = ctx.data.functions[f"{ns}:v{version}/load/confirm_load"].text
	assert "set_items_storage" not in confirm_content, \
		"confirm_load must not call set_items_storage when items_storage is false"
	assert f"scoreboard players set #{ns}.loaded load.status 1" in confirm_content, \
		"confirm_load must still set the loaded score"

