
#> your_namespace:calls/simpledrawer/super_iron/main
#
# @within	your_namespace:calls/simpledrawer/super_iron/block
#			your_namespace:calls/simpledrawer/super_iron/ingot
#			your_namespace:calls/simpledrawer/super_iron/nugget
#

# Set score of material found to 1
scoreboard players set #success_material simpledrawer.io 1

# Set the convert counts
scoreboard players set #ingot_in_block simpledrawer.io 9
scoreboard players set #nugget_in_ingot simpledrawer.io 9

# Set the material data
data modify storage simpledrawer:io material set value {material: "your_namespace.super_iron", material_name:'Super Iron'}

# Fill the NBT with your own items
data modify storage simpledrawer:io material.block.item set from storage your_namespace:items all.super_iron_block
data modify storage simpledrawer:io material.ingot.item set from storage your_namespace:items all.super_iron_ingot
data modify storage simpledrawer:io material.nugget.item set from storage your_namespace:items all.super_iron_nugget

