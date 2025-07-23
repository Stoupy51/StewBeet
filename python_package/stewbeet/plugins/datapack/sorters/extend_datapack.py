
# Imports
from beet import Context

from .constants import SorterFile


# Main entry point
def beet_default(ctx: Context):
	""" Extend the datapack namespace with the sorter resource type.

	This function registers the SorterFile class with the datapack context,
	allowing sorter configuration files to be recognized and processed.

	Args:
		ctx (Context): The beet context.
	"""
	ctx.data.extend_namespace.append(SorterFile)

