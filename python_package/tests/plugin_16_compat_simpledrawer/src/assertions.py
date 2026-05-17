
# Assertions for: stewbeet.plugins.compatibilities.simpledrawer

# Imports
from beet import Context


# Main entry point
def beet_default(ctx: Context):
    ns: str = ctx.project_id

    # ── simpledrawer:material function tag ────────────────────────────────────
    assert "material" in ctx.data["simpledrawer"].function_tags, \
        "simpledrawer:material function tag must be created"
    tag_text: str = ctx.data["simpledrawer"].function_tags["material"].text
    assert f"{ns}:calls/simpledrawer/material" in tag_text, \
        "simpledrawer:material tag must reference the namespace material function"

    # ── material dispatch function ────────────────────────────────────────────
    material_path: str = f"{ns}:calls/simpledrawer/material"
    assert material_path in ctx.data.functions, \
        "calls/simpledrawer/material function must be generated"
    material_content: str = ctx.data.functions[material_path].text
    # Must reference all three variant checks (block, ingot, nugget)
    assert "ruby_block" in material_content, \
        "material function must check for ruby_block"
    assert "ruby_ingot" in material_content, \
        "material function must check for ruby_ingot"
    assert "ruby_nugget" in material_content, \
        "material function must check for ruby_nugget"

    # ── per-variant dispatch functions ────────────────────────────────────────
    for variant in ["block", "ingot", "nugget"]:
        variant_path: str = f"{ns}:calls/simpledrawer/ruby/{variant}"
        assert variant_path in ctx.data.functions, \
            f"calls/simpledrawer/ruby/{variant} must be generated"
        variant_content: str = ctx.data.functions[variant_path].text
        assert f"function {ns}:calls/simpledrawer/ruby/main" in variant_content, \
            f"{variant} dispatch must call the ruby/main function"

    # ── main ruby function ────────────────────────────────────────────────────
    main_path: str = f"{ns}:calls/simpledrawer/ruby/main"
    assert main_path in ctx.data.functions, \
        "calls/simpledrawer/ruby/main must be generated"
    main_content: str = ctx.data.functions[main_path].text
    # Must set the ingot_in_block and nugget_in_ingot conversion scores
    assert "scoreboard players set #ingot_in_block simpledrawer.io" in main_content, \
        "ruby/main must set the ingot_in_block conversion ratio"
    assert "scoreboard players set #nugget_in_ingot simpledrawer.io" in main_content, \
        "ruby/main must set the nugget_in_ingot conversion ratio"
    # Must populate the material storage with ruby items
    assert "ruby_block" in main_content, \
        "ruby/main must reference ruby_block in storage"
    assert "ruby_ingot" in main_content, \
        "ruby/main must reference ruby_ingot in storage"
    assert "ruby_nugget" in main_content, \
        "ruby/main must reference ruby_nugget in storage"
