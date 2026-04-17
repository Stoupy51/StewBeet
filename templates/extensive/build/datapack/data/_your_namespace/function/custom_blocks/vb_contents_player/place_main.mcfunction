
#> _your_namespace:custom_blocks/vb_contents_player/place_main
#
# @executed	as @e[type=item_frame,tag=...] & at @s
#
# @within	_your_namespace:custom_blocks/vb_contents_player/search [ as @e[type=item_frame,tag=...] & at @s ]
#

# Get the facing direction of the item frame
scoreboard players set #item_frame_facing _your_namespace.data 1
execute if entity @s[type=item_frame] run function _your_namespace:custom_blocks/vb_contents_player/get_facing

# Summon the new item frame (not execute summon because it would not be invisible for a tick)
summon item_frame ~ ~ ~ {Tags: ["_your_namespace.new"], Invulnerable: false, Invisible: true, Fixed: false, Silent: true}
execute as @n[tag=_your_namespace.new] at @s run function _your_namespace:custom_blocks/vb_contents_player/place_secondary

# Increment count scores
scoreboard players add #total_custom_blocks _your_namespace.data 1
scoreboard players add #total_vanilla_item_frame _your_namespace.data 1
scoreboard players add #total_vb_contents_player _your_namespace.data 1

# Replace the placing sound
playsound minecraft:block.stone.place block @a[distance=..5]

