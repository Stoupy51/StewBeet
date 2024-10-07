
#> your_namespace:calls/simpledrawer/material
#
# @within	#simpledrawer:material
#

execute unless score #success_material simpledrawer.io matches 1 if data storage simpledrawer:io item_material.components."minecraft:custom_data".your_namespace.steel_block run function your_namespace:calls/simpledrawer/steel/block
execute unless score #success_material simpledrawer.io matches 1 if data storage simpledrawer:io item_material.components."minecraft:custom_data".your_namespace.steel_ingot run function your_namespace:calls/simpledrawer/steel/ingot
execute unless score #success_material simpledrawer.io matches 1 if data storage simpledrawer:io item_material.components."minecraft:custom_data".your_namespace.steel_nugget run function your_namespace:calls/simpledrawer/steel/nugget
execute unless score #success_material simpledrawer.io matches 1 if data storage simpledrawer:io item_material.components."minecraft:custom_data".your_namespace.raw_steel_block run function your_namespace:calls/simpledrawer/raw_steel/block
execute unless score #success_material simpledrawer.io matches 1 if data storage simpledrawer:io item_material.components."minecraft:custom_data".your_namespace.raw_steel run function your_namespace:calls/simpledrawer/raw_steel/ingot

