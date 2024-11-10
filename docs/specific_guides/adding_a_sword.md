
# ⚔️ Adding a Custom Sword
This guide will show you two different ways to add a custom sword named `test_sword` to your project.<br>
First, you'll have to put the `test_sword.png` texture file in the [`assets/textures`](../../assets/textures/) folder.<br>
Then, you'll have to add it to the database with one of the following methods through the [`setup_database.py`](../../user/setup_database.py) script.<br>
I **highly recommend** using the second method, as it is easier and faster.


## 📝 Method 1: Direct Database Entry
The first method involves directly defining the sword in your database.<br>
I'll go progressively through the code, explaining each part.<br>
Item definition should be written in the `main()` function:
```py
...
def main():
	...
	database["test_sword"] = {...}
	...
```

The simplest way is to simply define the item in the database like this:
```py
database["test_sword"] = {"id": "minecraft:diamond_sword"}
```
This will automatically generate the sword with the same properties as the diamond sword and use the `test_sword.png` texture.

You may want to customize the properties of the sword, such as its durability or attributes.<br>
You can do this by adding more keys to the dictionary:
```py
database["test_sword"] = {
	"id": "minecraft:diamond_sword",	# Base item

	# Components that will be added to the item like '/give @s diamond_sword[max_damage=1000,attribute_modifiers=[...]]'
	"max_damage": 1000,					# Custom durability
	"attribute_modifiers": [{			# Custom attributes, here we add 8 attack damage
		"type": "attack_damage",
		"amount": 8,
		"operation": "add_value",
		"slot": "mainhand",
		"id": "minecraft:base_attack_damage"
	}]
}
```

Finally, if you come up with a fully custom sword, you can define it like this:
```py
database["test_sword"] = {
	# Base item definition
	"id": "minecraft:diamond_sword",  # Using diamond sword as base
	"category": "combat",             # For in-game manual organization
	
	# Item properties
	"max_damage": 1000,               # Durability (lower than diamond sword)
	"attribute_modifiers": [{         # Combat stats
		"type": "attack_damage",
		"amount": 8,                  # Base damage (7 = diamond sword + 1)
		"operation": "add_value",
		"slot": "mainhand",
		"id": f"{namespace}:attack_damage.mainhand"
	}],
	
	# Crafting recipe
	RESULT_OF_CRAFTING: [{
		"type": "crafting_shaped",
		"category": "combat",
		"group": "test_sword",
		"shape": ["X", "X", "S"],
		"ingredients": {
			"X": ingr_repr("test_ingot", namespace),    # Your custom material (assuming you have a material named "test_ingot")
			"S": ingr_repr("minecraft:stick")           # Vanilla stick
		}
	}]
}
```


## 🛠️ Method 2: Using EquipmentsConfig
The second method uses the `EquipmentsConfig` helper to automatically generate equipment:

```py
ORES_CONFIGS: dict[str, EquipmentsConfig|None] = {

	# "test_ingot" is the name of the material but doesn't have to exist.
	# The 'generate_everything_about_these_materials()' function will try to find every stuff related to it in the textures folder tho, such as a "test_sword.png" texture.
	"test_ingot": EquipmentsConfig(
		# Base this material's properties on diamond
		equivalent_to = DEFAULT_ORE.DIAMOND,
		
		# Durability is calculated based on the pickaxe durability of the material it's equivalent to.
		# Even though you might not use pickaxes, the durability is still calculated based on the pickaxe durability.
		# Here, we make all our stuff 3 times more durable than iron (including the "test_sword" that we'll get)
		pickaxe_durability = 3 * VanillaEquipments.PICKAXE.value[DEFAULT_ORE.IRON]["durability"],
		
		# Custom attributes: Adds +1 attack damage to every mainhand item, +0.5 armor points to every armor, and increases mining speed by 20% to every mainhand item (pickaxe, axe, hoe, ...)
		attributes = {"attack_damage": 1, "armor": 0.5, "mining_efficiency": 0.2}
	)
}

...

# Generate everything about test_ingot (including sword)
generate_everything_about_these_materials(config, database, ORES_CONFIGS)
```


## 🔄 Comparison
### Method 1: Direct Database Entry
**Pros:**
- ✅ Complete control over every property
- ✅ Clear and explicit definition
- ✅ Can create unique items not based on vanilla equipment

**Cons:**
- ❌ More code to write
- ❌ Need to manually set all properties
- ❌ Need to remember attribute IDs and formats

### Method 2: EquipmentsConfig
**Pros:**
- ✅ Automatically generates all equipment types
- ✅ Less code to write
- ✅ Consistent with vanilla equipment patterns
- ✅ Handles all attribute IDs automatically

**Cons:**
- ❌ There are no cons


## 📚 Conclusion
You now know two ways to add custom swords to your datapack! 
- Use **EquipmentsConfig** for complete material sets
- Use **Direct Database Entry** for unique items

Choose the method that best fits your needs! 🎯<br>
Thank you for reading 🙌

