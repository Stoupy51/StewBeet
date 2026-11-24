
#> _your_namespace:custom_blocks/lamp/replace_item
#
# @executed	as @e[type=item,tag=_your_namespace.drop,distance=..0.01]
#
# @within	_your_namespace:custom_blocks/lamp/destroy [ as @e[type=item,tag=_your_namespace.drop,distance=..0.01] ]
#

# The item destroy summoned holding a placeholder
tag @s remove _your_namespace.drop

# Make it the custom item
loot replace entity @s contents loot _your_namespace:i/lamp

