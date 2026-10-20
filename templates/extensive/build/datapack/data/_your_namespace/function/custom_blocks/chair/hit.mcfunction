
#> _your_namespace:custom_blocks/chair/hit
#
# @executed	at @s & positioned ~ ~0.5 ~
#
# @within	_your_namespace:custom_blocks/_interaction/dispatch_hit [ at @s & positioned ~ ~0.5 ~ ]
#

# A hit coming 20 ticks or more after the previous one starts the count again
particle minecraft:item{item: {id: "minecraft:furnace", components: {"minecraft:item_model": "_your_namespace:chair"}}} ~ ~ ~ 0.25 0.25 0.25 0.05 8
playsound minecraft:block.wood.hit block @a ~ ~ ~ 0.4
execute unless score @s _your_namespace.last_hit matches -2147483648.. run scoreboard players set @s _your_namespace.last_hit 0
execute store result score #now _your_namespace.data run time query gametime
scoreboard players operation #elapsed _your_namespace.data = #now _your_namespace.data
scoreboard players operation #elapsed _your_namespace.data -= @s _your_namespace.last_hit
execute if score #elapsed _your_namespace.data matches 20.. run scoreboard players set @s _your_namespace.hits 0
scoreboard players operation @s _your_namespace.last_hit = #now _your_namespace.data
scoreboard players add @s _your_namespace.hits 1
execute unless entity @p[tag=_your_namespace.breaker, gamemode=creative] if score @s _your_namespace.hits matches ..2 run return 0

# Break it, dropping nothing for a creative player or a tool too weak
execute store success score #no_drop _your_namespace.data if entity @p[tag=_your_namespace.breaker, gamemode=creative]
execute if score #no_drop _your_namespace.data matches 0 unless items entity @p[tag=_your_namespace.breaker] weapon.mainhand #_your_namespace:mining/pickaxe_iron run scoreboard players set #no_drop _your_namespace.data 1
function _your_namespace:custom_blocks/_interaction/break

