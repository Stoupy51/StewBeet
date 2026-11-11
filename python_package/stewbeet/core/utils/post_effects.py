""" `/posteffect` chains that time themselves from the frame they are applied on.

A post effect has no parameters: the server only sends its id.
The one signal a chain gets is that `posteffect add` allocates its persistent targets at `clear_color`,
so a 1x1 persistent target whose alpha starts at 0 marks frame one.
Stamping `Globals.GameTime` there gives every chain a clock with sub-tick resolution, restarted by each `posteffect add`.
"""
# Lazy imports (PEP 810), ignored before Python 3.15
from stouputils.lazy import ALWAYS_LAZY

__lazy_modules__ = ALWAYS_LAZY

# Imports
from beet import FragmentShader, GlslShader, PostEffect
from stouputils.typing import JsonDict

from ..__memory__ import Mem
from .io import set_json_encoder

# Constants
POST_SHADER_HEADER: str = """#version 330
#extension GL_ARB_separate_shader_objects : require
"""
""" Preamble of every post shader from Minecraft 26.3, where each `in` and `out` also needs a `layout(location = N)`. """

SCREENQUAD_VERTEX_SHADER: str = "minecraft:core/screenquad"
""" Vanilla fullscreen-triangle vertex shader, emitting `texCoord` at location 0. """

POST_CLOCK_GLSL: str = """#ifndef CLOCK_GLSL
#define CLOCK_GLSL

// Activation timestamp: GameTime packed across RGB. Alpha 0 is frame one (a fresh persistent target
// reads back as its clear_color), CLOCK_RUNNING an armed clock, and 1 a clock whose ramps all ended.
#define CLOCK_RUNNING 0.5
#define CLOCK_SETTLE_TICKS 1200.0

vec3 clock_pack_time(float t) {
    vec3 enc = fract(t * vec3(1.0, 255.0, 65025.0));
    return enc - enc.yzz * vec3(1.0 / 255.0, 1.0 / 255.0, 0.0);
}

float clock_unpack_time(vec3 enc) {
    return dot(enc, vec3(1.0, 1.0 / 255.0, 1.0 / 65025.0));
}

// Ticks since the clock was armed. A settled clock is long expired, so the 24000-tick wrap of
// GameTime can only be crossed once while running. A small negative delta is the server's time sync
// stepping the client clock back, which must hold the ramp at its start rather than end it.
float clock_elapsed(vec4 clock, float gameTime) {
    if (clock.a < 0.25) return 0.0;
    if (clock.a > 0.75) return 1.0e6;
    float delta = gameTime - clock_unpack_time(clock.rgb);
    if (delta < -0.5) delta += 1.0;
    return max(delta * 24000.0, 0.0);
}

// Eased 0 to 1 ramp over `duration` ticks, holding at 1 afterwards.
float clock_ramp(vec4 clock, float gameTime, float duration) {
    float t = clamp(clock_elapsed(clock, gameTime) / max(duration, 1.0e-4), 0.0, 1.0);
    return t * t * (3.0 - 2.0 * t);
}

#endif
"""
""" Registered as `<ns>:clock.glsl`, for the apply shader of a `timed_post_effect` chain to include. """

POST_CLOCK_FSH: str = POST_SHADER_HEADER + "\n#include <minecraft:globals.glsl>\n" + POST_CLOCK_GLSL + """
uniform sampler2D ClockSampler;

layout(location = 0) in vec2 texCoord;
layout(location = 0) out vec4 fragColor;

void main() {
    vec4 clock = texture(ClockSampler, vec2(0.5));
    if (clock.a < 0.25) {
        fragColor = vec4(clock_pack_time(GameTime), CLOCK_RUNNING);
        return;
    }
    fragColor = clock_elapsed(clock, GameTime) > CLOCK_SETTLE_TICKS ? vec4(clock.rgb, 1.0) : clock;
}
"""
""" Stamps the activation time on frame one, then marks the clock settled once every ramp has ended. """

POST_COPY_FSH: str = POST_SHADER_HEADER + """
uniform sampler2D InSampler;

layout(location = 0) in vec2 texCoord;
layout(location = 0) out vec4 fragColor;

void main() {
    fragColor = texture(InSampler, texCoord);
}
"""
""" A pass may not sample the target it writes, so the clock and the frame both go through scratch targets. """


# Functions
def timed_post_effect(
	effect_id: str, fragment_shader: str, uniforms: JsonDict,
	inputs: list[JsonDict] | None = None, pre_passes: list[JsonDict] | None = None, targets: JsonDict | None = None,
) -> None:
	""" Register `<project_id>:<effect_id>`, a `/posteffect` chain whose clock restarts on every `posteffect add`.

	The apply pass gets `ClockSampler` and `InSampler` (bound to `minecraft:main`), and a last pass copies its output back to main.
	Its shader includes `<project_id>:clock.glsl` and calls `clock_elapsed(texture(ClockSampler, vec2(0.5)), GameTime)`.
	The clock include and the `post/clock` and `post/copy` shaders go to the project's namespace, so two packs never share them.

	Args:
		effect_id:       Path under `assets/<project_id>/post_effect/`.
		fragment_shader: Id of the apply pass shader, ex: "mgs:post/flash".
		uniforms:        std140 blocks baked into the apply pass, as `{block_name: [post_uniform(...)]}`.
		inputs:          Extra samplers of the apply pass, whose `SamplerInfo` entries follow `OutSize`, `ClockSize` and `InSize`.
		pre_passes:      Passes run before the clock, to prepare targets the extra `inputs` read.
		targets:         The targets those passes write, declared beside the clock's.
	"""
	ns: str = Mem.ctx.project_id
	assets = Mem.ctx.assets[ns]
	assets.glsl_shaders["include/clock"] = GlslShader(POST_CLOCK_GLSL)
	assets.fragment_shaders["post/clock"] = FragmentShader(POST_CLOCK_FSH)
	assets.fragment_shaders["post/copy"] = FragmentShader(POST_COPY_FSH)

	passes: list[JsonDict] = [
		*(pre_passes or []),
		{
			"vertex_shader": SCREENQUAD_VERTEX_SHADER,
			"fragment_shader": f"{ns}:post/clock",
			"inputs": [{"sampler_name": "Clock", "target": "clock"}],
			"output": "clock_next",
		},
		{
			"vertex_shader": SCREENQUAD_VERTEX_SHADER,
			"fragment_shader": f"{ns}:post/copy",
			"inputs": [{"sampler_name": "In", "target": "clock_next"}],
			"output": "clock",
		},
		{
			"vertex_shader": SCREENQUAD_VERTEX_SHADER,
			"fragment_shader": fragment_shader,
			"inputs": [
				{"sampler_name": "Clock", "target": "clock_next"},
				{"sampler_name": "In", "target": "minecraft:main"},
				*(inputs or []),
			],
			"output": "swap",
			"uniforms": uniforms,
		},
		{
			"vertex_shader": SCREENQUAD_VERTEX_SHADER,
			"fragment_shader": f"{ns}:post/copy",
			"inputs": [{"sampler_name": "In", "target": "swap"}],
			"output": "minecraft:main",
		},
	]
	chain: JsonDict = {
		"targets": {
			"clock":      {"width": 1, "height": 1, "persistent": True, "clear_color": 0},
			"clock_next": {"width": 1, "height": 1},
			"swap":       {},
			**(targets or {}),
		},
		"passes": passes,
	}
	assets.post_effects[effect_id] = set_json_encoder(PostEffect(chain), max_level=4)


def post_uniform(name: str, kind: str, value: float | list[float]) -> JsonDict:
	""" One entry of a baked std140 uniform block.

	Args:
		kind: "int", "ivec3", "float", "vec2", "vec3", "vec4" or "matrix4x4".

	>>> post_uniform("Duration", "float", 2.0)
	{'name': 'Duration', 'type': 'float', 'value': 2.0}
	"""
	return {"name": name, "type": kind, "value": value}

