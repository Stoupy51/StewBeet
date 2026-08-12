""" Placeholder overwritten by worker.py with the submitted code on every request.

It is committed so the image build selftest has something to build, and so the project can be run
by hand while working on the sandbox.
"""
# Imports
from beet import Context
from stewbeet import *  # type: ignore


# Main entry point
def beet_default(ctx: Context):
	Item(
		id="steel_ingot",
		manual_category="material",
		components={"item_name": {"text": "Steel Ingot"}},
	)

	add_item_model_component()
	add_item_name_and_lore_if_missing()
	add_private_custom_data_for_namespace()

