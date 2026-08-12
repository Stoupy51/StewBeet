/**
 * Starting points for the playground editor.
 *
 * Every one of them uses item ids the bundled packs have textures for, so a reader who presses
 * Build before editing anything sees real textures rather than the missing-texture checkerboard.
 * Renaming an item still works: the sandbox substitutes a placeholder and says so in the log.
 *
 * Four spaces, not tabs. This is rendered in a browser, where a tab stop is eight columns and the
 * lines would run past the pane.
 */

export interface Preset {
    id: string;
    code: string;
}

const ITEM = `from beet import Context
from stewbeet import *


def beet_default(ctx: Context):
    Item(
        id="steel_ingot",
        manual_category="material",
        components={
            "item_name": {"text": "Steel Ingot"},
            "lore": [{"text": "Refined from raw iron"}],
        },
    )

    add_item_model_component()
    add_item_name_and_lore_if_missing()
    add_private_custom_data_for_namespace()
`;

const BLOCK = `from beet import Context
from stewbeet import *


def beet_default(ctx: Context):
    Item(
        id="steel_ingot",
        components={"item_name": {"text": "Steel Ingot"}},
    )

    Block(
        id="steel_block",
        vanilla_block=VanillaBlock(id="minecraft:iron_block"),
        components={
            "item_name": {"text": "Steel Block"},
            "lore": [{"text": "Break it to get the ingots back"}],
        },
        no_silk_touch_drop=NoSilkTouchDrop(id="steel_ingot", count=9),
        recipes=[CraftingShapelessRecipe(
            category="building",
            result_count=1,
            ingredients=9 * [Ingr("steel_ingot")],
        )],
    )

    add_item_model_component()
    add_item_name_and_lore_if_missing()
`;

const RECIPES = `from beet import Context
from stewbeet import *


def beet_default(ctx: Context):
    Item(
        id="steel_ingot",
        components={"item_name": {"text": "Steel Ingot"}},
        recipes=[
            FurnaceRecipe(
                category="misc",
                ingredient=Ingr("minecraft:raw_iron"),
                result_count=1,
            ),
            CraftingShapedRecipe(
                category="misc",
                result_count=9,
                shape=["S"],
                ingredients={"S": Ingr("steel_block")},
            ),
        ],
    )

    Item(
        id="steel_block",
        components={"item_name": {"text": "Steel Block"}},
    )

    add_item_model_component()
    add_item_name_and_lore_if_missing()
`;

const RENDER = `from beet import Context
from stewbeet import *


def beet_default(ctx: Context):
    # A "render" node anywhere a text component is allowed becomes a font
    # glyph of that item, so the tooltip shows a picture of it.
    Item(
        id="steel_ingot",
        components={
            "item_name": {"text": "Steel Ingot"},
            "lore": [[
                {"render": "steel_ingot"},
                {"text": " smelted from raw iron"},
            ]],
        },
    )

    add_item_model_component()
    add_item_name_and_lore_if_missing()
`;

export const PRESETS: Preset[] = [
    { id: 'item', code: ITEM },
    { id: 'block', code: BLOCK },
    { id: 'recipes', code: RECIPES },
    { id: 'render', code: RENDER },
];

export const DEFAULT_CODE = ITEM;
