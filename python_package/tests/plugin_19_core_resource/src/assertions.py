
# Assertions for: stewbeet.core.cls.resource
#
# The expected locations below are written out as literals ON PURPOSE: they are the
# independent oracle for the conventions. If an accessor ever changes what it points
# at, this test fails instead of silently moving every generated file with it.

# Imports
from beet import Advancement, Context, Function, ItemModel, LootTable, Model, Texture

from stewbeet import Block, BlockAlternative, BlockHead, Item, Resource


# Main entry point
def beet_default(ctx: Context):
    ns: str = ctx.project_id

    # --- Item accessors point at the documented conventions ---
    plain = Item.from_id("plain_item")
    assert plain.loot_table == f"{ns}:i/plain_item", plain.loot_table
    assert plain.item_model == f"{ns}:plain_item", plain.item_model
    assert plain.generated_item_model == f"{ns}:plain_item", plain.generated_item_model
    assert plain.model == f"{ns}:item/plain_item", plain.model
    assert plain.texture == f"{ns}:item/plain_item", plain.texture
    assert plain.recipe() == f"{ns}:plain_item", plain.recipe()
    assert plain.recipe(2) == f"{ns}:plain_item_2", plain.recipe(2)

    # A Resource is a real str: it must compare, hash and format like one
    assert isinstance(plain.loot_table, str)
    keyed_by_resource: dict[str, int] = {plain.loot_table: 1}
    assert keyed_by_resource[f"{ns}:i/plain_item"] == 1
    assert f"loot give @s loot {plain.loot_table}" == f"loot give @s loot {ns}:i/plain_item"

    # --- Count variants ---
    bulk = Item.from_id("bulk_item")
    assert bulk.loot_table_for(1) == bulk.loot_table, "count=1 must not add a suffix"
    assert bulk.loot_table_for(4) == f"{ns}:i/bulk_item_x4", bulk.loot_table_for(4)
    assert bulk.loot_table_for({"min": 4, "max": 6}) == f"{ns}:i/bulk_item_x4to6"

    # --- item_model override is honored, generated_item_model is not moved by it ---
    overridden = Item.from_id("overridden_model")
    assert overridden.item_model == "minecraft:air", overridden.item_model
    assert overridden.item_model.namespace == "minecraft"
    assert overridden.generated_item_model == f"{ns}:overridden_model"

    # --- Block function accessors ---
    block = Block.from_id("regular_block")
    assert block.functions.folder == f"{ns}:custom_blocks/regular_block"
    assert block.functions.place_main == f"{ns}:custom_blocks/regular_block/place_main"
    assert block.functions.place_secondary == f"{ns}:custom_blocks/regular_block/place_secondary"
    assert block.functions.destroy == f"{ns}:custom_blocks/regular_block/destroy"
    assert block.functions["anything"] == f"{ns}:custom_blocks/regular_block/anything"
    assert block.no_silk_touch_loot_table == f"{ns}:custom_blocks/no_silk_touch_drop/regular_block"
    assert block.seed_loot_table == f"{ns}:seeds/regular_block"

    # A regular custom block has no placement advancement of its own
    try:
        _ = block.advancement
        raise AssertionError("regular custom blocks must not expose a placement advancement")
    except ValueError:
        pass

    # --- Advancement-backed custom blocks ---
    alt = BlockAlternative.from_id("alternative_block")
    assert alt.advancement == f"{ns}:custom_block_alternative/alternative_block"
    assert alt.advancement == alt.alternative_advancement

    head = BlockHead.from_id("head_block")
    assert head.advancement == f"{ns}:custom_block_head/head_block"
    assert head.head_search == f"{ns}:custom_blocks/_player_head/search_head_block"

    # --- Accessors reach the files the plugins actually generated ---
    assert plain.loot_table.exists(), "the loot_tables plugin must have generated this loot table"
    assert isinstance(plain.loot_table.obj, LootTable)
    assert plain.loot_table.get() is not None
    assert plain.loot_table.relative_path == "i/plain_item"
    assert plain.loot_table.namespace == ns
    assert plain.loot_table.file_type is LootTable

    assert block.functions.place_main.exists(), "custom_blocks must have generated place_main"
    assert isinstance(block.functions.place_main.obj, Function)
    assert alt.advancement.exists(), "custom_blocks must have generated the placement advancement"
    assert isinstance(alt.advancement.obj, Advancement)

    # --- A missing file raises KeyError on .obj but returns the default on .get() ---
    missing: Resource[LootTable] = Resource(LootTable, "i/does_not_exist")
    assert not missing.exists()
    assert missing.get() is None
    try:
        _ = missing.obj
        raise AssertionError(".obj must raise KeyError when the file does not exist")
    except KeyError:
        pass

    # --- The owning pack is resolved from the file type ---
    assert plain.loot_table.pack is ctx.data
    assert plain.model.pack is ctx.assets
    assert plain.model.file_type is Model
    assert plain.texture.file_type is Texture
    assert plain.item_model.file_type is ItemModel

    # --- Derivation helpers ---
    assert plain.model.suffixed("_on") == f"{ns}:item/plain_item_on"
    assert plain.model.suffixed("") == plain.model
    assert block.functions.folder.child("custom") == f"{ns}:custom_blocks/regular_block/custom"
    assert block.functions.place_main.sibling("destroy") == block.functions.destroy

    # --- Round-tripping a full location keeps the foreign namespace ---
    foreign: Resource[LootTable] = Resource(LootTable, "other_pack:base/thing")
    assert foreign.namespace == "other_pack"
    assert foreign.relative_path == "base/thing"
    assert foreign == "other_pack:base/thing"
