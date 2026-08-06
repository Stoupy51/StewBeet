import type { FileNode } from './FileTree';

/**
 * Adapted from the life_crystal_block of Stardust Fragment: the EQUIPMENT constant is inlined and
 * the long override_model dropped, from src/definitions/additions/equipments.py, and the ore
 * generation call is folded in from src/utils/custom_ore_generation.py, where that project keeps
 * it. Both belong here because the file tree beside this is the block's real build output, and
 * without the second call three of its entries would have nothing on this side that asks for them.
 *
 * Lines are kept under 66 columns: the snippet sits in half the hero and anything longer is
 * cut mid-string on a 1280px screen, which reads as a rendering bug rather than as scrollable code.
 *
 * It lives in its own module so scripts/prehighlight.ts can import it and run Shiki over it at
 * build time. Highlighting it in the browser meant the largest element in the viewport painted
 * as plain text and then swapped to coloured markup a few hundred milliseconds later.
 */
export const HERO_CODE: string = `Block(
    id="life_crystal_block",
    vanilla_block=VanillaBlock(id="minecraft:glass"),
    manual_category="equipment",
    components={
        "item_name": {"text": "Life Crystal Block"},
        "lore": [{"text": "Break it to get the crystal back"}],
    },
    # Broken without Silk Touch, it hands the crystal back
    no_silk_touch_drop=NoSilkTouchDrop(
        id="life_crystal", count=1,
    ),
    recipes=[CraftingShapelessRecipe(
        category="equipment", result_count=1,
        ingredients=8 * [Ingr("minecraft:glass")]
            + [Ingr("life_crystal")],
    )],
)
# Single-block veins, deep in the overworld, carved into stone
CustomOreGeneration.all_with_config({
    "life_crystal_block": [CustomOreGeneration(
    dimensions=["minecraft:overworld"],
    minimum_height=-32, maximum_height=50,
    veins_per_region=2.5,
    provider=["#minecraft:overworld_carver_replaceables"],
)]})`;

/** Every file in the Stardust Fragment build that belongs to life_crystal_block. */
export const GENERATED_FILES: FileNode[] = [
    {
        name: 'build/',
        children: [
            {
                name: 'datapack/',
                children: [
                    {
                        name: 'custom_blocks/life_crystal_block/',
                        children: [
                            { name: 'place_main.mcfunction' },
                            { name: 'place_secondary.mcfunction' },
                            { name: 'destroy.mcfunction' },
                            { name: 'replace_item.mcfunction', note: 'silk touch, else the crystal' },
                        ],
                    },
                    { name: 'calls/smithed_crafter/shapeless_recipes.mcfunction', note: 'the recipe, NBT-aware' },
                    { name: 'calls/smart_ore_generation/veins/life_crystal_block.mcfunction', note: 'world gen' },
                    { name: 'calls/smart_ore_generation/veins/retry/life_crystal_block.mcfunction' },
                    { name: 'tags/block/smart_ore_generation/life_crystal_block_provider.json' },
                    { name: 'loot_table/i/life_crystal_block.json' },
                ],
            },
            {
                name: 'resource_pack/',
                children: [
                    { name: 'items/life_crystal_block.json' },
                    { name: 'models/item/life_crystal_block.json' },
                    { name: 'textures/item/life_crystal_block.png' },
                    { name: 'textures/item/life_crystal_block.png.mcmeta' },
                    { name: 'textures/item/dialog_sprite/life_crystal_block.png' },
                    { name: 'textures/font/high_res/life_crystal_block.png' },
                    { name: 'textures/font/wiki_icons/life_crystal_block_crafting_shapeless.png' },
                ],
            },
        ],
    },
];
