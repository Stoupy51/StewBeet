
# Imports
from PIL import Image
from stewbeet import (
	BakedText,
	ButtonLayout,
	CustomPage,
	ItemPage,
	Manual,
	Phase,
	TexturePage,
	get_manual,
)


# Showcase of the ingame_manual v2 extension API.
# Everything here is OPTIONAL — delete this file (and its pipeline entry) if you don't need it.
def main() -> None:
	""" Customize the in-game manual using the public ingame_manual v2 API.

	Call this after all items are defined (see src/setup_definitions.py). The manual itself
	is built later by the ``stewbeet.plugins.ingame_manual`` pipeline step; the pages and
	hooks registered here are applied during that build.
	"""
	manual: Manual = get_manual()

	# 1) Insert a free-form page (unrelated to any item) right after the intro.
	#    CustomPage takes any list of Minecraft text components as its body.
	manual.insert_page(
		CustomPage(
			anchor="welcome",	# Page id used for linking and ordering
			title="Welcome",
			body=[
				{"text": "Welcome to the Extensive Template!", "color": "black", "bold": True},
				{"text": "\n\nThis page was added with the public manual API\n(CustomPage + insert_page).", "color": "#505050"},
			],
		),
		after="intro",	# After page with id "intro"
	)

	# 2) Insert a page whose body is a custom texture, with text baked into the image itself.
	#    Here the background is generated on the fly, but you can pass a PNG path instead.
	background = Image.new("RGBA", (256, 128), (30, 30, 46, 255))
	manual.insert_page(
		TexturePage(
			anchor="credits",
			title="Credits",
			background=background,
			baked_texts=[
				BakedText(text="Made with StewBeet", xy=(128, 38), font_size=20, color=(255, 255, 255, 255), align="center"),
				BakedText(text="ingame_manual v2", xy=(128, 70), font_size=14, color=(180, 180, 210, 255), align="center"),
			],
			body=[{"text": "\n\n\n\n\n\n\nThe text above is baked into the page texture.", "color": "black"}],
			glyph_height=64,
		),
		after="welcome",
	)

	# 3) Per-item hook: control where wiki buttons appear on every item page.
	def change_button_layout_for_steel_ingot(page: ItemPage, manual: Manual) -> None:
		if page.anchor == "item:steel_ingot":
			page.button_layout = ButtonLayout(columns=4, max_buttons=42, position="after_recipe")
	manual.on_item_page(change_button_layout_for_steel_ingot)

	# 4) Phase hook: edit one specific item's page once the default pages exist.
	#    Hooks run during manual creation, so get_page_for_item() returns a real page here.
	@manual.on(Phase.PREPARED)
	def tweak_steel_ingot(m: Manual) -> None: # pyright: ignore[reportUnusedFunction]
		page = m.get_page_for_item("steel_ingot")
		if page is not None:
			page.transformers.append(
				lambda content, _m: [
					*content,
					{"text": "\nTip: steel is the backbone of this pack!", "color": "dark_gray","font": "minecraft:default"}
				]
			)

