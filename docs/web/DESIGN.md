---
version: alpha
name: StewBeet website
description: A precise, technical datapack site built on a white page, a framed column and a 16 px pixel grid, where Minecraft's own interface frames the proof.
colors:
  surface: "#ffffff"
  surface-dark: "#0c0d0f"
  text: "#111214"
  text-dark: "#f2f3f5"
  text-muted: "#565964"
  text-muted-dark: "#a3a7b0"
  border: "#e3e4e8"
  border-dark: "#272930"
  grid: "rgba(17, 18, 20, 0.07)"
  grid-dark: "rgba(255, 255, 255, 0.06)"
  primary: "#c42340"
  primary-hover: "#9e1a33"
  on-primary: "#ffffff"
  link: "#b81d39"
  link-dark: "#ff6b7d"
  generated: "#2b7a19"
  generated-dark: "#7fd35b"
  electric: "#0a6fd6"
  electric-dark: "#2e9bff"
  code-surface: "#ffffff"
  code-surface-dark: "#15171b"
  code-border: "#e3e4e8"
  code-border-dark: "#2a2d34"
  code-text: "#1f2328"
  code-text-dark: "#e6e7ea"
  code-text-muted: "#565964"
  code-text-muted-dark: "#9aa0aa"
  section-start: "#1f7a2a"
  section-start-dark: "#63d96b"
  section-guides: "#3045c0"
  section-guides-dark: "#7c9cff"
  section-plugins: "#8a5a00"
  section-plugins-dark: "#f0b23c"
  section-contrib: "#cb1b98"
  section-contrib-dark: "#fe5acc"
  section-reference: "#8b2fa3"
  section-reference-dark: "#d98cf0"
  section-understand: "#0b6f7a"
  section-understand-dark: "#5fd3e0"
  mc-panel: "#c6c6c6"
  mc-slot: "#8b8b8b"
  mc-tooltip: "#100010"
  mc-tooltip-border: "#5000ff"
  mc-lore: "#cc66dd"
typography:
  display:
    fontFamily: "Archivo"
    fontSize: "3.25rem"
    fontWeight: 700
    lineHeight: 1.12
    letterSpacing: "0em"
  display-phone:
    fontFamily: "Archivo"
    fontSize: "2.25rem"
    fontWeight: 700
    lineHeight: 1.15
    letterSpacing: "0em"
  body:
    fontFamily: "Archivo"
    fontSize: "1.0625rem"
    fontWeight: 400
    lineHeight: 1.5
  mono:
    fontFamily: "JetBrains Mono"
    fontSize: "0.8125rem"
    lineHeight: 1.6
  label:
    fontFamily: "JetBrains Mono"
    fontSize: "0.6875rem"
    fontWeight: 400
    letterSpacing: "0.08em"
  pixel:
    fontFamily: "Monocraft"
    fontSize: "0.8125rem"
    lineHeight: 1.55
rounded:
  none: 0px
spacing:
  unit: 4px
  gutter: 16px
  grid-cell: 16px
  page: 1200px
components:
  button-primary:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.on-primary}"
    rounded: "{rounded.none}"
    height: 48px
    padding: 22px
  code-panel:
    backgroundColor: "{colors.code-surface}"
    textColor: "{colors.code-text}"
    typography: "{typography.mono}"
    rounded: "{rounded.none}"
  step-marker:
    typography: "{typography.label}"
    size: 30px
    rounded: "{rounded.none}"
  mc-tooltip:
    backgroundColor: "{colors.mc-tooltip}"
    typography: "{typography.pixel}"
    rounded: "{rounded.none}"
---

## Overview

Precise, technical, direct, a bit raw. Never cute, never editorial. The register is technical, with a few moments of large type.

The site speaks to people who write their datapack commands by hand, from their first custom block to a 300-item pack. They mostly arrive from a Discord link on a phone, and half of them read French, so every screen is designed at 390 px first, then at 1440 px.

The look is a hybrid. Minecraft's own interface (inventory slots, the item tooltip, Monocraft) appears only where a page shows something from the game: the home page and the Showcase. The docs, the Tools, the header and the footer use the terminal-and-files style. Mockups of both: <https://claude.ai/artifact/VGbCwm7AFG1mPyz2H4GnQd>.

The signature is a 16 px pixel grid visible in the page margins, behind a content column framed by 1 px borders. References: the Tailwind CSS docs for the grid and the steps beside their terminal, Motion for the contrast of scale, beet's own docs for file-titled code blocks and the red accent, the Fabric docs.

## Colors

The light page is pure white and the dark page a neutral near-black: no cream, no brown tint, grey neutrals only. Beet red is the only accent, kept for the one primary button of a screen and for links; white on `primary` is 5.9:1, and a pressed or hovered button darkens to `primary-hover`. Leaf green marks generated output and success. Electric blue is StewBeet itself in the beet, bolt and mecha diagram, with a spark running along its frame and down into beet; the light value keeps 4.9:1 on white. Code follows the page: a white panel framed by its border in the light theme, a raised near-black one in the dark theme, highlighted with VS Code's Light+ and Dark+. A light page with dark code blocks makes the eye adapt at every block, and dark text on a light background reads better.

Each docs section has a color taken from Minecraft's text colors and darkened for the light theme, all at 4.5:1 or more: Start here green, Guides blue, Plugins gold, Contrib magenta, Reference purple, Understand cyan. A section's color appears wherever the section does: its sidebar label with an 8 px square, the current page marker, the breadcrumb, the docs home and the search results.

The `mc-` colors are the game's and only paint Minecraft elements.

## Typography

Archivo carries headings and text at its normal width. Headings are weight 700 with normal tracking and a line height of 1.12 to 1.15, never compressed: 52 px on desktop (`display`), 36 px on a phone (`display-phone`). JetBrains Mono sets code, paths, numbers, and the uppercase labels of navigation and code panels. Monocraft, under the OFL 1.1, sets the item tooltip, the small labels and the numbers of the home page and the Showcase, and nothing else. Body text is 16 to 17 px on a phone. Doc text runs as wide as the code blocks, about 80 characters a line on a desktop: on screen, reading speed rises up to 95 to 100 characters a line with comprehension unchanged, and readers prefer 60 to 90 (Shaikh and Chaparro 2005, Dyson 2004). The 45 to 75 of print typography is a rule of thumb for books, not a measured optimum.

## Layout

The page column is 1200 px at most. On a phone the grid shows in 16 px strips on both sides of the column.

Navigation holds Docs, Showcase and Tools. Docs on desktop have three columns: every page grouped in a 264 px sidebar, the page, and "On this page" in 216 px, which lists the H2s and unfolds the H3s and H4s of the section being read. On a phone the header hides while scrolling down a doc page, and one 48 px bar keeps "Pages" (a full-screen list of every page, grouped by section) and "On this page". The breadcrumb sits above the H1 and there is no Back button.

Steps are numbered only when they are a real sequence, in framed "01" markers: instruction left and terminal right on desktop, stacked on a phone. Every code block has a copy button and wraps on a phone.

Budgets: the home page fits in 7 phone screens and 600 words, a plugin page in 5 screens. Primary touch targets are 44 px, and none is under 24 px.

## Elevation

No shadow on a card or a panel: a 1 px border separates surfaces. The home page proof is the one overlap, the output laid over the definition with a ring of page color between them.

## Shapes

Corners are square everywhere. Avatars are circles. Minecraft elements keep the game's bevels: a slot is inset with a dark top-left edge and a light bottom-right one.

## Motion

Three moments move and nothing else does. On the home page the build plays: the definition's lines light up, their files drop, and the last frame is a real in-game capture. The 8 hand-written files crack like a mined block and drop one definition. The Showcase strip fills chest slots the way `_give_all` does. Smaller details: the inventory hover overlay on cards, manual pages turned with a swipe, the stack diagram building itself when its page opens, and a view transition between doc pages. In that transition the page column clears in 16 px cells, the size of the margin grid, in a random order, then the next page fills in the same way, while the current-page marker glides to its row. A language change fades the screen in place and keeps the reader in the same section.

Nothing makes the visitor wait. Text is readable before and during every animation. The build plays once in about 2 seconds and replays on a tap, and a page entrance lasts 0.6 seconds at most. Only `transform` and `opacity` animate, plus the cell masks of the doc page transition, and reduced motion shows the final frame. A press takes 150 ms on `cubic-bezier(0.4, 0, 0.2, 1)`, an entrance 400 ms on `cubic-bezier(0.16, 1, 0.3, 1)`.

## Voice

Copy starts from the maintainer's words, and each headline comes in 2 or 3 versions for him to pick. Sentences are short and declarative, with real numbers and the datapack vocabulary: loot table, predicate, `/reload`, namespace. The home headline is "Custom items and blocks without writing every file". User quotes are trimmed, never rewritten, and placed beside the objection they answer.

In French, keywords stay English (Showcase, Tools, Playground, item, block, recipe, loot table) and ordinary words are translated ("Commencer ici", "Référence").

## Components

- `button-primary`: one per screen, beet red, square, 48 px high.
- `code-panel`: a panel in the page's theme, titled by its file name or "Terminal", with a copy button.
- `step-marker`: a 30 px framed number, "01" to "09".
- `mc-tooltip`: the game's item tooltip, its border going from `#5000ff` to `#28007f`.

## Do's and Don'ts

- Do show real artefacts: the definition, the files it generates, in-game captures, real counts.
- Do give a color one meaning: a docs section, or generated output.
- Don't repeat one card style on every section.
- Don't use cream or a warm off-white, gradients, check-mark lists or emoji.
- Don't set headings compressed: no negative tracking, no widened heavy display.
- Don't scatter uppercase labels over cards: they belong to navigation and code panels.
- Don't write "X, not Y" or "Your X, verb-ed" headings, or invent a stat or a quote.
- Don't use Minecraft's interface outside the home page and the Showcase.

