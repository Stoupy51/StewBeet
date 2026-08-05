# Cookbook

Complete, working examples of writing datapack files with StewBeet. Each one is a whole file
you can read top to bottom, not a fragment.

**See also** [the helper reference](reference.md) for what each function accepts.

## Real-World Examples

### Example 1: Custom Block Ticking

Generate tick functions for custom blocks with different behaviors.

```python
from stewbeet import write_function, write_versioned_function, Mem

def setup_custom_blocks(ctx: Context):
    ns = ctx.project_id
    
    # Solar panel generates energy during daytime
    write_versioned_function("custom_blocks/solar_panel/second", """
# Check daylight level and generate energy
execute if predicate simplenergy:check_daylight_power run scoreboard players operation @s energy.storage += @s simplenergy.energy_rate
execute if score @s energy.storage > @s energy.max_storage run scoreboard players operation @s energy.storage = @s energy.max_storage
""")
    
    # Electric furnace smelts items using energy
    write_versioned_function("custom_blocks/electric_furnace/second", f"""
# Prevent vanilla cooking
data modify block ~ ~ ~ cooking_total_time set value -200s

# Check if has energy and items
execute if score @s energy.storage matches 20.. if data block ~ ~ ~ Items[{{Slot:0b}}] run function {ns}:custom_blocks/electric_furnace/process
""")
    
    write_function(f"{ns}:custom_blocks/electric_furnace/process", """
# Consume energy
scoreboard players remove @s energy.storage 20

# Cook item (will complete on next check)
data modify block ~ ~ ~ CookTime set value 199s
""")
```

---

### Example 2: Machine State Management

Manage machine states with multiple functions.

```python
def setup_machine_states(ctx: Context):
    ns = ctx.project_id
    
    # Main machine tick
    write_function(f"{ns}:machines/processor/tick", f"""
# Check if machine should run
execute if score @s {ns}.power matches 100.. run function {ns}:machines/processor/running
execute unless score @s {ns}.power matches 100.. run function {ns}:machines/processor/idle
""")
    
    # Running state
    write_function(f"{ns}:machines/processor/running", f"""
# Consume power
scoreboard players remove @s {ns}.power 10

# Show running particles
particle electric_spark ~ ~0.5 ~ 0.2 0.2 0.2 0.01 5

# Process items
execute if predicate {ns}:has_input_item run function {ns}:machines/processor/process_item
""")
    
    # Idle state
    write_function(f"{ns}:machines/processor/idle", """
# Show idle particles
particle smoke ~ ~0.5 ~ 0.1 0.1 0.1 0.01 1
""")
    
    # Processing logic
    write_function(f"{ns}:machines/processor/process_item", f"""
# Remove input
item replace block ~ ~ ~ container.0 with air

# Give output
loot spawn ~ ~ ~ loot {ns}:items/processed_material
""")
```

---

### Example 3: Advancement Triggers

Set up advancement-based detection system.

```python
def setup_advancement_triggers(ctx: Context):
    ns = ctx.project_id
    
    # Inventory changed trigger
    write_advancement(f"{ns}:technical/inventory_changed", {
        "criteria": {
            "requirement": {
                "trigger": "minecraft:inventory_changed"
            }
        },
        "rewards": {
            "function": f"{ns}:advancements/check_inventory"
        }
    })
    
    write_function(f"{ns}:advancements/check_inventory", f"""
# Revoke advancement
advancement revoke @s only {ns}:technical/inventory_changed

# Check for custom items
execute if items entity @s container.* *[custom_data~{{{ns}:{{}}}}] run function {ns}:items/handle_custom_item
""", prepend=True)
    
    # Item used trigger (for right-click detection)
    write_advancement(f"{ns}:technical/used_item", {
        "criteria": {
            "requirement": {
                "trigger": "minecraft:using_item",
                "conditions": {
                    "item": {
                        "predicates": {
                            "custom_data": {ns: {}}
                        }
                    }
                }
            }
        },
        "rewards": {
            "function": f"{ns}:advancements/item_used"
        }
    })
    
    write_function(f"{ns}:advancements/item_used", f"""
advancement revoke @s only {ns}:technical/used_item
function {ns}:items/right_click_handler
""")
```

---

### Example 4: Programmatic Function Generation

Generate multiple similar functions automatically.

```python
def generate_tier_functions(ctx: Context):
    ns = ctx.project_id
    
    # Generate functions for each tier
    tiers = {
        "basic": {"power": 10, "speed": 100, "color": "gray"},
        "advanced": {"power": 25, "speed": 50, "color": "blue"},
        "elite": {"power": 50, "speed": 25, "color": "purple"}
    }
    
    for tier_name, tier_data in tiers.items():
        # Generate upgrade function
        write_function(f"{ns}:machines/{tier_name}/upgrade", f"""
# Set tier stats
scoreboard players set @s {ns}.power {tier_data['power']}
scoreboard players set @s {ns}.speed {tier_data['speed']}

# Show upgrade message
tellraw @s {{"text":"Upgraded to {tier_name.title()} Tier!","color":"{tier_data['color']}"}}
""")
        
        # Generate operation function
        write_function(f"{ns}:machines/{tier_name}/operate", f"""
# Check power requirement
execute if score @s {ns}.energy matches {tier_data['power']}.. run function {ns}:machines/{tier_name}/process

# Show status
title @s actionbar {{"text":"Power: ","color":"gray","extra":[{{"score":{{"name":"@s","objective":"{ns}.energy"}}}}]}}
""")
```

---

### Example 5: Complex Load Setup

Initialize complete datapack systems on load.

```python
def setup_load_system(ctx: Context):
    ns = ctx.project_id
    
    # Prepend early initialization (runs first)
    write_load_file("""
# Create core scoreboards
scoreboard objectives add data dummy
scoreboard objectives add private dummy
""", prepend=True)
    
    # Main initialization
    write_load_file(f"""
# Create game-specific scoreboards
scoreboard objectives add {ns}.energy dummy
scoreboard objectives add {ns}.power dummy
scoreboard objectives add {ns}.right_click minecraft.used:minecraft.warped_fungus_on_a_stick

# Set constants
scoreboard players set #2 data 2
scoreboard players set #10 data 10
scoreboard players set #100 data 100
scoreboard players set #1000 data 1000

# Create teams
team add {ns}.green
team add {ns}.gold
team add {ns}.aqua
team modify {ns}.green color green
team modify {ns}.gold color gold
team modify {ns}.aqua color aqua

# Initialize storage
data modify storage {ns}:main config set value {{}}
data modify storage {ns}:main temp set value {{}}
""")
    
    # Load custom modules
    write_load_file(f"""
# Load module systems
function {ns}:modules/energy/load
function {ns}:modules/machines/load
function {ns}:modules/items/load
""")
```

---

### Example 6: Right-Click Detection System

Complete right-click detection using custom items.

```python
def setup_right_click_detection(ctx: Context):
    ns = ctx.project_id
    
    # Create detection scoreboard on load
    write_load_file(f"""
scoreboard objectives add {ns}.right_click minecraft.used:minecraft.warped_fungus_on_a_stick
""")
    
    # Check for right-clicks every tick
    write_tick_file(f"""
# Detect right-clicks
execute as @a[scores={{{ns}.right_click=1..}}] run function {ns}:items/right_click_handler
""")
    
    # Main right-click handler
    write_function(f"{ns}:items/right_click_handler", f"""
# Reset score
scoreboard players set @s {ns}.right_click 0

# Check which item was used
execute if items entity @s weapon.mainhand *[custom_data~{{{ns}:{{wrench:true}}}}] run function {ns}:items/wrench/use
execute if items entity @s weapon.mainhand *[custom_data~{{{ns}:{{teleporter:true}}}}] run function {ns}:items/teleporter/use
execute if items entity @s weapon.mainhand *[custom_data~{{{ns}:{{scanner:true}}}}] run function {ns}:items/scanner/use
""")
    
    # Individual item handlers
    write_function(f"{ns}:items/wrench/use", """
# Rotate the block player is looking at
execute anchored eyes positioned ^ ^ ^1 align xyz positioned ~0.5 ~ ~0.5 as @n[type=item_display,tag=custom_block,distance=..1] run function simplenergy:items/wrench/rotate_block
""")
```

---

### Example 7: Growing Crops System

Implement custom growing mechanics.

```python
def setup_growing_system(ctx: Context):
    ns = ctx.project_id
    
    # Check growth every 5 seconds
    write_versioned_function("second_5", f"""
# Update growing crops
execute as @e[type=item_display,tag={ns}.growing_crop] at @s run function {ns}:crops/check_growth
""")
    
    # Growth check function
    write_function(f"{ns}:crops/check_growth", f"""
# Increment growth timer
scoreboard players add @s {ns}.growth_time 5

# Check if fully grown
execute if score @s {ns}.growth_time >= @s {ns}.growth_required run function {ns}:crops/fully_grown

# Visual feedback (random particle)
execute if predicate {ns}:random/0.3 run particle happy_villager ~ ~0.3 ~ 0.2 0.2 0.2 0 1
""")
    
    # Fully grown handler
    write_function(f"{ns}:crops/fully_grown", f"""
# Update model to grown state
data modify entity @s item.components."minecraft:item_model" set value "{ns}:block/crop_grown"

# Add grown tag
tag @s add {ns}.crop_grown
tag @s remove {ns}.growing_crop

# Play sound
playsound minecraft:block.crop.break block @a ~ ~ ~ 1 1.2
""")
    
    # Harvesting
    write_function(f"{ns}:crops/harvest", f"""
# Drop items
loot spawn ~ ~ ~ loot {ns}:crops/harvest_crop

# Remove entity
kill @s

# Play sound
playsound minecraft:block.crop.break block @a ~ ~ ~ 1 0.8
""")
```

---

### Example 8: Tag Management

Organize functions and entities with tags.

```python
def setup_tags(ctx: Context):
    ns = ctx.project_id
    
    # Add to minecraft:load
    write_function_tag("minecraft:load", [
        f"{ns}:v{ctx.project_version}/load/main"
    ])
    
    # Add to minecraft:tick
    write_function_tag("minecraft:tick", [
        f"{ns}:v{ctx.project_version}/load/tick_verification"
    ])
    
    # Custom function tags for organization
    write_function_tag(f"{ns}:custom_blocks/tick", [
        f"{ns}:custom_blocks/solar_panel/tick",
        f"{ns}:custom_blocks/electric_furnace/tick",
        f"{ns}:custom_blocks/battery/tick"
    ])
    
    write_function_tag(f"{ns}:machines/process", [
        f"{ns}:machines/crusher/process",
        f"{ns}:machines/smelter/process",
        f"{ns}:machines/assembler/process"
    ])
    
    # Entity type tags
    write_tag("mob_grinder_blacklist", Mem.ctx.data.entity_type_tags, [
        "minecraft:warden",
        "minecraft:ender_dragon",
        "minecraft:wither"
    ])
    
    write_tag("machines", Mem.ctx.data.entity_type_tags, [
        "minecraft:item_display",
        "minecraft:interaction"
    ])
    
    # Block tags
    write_tag(f"{ns}:machines", Mem.ctx.data.block_tags, [
        "minecraft:furnace",
        "minecraft:barrel",
        "minecraft:dropper"
    ])
```

---
## Complete Example

Here's a complete example combining all approaches (example from [Stardust Fragment](https://github.com/Stoupy51/StardustFragment/blob/main/src/utils/remaining.py)):

```python
# Imports
import json

from stewbeet import *  # type: ignore
from stouputils import get_root_path

# Constants
ROOT: str = get_root_path(__file__)

# Setup remaining utilities
def setup_remaining() -> None:
	ns: str = Mem.ctx.project_id

	# Get player head loot table
	json_content: JsonDict = {"pools":[{"rolls":1,"entries":[{"type":"minecraft:item","name":"minecraft:player_head","functions":[{"function":"minecraft:fill_player_head","entity":"this"}]}]}]}
	Mem.ctx.data[ns].loot_tables["player_head"] = set_json_encoder(LootTable(json_content), max_level=-1)

	# Boss Music
	write_load_file(f"\n# Boss music timers\nscoreboard objectives add {ns}.boss_music dummy", prepend=True)

	# Inventory Changed
	write_advancement(f"{ns}:technical/inventory_changed", {
		"criteria": {"requirement": {"trigger": "minecraft:inventory_changed"}},
		"rewards": {"function": f"{ns}:advancements/inventory_changed"}
	})
	write_function(f"{ns}:advancements/inventory_changed", f"""
# Revoke advancement
advancement revoke @s only {ns}:technical/inventory_changed
""", prepend=True)


	# Right click detection
	write_load_file(f"\n# Right click detection\nscoreboard objectives add {ns}.right_click minecraft.used:minecraft.warped_fungus_on_a_stick\nscoreboard objectives add {ns}.cooldown dummy\n", prepend=True)
	write_advancement(f"{ns}:technical/right_click", {
		"criteria": {
			"requirement": {
				"trigger": "minecraft:tick",
				"conditions": {
					"player": [
						{
							"condition": "minecraft:entity_scores",
							"entity": "this",
							"scores": {f"{ns}.right_click": {"min": 1}}
						}
					]
				}
			}
		},
		"rewards": {
			"function": f"{ns}:advancements/right_click"
		}
	})
	write_function(f"{ns}:advancements/right_click", f"""
# Revoke advancement and reset score
advancement revoke @s only {ns}:technical/right_click
scoreboard players set @s {ns}.right_click 0
""", prepend=True)

	# Global counter
	write_tick_file(f"\n# Global counter for various features\nscoreboard players add #global_tick {ns}.data 1\n", prepend=True)
	write_versioned_function("second", f"\n# Global counter for various features\nscoreboard players add #global_second {ns}.data 1\n", prepend=True)

	# Compute motion towards
	write_function(f"{ns}:utils/compute_motion_towards", """
# Compute motion towards
scoreboard players set @s bs.vel.x 0
scoreboard players set @s bs.vel.y 0
$scoreboard players set @s bs.vel.z $(towards)
function #bs.move:local_to_canonical

# Apply motion
$function #bs.move:set_motion {scale:$(scale)}
""")

	# Use durability
	write_function(f"{ns}:utils/use_durability/main", f"""
# Compute durability usage (6 digits precision)
scoreboard players set #1000000 {ns}.data 1000000
$scoreboard players set #temp_durability {ns}.data -$(amount)
scoreboard players operation #temp_durability {ns}.data *= #1000000 {ns}.data
$scoreboard players set #temp_divider {ns}.data $(max_damage)
scoreboard players operation #temp_durability {ns}.data /= #temp_divider {ns}.data
execute store result storage {ns}:temp use_durability double 0.000001 run scoreboard players get #temp_durability {ns}.data
$data modify storage {ns}:temp slot set value "$(slot)"
function {ns}:utils/use_durability/item_modifier with storage {ns}:temp

# If item broke, destroy it
execute store result score #current_damage {ns}.data run data get entity @s SelectedItem.components."minecraft:damage"
$execute if score #current_damage {ns}.data matches $(max_damage).. anchored eyes run particle item{{item:{{id:"minecraft:stone",components:{{"minecraft:item_model":"$(item_model)"}}}}}} ^ ^ ^0.5 0 0 0 0.1 10
$execute if score #current_damage {ns}.data matches $(max_damage).. run playsound minecraft:item.shield.break ambient @a[distance=..16]
$execute if score #current_damage {ns}.data matches $(max_damage).. run item replace entity @s $(slot) with minecraft:air
""")
	write_function(f"{ns}:utils/use_durability/item_modifier", r"""
$item modify entity @s $(slot) {"function": "minecraft:set_damage","damage": $(use_durability),"add": true}
""")

	## Life Crystal consuming
	# Add life crystal instrument
	Mem.ctx.data[ns].instruments["life_crystal"] = set_json_encoder(Instrument({
		"description": item_id_to_text_component("life_crystal"),
		"range": 16.0,
		"sound_event": {"sound_id": f"{ns}:life_crystal"},
		"use_duration": 1.0
	}))
	# Detect using life crystal
	write_load_file(f"\n# Life Crystal tracker\nscoreboard objectives add {ns}.life_crystal dummy\n", prepend=True)
	write_advancement(f"{ns}:technical/use_life_crystal", {
		"criteria": {
			"requirements": {
				"trigger": "minecraft:using_item",
				"conditions": {"item": {"predicates": {"minecraft:custom_data": {ns: {"life_crystal": True}}}}}
			}
		},
		"rewards": {"function": f"{ns}:advancements/use_life_crystal"}
	})
	write_function(f"{ns}:advancements/use_life_crystal", f"""
# Revoke advancement
advancement revoke @s only {ns}:technical/use_life_crystal

# Stop if runned a tick ago (to prevent double consuming)
scoreboard players operation #cooldown {ns}.data = @s {ns}.cooldown
execute if score #cooldown {ns}.data > #global_tick {ns}.data run return fail
scoreboard players operation @s {ns}.cooldown = #global_tick {ns}.data
scoreboard players add @s {ns}.cooldown 20

# Stop if already at max life crystals
execute if score @s {ns}.life_crystal matches 20 run return run tellraw @s {{"text":"[Stardust Fragment] You have already reached the maximum number of Life Crystals!","color":"red"}}

# Update life crystal count & attribute
scoreboard players add @s {ns}.life_crystal 1
particle minecraft:heart ~ ~1 ~ .5 .5 .5 1 10 normal
attribute @s minecraft:max_health modifier remove {ns}:life_crystal
{'\n'.join([f'execute if score @s {ns}.life_crystal matches {i+1} run attribute @s minecraft:max_health modifier add {ns}:life_crystal {i+1} add_value' for i in range(20)])}

# Clear one life crystal
clear @s *[custom_data~{{{ns}:{{"life_crystal":true}}}}] 1

# Grant life crystal advancement(s)
advancement grant @s only {ns}:visible/stuff/life_crystal
execute if score @s {ns}.life_crystal matches 20 run advancement grant @s only {ns}:visible/stuff/life_crystal_max
""")

	# Dog excrement production
	Mem.ctx.data[ns].predicates["random/0.05"] = set_json_encoder(Predicate({"condition":"minecraft:random_chance","chance": 0.05}))
	write_versioned_function("minute", f"""
# Dog Excrement production (about 1 every 20 minutes per wolf)
execute at @e[type=minecraft:wolf,{Conventions.AVOID_ENTITY_TAGS},predicate={ns}:random/0.05] run loot spawn ~ ~ ~ loot {ns}:i/dog_excrement
""")

	# Travel Staff
	max_damage: int = Mem.definitions["home_travel_staff"]["max_damage"]
	write_load_file(f"""
# Travel Staff Logic
scoreboard objectives add {ns}.travel_staff_cooldown dummy
scoreboard objectives add {ns}.travel_x dummy
scoreboard objectives add {ns}.travel_y dummy
scoreboard objectives add {ns}.travel_z dummy
""", prepend=True)
	write_function(f"{ns}:advancements/right_click", f"""
# If holding a home travel staff, handle it
execute if items entity @s weapon.* *[custom_data~{{{ns}:{{home_travel_staff:true}}}}] run function {ns}:utils/home_travel_staff/right_click
""")
	write_function(f"{ns}:utils/home_travel_staff/right_click", f"""
# Stop if already clicked recently
execute if score @s {ns}.travel_staff_cooldown > #global_tick {ns}.data run return fail

# Mainhand or offhand?
data modify storage {ns}:temp slot set value "weapon.mainhand"
execute unless items entity @s weapon.mainhand *[custom_data~{{{ns}:{{home_travel_staff:true}}}}] run data modify storage {ns}:temp slot set value "weapon.offhand"

# Time to teleport (100 ticks)
scoreboard players operation @s {ns}.travel_staff_cooldown = #global_tick {ns}.data
scoreboard players add @s {ns}.travel_staff_cooldown 100
schedule function {ns}:utils/home_travel_staff/schedule_teleport 100t append
schedule function {ns}:utils/home_travel_staff/schedule_particles 50t append

# Copy current position (to detect if moved)
execute store result score @s {ns}.travel_x run data get entity @s Pos[0] 100
execute store result score @s {ns}.travel_y run data get entity @s Pos[1] 100
execute store result score @s {ns}.travel_z run data get entity @s Pos[2] 100

# Use 1 durability
data modify storage {ns}:temp amount set value 1
data modify storage {ns}:temp max_damage set value {max_damage}
data modify storage {ns}:temp item_model set value "{ns}:home_travel_staff"
function {ns}:utils/use_durability/main with storage {ns}:temp

# Feedback
playsound minecraft:block.portal.trigger ambient @s ~ ~ ~ 0.5
effect give @s minecraft:nausea 8 255 true
""")
	write_function(f"{ns}:utils/home_travel_staff/schedule_teleport", f"execute as @a if score @s {ns}.travel_staff_cooldown = #global_tick {ns}.data at @s run function {ns}:utils/home_travel_staff/check")
	write_function(f"{ns}:utils/home_travel_staff/schedule_particles", f"""
# Particle effect when 50 ticks left
scoreboard players operation #plus_50 {ns}.data = #global_tick {ns}.data
scoreboard players add #plus_50 {ns}.data 50
execute as @a if score @s {ns}.travel_staff_cooldown = #plus_50 {ns}.data at @s run particle minecraft:portal ~ ~1 ~ 1 1 1 3 2500
""")
	write_function(f"{ns}:utils/home_travel_staff/check", f"""
# Check if player has moved
scoreboard players reset @s {ns}.travel_staff_cooldown
execute store result score #new_x {ns}.data run data get entity @s Pos[0] 100
execute store result score #new_y {ns}.data run data get entity @s Pos[1] 100
execute store result score #new_z {ns}.data run data get entity @s Pos[2] 100
execute unless score @s {ns}.travel_x = #new_x {ns}.data run return run function {ns}:utils/home_travel_staff/fail
execute unless score @s {ns}.travel_y = #new_y {ns}.data run return run function {ns}:utils/home_travel_staff/fail
execute unless score @s {ns}.travel_z = #new_z {ns}.data run return run function {ns}:utils/home_travel_staff/fail

# Teleport
advancement grant @s only {ns}:visible/stuff/home_travel_staff
function {ns}:dimensions/teleport_home
""")
	write_function(f"{ns}:utils/home_travel_staff/fail", """tellraw @s {"text":"[Stardust Fragment] Teleportation cancelled because you moved!","color":"red"}\nplaysound entity.villager.no ambient @s""")

	# Wormhole Potion
	title: str = json.dumps(item_id_to_text_component("wormhole_potion"))
	write_function(f"{ns}:advancements/right_click", f"""
# If holding a wormhole potion, handle it
execute if items entity @s weapon.* *[custom_data~{{{ns}:{{wormhole_potion:true}}}}] run function {ns}:utils/wormhole_potion/right_click
""")
	write_function(f"{ns}:utils/wormhole_potion/right_click", f"""
# Prepare dialog for which player to teleport to
tag @s add {ns}.temp
data modify storage {ns}:temp dialog set value {{"actions":[],"title":{title}}}
execute as @a[tag=!{ns}.temp] run function {ns}:utils/wormhole_potion/add_to_actions
tag @s remove {ns}.temp

# Message if no other players connected
execute unless data storage {ns}:temp dialog.actions[1] run playsound minecraft:entity.villager.no ambient @s
execute unless data storage {ns}:temp dialog.actions[1] run return run tellraw @s {{"text":"[Stardust Fragment] No other players are currently connected to teleport to.","color":"red"}}

# Show dialog
function {ns}:utils/wormhole_potion/show_dialog with storage {ns}:temp dialog
""")
	write_function(f"{ns}:utils/wormhole_potion/add_to_actions", f"""
# Get player username for macro
tag @e[type=item] add {ns}.temp
execute at @s run loot spawn ~ ~ ~ loot {ns}:player_head
data modify storage {ns}:temp player_name set from entity @n[type=item,tag=!{ns}.temp] Item.components."minecraft:profile".name
kill @e[type=item,tag=!{ns}.temp]
tag @e[type=item,tag={ns}.temp] remove {ns}.temp

# Prepare action
data modify storage {ns}:temp element set value {{"label":[],"action":{{}}}}
data modify storage {ns}:temp element.label append value {{"player":{{"name":""}},"hat":true}}
data modify storage {ns}:temp element.label[-1].player.name set from storage {ns}:temp player_name
data modify storage {ns}:temp element.label append value " "
data modify storage {ns}:temp element.label append from storage {ns}:temp player_name
data modify storage {ns}:temp element.label append value " "
data modify storage {ns}:temp element.label append from storage {ns}:temp element.label[0]
data modify storage {ns}:temp element.action set value {{"type":"minecraft:run_command","command":""}}
function {ns}:utils/wormhole_potion/set_teleport_command with storage {ns}:temp

# Add action to dialog
data modify storage {ns}:temp dialog.actions append from storage {ns}:temp element
""")
	write_function(f"{ns}:utils/wormhole_potion/set_teleport_command", f"""
$data modify storage {ns}:temp element.action.command set value 'function {ns}:utils/wormhole_potion/teleport_to {{"name":"$(player_name)"}}'
""")
	write_function(f"{ns}:utils/wormhole_potion/show_dialog", r"""
$dialog show @s {"type":"minecraft:multi_action","columns":3,"exit_action":{"label":{"translate":"gui.back"},"width":200},"title":$(title),"actions":$(actions)}
""")
	write_function(f"{ns}:utils/wormhole_potion/teleport_to", f"""
# Slow falling effect to avoid fall damage
effect give @s minecraft:slow_falling 3 255 true

# Teleport to selected player
$tp @s $(name)

# Feedback
execute at @s run particle minecraft:portal ~ ~1 ~ 1 1 1 0 2500
execute at @s run playsound {ns}:wormhole_potion ambient @a[distance=..16]

# Consume one wormhole potion
clear @s *[custom_data~{{{ns}:{{"wormhole_potion":true}}}}] 1
""")

	## Dragon & Ender Dragon pearls
	write_load_file(f"\n# Ender Pearl detection\nscoreboard objectives add {ns}.ender_pearl minecraft.used:minecraft.ender_pearl\n", prepend=True)
	write_advancement(f"{ns}:technical/ender_pearl", {
		"criteria": {
			"requirement": {
				"trigger": "minecraft:tick",
				"conditions": {
					"player": [
						{
							"condition": "minecraft:entity_scores",
							"entity": "this",
							"scores": {f"{ns}.ender_pearl": {"min": 1}}
						}
					]
				}
			}
		},
		"rewards": {
			"function": f"{ns}:advancements/ender_pearl"
		}
	})
	dragon_data: str = f"""{{{ns}:{{"dragon_pearl":true}}}}"""
	ender_dragon_data: str = f"""{{{ns}:{{"ender_dragon_pearl":true}}}}"""
	def line_pearl(data: str, scale: int) -> str:
		return f"""execute if items entity @s weapon.mainhand *[custom_data~{data}] as @n[type=ender_pearl,tag=!{ns}.motion_applied,nbt={{Item:{{components:{{"minecraft:custom_data":{data}}}}}}}] run function {ns}:utils/multiply_motion {{scale:{scale}}}"""
	write_function(f"{ns}:advancements/ender_pearl", f"""
# Revoke advancement and reset score
advancement revoke @s only {ns}:technical/ender_pearl
scoreboard players set @s {ns}.ender_pearl 0

# If Dragon Pearl (Motion x1.5), if Ender Dragon pearl (Motion x2)
{line_pearl(dragon_data, 1500)}
{line_pearl(ender_dragon_data, 2000)}
""", prepend=True)
	write_function(f"{ns}:utils/multiply_motion", f"""
# Can't directly multiply motion (Minecraft bug), so store in scoreboards first
$execute store result score #motion_x {ns}.data run data get entity @s Motion[0] $(scale)
$execute store result score #motion_y {ns}.data run data get entity @s Motion[1] $(scale)
$execute store result score #motion_z {ns}.data run data get entity @s Motion[2] $(scale)
execute store result entity @s Motion[0] double 0.001 run scoreboard players get #motion_x {ns}.data
execute store result entity @s Motion[1] double 0.001 run scoreboard players get #motion_y {ns}.data
execute store result entity @s Motion[2] double 0.001 run scoreboard players get #motion_z {ns}.data
tag @s add {ns}.motion_applied
""")

	# Bows damage multiplier
	write_load_file(f"\n# Bow shooting detection\nscoreboard objectives add {ns}.bow_shoot minecraft.used:minecraft.bow\n", prepend=True)
	write_advancement(f"{ns}:technical/bow_shoot", {
		"criteria": {
			"requirement": {
				"trigger": "minecraft:tick",
				"conditions": {
					"player": [
						{
							"condition": "minecraft:entity_scores",
							"entity": "this",
							"scores": {f"{ns}.bow_shoot": {"min": 1}}
						}
					]
				}
			}
		},
		"rewards": {
			"function": f"{ns}:advancements/bow_shoot"
		}
	})

	# Create predicate for sneaking
	Mem.ctx.data[ns].predicates["player/sneaking"] = set_json_encoder(Predicate({"condition":"minecraft:entity_properties","entity":"this","predicate":{"flags":{"is_sneaking":True}}}))

	sb_data: str = f"""{{{ns}:{{"stardust_bow":true}}}}"""
	asb_data: str = f"""{{{ns}:{{"awakened_stardust_bow":true}}}}"""
	ub_data: str = f"""{{{ns}:{{"ultimate_bow":true}}}}"""
	def line_bow(data: str, scale: float) -> str:
		return f"""execute if items entity @s weapon.mainhand *[custom_data~{data}] as @n[type=arrow,tag=!{ns}.damage_multiplied,nbt={{weapon:{{components:{{"minecraft:custom_data":{data}}}}}}}] run function {ns}:utils/modify_arrow {{scale:{scale}}}"""
	write_function(f"{ns}:advancements/bow_shoot", f"""
# Revoke advancement and reset score
advancement revoke @s only {ns}:technical/bow_shoot
scoreboard players set @s {ns}.bow_shoot 0

# Set sneaking flag if player is sneaking
scoreboard players set #is_sneaking {ns}.data 0
execute if predicate {ns}:player/sneaking run scoreboard players set #is_sneaking {ns}.data 1

# If Stardust Bow (x2.0), if Awakened Stardust Bow (x3.0), if Ultimate Bow (x4.0)
{line_bow(sb_data, 2.0)}
{line_bow(asb_data, 3.0)}
{line_bow(ub_data, 4.0)}
""", prepend=True)
	write_function(f"{ns}:utils/modify_arrow", f"""
# Multiply arrow damage
$execute store result entity @s damage double $(scale) run data get entity @s damage 1.0

# Set NoGravity if sneaking
execute if score #is_sneaking {ns}.data matches 1 run data modify entity @s NoGravity set value 1b

# Mark as modified
tag @s add {ns}.damage_multiplied
""")

	# Always dragon egg on death
	write_versioned_function("second_5", f"""
# Always drop dragon egg on death
execute unless score #dragon_in_end {ns}.data matches 1.. in minecraft:the_end if entity @e[type=minecraft:ender_dragon,x=0,y=0,z=0,distance=..320,nbt={{Brain:{{}}}}] run function {ns}:utils/dragon_egg_on_death/has_dragon
""")
	write_function(f"{ns}:utils/dragon_egg_on_death/has_dragon", f"""
# We know there is a dragon, set the flag
scoreboard players set #dragon_in_end {ns}.data 1

# Start monitoring dragon's death
schedule function {ns}:utils/dragon_egg_on_death/monitor 1s append
""")
	write_function(f"{ns}:utils/dragon_egg_on_death/monitor", f"""
# Check if dragon is dead
execute in minecraft:the_end unless entity @e[type=minecraft:ender_dragon,x=0,y=0,z=0,distance=..320,nbt={{Brain:{{}}}}] run function {ns}:utils/dragon_egg_on_death/schedule_place_egg

# Reschedule check
execute if score #dragon_in_end {ns}.data matches 1.. run schedule function {ns}:utils/dragon_egg_on_death/monitor 1s replace
""")
	write_function(f"{ns}:utils/dragon_egg_on_death/schedule_place_egg", f"""
# Schedule dragon egg drop after 10 seconds (to ensure dragon death sequence is over)
schedule function {ns}:utils/dragon_egg_on_death/place_egg_start 10s append
scoreboard players reset #dragon_in_end {ns}.data
""")
	write_function(f"{ns}:utils/dragon_egg_on_death/place_egg_start", f"""
# Drop dragon egg at center of the end
execute in minecraft:the_end positioned 0 100 0 run function {ns}:utils/dragon_egg_on_death/place_egg_loop
""")
	write_function(f"{ns}:utils/dragon_egg_on_death/place_egg_loop", f"""
# If current block is bedrock, stop and place egg
execute unless loaded ~ ~ ~ run return fail
execute if block ~ ~ ~ bedrock run return run setblock ~ ~1 ~ minecraft:dragon_egg

# Else, move down and repeat until bedrock found or bottom reached
execute positioned ~ ~-1 ~ run function {ns}:utils/dragon_egg_on_death/place_egg_loop
""")

	# Magnet functionality
	write_function(f"{ns}:advancements/inventory_changed", f"""
# If has item magnet, add tag and score
execute if entity @s[tag={ns}.has_item_magnet] unless items entity @s weapon.offhand *[custom_data~{{{ns}:{{"item_magnet":true}}}}] run function {ns}:utils/magnet/removed
execute if entity @s[tag=!{ns}.has_item_magnet] if items entity @s weapon.offhand *[custom_data~{{{ns}:{{"item_magnet":true}}}}] run function {ns}:utils/magnet/added
""", prepend=True)
	write_function(f"{ns}:utils/magnet/added", f"""
# Add tag and score
tag @s add {ns}.has_item_magnet
scoreboard players add #has_item_magnet {ns}.data 1
""")
	write_function(f"{ns}:utils/magnet/removed", f"""
# Remove tag and score
tag @s remove {ns}.has_item_magnet
scoreboard players remove #has_item_magnet {ns}.data 1
""")
	write_versioned_function("tick_2", f"""
# Item Magnet functionality
execute if score #has_item_magnet {ns}.data matches 1.. at @a[tag={ns}.has_item_magnet] run tp @e[type=item,distance=..4] ~ ~ ~
""")

	# Lucky Artifact Bag
	write_function(f"{ns}:advancements/right_click", f"""
# If holding a lucky artifact bag, handle it
execute if items entity @s weapon.* *[custom_data~{{{ns}:{{"lucky_artifact_bag":true}}}}] run function {ns}:utils/lucky_artifact_bag
""")
	write_function(f"{ns}:utils/lucky_artifact_bag", f"""
# Give random artifact
loot give @s loot {ns}:random_artifact

# Playsound and particles
particle minecraft:happy_villager ~ ~1 ~ 0.5 0.5 0.5 0 20
playsound minecraft:entity.player.levelup ambient @s ~ ~ ~ 0.5

# Consume one lucky artifact bag
clear @s *[custom_data~{{{ns}:{{lucky_artifact_bag:true}}}}] 1
""")
	Mem.ctx.data[ns].loot_tables["random_artifact"] = set_json_encoder(LootTable({
		"pools": [{
			"rolls": 1,
			"bonus_rolls": 0,
			"entries": [
				{"type": "minecraft:loot_table", "weight": 5, "value": "stardust:i/health_artifact_lv1"},
				{"type": "minecraft:loot_table", "weight": 5, "value": "stardust:i/damage_artifact_lv1"},
				{"type": "minecraft:loot_table", "weight": 5, "value": "stardust:i/speed_artifact_lv1"},
				{"type": "minecraft:loot_table", "value": "stardust:i/health_artifact_lv2"},
				{"type": "minecraft:loot_table", "value": "stardust:i/damage_artifact_lv2"},
				{"type": "minecraft:loot_table", "value": "stardust:i/speed_artifact_lv2"},
			]
		}]
	}), max_level=4)
```

---

## Next steps

- [Helper function reference](reference.md) — the arguments each helper takes.
- [Defining items and blocks](../1_definitions_setup/en.md) — where the content these files
  operate on is declared.
- [Configuring the build](../3_beet_config/en.md) — control when your code runs.
