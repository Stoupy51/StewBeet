
# A .mcfunction holding bolt, which StewBeet's own minimal template ships too.
# Spyglass cannot parse a `for` loop, so the extension gives this file the bolt language id.

for offset in range(1, 4):
    execute if block ~ ~-offset ~ #voltaic:elevator run function ./lift

execute function ./lift:
    tp @s ~ ~0.6 ~
    playsound voltaic:elevator block @s

