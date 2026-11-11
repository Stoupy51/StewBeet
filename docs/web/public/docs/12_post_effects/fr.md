
# Post effects chronométrés

`timed_post_effect` enregistre une chaîne `/posteffect` dont le shader sait combien de ticks se sont écoulés depuis que l'effet a été appliqué. Il faut Minecraft 26.3, où `/posteffect add <joueurs> <id>` applique à un joueur un post effect du resource pack.

**Code source** : [stewbeet/core/utils/post_effects.py](https://github.com/Stoupy51/StewBeet/blob/main/python_package/stewbeet/core/utils/post_effects.py) <br>
**Requis** : Framework StewBeet (`from stewbeet import *`)  
**Position** : Appelé dans un hook de plugin `beet_default`

## Pourquoi une horloge

Le serveur envoie l'id d'un post effect et rien d'autre : ni argument, ni durée, ni instant de départ. Un shader qui fait un fondu, un flash ou une animation doit trouver lui-même son point de départ.

`posteffect add` alloue les cibles persistantes de la chaîne à leur `clear_color`. La chaîne que construit `timed_post_effect` garde une cible persistante 1x1 dont l'alpha part de 0, y inscrit `GameTime` à la première frame, et la donne à votre shader sous le nom `ClockSampler`. Retirer l'effet détruit la cible, donc le `posteffect add` suivant relance l'horloge.

## Exemple : fondu depuis une couleur

```python
from beet import FragmentShader
from stewbeet import POST_SHADER_HEADER, Mem, post_uniform, timed_post_effect

ns: str = Mem.ctx.project_id
Mem.ctx.assets[ns].fragment_shaders["post/fade"] = FragmentShader(POST_SHADER_HEADER + f"""
#include <minecraft:globals.glsl>
#include <{ns}:clock.glsl>

uniform sampler2D ClockSampler;
uniform sampler2D InSampler;

layout(std140) uniform FadeConfig {{
    vec3 Color;
    float Duration;
}};

layout(location = 0) in vec2 texCoord;
layout(location = 0) out vec4 fragColor;

void main() {{
    float shown = clock_ramp(texture(ClockSampler, vec2(0.5)), GameTime, Duration);
    fragColor = vec4(mix(Color, texture(InSampler, texCoord).rgb, shown), 1.0);
}}
""")

timed_post_effect("fade_in", f"{ns}:post/fade", {"FadeConfig": [
	post_uniform("Color", "vec3", [0.0, 0.0, 0.0]),
	post_uniform("Duration", "float", 20.0),
]})
```

```mcfunction
posteffect add @s <ns>:fade_in
# une fois le fondu terminé
posteffect remove @s <ns>:fade_in
```

## `timed_post_effect`

```python
timed_post_effect(effect_id, fragment_shader, uniforms, inputs=None, pre_passes=None, targets=None)
```

| Paramètre | Description |
|-----------|-------------|
| `effect_id` | Chemin sous `assets/<project_id>/post_effect/`, donc l'id que prend `/posteffect` est `<project_id>:<effect_id>` |
| `fragment_shader` | Id de votre shader, ex. `"mgs:post/flash"` pour `assets/mgs/shaders/post/flash.fsh` |
| `uniforms` | Constantes écrites dans l'effet, sous la forme `{nom_du_bloc: [post_uniform(...)]}` |
| `inputs` | Samplers en plus pour votre shader : une texture de `textures/effect/`, une cible, ou la profondeur de `minecraft:main` |
| `pre_passes` | Passes exécutées avant l'horloge, pour remplir les cibles que lisent vos `inputs` |
| `targets` | Les cibles qu'écrivent ces passes |

Votre shader est la passe "apply" de cette chaîne :

| Passe | Lit | Écrit |
|-------|-----|-------|
| `pre_passes` | les vôtres | les vôtres |
| `<ns>:post/clock` | `clock` | `clock_next` |
| `<ns>:post/copy` | `clock_next` | `clock` |
| votre shader | `ClockSampler` (`clock_next`), `InSampler` (`minecraft:main`), puis `inputs` | `swap` |
| `<ns>:post/copy` | `swap` | `minecraft:main` |

`SamplerInfo` contient `OutSize`, puis un `vec2` par sampler dans cet ordre : `ClockSize`, `InSize`, puis vos `inputs`.

## `<ns>:clock.glsl`

Lisez l'horloge en `vec2(0.5)` et passez-la avec `GameTime` :

| Fonction | Renvoie |
|----------|---------|
| `clock_elapsed(clock, GameTime)` | Les ticks depuis `posteffect add`, avec une précision inférieure au tick. `1.0e6` une fois 1200 ticks passés |
| `clock_ramp(clock, GameTime, duration)` | Une rampe adoucie de 0 à 1 sur `duration` ticks, puis 1 |

## `post_uniform`

```python
post_uniform(name, kind, value)
```

`kind` vaut `"int"`, `"ivec3"`, `"float"`, `"vec2"`, `"vec3"`, `"vec4"` ou `"matrix4x4"`. Les valeurs sont écrites dans le JSON de l'effet : le serveur ne peut pas les changer, donc une valeur qui varie demande un id d'effet par valeur, généré dans une boucle.

## Règles du moteur

- **Un effet retiré disparaît à cette frame.** Une animation de sortie est soit chronométrée dans le même effet, qui affiche ensuite l'image inchangée jusqu'à ce que le serveur le retire, soit un second effet échangé au même tick.
- **Une horloge ne suit pas un changement d'id.** Une animation qui doit se dérouler sans saut reste dans un seul effet.
- **`add` puis `remove` du même id au même tick n'envoie rien.** Pour rejouer un effet à chaque tick, alternez entre deux ids.
- **Les effets survivent à la mort, à la reconnexion et au changement de dimension.** Retirez vos propres ids à la réapparition, à la connexion et à la fin de la partie. N'utilisez jamais `posteffect clear`, qui retire aussi les effets des autres packs.
- **Un shader qui ne compile pas est ignoré jusqu'au rechargement des ressources.** Appuyez sur F3+T après avoir corrigé du GLSL.
- **Les post effects sont dessinés avant le GUI.** Chat, bossbars et titles restent nets par-dessus.
- **Une passe ne lit jamais la cible qu'elle écrit**, `minecraft:main` compris. Vos propres passes écrivent une cible de travail, comme la chaîne le fait avec `swap`.
- **Chaque `in` et `out` a besoin de `layout(location = N)`**, et le shader commence par `POST_SHADER_HEADER`.

