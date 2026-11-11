
# Timed post effects

`timed_post_effect` registers a `/posteffect` chain whose shader knows how many ticks have passed since the effect was applied. It needs Minecraft 26.3, where `/posteffect add <players> <id>` applies a resource pack post effect to a player.

**Source Code**: [stewbeet/core/utils/post_effects.py](https://github.com/Stoupy51/StewBeet/blob/main/python_package/stewbeet/core/utils/post_effects.py) <br>
**Required**: StewBeet framework (`from stewbeet import *`)  
**Position**: Called inside a `beet_default` plugin hook

## Why a clock

The server sends a post effect's id and nothing else: no argument, no duration, no start time. A shader that fades, flashes or plays an animation has to find its own starting point.

`posteffect add` allocates the chain's persistent targets at their `clear_color`. The chain `timed_post_effect` builds keeps a 1x1 persistent target whose alpha starts at 0, stamps `GameTime` into it on the first frame, and hands it to your shader as `ClockSampler`. Removing the effect destroys the target, so the next `posteffect add` starts the clock again.

## Example: fade in from a color

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
# once the fade is over
posteffect remove @s <ns>:fade_in
```

## `timed_post_effect`

```python
timed_post_effect(effect_id, fragment_shader, uniforms, inputs=None, pre_passes=None, targets=None)
```

| Parameter | Description |
|-----------|-------------|
| `effect_id` | Path under `assets/<project_id>/post_effect/`, so the id `/posteffect` takes is `<project_id>:<effect_id>` |
| `fragment_shader` | Id of your shader, ex: `"mgs:post/flash"` for `assets/mgs/shaders/post/flash.fsh` |
| `uniforms` | Constants baked into the effect, as `{block_name: [post_uniform(...)]}` |
| `inputs` | Extra samplers for your shader: a texture of `textures/effect/`, a target, or the depth of `minecraft:main` |
| `pre_passes` | Passes run before the clock, to fill the targets your `inputs` read |
| `targets` | The targets those passes write |

Your shader runs as the "apply" pass of this chain:

| Pass | Reads | Writes |
|------|-------|--------|
| `pre_passes` | yours | yours |
| `<ns>:post/clock` | `clock` | `clock_next` |
| `<ns>:post/copy` | `clock_next` | `clock` |
| your shader | `ClockSampler` (`clock_next`), `InSampler` (`minecraft:main`), then `inputs` | `swap` |
| `<ns>:post/copy` | `swap` | `minecraft:main` |

`SamplerInfo` holds `OutSize`, then one `vec2` per sampler in that order: `ClockSize`, `InSize`, then your `inputs`.

## `<ns>:clock.glsl`

Sample the clock at `vec2(0.5)` and pass it with `GameTime`:

| Function | Returns |
|----------|---------|
| `clock_elapsed(clock, GameTime)` | Ticks since `posteffect add`, with sub-tick precision. `1.0e6` once 1200 ticks have passed |
| `clock_ramp(clock, GameTime, duration)` | An eased 0 to 1 ramp over `duration` ticks, then 1 |

## `post_uniform`

```python
post_uniform(name, kind, value)
```

`kind` is `"int"`, `"ivec3"`, `"float"`, `"vec2"`, `"vec3"`, `"vec4"` or `"matrix4x4"`. The values are written in the effect's JSON: the server cannot change them, so a value that varies takes one effect id per value, generated in a loop.

## Rules of the engine

- **A removed effect disappears on that frame.** An exit animation is either timed inside the same effect, which then shows the frame unchanged until the server removes it, or a second effect swapped in on the same tick.
- **A clock does not follow a change of id.** An animation that must run without a jump stays in one effect.
- **`add` then `remove` of one id in the same tick sends nothing.** To replay an effect every tick, alternate between two ids.
- **Effects survive death, relog and dimension changes.** Remove your own ids on respawn, on join and when the game ends. Never use `posteffect clear`, which also takes off the effects of other packs.
- **A shader that fails to compile is skipped until resources reload.** Press F3+T after fixing GLSL.
- **Post effects are drawn before the GUI.** Chat, bossbars and titles stay sharp on top.
- **A pass never samples the target it writes**, `minecraft:main` included. Passes of your own write a scratch target, as the chain does with `swap`.
- **Every `in` and `out` needs `layout(location = N)`**, and the shader starts with `POST_SHADER_HEADER`.

