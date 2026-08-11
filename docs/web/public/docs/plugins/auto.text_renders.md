# stewbeet.plugins.auto.text_renders

The `auto.text_renders` plugin adds a `render` key to Minecraft text components.<br>
Anywhere a text component can appear (an item lore, the `source_lore`, a `tellraw`, a manual dialog),<br>
`{"render": "steel_ingot"}` becomes a picture of that item, drawn with a bitmap font the plugin generates for you.

No font to declare, no unicode character to reserve, no texture to place: write the item id and the glyph appears.

### <u>Feature Showcase</u>

**Example of text components code being modified to use font glyphs:**<br>
<img src="https://raw.githubusercontent.com/Stoupy51/StewBeet/main/docs/plugins/img/auto.text_renders.example_code.jpg">

**And the result in-game:**<br>
<img src="https://raw.githubusercontent.com/Stoupy51/StewBeet/main/docs/plugins/img/auto.text_renders.example_ingame.jpg">

**Required**: Beet context with generated datapack files  
**Required**: Item images in `iso_renders_path` (produced by `ingame_manual`, or dropped there yourself)  
**Position**: After `auto.lang_file`, before `auto.headers`  
**Related**: [`ingame_manual`](../7_ingame_manual/en.md) shares the same item renders, [`initialize`](initialize.md) owns `source_lore`  
**Source Code**: [`stewbeet/plugins/auto/text_renders/__init__.py`](https://github.com/Stoupy51/StewBeet/blob/main/python_package/stewbeet/plugins/auto/text_renders/__init__.py) <br>


## What it does

- Scans every generated datapack file for `render` keys inside text components
- Resolves each item id to a PNG: a project item is rendered with `model_resolver`, a `minecraft:` item is downloaded, any other namespace is read from `iso_renders_path`
- Generates one glyph per distinct `(item id, height, ascent, resolution)`, and one texture per distinct `(item id, stored pixels)`
- Writes them all into a single `<namespace>:renders` font
- Rewrites the files, replacing each `render` node with `{"text": "<glyph>", "font": "<namespace>:renders"}`

## The `render` key

```jsonc
{"render": "steel_ingot"}                    // bare id -> your project namespace
{"render": "minecraft:stone"}                // a vanilla item
{"render": "mechanization:tin_ore"}          // an item from another pack
{"render": "ICON"}                           // your pack.png
{"render": "steel_ingot", "height": 32}      // displayed height in pixels, default 16
{"render": "steel_ingot", "resolution": 64}  // shrink the stored texture to 64px, display unchanged
{"render": "steel_ingot", "ascent": 7}       // baseline offset, default centers the glyph on the text
```

### `height` is what you see, `resolution` is what is stored

There is no width to set. A Minecraft bitmap provider only takes a `height`, and the on-screen width
follows the texture's aspect ratio, so a glyph is always scaled and never stretched.

`resolution` is how many real pixels the texture keeps. **By default the source image is stored
untouched**, so a 256px item render still ships at 256px even when shown 10 pixels tall. That is what keeps
a glyph sharp at high GUI scales, where a 10px glyph covers 40 real pixels.

Set `resolution` when you would rather trade some of that sharpness for a smaller resource pack:

```jsonc
{"render": "steel_ingot", "height": 10, "resolution": 64}
```

That shrinks the stored texture to 64px tall while still displaying it at 10. Set
`text_renders.default_resolution` to apply it to every render of the pack at once.

Textures are named after the pixels they store, so several glyph heights of the same item share one file.
An animated vanilla texture (a vertical strip of frames) is cropped to its first frame instead of being
squeezed into a ribbon.

`render`, `height`, `ascent` and `resolution` are consumed by the plugin. **Every other key of the node is kept**, so a render
carries its own `color`, `hover_event` or `click_event` like any other component:

```json
[
    {"text": "Smelted from ", "color": "gray"},
    {"render": "raw_steel", "height": 10, "hover_event": {"action": "show_text", "value": "Raw Steel"}},
    {"text": " raw steel", "color": "gray"}
]
```

A node carrying `render` must not also carry `text`: the glyph occupies that slot, and the plugin warns then drops it.

### Where the images come from

| Item id | Source | What you have to do |
|---------|--------|---------------------|
| `steel_ingot`, `mypack:steel_ingot` | Isometric render of the item model, via `model_resolver` | Nothing |
| `minecraft:stone` | Downloaded from the Minecraft wiki | Nothing |
| `mechanization:tin_ore` | `<iso_renders_path>/mechanization/tin_ore.png` | Drop the PNG there yourself |
| `ICON` | Your `assets/pack.png` | Nothing |

An id that resolves to nothing gets a warning and is left untouched in the output, so a typo never silently
disappears from a message.

### Using it without the rest of StewBeet

The plugin needs no item definitions. A project item is looked up in `Mem.definitions` when StewBeet is
driving the build, and otherwise falls back to the conventional `item/<id>` model of your resource pack, so
a plain beet project renders its own items just the same:

```yaml
require:
  - "stewbeet"
pipeline:
  - "stewbeet.plugins.auto.text_renders"
```

With `assets/<namespace>/models/item/widget.json` in your resource pack, `{"render": "widget"}` works out of
the box. Vanilla ids, other packs' ids and `ICON` never needed definitions in the first place.

## Configuration

### Basic Example Configuration
```yaml
pipeline:
  - ...
  - stewbeet.plugins.auto.lang_file
  - stewbeet.plugins.auto.text_renders
  - stewbeet.plugins.auto.headers
  - ...

meta:
  stewbeet:
    # Shared with ingame_manual: an item is only ever rendered once
    iso_renders_path: "iso_renders"
    text_renders:
      default_height: 16
      default_resolution: 0   # 0 = store each source image untouched
      font: "renders"
```

### Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `iso_renders_path` | string | `"manual_cache/items"` | Folder holding the per-item PNGs, as `<folder>/<namespace>/<item>.png`. Shared with `ingame_manual`. |
| `text_renders.default_height` | int | `16` | On-screen glyph height used when a render node omits its own `height`. |
| `text_renders.default_resolution` | int | `0` | Texture height used when a render node omits its own `resolution`. `0` stores each source image untouched. |
| `text_renders.font` | string | `"renders"` | Name of the generated font, inside the project namespace. |
| `text_renders.cache_assets` | bool | inherits `manual.cache_assets` | Reuse the item PNGs that already exist instead of regenerating them. |

## Features

### Works on everything already generated
The pass runs late, on the text of the generated files rather than on the definitions. By then every item
component has been serialised into loot tables, `give` commands and dialogs, so one scan covers:
- 🏷️ Item lores and `item_name`, through the generated loot tables
- 💬 `tellraw`, `title` and any other command carrying a text component
- 🎨 The `source_lore` shared by every item of the pack
- 📖 The `ingame_manual` dialogs, whose item titles are glyphs rather than 16x16 atlas sprites

Running after `auto.lang_file` also keeps the two passes independent: the lang plugin never sees a glyph, and
this one never sees a translate key.

### One glyph per distinct render
- 🔁 The same item at the same height reuses a single provider, however many times it appears
- 🗂️ Glyphs that only differ by `ascent` or `height` share one texture instead of writing it twice
- 📐 The stored texture keeps the source aspect ratio, and Minecraft derives the on-screen width from it
- 🧮 The default ascent centers the glyph on the line of text (`height / 2 + 3`, which is vanilla's `7` for an 8px glyph), whatever its size

### Shared with the manual
- 📦 `ingame_manual` and this plugin read the same `iso_renders_path`, so an item is rendered once per build
- ⚡ With the manual in the pipeline, the renders already exist and nothing is regenerated
- 🏷️ Dialog titles ask for their glyph directly, so they keep the full render resolution instead of the
  16x16 an atlas sprite forces. They fall back to a sprite when no image can be resolved, and an animated
  texture keeps its sprite so it does not freeze on the first frame.

## Next steps

- [In-game manual](../7_ingame_manual/en.md): the other consumer of the item renders.
- [initialize](initialize.md): the `source_lore` that every item carries.
- [All plugins](README.md): the rest of the pipeline, in the order it runs.
- [Configuring the build](../3_beet_config/en.md): enabling, ordering and configuring plugins.
