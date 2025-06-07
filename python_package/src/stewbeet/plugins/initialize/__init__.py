
# Imports
from beet import Context
from beet.core.utils import TextComponent
from box import Box

from ...core import Mem


# Main entry point
def beet_default(ctx: Context):

	# Store the Box object in ctx for access throughout the codebase
	meta_box: Box = Box(ctx.meta, default_box=True, default_box_attr={})
	object.__setattr__(ctx, "meta", meta_box) # Bypass FrozenInstanceError
	Mem.ctx = ctx

	# Preprocess source lore
	source_lore: TextComponent = Mem.ctx.meta.stewbeet.source_lore
	if not source_lore or source_lore == "auto":
		Mem.ctx.meta.stewbeet.source_lore = [{"text":"ICON"},{"text":f" {ctx.project_name}","italic":True,"color":"blue"}]

	# Preprocess manual name
	manual_name: TextComponent = Mem.ctx.meta.stewbeet.manual.name
	if not manual_name:
		Mem.ctx.meta.stewbeet.manual.name = f"{ctx.project_name} Manual"

	pass

