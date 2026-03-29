
# Imports
from stewbeet import *  # type: ignore


# Main entry point
def main():

    # Configuration to generate everything about a material
    ORES_CONFIGS: dict[str, EquipmentsConfig|None] = {
        # See extensive_template/src/definitions/ores.py for an example
    }

    # Generate ores in definitions (add every stuff (found in the textures folder) related to the given materials, to the definitions)
    generate_everything_about_these_materials(ORES_CONFIGS)

    return

