
#> _your_namespace:custom_blocks/vb_contents/search
#
# @executed	as the player & at current position
#
# @within	advancement _your_namespace:custom_block_alternative/vb_contents
#

# Advancement revoke
advancement revoke @s only _your_namespace:custom_block_alternative/vb_contents

# Execute the place function as and at the new placed item frame
execute as @e[type=item_frame, tag=_your_namespace.new, tag=_your_namespace.vb_contents] at @s run function _your_namespace:custom_blocks/vb_contents/place_main

