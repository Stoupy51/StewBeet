
# 📖 Guide du Manuel en jeu StewBeet

## 📖 Définitions
- **Manual** : L'objet orchestrateur qui possède la liste ordonnée des pages, le registre de glyphes/polices, le constructeur d'images, le rendu des recettes et les hooks développeur. Récupéré avec `get_manual()`.
- **Page** : Une unité autonome rendue en composants de texte Minecraft. Sous-classes : `IntroPage`, `CategoryBrowserPage`, `CategoryPage`, `ItemPage`, ainsi que `CustomPage`, `TexturePage` et `RawPage` destinées aux développeurs.
- **PageRef** : Un lien *différé* vers une page (par `item`, `anchor` ou `page` littéral). Les liens sont résolus en numéros de page concrets **après** l'ordonnancement, donc insérer/réordonner des pages ne casse jamais les liens inter-pages.
- **Phase hook** : Une fonction que vous enregistrez pour s'exécuter pendant la création du manuel (`manual.on(Phase.X)`), à une étape précise du pipeline de génération.
- **ButtonLayout** : Contrôle *où* et *quels* boutons wiki apparaissent sur une page (colonnes, maximum, tri, filtrage, position).
- **BakedText** : Un texte dessiné directement sur l'image de fond d'une `TexturePage` avec PIL.
- **WikiButton** : Texte d'information par item affiché comme un bouton dans le manuel (inchangé depuis v1, défini via `Item(wiki_buttons=...)`).

## 🧪 Exemples
📄 **Fichier d'exemple** : [extensive/src/definitions/manual_customization.py](../../templates/extensive/src/definitions/manual_customization.py) 🔗<br>
📄 **Code source** : [stewbeet/plugins/ingame_manual_v2/](../../python_package/stewbeet/plugins/ingame_manual_v2/) 🔗<br>

## 🔗 Dépendances
- **✅ Requis** : Framework StewBeet (`from stewbeet import *`)
- **📍 Position** : L'étape `stewbeet.plugins.ingame_manual_v2` de votre pipeline `beet.yml`, après `custom_recipes` et avant les plugins de datapack
- **🧩 Personnalisation** : Appelez `get_manual()` dans votre `setup_definitions` (après la définition des items) pour enregistrer pages et hooks
- **🗨 Sortie** : Orienté dialogue — génère un dialogue Minecraft par page, accessible via le menu **quick actions** natif (et l'item `manual` en mode 1)

## 📋 Vue d'ensemble
`ingame_manual_v2` génère un manuel en jeu à partir de vos items `Mem.definitions` : une page d'introduction, un navigateur de catégories, une page par catégorie, et une page par item avec ses recettes et boutons wiki. Il est **orienté dialogue** (l'ancien mode livre écrit NBT est supprimé) et entièrement **extensible** — vous pouvez modifier la page de n'importe quel item, insérer des pages arbitraires (même sans rapport avec un item), contrôler le placement des boutons, et rendre des pages basées sur votre propre texture. Chaque classe publique de l'API (sous-classes de `Page`, `ButtonLayout`, `BakedText`, `PageRef`, `CraftRenderer`, `Manual` lui-même...) est une **dataclass** Python.

**Activez-le en remplaçant `stewbeet.plugins.ingame_manual` par `stewbeet.plugins.ingame_manual_v2`** dans votre pipeline.

## 🎯 Objectif
- 📚 Générer automatiquement les pages de recettes de chaque item (craft, cuisson, forge, découpe, minage, et types de recettes personnalisés)
- 🧩 Insérer/remplacer/réordonner des pages arbitraires via une API Python claire
- 🔌 Enregistrer des fonctions exécutées pendant la création du manuel (hooks `Phase`)
- 🎨 Fournir des pages basées sur une texture personnalisée, avec le texte intégré dans l'image elle-même
- 🔘 Décider où apparaissent les boutons wiki et comment gérer le dépassement (`ButtonLayout`)
- 🔗 Les liens différés `PageRef` gardent la navigation correcte après toute insertion/réorganisation

---

## ⚙️ Configuration

À définir dans `beet.yml` sous `meta.stewbeet.manual` :

| Clé                 | Type            | Défaut              | Description                                                                  |
| ------------------- | --------------- | ------------------- | ---------------------------------------------------------------------------- |
| `cache_path`        | `str`           | —                   | **Requis.** Dossier des polices/textures/rendus d'items générés              |
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

## 🧩 API d'extension

Récupérez le manuel actif après la définition de vos items :

```python
from stewbeet import get_manual, Phase, CustomPage, TexturePage, BakedText, ButtonLayout

manual = get_manual()
```

### 🔌 Hooks & Phases
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

### 📄 Pages personnalisées & texture
`insert_page` accepte `before=`/`after=` (un anchor) ou `index=`. Les anchors par défaut incluent `"intro"`, `"category_browser"`, `"category:<Titre>"` et `"item:<id>"`.

```python
# Une page libre (n'importe quels composants de texte)
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
), after="welcome")
```

### 🔘 Placement des boutons
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

### 🗂 Gestion des pages
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

## 🍳 Plus d'exemples

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
        page.transformers.append(lambda content, _m: [*content, {"text": "\n— MonPack", "color": "dark_gray"}])
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

## 🧱 Types de recettes personnalisés
Chaque type de recette est rendu par un `CraftRenderer` enregistré dans un registre global : ajouter un type = une classe + un appel à `register_craft_renderer(...)`. Les types intégrés vivent un par fichier sous `recipes/types/` (`shaped`, `furnace`, `smithing`, `linear`, `awakened_forge`). Comme toutes les classes de l'API du manuel, les renderers sont des dataclasses — décorez votre sous-classe avec `@dataclass` pour suivre le style des types intégrés.

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

## 🔄 Migration depuis la v1
- Changez l'entrée du pipeline en `stewbeet.plugins.ingame_manual_v2`.
- `WikiButton` et `set_manual_components(...)` continuent de fonctionner sans changement.
- Retirez la clé `cache_pages` et utilisez `use_dialog: 1` ou `2` (le mode `0` n'existe plus).
- Le storage `universal_manual` n'est plus enregistré ; le manuel s'ouvre depuis le menu quick actions natif.

