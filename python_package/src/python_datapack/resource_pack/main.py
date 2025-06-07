
# Imports
from ..utils.io import write_all_files
from .item_models import main as item_models_main
from .power_of_2 import main as check_all_textures_power_of_2
from .sounds import main as sounds_main


def main(config: dict):

	# Add the sounds folder to the resource pack
	sounds_main(config)

	# For each item, copy textures and make models
	item_models_main(config)

	# Check all textures if they are in power of 2 resolution
	check_all_textures_power_of_2(config)

	# Write resource pack files to write
	build_rp: str = config["build_resource_pack"]
	write_all_files(contains=f"{build_rp}/assets")

