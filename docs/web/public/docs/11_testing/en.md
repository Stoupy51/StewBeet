
# Testing your pack with Ward

[Ward](https://github.com/mcbookshelf/ward) runs `.mcfunction` tests on a headless server and reports each `assert` that fails with its file and line.
A StewBeet project keeps its tests in a `tests/` folder next to `src/`, as a second datapack loaded beside the built zip, so the tests run against exactly what players download, libraries included.

### Layout

```
tests/
	pack.mcmeta
	data/
		minecraft/tags/function/load.json           -> {"values": ["<ns>_test:load"]}
		<ns>_test/
			function/load.mcfunction                 -> scoreboard objectives add <ns>_test.data dummy
			function/spawn_loader.mcfunction         -> dummy loader spawn
			structure/room.nbt                       -> an empty 5x5x5 structure
			test_environment/loaded.json
			test/<behaviour>.mcfunction              -> one file per test
```

Use a namespace of its own, `<ns>_test`, so the command below runs your tests only: libraries like ItemIO ship their own Ward tests in the zip, and those run too when the selector matches them.

### A pack that waits for a player

A StewBeet pack only loads once a player is online: `valid_dependencies` reads the game version from `@p` and reschedules itself while nobody is there.
A Ward world has no player, so `#<ns>.loaded` never reaches 1 unless a test environment spawns a [dummy](https://github.com/mcbookshelf/ward/blob/main/docs/dummies.md) that stays for the whole run:

```json
{
	"type": "minecraft:function",
	"setup": "<ns>_test:spawn_loader"
}
```

Every test then names this environment and waits for the pack before doing anything:

```mcfunction
# @template <ns>_test:room
# @environment <ns>_test:loaded
# @dummy ~ ~ ~
# @timeout 200
await score #<ns>.loaded load.status matches 1

loot replace entity @s weapon.mainhand loot <ns>:i/pulverizer
item modify entity @s weapon.mainhand {type:"minecraft:set_count",count:2}
dummy @s use block ~2 ~-1 ~2
execute positioned ~2.5 ~.5 ~2.5 run await entity @e[tag=<ns>.pulverizer,distance=..0.5]
```

`dummy @s use block` places a custom block the way a player does, so Smithed Custom Block and the `place` functions run for real.
Hand the dummy a stack of two. Its action runs inside a command, so the game queues the Smithed Custom Block advancement reward until that command ends, after the survival dummy's item is taken. Placed from the last item of a stack, the block then finds `SelectedItem` empty and whatever its `place` functions copy from the item (stored energy, saved slots) is lost. A real player's reward runs before the item is taken, so this only happens in tests.

`room.nbt` exists because the 26.3 build of Ward has no `ward:empty/*` templates, and its default template is one block of air, too low for a dummy. Write it once with the nbtlib that beet installs:

```python
from nbtlib import File, Compound, List, Int
room = Compound({"size": List[Int]([5, 5, 5]), "entities": List([]), "blocks": List([]), "palette": List([]), "DataVersion": Int(5023)})
File({"": room}, gzipped=True).save("tests/data/<ns>_test/structure/room.nbt")
```

### Building and running

Build without the copy to your world: `build_copy_destinations` would otherwise overwrite the datapack of the world you play in.

```sh
beet -s "meta.stewbeet.build_copy_destinations.datapack=null" -s "meta.stewbeet.build_copy_destinations.resource_pack=null" build
uvx "mcward[cli]" test -p build/<Name>_datapack_with_libs.zip -p tests -v 26.3 "<ns>_test:*"
```

Add `--verbose` to list every test. The first run starts a server that stays up, so the next runs take a few seconds; `uvx "mcward[cli]" stop --all` stops it.
Do not use `beet test`: it tests the source pack, without the libraries Smithed Weld merges into the zip.

A function that does not parse is not loaded, and Ward lists it before the results, as `[minecraft:function] <ns>:<path>`, so a typo in a generated command shows up even when no test calls that function.

### Traps

- Tests of one batch run at the same time in areas a few blocks apart. Select your blocks with `distance=`, as in `execute positioned ~2.5 ~.5 ~2.5 run assert entity @e[tag=<ns>.pulverizer,distance=..0.5]`, never with a bare tag.
- `~ ~ ~` is the north-west bottom corner of the template, and a test runs as its dummy but at that corner.
- `tp @s ~.5 ~ ~.5 facing <pos>` aims from the feet, not the eyes. Give an explicit rotation (`tp @s ~.5 ~ ~.5 -45 22`) to make the dummy look at a block for a raycast.
- `loot replace block` refuses a furnace output slot. Put the item in the dummy's inventory with `loot replace entity @s hotbar.8`, then `item replace block <pos> container.2 from entity @s hotbar.8`.
- An inline item modifier takes `type` in 26.x, not `function`: `item modify block <pos> container.0 {type:"minecraft:set_count",count:64}`.
- Furnace NBT Recipes starts ticking furnaces two seconds after it loads. A furnace test first waits for its shulker box: `await block -30000000 14 1610 minecraft:yellow_shulker_box`.
- A test that runs the load function again, or changes anything shared, gets an environment of its own, an `all_of` around the same setup, so that it runs in a batch alone.
- The 26.3 build of Ward has no `log` command. To see a value, store it in a storage and end the test with `fail {"storage":"dbg","nbt":"{}"}`.
- `@optional` failures count as passed in the summary: keep a test that reproduces a known bug failing.

### Checking that a test catches something

A test proves something only once it has failed. Break the line it guards in the built zip (a copy, the project stays untouched), run the suite on that zip, and check that this test, and no unrelated one, turns red.

