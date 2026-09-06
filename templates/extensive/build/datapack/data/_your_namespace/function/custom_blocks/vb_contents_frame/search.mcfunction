
#> _your_namespace:custom_blocks/vb_contents_frame/search
#
# @executed	as the player & at current position
#
# @within	advancement _your_namespace:custom_block_alternative/vb_contents_frame
#

# Advancement revoke
advancement revoke @s only _your_namespace:custom_block_alternative/vb_contents_frame

# Execute the place function as and at the new placed item frame
execute as @e[type=item_frame, tag=_your_namespace.new, tag=_your_namespace.vb_contents_frame] at @s run function _your_namespace:custom_blocks/vb_contents_frame/place_main

## sourceMappingURL=search.mcfunction.map
