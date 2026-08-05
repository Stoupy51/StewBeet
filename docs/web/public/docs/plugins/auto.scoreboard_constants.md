# stewbeet.plugins.auto.scoreboard_constants

The `auto.scoreboard_constants` plugin automatically detects scoreboard constant usages across all datapack functions<br>
and generates their initialization commands in the load file.<br>
It scans every function for the pattern `#{integer} {project_id}.data` and produces a sorted list of<br>
`scoreboard players set` commands, ensuring every constant is properly initialized on load without any manual tracking.

### <u>Feature Showcase</u>

**Generated scoreboard constants initialization in the load file:**<br>
<img src="https://raw.githubusercontent.com/Stoupy51/StewBeet/main/docs/plugins/img/auto.scoreboard_constants.example.jpg">

**Required**: Beet context with functions  
**Required**: Project ID for scoreboard objective namespacing  
**Position**: Should run after all function content is generated but before finalization  
**Related**: Works with any plugin that uses scoreboard constants in mcfunction files  
**Source Code**: [`stewbeet/plugins/auto/scoreboard_constants/__init__.py`](https://github.com/Stoupy51/StewBeet/blob/main/python_package/stewbeet/plugins/auto/scoreboard_constants/__init__.py) <br>


## What it does

- Automatically detects all scoreboard constant usages across datapack functions
- Generates `scoreboard players set #{n} {project_id}.data {n}` initialization commands
- Targets the `{project_id}.data` scoreboard objective
- Writes constants to the project's load file in sorted numerical order
- Eliminates manual tracking and declaration of scoreboard constants

## Configuration

### Basic Example Configuration
```yaml
pipeline:
  - ...
  - stewbeet.plugins.auto.scoreboard_constants
  - ...

# No configuration required - plugin runs automatically
# Scans all functions for the pattern: #{integer} {project_id}.data
```

### Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| Pattern Detection | automatic | Enabled | Scans all functions for `#{integer} {project_id}.data` |
| Initialization Target | automatic | Load function | Writes set commands to the project's load file |
| Deduplication | automatic | Enabled | Duplicate constant values are collected once via a set |
| Sorting | automatic | Ascending | Constants are sorted numerically before output |

## Features

### Constant Discovery
Scans every datapack function line by line for scoreboard constant references:
- 🎯 Uses compiled regex `#(\d+) {project_id}.data` for efficient detection
- 📊 Collects all unique integer constant values into a set for automatic deduplication
- 🔄 Processes every function present in the beet pipeline

### Load File Generation
Writes sorted initialization commands to the project's load function:
- 📋 Produces `scoreboard players set #{n} {project_id}.data {n}` for each discovered constant
- 🔢 Sorts constants numerically for deterministic and readable output
- 💾 Appends the constants block to the existing load file content
- ✅ Skips output entirely if no constants are found

## Next steps

- [Writing functions and files](../2_writing_to_files/en.md) — the functions this plugin post-processes.
- [All plugins](README.md) — the rest of the pipeline, in the order it runs.
- [Configuring the build](../3_beet_config/en.md) — enabling, ordering and configuring plugins.
