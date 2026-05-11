
# Imports
from beet import Context
from stewbeet import *  # type: ignore


# Main entry point
def beet_default(ctx: Context):
    ns: str = ctx.project_id

    # Write a function that uses several scoreboard constants
    # Pattern: #{integer} {ns}.data
    write_function(f"{ns}:utils/compute", f"""
# Clamp value between 0 and 100
scoreboard players set #0 {ns}.data 0
scoreboard players set #100 {ns}.data 100
execute if score #value {ns}.data < #0 {ns}.data run scoreboard players operation #value {ns}.data = #0 {ns}.data
execute if score #value {ns}.data > #100 {ns}.data run scoreboard players operation #value {ns}.data = #100 {ns}.data

# Multiply by 42
scoreboard players set #42 {ns}.data 42
scoreboard players operation #result {ns}.data *= #42 {ns}.data
""")
