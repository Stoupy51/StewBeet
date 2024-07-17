
#> your_namespace:calls/simpledrawer/material
#
# @within	#simpledrawer:material
#

execute unless score #success_material simpledrawer.io matches 1 if data storage simpledrawer:io item_material.components."minecraft:custom_data".your_namespace.super_iron_block run function your_namespace:calls/simpledrawer/super_iron/block
execute unless score #success_material simpledrawer.io matches 1 if data storage simpledrawer:io item_material.components."minecraft:custom_data".your_namespace.super_iron_ingot run function your_namespace:calls/simpledrawer/super_iron/ingot
execute unless score #success_material simpledrawer.io matches 1 if data storage simpledrawer:io item_material.components."minecraft:custom_data".your_namespace.super_iron_nugget run function your_namespace:calls/simpledrawer/super_iron/nugget
execute unless score #success_material simpledrawer.io matches 1 if data storage simpledrawer:io item_material.components."minecraft:custom_data".your_namespace.raw_super_iron_block run function your_namespace:calls/simpledrawer/raw_super_iron/block
execute unless score #success_material simpledrawer.io matches 1 if data storage simpledrawer:io item_material.components."minecraft:custom_data".your_namespace.raw_super_iron run function your_namespace:calls/simpledrawer/raw_super_iron/ingot

