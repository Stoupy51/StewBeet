
# 🔁 stewbeet.plugins.livereload

📄 **Source Code**: [`stewbeet/plugins/livereload/__init__.py`](../../python_package/stewbeet/plugins/livereload/__init__.py) 🔗

## 🔗 Dependencies
- **✅ Required**: [`beet.contrib.livereload`](https://github.com/mcbeet/beet) (bundled with beet, required automatically)
- **🔧 Optional**: `build_copy_destinations.datapack` in project metadata (from [copy_to_destination](./copy_to_destination.md))
- **🔧 Optional**: A `beet link` association (classic beet workflow)
- **📍 Position**: Only needs to be *required*; it hooks into beet's autosave/watch system on its own

## 📋 Overview
The `livereload` plugin is a thin wrapper around beet's built-in `beet.contrib.livereload` that adds
support for StewBeet's `build_copy_destinations.datapack` folders.<br>
With vanilla beet, live reloading only works when the project is associated to a world through
`beet link`. Most StewBeet users instead deploy their datapack to one or more folders via
`build_copy_destinations`. This plugin bridges the two, so a simple `stewbeet watch` triggers an
automatic in-game `/reload` after every rebuild — **no `beet link` required**.

Both mechanisms coexist: if the project is *also* linked with `beet link`, the linked folder keeps
working alongside the configured copy destinations.

## 🎯 Purpose
- 🔁 Automatic in-game `/reload` after each rebuild while running `stewbeet watch`
- 📂 Targets the folders from `build_copy_destinations.datapack` (no `beet link` needed)
- 🔗 Stays compatible with the classic `beet link` workflow (all methods can be used at once)
- 🌐 Works with remote `sftp://` datapack destinations too (deploy to a remote server and reload)
- 🧩 Zero extra wiring: require this single plugin instead of `beet.contrib.livereload` + `beet link`

## ⚙️ Configuration

### 🎯 Basic Example Configuration
```yaml
require:
  - stewbeet.plugins.livereload   # requires beet.contrib.livereload for you

meta:
  stewbeet:
    build_copy_destinations:
      datapack:
        - "path/to/minecraft/saves/world/datapacks"
        - "path/to/server/world/datapacks"
```

Then simply run:
```bash
stewbeet watch
```
Every time a source file changes, the datapack is rebuilt, copied to the destinations, and the game
reloads it automatically. A `livereload - Reloaded` message appears in the in-game chat.

### 📋 Configuration Options
It reuses the datapack destinations already configured for
[copy_to_destination](./copy_to_destination.md), plus one optional override:

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `build_copy_destinations.datapack` | array | `[]` | Datapack folders to live-reload — local paths **or** `sftp://` URLs |
| `livereload.minecraft` | string | *(auto)* | Directory containing `logs/` for the **client** you play on. Required for `sftp://`-only setups, and whenever auto-detection fails |

### 🌐 Remote server over SFTP
```yaml
meta:
  stewbeet:
    livereload:
      minecraft: "C:/Users/you/AppData/Roaming/.minecraft"   # YOUR client, not the server
    build_copy_destinations:
      datapack:
        - "sftp://user@host/home/mc/server/world/datapacks"
```
The helper datapack is uploaded (as `livereload.zip`) and removed over SFTP, while the reload
confirmation is read from your **local client's** log — because the remote server broadcasts the
`livereload - Reloaded` chat to you, and your client is what logs the `[CHAT]` line. This is why
`livereload.minecraft` must point at your client when the datapack lives on a remote server. SFTP
credentials are resolved exactly like [copy_to_destination](./copy_to_destination.md) (inline in the
URL or `~/stewbeet/credentials.yml`).

### 🎯 Explicit game folder (when auto-detection fails)
```yaml
meta:
  stewbeet:
    livereload:
      minecraft: "D:/my_server"   # the folder that contains logs/latest.log
    build_copy_destinations:
      datapack:
        - "D:/my_server/world/datapacks"
```

## ✨ How It Works
1. On each build, a tiny helper datapack named `livereload` is written into every configured datapack
   destination (and the `beet link` folder, if any). Local destinations get it as a folder; remote
   `sftp://` destinations get it uploaded as `livereload.zip`.
2. That helper datapack polls `datapack list available` in-game; when it detects the change it runs
   `/reload` by itself.
3. A single background worker tails the **client's** `logs/latest.log`; once it sees the reload
   confirmation it removes every helper datapack — deleting local folders and `rm`-ing remote zips
   over SFTP — so the next build can trigger the cycle again.
4. The client folder holding `logs/latest.log` is auto-detected. Because live reload watches the
   **client** `[CHAT]` log, detection walks up from the **resource pack** destination first (which
   usually sits inside `.minecraft`), then from the local datapack destination. This means it still
   works when your datapack is deployed to a separate server/world tree — even a remote one over
   SFTP — while you play on a client whose logs live elsewhere. For remote/`sftp://`-only setups,
   set `livereload.minecraft` to your client folder explicitly.

> ℹ️ Under the hood this monkey-patches `beet.contrib.livereload.livereload` so it understands copy
> destinations. The patch is idempotent and is also applied by
> [`stewbeet.plugins.initialize`](./initialize.md), which means live reload works even if you only
> require `beet.contrib.livereload` directly (as long as `build_copy_destinations.datapack` is set).

## 🩺 Troubleshooting

### `WARN | livereload  Not linked to any Minecraft installation. Reloading disabled.`
The plugin could not find the game's `logs/latest.log`, so the reload cycle can't run (the helper
datapack is copied but the game never reloads). Fix one of the following:
- ▶️ **Run `stewbeet watch`, not `stewbeet`.** A one-shot build has nothing to live-reload.
- 🎮 **Make sure the game/server is running** when you build — the log file only exists then.
- 🎨 **Configure a `resource_pack` destination.** Detection walks up from the resource pack folder
  (which normally lives inside the client `.minecraft`) to find `logs/latest.log`, which is often the
  only place the log can be reached when the datapack goes to a separate server/world tree.
- 📁 **Set `meta.stewbeet.livereload.minecraft`** to the folder containing `logs/` as a last resort
  (e.g. a custom log path, or when neither destination is inside the client directory).

## 🧪 Notes & Limitations
- Live reload only runs under `stewbeet watch` / beet's autosave (not on a one-shot `stewbeet build`).
- The reload is driven by removing and re-adding the helper datapack, which requires reading the game
  log — that's why the `logs/latest.log` folder must be correctly detected or configured.
- The first time, you may need one manual `/reload` (or to re-enter the world) so the helper datapack
  gets enabled and starts polling; subsequent builds then reload automatically.
- The helper datapack is dropped into **all** configured destinations (local and remote), and a
  single worker cleans them all up on each confirmed reload.
- For remote `sftp://` destinations you must connect to that server with your local client and set
  `livereload.minecraft` to your client folder — the reload confirmation is only ever logged by the
  client that receives the chat, never by the remote server itself.

