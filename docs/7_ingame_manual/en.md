
# 📖 StewBeet In-game Manual Guide

## 📖 Definitions
- **Manual**: The orchestrator object that owns the ordered list of pages, the glyph/font registry, the image builder, the recipe renderer and the developer hooks. Retrieved with `get_manual()`.
- **Page**: A self-contained unit rendered to Minecraft text components. Subclasses: `IntroPage`, `CategoryBrowserPage`, `CategoryPage`, `ItemPage`, plus the developer-facing `CustomPage`, `TexturePage` and `RawPage`.
- **PageRef**: A *deferred* link to a page (by `item`, `anchor` or literal `page`). Links are resolved to concrete page numbers **after** ordering, so inserting/reordering pages never breaks cross-page links.
- **Phase hook**: A function you register to run during manual creation (`manual.on(Phase.X)`), at a precise step of the build pipeline.
- **ButtonLayout**: Controls *where* and *which* wiki buttons appear on a page (columns, max, ordering, filtering, position).
- **BakedText**: A piece of text drawn directly onto a `TexturePage` background image with PIL.
- **WikiButton**: Per-item info text shown as a button in the manual (unchanged from v1, set via `Item(wiki_buttons=...)`).

## 🧪 Examples
📄 **Example File**: [extensive/src/definitions/manual_customization.py](../../templates/extensive/src/definitions/manual_customization.py) 🔗<br>
📄 **Source Code**: [stewbeet/plugins/ingame_manual/](../../python_package/stewbeet/plugins/ingame_manual/) 🔗<br>

## 🔗 Dependencies
- **✅ Required**: StewBeet framework (`from stewbeet import *`)
- **📍 Position**: The `stewbeet.plugins.ingame_manual` step in your `beet.yml` pipeline, after `custom_recipes` and before the datapack plugins
- **🧩 Customization**: Call `get_manual()` in your `setup_definitions` (after items are defined) to register pages and hooks
- **🗨 Output**: Dialog-first — generates one Minecraft dialog per page, reachable through the vanilla **quick actions** menu (and the `manual` item in mode 1)

## 📋 Overview
`ingame_manual` generates an in-game manual from your `Mem.definitions` items: an introduction page, a category browser, one page per category, and one page per item with its recipes and wiki buttons. It is **dialog-first** (the old written-book NBT mode is removed) and fully **extensible** — you can edit any item's page, insert arbitrary pages (even unrelated to items), control button placement, and render pages backed by your own texture. Every public class of the API (`Page` subclasses, `ButtonLayout`, `BakedText`, `PageRef`, `CraftRenderer`, `Manual` itself...) is a Python **dataclass**.

**Opt in by replacing `stewbeet.plugins.ingame_manual` with `stewbeet.plugins.ingame_manual`** in your pipeline.

## 🎯 Purpose
- 📚 Auto-generate recipe pages for every item (crafting, smelting, smithing, stonecutting, mining, and custom recipe types)
- 🧩 Insert/replace/reorder arbitrary pages via a clean Python API
- 🔌 Register functions that run during manual creation (`Phase` hooks)
- 🎨 Ship pages backed by a custom texture, with text baked into the image itself
- 🔘 Decide where wiki buttons appear and how overflow is handled (`ButtonLayout`)
- 🔗 Deferred `PageRef` links keep navigation correct after any insert/reorder

---

## ⚙️ Configuration

Set in `beet.yml` under `meta.stewbeet.manual`:

| Key                 | Type            | Default              | Description                                                              |
| ------------------- | --------------- | -------------------- | ------------------------------------------------------------------------ |
| `cache_path`        | `str`           | —                    | **Required.** Directory for generated fonts/textures/item renders        |
| `use_dialog`        | `int`           | `1`                  | `1` = dialog + `manual` item that opens it · `2` = dialog only (no item) |
| `high_resolution`   | `bool`          | `true`               | High-res (256px) item icons in recipes                                   |
| `cache_assets`      | `bool`          | `true`               | Skip re-rendering/re-downloading item textures that already exist        |
| `max_items_per_row` | `int`           | `5`                  | Category grid width (max 6)                                              |
| `max_rows_per_page` | `int`           | `5`                  | Category grid height (max 7)                                             |
| `name`              | `str`           | `"{project} Manual"` | Manual title (max 32 chars)                                              |
| `first_page_text`   | `TextComponent` | `""`                 | Intro page text                                                          |
| `manual_overrides`  | `str`           | `""`                 | Folder of textures that override the bundled defaults                    |
| `showcase_image`    | `int`           | `3`                  | `0` off · `1` manual items · `2` all items · `3` both                    |
| `json_dump_path`    | `str`           | `""`                 | Optional debug dump of the rendered pages                                |

> **Note**: `use_dialog: 0` and `cache_pages` from v1 are removed. The manual is always dialog-based.

---

## 🧩 Extension API

Grab the live manual after your items are defined:

```python
from stewbeet import get_manual, Phase, CustomPage, TexturePage, BakedText, ButtonLayout

manual = get_manual()
```

### 🔌 Hooks & Phases
Register functions to run during manual creation. This is the main extension mechanism, because default pages only exist *during* the build.

```python
@manual.on(Phase.PREPARED)
def tweak(m):
    page = m.get_page_for_item("steel_ingot")
    if page is not None:
        page.transformers.append(lambda content, _m: [*content, {"text": "\nGreat metal!", "color": "dark_gray"}])
```

| Phase         | Fires after             | Typical use                         |
| ------------- | ----------------------- | ----------------------------------- |
| `DISCOVERED`  | default pages created   | insert/reorder pages                |
| `PREPARED`    | per-page data collected | edit item pages, set button layouts |
| `ORDERED`     | final order computed    | last-minute reordering              |
| `RENDERED`    | pages rendered          | append transformers                 |
| `RESOLVED`    | links resolved          | inspect final links                 |
| `BEFORE_EMIT` | just before output      | final tweaks                        |

`manual.on_item_page(fn)` runs `fn(page, manual)` on every item page during preparation.

### 📄 Custom & texture pages
`insert_page` accepts `before=`/`after=` (an anchor) or `index=`. Default anchors include `"intro"`, `"category_browser"`, `"category:<Title>"` and `"item:<id>"`.

```python
# A free-form page (any text components)
manual.insert_page(CustomPage(
    anchor="welcome", title="Welcome",
    body=[{"text": "Hello from a custom page!", "color": "black"}],
), after="intro")

# A page whose body is a texture, with text baked into the image itself
from PIL import Image
manual.insert_page(TexturePage(
    anchor="credits", title="Credits",
    background=Image.new("RGBA", (256, 128), (30, 30, 46, 255)),  # or a PNG path
    baked_texts=[BakedText(text="Made with StewBeet", xy=(128, 40), align="center", color=(255, 255, 255, 255))],
    body=[{"text": "\n[the text above is part of the image]", "color": "black"}],
    glyph_height=64,
), after="welcome")
```

### 🔘 Button placement
Control where wiki buttons render, per page or as the manual-wide default (`ManualConfig.button_layout`):

```python
manual.on_item_page(lambda page, _m: setattr(
    page, "button_layout", ButtonLayout(columns=6, max_buttons=42, position="after_recipe")
))
```

| Field           | Description                                             |
| --------------- | ------------------------------------------------------- |
| `columns`       | Buttons per row                                         |
| `max_buttons`   | Hard cap (overflow dropped by priority)                 |
| `position`      | `"after_recipe"` · `"top"` · `"bottom"` · or a callable |
| `order`         | Sort key, e.g. `lambda b: -b.priority`                  |
| `include`       | Predicate `(button) -> bool` to filter                  |
| `extra_buttons` | Extra `WikiButtonRender`s to append                     |

### 🗂 Page management
| Method                                              | Description          |
| --------------------------------------------------- | -------------------- |
| `manual.add_page(page)`                             | Append a page        |
| `manual.insert_page(page, *, before/after/index)`   | Insert at a position |
| `manual.replace_page(anchor, page)`                 | Replace a page       |
| `manual.move_page(anchor, *, before/after/index)`   | Move a page          |
| `manual.remove_page(anchor)`                        | Remove a page        |
| `manual.get_page(anchor)` / `get_page_for_item(id)` | Look up a page       |

> Page operations called from setup are deferred and replayed once the default pages exist, so you can reference default anchors like `"intro"` directly.

---

## 🍳 More examples

### Insert a lore page between two categories
```python
manual.insert_page(CustomPage(
    anchor="lore", title="Lore",
    body=[{"text": "Long ago, the world ran on steel...", "color": "black"}],
), after="category:Materials")
```

### Replace an item's page entirely
```python
@manual.on(Phase.DISCOVERED)
def custom_wrench_page(m):
    m.replace_page("item:wrench", CustomPage(
        anchor="item:wrench", item_id="wrench", title="Wrench",
        body=[{"text": "A hand-written page for the wrench.", "color": "black"}],
    ))
```

### Add a footer to every page
```python
@manual.on(Phase.RENDERED)
def add_footer(m):
    for page in m.pages:
        page.transformers.append(lambda content, _m: [*content, {"text": "\n— MyPack", "color": "dark_gray"}])
```

### Reorder pages (move a category right after the browser)
```python
@manual.on(Phase.DISCOVERED)
def reorder(m):
    m.move_page("category:Energy", after="category_browser")
```

### Filter & sort the wiki buttons of one item
```python
@manual.on(Phase.PREPARED)
def tidy_buttons(m):
    page = m.get_page_for_item("simplunium_ingot")
    if page is not None:
        page.button_layout = ButtonLayout(
            columns=5,
            include=lambda b: not b.blue_craft,   # keep only recipes that produce a result
            order=lambda b: -b.priority,          # highest priority first
        )
```

### Insert a texture page from a PNG file (instead of a generated image)
```python
manual.insert_page(TexturePage(
    anchor="tutorial", title="Tutorial",
    background="assets/manual/tutorial_bg.png",   # your own texture
    baked_texts=[BakedText(text="Step 1: mine ore", xy=(20, 40))],
), before="category:Materials")
```

### Add a page only when a condition is met
```python
@manual.on(Phase.DISCOVERED)
def maybe_changelog(m):
    if m.get_page_for_item("prototype") is not None:
        m.insert_page(CustomPage(anchor="changelog", title="Changelog",
            body=[{"text": "Prototype is enabled in this build.", "color": "red"}]), index=1)
```

---

## 🧱 Custom recipe types
Each recipe type is rendered by a `CraftRenderer` kept in a global registry, so adding a new type is one class + one `register_craft_renderer(...)` call. The built-in types live one-per-file under `recipes/types/` (`shaped`, `furnace`, `smithing`, `linear`, `awakened_forge`). Like every class of the manual API, renderers are dataclasses — decorate your subclass with `@dataclass` to match the built-ins.

```python
from dataclasses import dataclass
from typing import ClassVar

from stewbeet import CraftRenderer, register_craft_renderer

@dataclass
class MyMachineRenderer(CraftRenderer):
    types: ClassVar[tuple[str, ...]] = ("myplugin_machining",)  # the craft "type" string(s) this handles
    name: ClassVar[str] = "My Machining"                        # hover title ("" = no title, like vanilla crafting)

    def render_body(self, r, craft, name, content, result_component, page_font, use_dialog, add_change_page_to_ingr):
        # Append your page layout to `content`. Build item cells with r.item_component(...)
        # and r.append_or_invisible(content, component, row). `result_component` is prebuilt.
        ...

    def append_hover(self, r, craft, hover):   # wiki-button hover lines (default: a single "- x1 <ingredient>")
        ...

register_craft_renderer(MyMachineRenderer())
```

Only `types` and `render_body` are required; `static_glyph` (high-res template glyph), `append_hover` and `build_image` (low-res PNG) all have defaults. `r` is the `RecipeRenderer`, exposing `r.config`, `r.glyphs`, `r.images`, `r.item_component(...)` and `r.append_or_invisible(...)`. Call `register_craft_renderer(...)` once (e.g. in your setup); a craft whose type has no registered renderer is skipped.

---

## 🔄 Migration from v1
- Switch the pipeline entry to `stewbeet.plugins.ingame_manual`.
- `WikiButton` and `set_manual_components(...)` keep working unchanged.
- Remove the `cache_pages` key and use `use_dialog: 1` or `2` (mode `0` is gone).
- The `universal_manual` storage is no longer registered; the manual is opened from the vanilla quick actions menu.

