
# 📝 stewbeet.plugins.auto.headers

📄 **Source Code**: [stewbeet/plugins/auto/headers/__init__.py](../../python_package/src/stewbeet/plugins/auto/headers/__init__.py) 🔗

## 📋 Overview
The `auto.headers` plugin automatically generates documentation headers for mcfunction files.<br>
It analyzes function calls, function tags, advancement rewards, and macro usage to create<br>
comprehensive `@within` documentation that shows which functions, tags, or advancements<br>
call each function, providing clear dependency tracking and usage documentation.

## 🎯 Purpose
- 📝 Automatically generates function documentation headers
- 🔍 Tracks function call relationships and dependencies
- 🏷️ Analyzes function tag memberships and usage
- 🎖️ Monitors advancement reward function calls
- 🔧 Handles macro parameters and scheduling information
- 📊 Creates comprehensive `@within` documentation

## 🔗 Dependencies
- **✅ Required**: Beet context with functions, function tags, and advancements
- **📍 Position**: Should run after content generation but before finalization
- **🔧 Optional**: Existing function headers (will be parsed and updated)
- **📋 Related**: Works with any plugins that generate mcfunction content

## ⚙️ Configuration

### 🎯 Basic Configuration
```yaml
# No configuration required - plugin runs automatically
# Processes all functions, function tags, and advancements by default
```

### 📋 Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| Header Generation | automatic | Enabled | Creates headers for all mcfunction files |
| Dependency Tracking | automatic | Enabled | Analyzes function calls and references |
| Tag Analysis | automatic | Enabled | Processes function tag memberships |
| Advancement Rewards | automatic | Enabled | Tracks advancement reward functions |

## ✨ Features

### 📝 Function Header Parsing
Intelligently parses existing function headers: [`object.py#L30-L85`](../../python_package/src/stewbeet/plugins/auto/headers/object.py#L30-L85)
- 🔍 Detects `#> function_name` header format
- 📋 Extracts existing `@within` information
- 📝 Preserves custom documentation comments
- 🔄 Separates header content from actual function code

### 🏷️ Function Tag Analysis
Analyzes function tag memberships for documentation: [`__init__.py#L28-L39`](../../python_package/src/stewbeet/plugins/auto/headers/__init__.py#L28-L39)
- 📊 Processes all function tags in the datapack
- 🔗 Creates `#namespace:tag_name` references for tagged functions
- 📝 Handles both string and object-based tag entries
- ✅ Supports conditional tag entries with IDs

### 🎖️ Advancement Reward Tracking
Monitors advancement reward function calls: [`__init__.py#L42-L50`](../../python_package/src/stewbeet/plugins/auto/headers/__init__.py#L42-L50)
- 🎯 Scans advancement reward sections for function calls
- 📋 Creates `advancement namespace:advancement_name` references
- 🔗 Links reward functions to their triggering advancements
- ✅ Ensures proper advancement-to-function relationship tracking

### 🔍 Function Call Analysis
Analyzes direct function calls within mcfunction files: [`__init__.py#L53-L68`](../../python_package/src/stewbeet/plugins/auto/headers/__init__.py#L53-L68)
- 🔍 Scans each line for `function ` commands
- 🎯 Extracts called function names with quote handling
- 🔧 Captures macro parameters and scheduling information
- 📊 Prevents duplicate entries in the `@within` list

### 📄 Header Generation System
Generates comprehensive documentation headers: [`object.py#L107-L143`](../../python_package/src/stewbeet/plugins/auto/headers/object.py#L107-L143)
- 📝 Creates standardized `#> function_name` headers
- 📋 Generates `@within` sections listing all callers
- 🔧 Preserves existing custom documentation
- ✅ Uses proper formatting with tabs and spacing

### 💾 File Writing and Updates
Updates all mcfunction files with generated headers: [`__init__.py#L71-L72`](../../python_package/src/stewbeet/plugins/auto/headers/__init__.py#L71-L72)
- 📝 Writes updated headers to all processed functions
- 🔄 Overwrites existing files with new documentation
- 📊 Maintains clean formatting and structure
- ✅ Ensures all functions have complete documentation headers 

