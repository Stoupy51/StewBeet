
# Assertions for: stewbeet.plugins.compatibilities.neo_enchant

# Imports
from beet import Context


# Main entry point
def beet_default(ctx: Context):
    # ── enchantplus:veinminer block tag must be created ───────────────────────
    assert "enchantplus:veinminer" in ctx.data["enchantplus"].block_tags, \
        "enchantplus:veinminer block tag must be generated"

    veinminer_text: str = ctx.data["enchantplus"].block_tags["veinminer"].text

    # The VANILLA_BLOCK_FOR_ORES id (minecraft:polished_deepslate) must be in the tag
    assert "minecraft:polished_deepslate" in veinminer_text, \
        "veinminer tag must contain minecraft:polished_deepslate (VANILLA_BLOCK_FOR_ORES)"

    # Only the vanilla ore placeholder appears — not the custom block that uses red_concrete
    assert "red_concrete" not in veinminer_text, \
        "veinminer tag must NOT contain the non-ore block's vanilla id"
