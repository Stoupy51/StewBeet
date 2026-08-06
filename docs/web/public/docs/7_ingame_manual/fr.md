# Générer le manuel en jeu

`ingame_manual` génère un manuel en jeu à partir de vos items `Mem.definitions` : une page d'introduction, un navigateur de catégories, une page par catégorie, et une page par item avec ses recettes et boutons wiki. Il est **orienté dialogue** (l'ancien mode livre écrit NBT est supprimé) et entièrement **extensible**: vous pouvez modifier la page de n'importe quel item, insérer des pages arbitraires (même sans rapport avec un item), contrôler le placement des boutons, et rendre des pages basées sur votre propre texture. Chaque classe publique de l'API (sous-classes de `Page`, `ButtonLayout`, `BakedText`, `PageRef`, `CraftRenderer`, `Manual` lui-même...) est une **dataclass** Python.

**Activez-le en remplaçant `stewbeet.plugins.ingame_manual` par `stewbeet.plugins.ingame_manual`** dans votre pipeline.

**Fichier d'exemple** : [extensive/src/definitions/manual_customization.py](https://github.com/Stoupy51/StewBeet/blob/main/templates/extensive/src/definitions/manual_customization.py) <br>  
**Code source** : [stewbeet/plugins/ingame_manual/](https://github.com/Stoupy51/StewBeet/blob/main/python_package/stewbeet/plugins/ingame_manual/) <br>  
**Requis** : Framework StewBeet (`from stewbeet import *`)  
**Position** : L'étape `stewbeet.plugins.ingame_manual` de votre pipeline `beet.yml`, après `custom_recipes` et avant les plugins de datapack  
**Personnalisation** : Appelez `get_manual()` dans votre `setup_definitions` (après la définition des items) pour enregistrer pages et hooks  
**Sortie** : Orienté dialogue: génère un dialogue Minecraft par page, accessible via le menu **quick actions** natif (et l'item `manual` en mode 1)

- Générer automatiquement les pages de recettes de chaque item (craft, cuisson, forge, découpe, minage, et types de recettes personnalisés)
- Insérer/remplacer/réordonner des pages arbitraires via une API Python claire
- Enregistrer des fonctions exécutées pendant la création du manuel (hooks `Phase`)
- Fournir des pages basées sur une texture personnalisée, avec le texte intégré dans l'image elle-même
- Remplacer la texture de fond du livre ou du bouton home sur une page spécifique (`book_texture`, `home_texture`)
- Lier des pages entre elles : afficher le bouton de recette d'un autre item, ou un bouton de lien vers sa page (`extra_buttons`)
- Décider où apparaissent les boutons wiki et comment gérer le dépassement (`ButtonLayout`)
- Les liens différés `PageRef` gardent la navigation correcte après toute insertion/réorganisation

## Présentation des fonctionnalités

<img src="../plugins/img/ingame_manual.gif" style="width: min(480px, 100%)">

## Configuration

À définir dans `beet.yml` sous `meta.stewbeet.manual` :

| Clé                 | Type            | Défaut              | Description                                                                  |
| ------------------- | --------------- | ------------------- | ---------------------------------------------------------------------------- |
| `cache_path`        | `str`           | - | **Requis.** Dossier des polices/textures/rendus d'items générés              |
| `use_dialog`        | `int`           | `1`                 | `1` = dialogue + item `manual` qui l'ouvre · `2` = dialogue seul (sans item) |
| `high_resolution`   | `bool`          | `true`              | Icônes d'items haute résolution (256px) dans les recettes                    |
| `cache_assets`      | `bool`          | `true`              | Évite de re-rendre/re-télécharger les textures d'items déjà présentes        |
| `max_items_per_row` | `int`           | `5`                 | Largeur de la grille de catégorie (max 6)                                    |
| `max_rows_per_page` | `int`           | `5`                 | Hauteur de la grille de catégorie (max 7)                                    |
| `name`              | `str`           | `"{projet} Manual"` | Titre du manuel (max 32 caractères)                                          |
| `first_page_text`   | `TextComponent` | `""`                | Texte de la page d'introduction                                              |
| `manual_overrides`  | `str`           | `""`                | Dossier de textures remplaçant les défauts fournis                           |
| `showcase_image`    | `int`           | `3`                 | `0` off · `1` items du manuel · `2` tous les items · `3` les deux            |
| `json_dump_path`    | `str`           | `""`                | Export de debug optionnel des pages rendues                                  |

> **Note** : `use_dialog: 0` et `cache_pages` de la v1 sont supprimés. Le manuel est toujours basé sur les dialogues.

---

## API d'extension

Récupérez le manuel actif après la définition de vos items :

```python
from stewbeet import get_manual, Phase, CustomPage, TexturePage, BakedText, ButtonLayout

manual = get_manual()
```

### Hooks & Phases
Enregistrez des fonctions exécutées pendant la création du manuel. C'est le mécanisme d'extension principal, car les pages par défaut n'existent que *pendant* la génération.

```python
@manual.on(Phase.PREPARED)
def tweak(m):
    page = m.get_page_for_item("steel_ingot")
    if page is not None:
        page.transformers.append(lambda content, _m: [*content, {"text": "\nQuel métal !", "color": "dark_gray"}])
```

| Phase         | Se déclenche après          | Usage typique                                            |
| ------------- | --------------------------- | -------------------------------------------------------- |
| `DISCOVERED`  | pages par défaut créées     | insérer/réordonner des pages                             |
| `PREPARED`    | données par page collectées | éditer les pages d'items, définir les layouts de boutons |
| `ORDERED`     | ordre final calculé         | réorganisation de dernière minute                        |
| `RENDERED`    | pages rendues               | ajouter des transformers                                 |
| `RESOLVED`    | liens résolus               | inspecter les liens finaux                               |
| `BEFORE_EMIT` | juste avant la sortie       | ajustements finaux                                       |

`manual.on_item_page(fn)` exécute `fn(page, manual)` sur chaque page d'item pendant la préparation.

### Pages personnalisées & texture
`insert_page` accepte `before=`/`after=` (un anchor) ou `index=`. Les anchors par défaut incluent `"intro"`, `"category_browser"`, `"category:<Titre>"` et `"item:<id>"`.

```python
# Une page libre (n'importe quels components de texte)
manual.insert_page(CustomPage(
    anchor="welcome", title="Bienvenue",
    body=[{"text": "Bonjour depuis une page personnalisée !", "color": "black"}],
), after="intro")

# Une page dont le corps est une texture, avec le texte intégré dans l'image elle-même
from PIL import Image
manual.insert_page(TexturePage(
    anchor="credits", title="Crédits",
    background=Image.new("RGBA", (256, 128), (30, 30, 46, 255)),  # ou un chemin PNG
    baked_texts=[BakedText(text="Fait avec StewBeet", xy=(128, 40), align="center", color=(255, 255, 255, 255))],
    body=[{"text": "\n[le texte ci-dessus fait partie de l'image]", "color": "black"}],
    glyph_height=64,
    left_padding=10,  # décale la texture vers la droite (voir ci-dessous)
), after="welcome")
```

Attributs de placement de `TexturePage` :

| Attribut                        | Description                                                                          |
| ------------------------------- | ------------------------------------------------------------------------------------ |
| `glyph_ascent` / `glyph_height` | Placement bitmap de la texture de page : taille et **décalage Y**                    |
| `left_padding` / `right_padding`| Pixels invisibles émis avant/après le glyphe de la texture (**décalage X**)          |

Le dialogue centre la ligne : `left_padding` décale donc la texture vers la **droite** et `right_padding` vers la **gauche**, chacun de la moitié du padding. Gardez largeur de texture + paddings dans le corps du dialogue (140px), sinon la ligne passe à la ligne.

### Fond de livre & bouton home par page
Chaque page (toute sous-classe de `Page`) accepte `book_texture` pour remplacer le fond de livre (`book.png`) et `home_texture` pour remplacer le bouton home (`home.png`) sur cette page uniquement: ex. un livre fermé sur la première page. Les deux prennent une image PIL prête, ou un chemin résolu d'abord comme chemin du projet, puis dans le dossier des templates (un nom de fichier de votre dossier `manual_overrides` fonctionne donc). `template_path(filename)` retourne le chemin effectif d'un asset de template fourni/surchargé.

```python
from stewbeet import CustomPage, Mem, Phase, get_manual

manual = get_manual()

# Tiré du template extensive : une page d'accueil avec son propre fond de livre et sa propre flèche home
textures_folder: str = Mem.ctx.meta["stewbeet"]["textures_folder"]
manual.insert_page(
    CustomPage(
        anchor="welcome", title="Bienvenue",
        body=[{"text": "Bienvenue dans le Template Extensive !", "color": "black", "bold": True}],
        book_texture=f"{textures_folder}/manual/a_custom_book_page.png",
        home_texture=f"{textures_folder}/manual/home_for_welcome_page.png",
    ),
    after="intro",
)

# Les pages existantes fonctionnent aussi, ex. un livre fermé depuis votre dossier manual_overrides sur la page d'intro
@manual.on(Phase.DISCOVERED)
def closed_book_intro(m):
    m.get_page("intro").book_texture = "closed_book.png"  # résolu depuis manual_overrides
```

> **Notes** : gardez une `home_texture` proche des proportions 16x16 par défaut, car l'avance du glyphe dépend du contenu de l'image (une flèche plus large décale les boutons précédent/suivant sur cette page). La **première page n'affiche jamais le bouton home**: elle *est* la page d'accueil (un espaceur invisible conserve la mise en page des boutons précédent/suivant), et toute autre page peut aussi le masquer avec `home_button=False`.

### Placement des boutons
Contrôlez où les boutons wiki sont rendus, par page ou comme défaut global du manuel (`ManualConfig.button_layout`) :

```python
manual.on_item_page(lambda page, _m: setattr(
    page, "button_layout", ButtonLayout(columns=6, max_buttons=42, position="after_recipe")
))
```

| Champ           | Description                                              |
| --------------- | -------------------------------------------------------- |
| `columns`       | Boutons par ligne                                        |
| `max_buttons`   | Plafond strict (dépassement supprimé par priorité)       |
| `position`      | `"after_recipe"` · `"top"` · `"bottom"` · ou un callable |
| `order`         | Clé de tri, ex. `lambda b: -b.priority`                  |
| `include`       | Prédicat `(button) -> bool` pour filtrer                 |
| `extra_buttons` | `WikiButtonRender` supplémentaires à ajouter             |

### Gestion des pages
| Méthode                                             | Description              |
| --------------------------------------------------- | ------------------------ |
| `manual.add_page(page)`                             | Ajoute une page à la fin |
| `manual.insert_page(page, *, before/after/index)`   | Insère à une position    |
| `manual.replace_page(anchor, page)`                 | Remplace une page        |
| `manual.move_page(anchor, *, before/after/index)`   | Déplace une page         |
| `manual.remove_page(anchor)`                        | Supprime une page        |
| `manual.get_page(anchor)` / `get_page_for_item(id)` | Récupère une page        |

> Les opérations de page appelées depuis le setup sont différées et rejouées une fois les pages par défaut créées, vous pouvez donc référencer directement des anchors par défaut comme `"intro"`.

---

## Plus d'exemples

### Insérer une page de lore entre deux catégories
```python
manual.insert_page(CustomPage(
    anchor="lore", title="Lore",
    body=[{"text": "Il y a longtemps, le monde fonctionnait à l'acier...", "color": "black"}],
), after="category:Materials")
```

### Remplacer entièrement la page d'un item
```python
@manual.on(Phase.DISCOVERED)
def custom_wrench_page(m):
    m.replace_page("item:wrench", CustomPage(
        anchor="item:wrench", item_id="wrench", title="Clé",
        body=[{"text": "Une page écrite à la main pour la clé.", "color": "black"}],
    ))
```

### Ajouter un pied de page à chaque page
```python
@manual.on(Phase.RENDERED)
def add_footer(m):
    for page in m.pages:
        page.transformers.append(lambda content, _m: [*content, {"text": "\n- MonPack", "color": "dark_gray"}])
```

### Réordonner les pages (déplacer une catégorie juste après le navigateur)
```python
@manual.on(Phase.DISCOVERED)
def reorder(m):
    m.move_page("category:Energy", after="category_browser")
```

### Filtrer & trier les boutons wiki d'un item
```python
@manual.on(Phase.PREPARED)
def tidy_buttons(m):
    page = m.get_page_for_item("simplunium_ingot")
    if page is not None:
        page.button_layout = ButtonLayout(
            columns=5,
            include=lambda b: not b.blue_craft,   # garder uniquement les recettes qui produisent un résultat
            order=lambda b: -b.priority,          # priorité la plus haute en premier
        )
```

### Lier deux pages d'items entre elles (boutons de recette inter-pages)
`ItemPage.extra_buttons` contient les boutons wiki ajoutés par le développeur, placés après les boutons automatiques. Construisez-les avec :
- `manual.recipes.button_for_item(item_id, index=0)`: le **bouton de recette** d'un autre item : le survol montre sa recette, le clic ouvre sa page (`index` choisit lequel de ses crafts ; retourne `None` avec un avertissement si le craft n'existe pas) ;
- `manual.recipes.link_button(item_id, hover=None)`: un simple **lien de page** : l'icône de l'item dans une case wiki, le clic ouvre sa page (`hover` vaut par défaut le nom de l'item plus une indication de clic).

```python
# Exemple tiré de Stardust Fragment : le Starlight Infuser invoque le boss Stardust Pillar,
# donc chaque page pointe vers l'autre.
@manual.on(Phase.PREPARED)
def link_pillar_and_infuser(m):
    pillar = m.get_page_for_item("stardust_pillar")
    infuser = m.get_page_for_item("starlight_infuser")
    if pillar is not None and infuser is not None:
        # Afficher la recette du Starlight Infuser sur la page du Stardust Pillar (clic -> sa page)
        button = m.recipes.button_for_item("starlight_infuser")
        if button is not None:
            pillar.extra_buttons.append(button)
        # Et le lien retour : un bouton sur la page du Starlight Infuser ouvrant la page du Stardust Pillar
        infuser.extra_buttons.append(m.recipes.link_button("stardust_pillar"))
```

### Insérer une page texture depuis un fichier PNG (au lieu d'une image générée)
```python
manual.insert_page(TexturePage(
    anchor="tutorial", title="Tutoriel",
    background="assets/manual/tutorial_bg.png",   # votre propre texture
    baked_texts=[BakedText(text="Étape 1 : miner le minerai", xy=(20, 40))],
), before="category:Materials")
```

### Ajouter une page seulement si une condition est remplie
```python
@manual.on(Phase.DISCOVERED)
def maybe_changelog(m):
    if m.get_page_for_item("prototype") is not None:
        m.insert_page(CustomPage(anchor="changelog", title="Changelog",
            body=[{"text": "Le prototype est activé dans ce build.", "color": "red"}]), index=1)
```

---

## Types de recettes personnalisés
Chaque type de recette est rendu par un `CraftRenderer` enregistré dans un registre global : ajouter un type = une classe + un appel à `register_craft_renderer(...)`. Les types intégrés vivent un par fichier sous `recipes/types/` (`shaped`, `furnace`, `smithing`, `linear`, `awakened_forge`). Comme toutes les classes de l'API du manuel, les renderers sont des dataclasses: décorez votre sous-classe avec `@dataclass` pour suivre le style des types intégrés.

```python
from dataclasses import dataclass
from typing import ClassVar

from stewbeet import CraftRenderer, register_craft_renderer

@dataclass
class MyMachineRenderer(CraftRenderer):
    types: ClassVar[tuple[str, ...]] = ("myplugin_machining",)  # le(s) "type" de craft géré(s)
    name: ClassVar[str] = "Mon Usinage"                         # titre du survol ("" = pas de titre, comme le craft vanilla)

    def render_body(self, r, craft, name, content, result_component, page_font, use_dialog, add_change_page_to_ingr):
        # Ajoutez votre mise en page à `content`. Construisez les cases avec r.item_component(...)
        # et r.append_or_invisible(content, component, ligne). `result_component` est déjà prêt.
        ...

    def append_hover(self, r, craft, hover):   # lignes de survol du bouton wiki (défaut : un seul "- x1 <ingrédient>")
        ...

register_craft_renderer(MyMachineRenderer())
```

Seuls `types` et `render_body` sont obligatoires ; `static_glyph` (glyphe de template haute résolution), `append_hover` et `build_image` (PNG basse résolution) ont tous des valeurs par défaut. `r` est le `RecipeRenderer`, exposant `r.config`, `r.glyphs`, `r.images`, `r.item_component(...)` et `r.append_or_invisible(...)`. Appelez `register_craft_renderer(...)` une fois (ex. dans votre setup) ; un craft dont le type n'a pas de renderer enregistré est ignoré.

---

## Migration depuis la v1
- Changez l'entrée du pipeline en `stewbeet.plugins.ingame_manual`.
- `WikiButton` et `set_manual_components(...)` continuent de fonctionner sans changement.
- Retirez la clé `cache_pages` et utilisez `use_dialog: 1` ou `2` (le mode `0` n'existe plus).
- Le storage `universal_manual` n'est plus enregistré ; le manuel s'ouvre depuis le menu quick actions natif.

## Glossaire

| Terme | Signification |
|-------|---------------|
| **Manual** | L'objet orchestrateur qui possède la liste ordonnée des pages, le registre de glyphes/polices, le constructeur d'images, le rendu des recettes et les hooks développeur. Récupéré avec `get_manual()`. |
| **Page** | Une unité autonome rendue en components de texte Minecraft. Sous-classes : `IntroPage`, `CategoryBrowserPage`, `CategoryPage`, `ItemPage`, ainsi que `CustomPage`, `TexturePage` et `RawPage` destinées aux développeurs. |
| **PageRef** | Un lien *différé* vers une page (par `item`, `anchor` ou `page` littéral). Les liens sont résolus en numéros de page concrets **après** l'ordonnancement, donc insérer/réordonner des pages ne casse jamais les liens inter-pages. |
| **Phase hook** | Une fonction que vous enregistrez pour s'exécuter pendant la création du manuel (`manual.on(Phase.X)`), à une étape précise du pipeline de génération. |
| **ButtonLayout** | Contrôle *où* et *quels* boutons wiki apparaissent sur une page (colonnes, maximum, tri, filtrage, position). |
| **BakedText** | Un texte dessiné directement sur l'image de fond d'une `TexturePage` avec PIL. |
| **WikiButton** | Texte d'information par item affiché comme un bouton dans le manuel (inchangé depuis v1, défini via `Item(wiki_buttons=...)`). |

## Prochaines étapes

- [Définir objets et blocs](../1_definitions_setup/fr.md): les objets dont chaque page est générée.
- [Recettes](../plugins/custom_recipes.md): d'où viennent les grilles de craft dessinées.
- [Tous les plugins](../plugins/README.md): le reste du pipeline.
