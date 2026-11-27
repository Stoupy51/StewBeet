
# Générer le manual en jeu

Le plugin `ingame_manual` construit un manual en jeu à partir des items de votre `Mem.definitions` : une page d'introduction, un navigateur de catégories, une page par catégorie, et une page par item avec ses recipes et ses wiki buttons (les boutons par item définis avec `Item(wiki_buttons=...)`). Une page d'item affiche aussi les effets que l'item donne quand il est consommé, un lien vers le récipient qu'il laisse (`remainder`) et un lien vers les graines qui poussent et le font tomber. Vous pouvez modifier la page de n'importe quel item, insérer des pages sans rapport avec les items, contrôler le placement des boutons, et rendre des pages appuyées sur votre propre texture. Chaque classe publique de l'API (les sous-classes de `Page`, `ButtonLayout`, `BakedText`, `PageRef`, `CraftRenderer`, `Manual` lui-même) est une dataclass Python.

L'entrée du manual dans le pipeline est `stewbeet.plugins.ingame_manual`, placée après `custom_recipes` et avant les plugins du datapack.

- Fichier d'exemple : [extensive/src/definitions/manual_customization.py](https://github.com/Stoupy51/StewBeet/blob/main/templates/extensive/src/definitions/manual_customization.py)
- Code source : [stewbeet/plugins/ingame_manual/](https://github.com/Stoupy51/StewBeet/blob/main/python_package/stewbeet/plugins/ingame_manual/)

Ce que fait le plugin :

- Génère une page de recipe pour chaque item (crafting, smelting, smithing, stonecutting, mining, et types de recipes custom).
- Insère, remplace et réordonne des pages par une API Python.
- Lance vos functions à des étapes fixes de la création du manual (hooks `Phase`).
- Remplace le fond du livre ou la texture du bouton home sur une seule page (`book_texture`, `home_texture`).
- Relie les pages entre elles : le bouton de recipe d'un autre item, ou un bouton de lien vers sa page (`extra_buttons`).
- Garde la navigation correcte après tout insert ou réordonnancement, grâce aux liens `PageRef` différés.

Personnalisez-le en appelant `get_manual()` dans votre `setup_definitions`, après la définition des items, pour enregistrer des pages et des hooks. La sortie est un dialog Minecraft par page, accessible par le menu vanilla des quick actions, et par l'item `manual` quand `use_dialog` vaut `1`.

## Features showcase

<video src="/ingame_manual.mp4" poster="/ingame_manual_poster.jpg" controls loop muted playsinline preload="auto" style="width: min(480px, 100%)">
</video>

## Configuration

À définir dans `beet.yml` sous `meta.stewbeet.manual` :

| Clé                 | Type            | Défaut               | Description                                                              |
| ------------------- | --------------- | -------------------- | ------------------------------------------------------------------------ |
| `use_dialog`        | `int`           | `1`                  | `1` = dialog + item `manual` qui l'ouvre, `2` = dialog seul (pas d'item). Toute autre valeur devient `1` |
| `high_resolution`   | `bool`          | `true`               | Icônes d'items en haute résolution (256px) dans les recipes              |
| `cache_assets`      | `bool`          | `true`               | Évite de refaire le rendu et de retélécharger les textures d'items qui existent déjà |
| `max_items_per_row` | `int`           | `5`                  | Largeur de la grille de catégorie (max 6)                                |
| `max_rows_per_page` | `int`           | `5`                  | Hauteur de la grille de catégorie (max 7)                                |
| `name`              | `str`           | `"{project} Manual"` | Titre du manual, moins de 32 caractères                                  |
| `first_page_text`   | `TextComponent` | `""`                 | Texte de la page d'intro                                                 |
| `manual_overrides`  | `str`           | `""`                 | Dossier de textures qui remplacent les défauts fournis                   |
| `showcase_image`    | `int`           | `3`                  | `0` désactivé, `1` items du manual, `2` tous les items, `3` les deux     |
| `item_layout`       | `str`           | `"craft"`            | Ce que montre une page d'item : `"craft"`, `"item"` ou `"item+craft"`, voir plus bas |
| `item_box_gap`      | `int`           | `4`                  | Pixels entre la boîte de l'item et la recipe de `"item+craft"`            |
| `debug_mode`        | `bool`          | `false`              | Dessine une grille en surimpression pour déboguer la mise en page        |
| `json_dump_path`    | `str`           | `""`                 | Dump de débogage optionnel des pages rendues                             |

Les rendus d'items vivent dans le `iso_renders_path` de premier niveau, et les fonts et textures générées dans `.beet_cache`.

### Mise en page d'une page d'item

`item_layout` choisit ce que montre chaque page d'item. `"craft"` est la recipe principale, ou l'item dans sa boîte quand il n'en a pas. `"item"` est la boîte seule, même pour un item qui a une recipe. `"item+craft"` place la boîte à `item_box_gap` pixels à gauche de la recipe.

Le dialog centre chaque ligne séparément, donc chaque ligne de la recipe finit par un espace négatif aussi large que la boîte plus l'écart : la boîte et la recipe sont centrées ensemble. Un écart négatif ramène la recipe sur la marge vide à gauche de sa grille, puis sur la boîte. `ItemPage.layout` et `ItemPage.box_gap` remplacent ces deux réglages sur une page :

```python
def change_steel_ingot(page: ItemPage, manual: Manual) -> None:
	if page.anchor == "item:steel_ingot":
		page.layout = "item+craft"
		page.box_gap = -8
manual.on_item_page(change_steel_ingot)
```

Pour composer une page sur un `book_texture` personnalisé, `ItemPage.content_offset = (x, y)` déplace la boîte et la recipe ensemble, `x` au pixel près et `y` en lignes de texte entières (9 pixels). `ItemPage.box_offset` déplace la boîte seule vers le bas, ou vers le haut en négatif, au pixel près. La boîte garde son infobulle sur chaque ligne qu'elle couvre.

`ItemPage.show_result = False` dessine une grille de craft sans sa case de résultat, pour une page dont la boîte montre déjà le résultat. La grille reste centrée seule et ne fonctionne qu'en haute résolution.

---

## API d'extension

Récupérez le manual en cours une fois vos items définis :

```python
from stewbeet import get_manual, Phase, CustomPage, TexturePage, BakedText, ButtonLayout

manual = get_manual()
```

### Hooks et phases

Enregistrez des functions à lancer pendant la création du manual. C'est le principal mécanisme d'extension, car les pages par défaut n'existent que pendant le build.

```python
@manual.on(Phase.PREPARED)
def tweak(m):
    page = m.get_page_for_item("steel_ingot")
    if page is not None:
        page.transformers.append(lambda content, _m: [*content, {"text": "\nGreat metal!", "color": "dark_gray"}])
```

| Phase         | Se déclenche après      | Usage typique                       |
| ------------- | ----------------------- | ----------------------------------- |
| `DISCOVERED`  | création des pages par défaut | insérer et réordonner des pages |
| `PREPARED`    | collecte des données par page | modifier les pages d'items, définir les button layouts |
| `ORDERED`     | calcul de l'ordre final | réordonnancement de dernière minute |
| `RENDERED`    | rendu des pages         | ajouter des transformers            |
| `RESOLVED`    | résolution des liens    | inspecter les liens finaux          |
| `BEFORE_EMIT` | juste avant la sortie   | derniers ajustements                |

`manual.on_item_page(fn)` lance `fn(page, manual)` sur chaque page d'item pendant la préparation.

### Pages custom et pages de texture

`insert_page` accepte `before=` ou `after=` (une ancre), ou `index=`. Les ancres par défaut sont `"intro"`, `"category_browser"`, `"category:<Title>"` et `"item:<id>"`. Un titre de catégorie est le nom de la catégorie en title case, suivi de ` #2`, ` #3` et ainsi de suite quand ses items remplissent plusieurs pages (`"category:Materials #2"`).

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

Attributs de placement de `TexturePage` :

| Attribut                        | Description                                                                 |
| ------------------------------- | --------------------------------------------------------------------------- |
| `glyph_ascent` / `glyph_height` | Placement bitmap de la texture de la page : taille et décalage en Y (défauts 1 et 131) |
| `left_padding` / `right_padding` | Pixels invisibles émis avant et après le glyphe de la texture, le décalage en X |

Le dialog centre la ligne, donc `left_padding` décale la texture vers la droite et `right_padding` vers la gauche, chacun de la moitié du padding. Gardez la largeur de la texture plus les paddings dans le corps du dialog (140px), sinon la ligne passe à la ligne suivante.

Une image de page de plus de 256 pixels de haut ou de large, le fond d'une `TexturePage` comme un `book_texture` ou un `home_texture`, est découpée toute seule en une grille de glyphes, avec le même découpage qu'un `render` de [Images d'items dans le texte](../plugins/auto.text_renders.fr.md). La hauteur affichée reste la même, la largeur suit le ratio de l'image, et la grille avance comme le glyphe unique le ferait. Chaque tuile est une texture. Les templates remplacés par `manual_overrides` (`book.png`, `shaped_3x3.png`...) ne sont pas découpés et doivent rester dans 256 pixels.

Pour composer une page à la main avec des fonts (décalages négatifs, plusieurs images côte à côte, texte aligné sur un dessin), [DynamicBookBreakdown](https://github.com/Stoupy51/DynamicBookBreakdown) est un cours qui reconstruit un livre complet à partir d'une font et d'un dialog : providers, `ascent` et `height`, avance d'un glyphe, espacement. Il explique pourquoi les glyphes du manual sont placés comme ils le sont.

### Fond de livre et bouton home par page

Chaque page (toute sous-classe de `Page`) accepte `book_texture` pour remplacer le fond du livre (`book.png`) et `home_texture` pour remplacer le bouton home (`home.png`) sur cette page seulement, par exemple un livre fermé sur la première page. Les deux prennent une image PIL prête, ou un chemin résolu d'abord comme chemin du projet, puis par rapport au dossier des templates, donc un nom de fichier de votre dossier `manual_overrides` fonctionne. `template_path(filename)` renvoie le chemin effectif d'un asset de template fourni ou remplacé. Un fond de livre est dessiné aussi large que `book.png`, donc une image plus haute que large dessine un livre plus haut.

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

Gardez une `home_texture` proche des proportions 16x16 de celle par défaut, puisque l'avance du glyphe suit le contenu de l'image : une flèche plus large décale les boutons précédent et suivant sur cette page. La première page n'affiche jamais le bouton home, puisque c'est la page d'accueil (un espaceur invisible garde la disposition des boutons précédent et suivant inchangée). Toute autre page peut le masquer avec `home_button=False`.

### Placement des boutons

Contrôlez où les wiki buttons sont rendus, par page ou comme défaut pour tout le manual (`manual.config.button_layout`, 6 colonnes et 42 boutons tant que vous ne le remplacez pas) :

```python
manual.on_item_page(lambda page, _m: setattr(
    page, "button_layout", ButtonLayout(columns=6, max_buttons=42, position="after_recipe")
))
```

| Champ           | Description                                                              |
| --------------- | ------------------------------------------------------------------------ |
| `columns`       | Boutons par ligne (défaut 5)                                             |
| `max_buttons`   | Plafond strict, le surplus est écarté par priorité (défaut 20)           |
| `position`      | `"after_recipe"` (défaut), `"top"`, `"bottom"`, ou un callable           |
| `order`         | Clé de tri, ex : `lambda b: -b.priority`                                 |
| `include`       | Prédicat `(button) -> bool` pour filtrer                                 |
| `extra_buttons` | `WikiButtonRender` supplémentaires à ajouter                             |
| `side_grid`     | `SideGrid(count, columns, gap, lines)` : les `count` premiers boutons dans une seconde grille à gauche, à `gap` pixels et `lines` lignes plus bas |
| `offset`        | `(x, y)` qui déplace la grille, `x` au pixel près et `y` en lignes entières (9 pixels) |

### Gestion des pages

| Méthode                                             | Description          |
| --------------------------------------------------- | -------------------- |
| `manual.add_page(page)`                             | Ajoute une page à la fin |
| `manual.insert_page(page, *, before/after/index)`   | Insère à une position |
| `manual.replace_page(anchor, page)`                 | Remplace une page    |
| `manual.move_page(anchor, *, before/after/index)`   | Déplace une page     |
| `manual.remove_page(anchor)`                        | Retire une page      |
| `manual.get_page(anchor)` / `get_page_for_item(id)` | Retrouve une page    |

Les opérations de page appelées depuis le setup sont différées et rejouées une fois les pages par défaut créées, donc vous pouvez référencer directement des ancres par défaut comme `"intro"`.

---

## Autres exemples

### Insérer une page de lore entre deux catégories

```python
manual.insert_page(CustomPage(
    anchor="lore", title="Lore",
    body=[{"text": "Long ago, the world ran on steel...", "color": "black"}],
), after="category:Materials")
```

### Remplacer entièrement la page d'un item

```python
@manual.on(Phase.DISCOVERED)
def custom_infuser_page(m):
    m.replace_page("item:starlight_infuser", CustomPage(
        anchor="item:starlight_infuser", item_id="starlight_infuser", title="Starlight Infuser",
        body=[{"text": "A hand-written page for the Starlight Infuser.", "color": "black"}],
    ))
```

### Ajouter un pied de page à chaque page

```python
@manual.on(Phase.RENDERED)
def add_footer(m):
    for page in m.pages:
        page.transformers.append(lambda content, _m: [*content, {"text": "\n- Stardust Fragment", "color": "dark_gray"}])
```

### Réordonner les pages (mettre une catégorie juste après le navigateur)

```python
@manual.on(Phase.DISCOVERED)
def reorder(m):
    m.move_page("category:Energy", after="category_browser")
```

### Filtrer et trier les wiki buttons d'un item

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

### Composer le category browser

`on_item_page` ne voit que les pages d'item. Le category browser s'atteint par son ancre, une fois les pages par défaut créées. `CategoryBrowserPage.columns` fixe le nombre de cases par ligne (`max_items_per_row` par défaut) et `content_offset = (x, y)` déplace la grille, `x` au pixel près et `y` en lignes de texte entières. `book_texture` et `home_texture` fonctionnent comme sur toute page.

```python
@manual.on(Phase.PREPARED)
def browser_layout(m):
    browser = m.get_page("category_browser")
    browser.columns = 3
    browser.content_offset = (10, 9)
```

### Choisir la recipe principale d'une page d'item

Par défaut, la recipe principale est la façon dont l'item est miné, quand il tombe d'un ore. Définissez `ItemPage.main_craft` pour en afficher une autre à la place. Les autres restent disponibles en boutons.

```python
@manual.on(Phase.PREPARED)
def craft_first(m):
    page = m.get_page_for_item("stardust_fragment")
    if page is not None:
        page.main_craft = next(c for c in page.crafts if c["type"].startswith("crafting"))
```

### Afficher une recipe sans item custom

Une recipe dont les ingrédients et le résultat sont tous vanilla n'a pas de page propre : affichez-la sur la page d'un de vos items. Un craft est le dict d'un objet recipe, avec un `result` puisque ce n'est pas l'item de la page. Ajoutez-le à `page.crafts` pour un bouton wiki montrant la recipe au survol, ou définissez-le comme `page.main_craft` pour le dessiner sur la page.

```python
furnace = CraftingShapedRecipe(
    shape=["###", "# #", "###"], ingredients={"#": Ingr("minecraft:cobblestone")}, result=Ingr("minecraft:furnace"),
).to_dict()
def show_furnace(page: ItemPage, manual: Manual) -> None:
    if page.anchor == "item:steel_block":
        page.crafts.append(furnace)
manual.on_item_page(show_furnace)
```

### Relier deux pages d'items liés

`ItemPage.extra_buttons` contient les wiki buttons ajoutés par le développeur, ajoutés après les automatiques. Construisez-les avec :

- `manual.recipes.button_for_item(item_id, index=0)` : le bouton de recipe d'un autre item. Au survol il affiche cette recipe et un clic ouvre la page de l'item. `index` choisit lequel de ses crafts, et l'appel renvoie `None` avec un avertissement s'il n'y a pas un tel craft.
- `manual.recipes.link_button(item_id, hover=None)` : un lien de page, l'icône de l'item dans un slot de wiki qui ouvre sa page au clic. `hover` vaut par défaut le nom de l'item plus une indication de clic.

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

### Insérer une page de texture depuis un fichier PNG

```python
manual.insert_page(TexturePage(
    anchor="tutorial", title="Tutorial",
    background="assets/manual/tutorial_bg.png",   # your own texture
    baked_texts=[BakedText(text="Step 1: mine ore", xy=(20, 40))],
), before="category:Materials")
```

### Ajouter une page seulement quand une condition est remplie

```python
@manual.on(Phase.DISCOVERED)
def maybe_boss_notes(m):
    if m.get_page_for_item("stardust_pillar") is not None:
        m.insert_page(CustomPage(anchor="boss_notes", title="Boss notes",
            body=[{"text": "The Stardust Pillar is enabled in this build.", "color": "red"}]), index=1)
```

---

## Types de recipes custom

Un `CraftRenderer` dessine chaque type de recipe. Les renderers vivent dans un registre global, donc un nouveau type tient en une classe et un appel à `register_craft_renderer(...)`. Les types intégrés vivent un par fichier sous `recipes/types/` (`shaped`, `furnace`, `smithing`, `linear`, `awakened_forge`). Comme toute classe de l'API du manual, les renderers sont des dataclasses : décorez votre sous-classe avec `@dataclass` pour être cohérent avec les types intégrés.

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

Seuls `types` et `render_body` sont requis. `static_glyph` (glyphe de template en haute résolution), `append_hover` et `build_image` (PNG en basse résolution) ont tous des défauts. `r` est le `RecipeRenderer`, qui expose `r.config`, `r.glyphs`, `r.images`, `r.item_component(...)` et `r.append_or_invisible(...)`. Appelez `register_craft_renderer(...)` une seule fois, dans votre setup. Un craft dont le type n'a pas de renderer enregistré reçoit un corps de page vide.

## Pour continuer

- [Definitions](../1_definitions_setup/fr.md) : les items dont chaque page de manual est générée.
- [Recipes](../plugins/custom_recipes.fr.md) : d'où viennent les grilles de crafting dessinées.
- [Référence de beet.yml](../3_beet_config/fr.md#manual) : chaque option `manual` à côté des autres.
- [DynamicBookBreakdown](https://github.com/Stoupy51/DynamicBookBreakdown) : comment les fonts, les dialogs et les advancements font un livre, pour des mises en page au-delà des pages du manual.

