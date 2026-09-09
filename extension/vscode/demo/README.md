# Voltaic, the showcase project

A working pack, small enough to record. One namespace, seventeen functions, and the same machines written three ways, because that is what the extension covers:

| File | Written with | What it is there to show |
|---|---|---|
| `src/data/voltaic/module/gui.bolt` | bolt | The Bolt language, and a lens per function a module writes |
| `src/data/voltaic/function/elevator.mcfunction` | bolt, in a `.mcfunction` | The language switch, and the Spyglass exclusion |
| `src/turbine.py` | beet on its own | `Function(...)` from text and from a `list[str]`, plus `.append` and `.lines.append` onto one |
| `src/machines.py` | StewBeet | Interpolated paths, a loop writing three functions, commands in a variable |

Nothing here is a mock: `beet build` produces the pack and the `.mcfunction.map` sidecars every recording below relies on.

## Before recording

```sh
pip install stewbeet bolt          # or your own venv, the extension never runs either of them
cd extension/vscode/demo
beet build
code .
```

The window needs the StewBeet extension and [Spyglass](https://marketplace.visualstudio.com/items?itemName=SPGoding.datapack-language-server). `.vscode/settings.json` turns off word based suggestions, which otherwise pad every completion list with words scraped from the open file, and leaves `StewBeet.buildOutput` unset so the maps are found wherever they are.

**To record the extension as it is in this repo rather than as it is on the marketplace**, open `extension/vscode/` in a second window and press F5. The Extension Development Host that opens is where you open this folder.

Leave a terminal on `beet watch` for the takes that need a rebuild, and none of the others.

## The recordings

Six takes, cut into the four GIFs the extension README embeds:

| GIF | Takes | Where it sits |
|---|---|---|
| `hero.gif` | 4 | The top of the README |
| `bolt.gif` | 1 and 2 | Bolt |
| `beet.gif` | 3 and 5 | beet |
| `edits.gif` | 6 | The links follow your edits |

Record them in this order. Bolt and beet come first because most people who write datapacks in Python have never used StewBeet, and the first ten seconds have to be about them.

### 1. Bolt has a language at all (`gui.bolt`, 8s)

Open `gui.bolt`. Every other extension on the marketplace opens it as plain text or as mcfunction; here `class`, `def` and `@cached_property` are Python, and `playsound` on line 16 is a command.

Show the language id in the status bar reading **Bolt**, then the lenses: one above line 16, one above line 24, one above line 33, each naming three functions because the loop at line 30 runs three times. Click the one on line 33 and take the peek list.

### 2. Bolt inside a `.mcfunction` (`elevator.mcfunction`, 10s)

**Record this one first, before opening the file in any other take.** The prompt appears once.

Open `elevator.mcfunction` with the extension disabled and Spyglass on: a wall of red, because `for offset in range(1, 4):` is not a command. Enable the extension, reopen: the file becomes **Bolt**, the red goes, and the prompt offers to write the exclusion. Take the prompt and the `.spyglassrc.json` it writes.

Delete `.spyglassrc.json` afterwards. It is this take's output, not part of the project.

### 3. beet with no StewBeet anywhere (`turbine.py`, 12s)

`src/turbine.py` imports `beet` and nothing else. Show, in this order:

1. The commands inside `Function("""...""")` are coloured as commands, and so are the entries of the `Function([...])` on line 22 and the `.lines.append` on line 26.
2. Type a space after `execute store result score #height voltaic.data` on line 11 and let the completion list open.
3. Break line 13: change `matches` to `mathes`, wait for the squiggle **on the Python line**, undo. No build is involved in that one, and saying so out loud is the point of the take.
4. Ctrl+click `voltaic:turbine/stall` on line 12. It lands on line 22, the assignment that wrote that function, rather than in `build/`.

### 4. StewBeet, where the paths are interpolated (`machines.py`, 15s)

1. Line 17, `function {ns}:turbine/tick`: ctrl+click it. `{ns}` is Python that no datapack parser can read, and the jump still lands, on `turbine.py` line 9, where a plugin that has never heard of StewBeet wrote that function.
2. Type `function {ns}:` on a new line inside the block and let completion offer the pack's own paths.
3. The lens above line 23 reads **voltaic:machines/pulverizer/fast (+2 more)**: one call in a loop, three functions. Click it for the peek list.
4. Line 29, `work: McFunction = f"""`: the commands are coloured six lines above the call that consumes them, and the lens for them sits on line 35 where that call is.

### 5. The generated side (`build/.../work.mcfunction`, 6s)

Open `build/datapack/data/voltaic/function/machines/pulverizer/work.mcfunction`. The header names four callers under `@within` and each one is a link. The lens at the top leads back to `machines.py:35`.

### 6. The links follow your edits (`machines.py`, 10s)

The one nobody expects. With no rebuild at all:

1. Note the lens above line 23.
2. Delete the whole `write_function` on lines 12 to 19. Every lens below moves up with its call, and none of them points at the wrong line.
3. Alt+up on the call that is left. Its lens goes with it.
4. Delete the `write_function(` line itself. Its lens disappears rather than sliding onto the line underneath.
5. Ctrl+Z back to where you started.

## Exporting a take

The four GIFs live under `extension/vscode/images/` as `hero.gif`, `bolt.gif`, `beet.gif` and `edits.gif`.
An `.mp4` would be a tenth of the size, and the VS Code marketplace renders no `<video>` tag at all, so a GIF is what a reader of the extension page actually sees.

Keep them small, since the page loads all four: crop to the editor, 12 to 15 frames a second, and no longer than the take needs.

```sh
ffmpeg -i take.mov -vf "fps=14,scale=1100:-1:flags=lanczos,split[a][b];[a]palettegen=max_colors=128[p];[b][p]paletteuse=dither=bayer:bayer_scale=3" -loop 0 hero.gif
```

## Keeping it honest

If you edit the sources, rebuild before recording: the takes above name line numbers, and half of them are about lines the build recorded.
