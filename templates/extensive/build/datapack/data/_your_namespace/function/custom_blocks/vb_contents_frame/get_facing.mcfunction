
#> _your_namespace:custom_blocks/vb_contents_frame/get_facing
#
# @executed	as @e[type=item_frame,tag=...] & at @s
#
# @within	_your_namespace:custom_blocks/vb_contents_frame/place_main
#

# Get the facing and delete the old entity
execute store result score #item_frame_facing _your_namespace.data run data get entity @s Facing
kill @s

## sourceMappingURL=get_facing.mcfunction.map
