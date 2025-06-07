
# Imports
import stouputils as stp

from .custom_blocks import main as custom_blocks_main
from .loading import main as loading_main
from .loot_tables import main as loot_tables_main


@stp.measure_time(stp.info, "Datapack successfully generated")
def main(config: dict):
	print()

	# Generate datapack loading
	loading_main(config)

	if config.get("database"):

		# Custom Blocks (place + destroy)
		custom_blocks_main(config)

		# Generate items loot tables
		loot_tables_main(config)

