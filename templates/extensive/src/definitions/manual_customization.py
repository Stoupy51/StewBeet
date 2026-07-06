
# Imports
from PIL import Image
from stewbeet import (
	BakedText,
	ButtonLayout,
	CustomPage,
	ItemPage,
	Manual,
	Mem,
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
	#    book_texture and home_texture (available on ANY page) replace the book background
	#    ("book.png") and the home button ("home.png") on this page only.
	textures_folder: str = Mem.ctx.meta["stewbeet"]["textures_folder"]
	manual.insert_page(
		CustomPage(
			anchor="welcome",	# Page id used for linking and ordering
			title="Welcome",
			body=[
				{"text": "Welcome to the Extensive Template!", "color": "black", "bold": True},
				{"text": "\n\nThis page was added with the public manual API\n(CustomPage + insert_page).", "color": "#505050"},
			],
			book_texture=f"{textures_folder}/manual/a_custom_book_page.png",
			home_texture=f"{textures_folder}/manual/home_for_welcome_page.png",
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
			# The dialog centers the texture; invisible paddings nudge it horizontally
			# (left_padding shifts right, right_padding shifts left, each by half the pixels).
			# Keep texture width + paddings within the dialog body (140px) or the line wraps.
			left_padding=10,
			# Any page can also hide its home button (prev/next layout is preserved)
			home_button=False,
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

	# 5) Cross-link two related pages with extra wiki buttons (ItemPage.extra_buttons):
	#    - button_for_item(): another item's full recipe button (hover shows the recipe, click opens its page)
	#    - link_button(): a simple button with the item's icon that just opens its page
	@manual.on(Phase.PREPARED)
	def cross_link_pages(m: Manual) -> None: # pyright: ignore[reportUnusedFunction]
		stone = m.get_page_for_item("super_stone")
		painting = m.get_page_for_item("stewbeet_painting")
		if stone is None or painting is None:
			return

		# Show the painting's recipe on the super stone page (click -> painting page)
		painting_recipe_button = m.recipes.button_for_item("stewbeet_painting")
		if painting_recipe_button is not None:
			stone.extra_buttons.append(painting_recipe_button)

		# And link back: a button on the painting page opening the super stone page
		painting.extra_buttons.append(m.recipes.link_button("super_stone"))

