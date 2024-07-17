
#> your_namespace:calls/simpledrawer/raw_super_iron/main
#
# @within	your_namespace:calls/simpledrawer/raw_super_iron/block
#			your_namespace:calls/simpledrawer/raw_super_iron/ingot
#

# Set score of material found to 1
scoreboard players set #success_material simpledrawer.io 1

# Set the convert counts
scoreboard players set #ingot_in_block simpledrawer.io 9
scoreboard players set #nugget_in_ingot simpledrawer.io 9

# Set the material data
data modify storage simpledrawer:io material set value {material: "your_namespace.raw_super_iron", material_name:'Raw Super Iron'}

# Fill the NBT with your own items
data modify storage simpledrawer:io material.block.item set from storage your_namespace:items all.raw_super_iron_block
data modify storage simpledrawer:io material.ingot.item set from storage your_namespace:items all.raw_super_iron

