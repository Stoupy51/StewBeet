
# Imports
from beet import Context
from stewbeet import *  # type: ignore


# Main entry point
def beet_default(ctx: Context):
    ns: str = ctx.project_id

    # Write functions that use scoreboard objectives and storages
    # so that the unload plugin can scan and generate removal commands
    write_function(f"{ns}:utils/setup", f"""
scoreboard objectives add {ns}.kills dummy
scoreboard objectives add {ns}.deaths dummy
data modify storage {ns}:state kills set value 0
data modify storage {ns}:state deaths set value 0
say Setup complete
""")

    write_function(f"{ns}:utils/stats", f"""
scoreboard players add @a {ns}.kills 0
execute as @a store result score @s {ns}.kills run data get storage {ns}:state kills
""")
