particle minecraft:enchant ~ ~1 ~ 0.4 0.6 0.4 0.02 24
scoreboard players set @s ns.aura 60
execute as @e[tag=ns.spawned] run scoreboard players remove @s ns.aura 1
## sourceMappingURL=aura.mcfunction.map
