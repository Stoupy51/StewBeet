
#> _your_namespace:custom_blocks/vb_contents_player/search
#
# @executed	as the player & at current position
#
# @within	advancement _your_namespace:custom_block_alternative/vb_contents_player
#

# Advancement revoke
advancement revoke @s only _your_namespace:custom_block_alternative/vb_contents_player

# Execute the place function as and at the new placed item frame
function _your_namespace:custom_blocks/get_rotation
execute as @e[type=item_frame, tag=_your_namespace.new, tag=_your_namespace.vb_contents_player] at @s run function _your_namespace:custom_blocks/vb_contents_player/place_main

