
# Generating the in-game manual

The `ingame_manual` plugin builds an in-game manual from your `Mem.definitions` items: an introduction page, a category browser, one page per category, and one page per item with its recipes and wiki buttons (the per-item buttons set with `Item(wiki_buttons=...)`). An item page also shows the effects the item gives when consumed, a link to the container it leaves (`remainder`) and a link to the growing seeds that drop it. You can edit any item's page, insert pages unrelated to items, control button placement, and render pages backed by your own texture. Every public class of the API (`Page` subclasses, `ButtonLayout`, `BakedText`, `PageRef`, `CraftRenderer`, `Manual` itself) is a Python dataclass.

The pipeline entry of the manual is `stewbeet.plugins.ingame_manual`, placed after `custom_recipes` and before the datapack plugins.

- Example file: [extensive/src/definitions/manual_customization.py](https://github.com/Stoupy51/StewBeet/blob/main/templates/extensive/src/definitions/manual_customization.py)
- Source code: [stewbeet/plugins/ingame_manual/](https://github.com/Stoupy51/StewBeet/blob/main/python_package/stewbeet/plugins/ingame_manual/)

What the plugin does:

- Generates a recipe page for every item (crafting, smelting, smithing, stonecutting, mining, and custom recipe types).
- Inserts, replaces and reorders pages through a Python API.
- Runs your functions at fixed steps of the manual creation (`Phase` hooks).
- Replaces the book background or the home button texture on any one page (`book_texture`, `home_texture`).
- Cross-links related pages: another item's recipe button, or a link button to its page (`extra_buttons`).
- Keeps navigation correct after any insert or reorder, through deferred `PageRef` links.

Customize it by calling `get_manual()` in your `setup_definitions`, after the items are defined, to register pages and hooks. The output is one Minecraft dialog per page, reachable through the vanilla quick actions menu, and through the `manual` item when `use_dialog` is `1`.

## Features showcase

<video src="/ingame_manual.mp4" poster="/ingame_manual_poster.jpg" controls loop muted playsinline preload="auto" style="width: min(480px, 100%)">
</video>

## Configuration

Set in `beet.yml` under `meta.stewbeet.manual`:

| Key                 | Type            | Default              | Description                                                              |
| ------------------- | --------------- | -------------------- | ------------------------------------------------------------------------ |
| `use_dialog`        | `int`           | `1`                  | `1` = dialog + `manual` item that opens it, `2` = dialog only (no item). Any other value becomes `1` |
| `high_resolution`   | `bool`          | `true`               | High-res (256px) item icons in recipes                                   |
| `cache_assets`      | `bool`          | `true`               | Skip re-rendering and re-downloading item textures that already exist     |
| `max_items_per_row` | `int`           | `5`                  | Category grid width (max 6)                                              |
| `max_rows_per_page` | `int`           | `5`                  | Category grid height (max 7)                                             |
| `name`              | `str`           | `"{project} Manual"` | Manual title, under 32 characters                                        |
| `first_page_text`   | `TextComponent` | `""`                 | Intro page text                                                          |
| `manual_overrides`  | `str`           | `""`                 | Folder of textures that override the bundled defaults                    |
| `showcase_image`    | `int`           | `3`                  | `0` off, `1` manual items, `2` all items, `3` both                       |
| `item_layout`       | `str`           | `"craft"`            | What an item page shows: `"craft"`, `"item"` or `"item+craft"`, see below  |
| `item_box_gap`      | `int`           | `4`                  | Pixels between the item's box and the recipe of `"item+craft"`           |
| `debug_mode`        | `bool`          | `false`              | Draws a grid overlay to debug the layout                                 |
| `json_dump_path`    | `str`           | `""`                 | Optional debug dump of the rendered pages                                |

The item renders live in the top-level `iso_renders_path`, and the generated fonts and textures in `.beet_cache`.

### Item page layout

`item_layout` picks what every item page shows. `"craft"` is the main recipe, or the item in its box when it has none. `"item"` is the box only, even for an item with a recipe. `"item+craft"` puts the box `item_box_gap` pixels left of the recipe.

The dialog centers every line on its own, so each line of the recipe ends with a negative space as wide as the box plus the gap: the box and the recipe are centered together. A negative gap pulls the recipe back over the blank left margin of its grid, then over the box. `ItemPage.layout` and `ItemPage.box_gap` override both settings on one page:

```python
def change_steel_ingot(page: ItemPage, manual: Manual) -> None:
	if page.anchor == "item:steel_ingot":
		page.layout = "item+craft"
		page.box_gap = -8
manual.on_item_page(change_steel_ingot)
```

To lay a page out over a custom `book_texture`, `ItemPage.content_offset = (x, y)` moves the box and the recipe together, `x` to the pixel and `y` in whole lines of text (9 pixels). `ItemPage.box_offset` moves the box alone down, or up when negative, to the pixel. The box keeps its tooltip over every line it covers.

`ItemPage.show_result = False` draws a crafting grid without its result slot, for a page whose box already shows the result. The grid stays centered on its own and only works in high resolution.

---

## Extension API

Grab the live manual after your items are defined:

```python
from stewbeet import get_manual, Phase, CustomPage, TexturePage, BakedText, ButtonLayout

manual = get_manual()
```

### Hooks and phases

Register functions to run during manual creation. This is the main extension mechanism, because default pages only exist during the build.

```python
@manual.on(Phase.PREPARED)
def tweak(m):
    page = m.get_page_for_item("steel_ingot")
    if page is not None:
        page.transformers.append(lambda content, _m: [*content, {"text": "\nGreat metal!", "color": "dark_gray"}])
```

| Phase         | Fires after             | Typical use                         |
| ------------- | ----------------------- | ----------------------------------- |
| `DISCOVERED`  | default pages created   | insert and reorder pages            |
| `PREPARED`    | per-page data collected | edit item pages, set button layouts |
| `ORDERED`     | final order computed    | last-minute reordering              |
| `RENDERED`    | pages rendered          | append transformers                 |
| `RESOLVED`    | links resolved          | inspect final links                 |
| `BEFORE_EMIT` | right before output     | final tweaks                        |

`manual.on_item_page(fn)` runs `fn(page, manual)` on every item page during preparation.

### Custom and texture pages

`insert_page` accepts `before=` or `after=` (an anchor), or `index=`. The default anchors are `"intro"`, `"category_browser"`, `"category:<Title>"` and `"item:<id>"`. A category title is the category name in title case, followed by ` #2`, ` #3` and so on when its items fill several pages (`"category:Materials #2"`).

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
    left_padding=10,  # nudge the texture to the right (see below)
), after="welcome")
```

`TexturePage` placement attributes:

| Attribute                       | Description                                                                 |
| ------------------------------- | --------------------------------------------------------------------------- |
| `glyph_ascent` / `glyph_height` | Bitmap placement of the page texture: size and Y offset (defaults 1 and 131) |
| `left_padding` / `right_padding` | Invisible pixels emitted before and after the texture glyph, the X offset  |

The dialog centers the line, so `left_padding` shifts the texture right and `right_padding` shifts it left, each by half the padding. Keep texture width plus paddings within the dialog body (140px), otherwise the line wraps.

A page image taller or wider than 256 pixels, the background of a `TexturePage` as well as a `book_texture` or a `home_texture`, is cut into a grid of glyphs by itself, with the same cutting as a `render` node of [Item images in text](../plugins/auto.text_renders.md). The displayed height stays the same, the width follows the image ratio, and the grid advances like the single glyph would. Each tile is one texture. The templates replaced through `manual_overrides` (`book.png`, `shaped_3x3.png`...) are not cut and must stay within 256 pixels.

To lay a page out with fonts by hand (negative offsets, several images side by side, text aligned on a drawing), [DynamicBookBreakdown](https://github.com/Stoupy51/DynamicBookBreakdown) is a course that rebuilds a full book from a font and a dialog: providers, `ascent` and `height`, the advance of a glyph, spacing. It explains why the manual's glyphs are placed the way they are.

### Per-page book background and home button

Every page (any `Page` subclass) accepts `book_texture` to replace the book background (`book.png`) and `home_texture` to replace the home button (`home.png`) on that page only, for example a closed book on the first page. Both take a ready PIL image, or a path resolved as a project path first, then against the templates folder, so a filename from your `manual_overrides` folder works. `template_path(filename)` returns the effective path of a bundled or overridden template asset. A book texture is drawn as wide as `book.png`, so an image taller than wide draws a taller book.

```python
from stewbeet import CustomPage, Mem, Phase, get_manual

manual = get_manual()

# From the extensive template: a welcome page with its own book background and home arrow
textures_folder: str = Mem.ctx.meta["stewbeet"]["textures_folder"]
manual.insert_page(
    CustomPage(
        anchor="welcome", title="Welcome",
        body=[{"text": "Welcome to the Extensive Template!", "color": "black", "bold": True}],
        book_texture=f"{textures_folder}/manual/a_custom_book_page.png",
        home_texture=f"{textures_folder}/manual/home_for_welcome_page.png",
    ),
    after="intro",
)

# Existing pages work too, e.g. a closed book from your manual_overrides folder on the intro page
@manual.on(Phase.DISCOVERED)
def closed_book_intro(m):
    m.get_page("intro").book_texture = "closed_book.png"  # resolved from manual_overrides
```

Keep a `home_texture` close to the default's 16x16 proportions, since the glyph advance follows the image content: a wider arrow shifts the prev and next buttons on that page. The first page never shows the home button, as it is the home page (an invisible spacer keeps the prev and next layout unchanged). Any other page can hide it with `home_button=False`.

### Button placement

Control where wiki buttons render, per page or as the manual-wide default (`manual.config.button_layout`, 6 columns and 42 buttons until you replace it):

```python
manual.on_item_page(lambda page, _m: setattr(
    page, "button_layout", ButtonLayout(columns=6, max_buttons=42, position="after_recipe")
))
```

| Field           | Description                                                              |
| --------------- | ------------------------------------------------------------------------ |
| `columns`       | Buttons per row (default 5)                                              |
| `max_buttons`   | Hard cap, overflow dropped by priority (default 20)                      |
| `position`      | `"after_recipe"` (default), `"top"`, `"bottom"`, or a callable           |
| `order`         | Sort key, e.g. `lambda b: -b.priority`                                   |
| `include`       | Predicate `(button) -> bool` to filter                                   |
| `extra_buttons` | Extra `WikiButtonRender`s to append                                      |
| `side_grid`     | `SideGrid(count, columns, gap, lines)`: the first `count` buttons in a second grid on the left, `gap` pixels away and `lines` lines lower |
| `offset`        | `(x, y)` moving the grid, `x` to the pixel and `y` in whole lines (9 pixels) |

### Page management

| Method                                              | Description          |
| --------------------------------------------------- | -------------------- |
| `manual.add_page(page)`                             | Append a page        |
| `manual.insert_page(page, *, before/after/index)`   | Insert at a position |
| `manual.replace_page(anchor, page)`                 | Replace a page       |
| `manual.move_page(anchor, *, before/after/index)`   | Move a page          |
| `manual.remove_page(anchor)`                        | Remove a page        |
| `manual.get_page(anchor)` / `get_page_for_item(id)` | Look up a page       |

Page operations called from setup are deferred and replayed once the default pages exist, so you can reference default anchors like `"intro"` directly.

---

## More examples

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
def custom_infuser_page(m):
    m.replace_page("item:starlight_infuser", CustomPage(
        anchor="item:starlight_infuser", item_id="starlight_infuser", title="Starlight Infuser",
        body=[{"text": "A hand-written page for the Starlight Infuser.", "color": "black"}],
    ))
```

### Add a footer to every page

```python
@manual.on(Phase.RENDERED)
def add_footer(m):
    for page in m.pages:
        page.transformers.append(lambda content, _m: [*content, {"text": "\n- Stardust Fragment", "color": "dark_gray"}])
```

### Reorder pages (move a category right after the browser)

```python
@manual.on(Phase.DISCOVERED)
def reorder(m):
    m.move_page("category:Energy", after="category_browser")
```

### Filter and sort the wiki buttons of one item

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

### Choose the main recipe of an item page

By default the main recipe is how the item is mined, when it drops from an ore. Set `ItemPage.main_craft` to show another craft instead. The others stay available as buttons.

```python
@manual.on(Phase.PREPARED)
def craft_first(m):
    page = m.get_page_for_item("stardust_fragment")
    if page is not None:
        page.main_craft = next(c for c in page.crafts if c["type"].startswith("crafting"))
```

### Show a recipe that uses no custom item

A recipe whose ingredients and result are all vanilla has no page of its own: show it on the page of one of your items. A craft is the dict of a recipe object, with a `result` since it is not the item of the page. Append it to `page.crafts` for a wiki button with the recipe on hover, or set it as `page.main_craft` to draw it on the page.

```python
furnace = CraftingShapedRecipe(
    shape=["###", "# #", "###"], ingredients={"#": Ingr("minecraft:cobblestone")}, result=Ingr("minecraft:furnace"),
).to_dict()
def show_furnace(page: ItemPage, manual: Manual) -> None:
    if page.anchor == "item:steel_block":
        page.crafts.append(furnace)
manual.on_item_page(show_furnace)
```

### Cross-link two related item pages

`ItemPage.extra_buttons` holds developer-added wiki buttons, appended after the automatic ones. Build them with:

- `manual.recipes.button_for_item(item_id, index=0)`: another item's recipe button. Hovering shows that recipe and clicking opens the item's page. `index` selects which of its crafts, and the call returns `None` with a warning if there is no such craft.
- `manual.recipes.link_button(item_id, hover=None)`: a page link, the item's icon in a wiki slot that opens its page on click. `hover` defaults to the item's name plus a click hint.

```python
# Example from Stardust Fragment: the Starlight Infuser summons the Stardust Pillar boss,
# so each page points to the other.
@manual.on(Phase.PREPARED)
def link_pillar_and_infuser(m):
    pillar = m.get_page_for_item("stardust_pillar")
    infuser = m.get_page_for_item("starlight_infuser")
    if pillar is not None and infuser is not None:
        # Show the Starlight Infuser's recipe on the Stardust Pillar page (click -> its page)
        button = m.recipes.button_for_item("starlight_infuser")
        if button is not None:
            pillar.extra_buttons.append(button)
        # And link back: a button on the Starlight Infuser page opening the Stardust Pillar page
        infuser.extra_buttons.append(m.recipes.link_button("stardust_pillar"))
```

### Insert a texture page from a PNG file

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
def maybe_boss_notes(m):
    if m.get_page_for_item("stardust_pillar") is not None:
        m.insert_page(CustomPage(anchor="boss_notes", title="Boss notes",
            body=[{"text": "The Stardust Pillar is enabled in this build.", "color": "red"}]), index=1)
```

---

## Custom recipe types

A `CraftRenderer` draws each recipe type. Renderers sit in a global registry, so a new type is one class and one `register_craft_renderer(...)` call. The built-in types live one per file under `recipes/types/` (`shaped`, `furnace`, `smithing`, `linear`, `awakened_forge`). Like every class of the manual API, renderers are dataclasses: decorate your subclass with `@dataclass` to match the built-ins.

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

Only `types` and `render_body` are required. `static_glyph` (high-res template glyph), `append_hover` and `build_image` (low-res PNG) all have defaults. `r` is the `RecipeRenderer`, exposing `r.config`, `r.glyphs`, `r.images`, `r.item_component(...)` and `r.append_or_invisible(...)`. Call `register_craft_renderer(...)` once, in your setup. A craft whose type has no registered renderer gets an empty page body.

## Next steps

- [Definitions](../1_definitions_setup/en.md): the items each manual page is generated from.
- [Recipes](../plugins/custom_recipes.md): where the drawn crafting grids come from.
- [beet.yml reference](../3_beet_config/en.md#manual): every `manual` option beside the others.
- [DynamicBookBreakdown](https://github.com/Stoupy51/DynamicBookBreakdown): how fonts, dialogs and advancements make a book, for layouts beyond the manual's own pages.

