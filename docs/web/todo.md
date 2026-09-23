# Website todo

Assets only the author can produce. The site works without them: each one has a fallback already in place, listed below. Drop the file where the table says and ping Claude to wire it in.

| # | Asset | Format | Goes to | Used in | Fallback today |
|---|-------|--------|---------|---------|----------------|
| 1 | Save a definition, run `stewbeet`, the new item appears in hand in game | MP4, 1280x720, 8 to 12 s, no audio | `public/build_to_game.mp4` | Gains lead tile, or the final call to action | The static "8 files vs 1 definition" tile |
| 2 | Livereload: edit the Python, the game reloads on its own | MP4, 1280x720, about 5 s, no audio | `public/livereload.mp4` | A new bento tile "No more /reload" | Tile not shown |
| 3 | One in-game manual page for a single item, high resolution | PNG or JPG, at least 1200 px wide | `public/ingame_manual_poster.jpg` (replaces it) | Poster of the manual video | The current poster |
| 4 | Two or three short quotes from real users, with their permission | Text, pseudo, avatar PNG 128x128 | `public/testimonials/` plus the quotes in a message | A testimonials block right after "Built with" | Block not shown |

## Recording tips

- Record at 1280x720 or crop to 16:9, so the video fills its frame without black bars.
- Hide the HUD elements that are not the point (F1 in game, a clean VS Code layout).
- Encode with `ffmpeg -i in.mp4 -an -vcodec libx264 -crf 28 -preset slow -movflags +faststart out.mp4` to keep each clip under 1 MB.
- Also export the first meaningful frame as a JPG poster next to the video (`<name>_poster.jpg`), so nothing is black before it loads.
