
# Imports
from beet import Context
from beet.core.utils import TextComponent
from box import Box
from stouputils import relative_path
from stouputils.decorators import measure_time
from stouputils.print import progress

from ...core import Mem


# Main entry point
@measure_time(progress, message="Execution time of 'stewbeet.plugins.initialize'")
def beet_default(ctx: Context):

	# Store the Box object in ctx for access throughout the codebase
	meta_box: Box = Box(ctx.meta, default_box=True, default_box_attr={})
	object.__setattr__(ctx, "meta", meta_box) # Bypass FrozenInstanceError
	Mem.ctx = ctx

	# Preprocess project description
	project_description: TextComponent = Mem.ctx.meta.stewbeet.project_description
	if not project_description or project_description == "auto":
		# Use project name, version, and author to create a default description
		Mem.ctx.meta.stewbeet.project_description = f"{ctx.project_name} [{ctx.project_version}] by {ctx.project_author}"

	# Preprocess source lore
	source_lore: TextComponent = Mem.ctx.meta.stewbeet.source_lore
	if not source_lore or source_lore == "auto":
		Mem.ctx.meta.stewbeet.source_lore = [{"text":"ICON"},{"text":f" {ctx.project_name}","italic":True,"color":"blue"}]

	# Preprocess manual name
	manual_name: TextComponent = Mem.ctx.meta.stewbeet.manual.name
	if not manual_name:
		Mem.ctx.meta.stewbeet.manual.name = f"{ctx.project_name} Manual"

	# Convert paths to relative ones
	object.__setattr__(ctx, "output_directory", relative_path(Mem.ctx.output_directory))

	pass

