""" Assertions for: stewbeet.core.utils.post_effects """
# Imports
from beet import Context
from stouputils.typing import JsonDict

from stewbeet import post_uniform, timed_post_effect


# Main entry point
def beet_default(ctx: Context):
	ns: str = ctx.project_id
	blur: JsonDict = {"vertex_shader": "minecraft:core/screenquad", "fragment_shader": f"{ns}:post/blur", "output": "blurred"}
	timed_post_effect(
		"intro", f"{ns}:post/intro", {"IntroConfig": [post_uniform("Duration", "float", 40.0)]},
		inputs=[{"sampler_name": "Blurred", "target": "blurred"}],
		pre_passes=[blur],
		targets={"blurred": {"width": 480, "height": 270}},
	)
	chain: JsonDict = ctx.assets[ns].post_effects["intro"].data
	passes: list[JsonDict] = chain["passes"]

	# Sampling the target a pass writes is a GPU feedback loop, minecraft:main included
	for index, one_pass in enumerate(passes):
		read: list[str] = [sampler["target"] for sampler in one_pass.get("inputs", []) if "target" in sampler]
		assert one_pass["output"] not in read, f"pass {index} samples its own output {one_pass['output']}"

	# The caller's passes run before the clock, and the frame ends back in main
	assert passes[0] == blur, passes[0]
	assert [one_pass["output"] for one_pass in passes] == ["blurred", "clock_next", "clock", "swap", "minecraft:main"]

	# SamplerInfo is filled in input order, so the extra samplers must come after Clock and In
	apply: JsonDict = passes[3]
	assert [sampler["sampler_name"] for sampler in apply["inputs"]] == ["Clock", "In", "Blurred"], apply["inputs"]
	assert apply["uniforms"] == {"IntroConfig": [{"name": "Duration", "type": "float", "value": 40.0}]}, apply["uniforms"]

	# Only a persistent target survives to the next frame, which is what makes alpha 0 mean "frame one"
	assert chain["targets"]["clock"] == {"width": 1, "height": 1, "persistent": True, "clear_color": 0}, chain["targets"]
	assert chain["targets"]["blurred"] == {"width": 480, "height": 270}, chain["targets"]

	# The shared shaders live in the project namespace
	assert "clock_elapsed" in ctx.assets[ns].glsl_shaders["include/clock"].text
	assert {"post/clock", "post/copy"} <= set(ctx.assets[ns].fragment_shaders)

