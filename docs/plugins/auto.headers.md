
# 📝 stewbeet.plugins.auto.headers

📄 **Source Code**: [`stewbeet/plugins/auto/headers/__init__.py`](../../python_package/stewbeet/plugins/auto/headers/__init__.py) 🔗<br>
📄 **Source Code**: [`stewbeet/plugins/auto/headers/object.py`](../../python_package/stewbeet/plugins/auto/headers/object.py) 🔗<br>
📄 **Source Code**: [`stewbeet/plugins/auto/headers/context_analyzer.py`](../../python_package/stewbeet/plugins/auto/headers/context_analyzer.py) 🔗<br>
📄 **Source Code**: [`stewbeet/plugins/auto/headers/execution_parser.py`](../../python_package/stewbeet/plugins/auto/headers/execution_parser.py) 🔗<br>
📄 **Source Code**: [`stewbeet/plugins/auto/headers/function_analyzer.py`](../../python_package/stewbeet/plugins/auto/headers/function_analyzer.py) 🔗<br>
📄 **Source Code**: [`stewbeet/plugins/auto/headers/macro_analyzer.py`](../../python_package/stewbeet/plugins/auto/headers/macro_analyzer.py) 🔗<br>
📄 **Source Code**: [`stewbeet/plugins/auto/headers/macro_parser.py`](../../python_package/stewbeet/plugins/auto/headers/macro_parser.py) 🔗<br>
📄 **Source Code**: [`stewbeet/plugins/auto/headers/type_inference.py`](../../python_package/stewbeet/plugins/auto/headers/type_inference.py) 🔗<br>

## 📋 Overview
The `auto.headers` plugin automatically generates documentation headers for mcfunction files.<br>
It analyzes function calls, function tags, advancement rewards, and **macro function arguments**<br>
to create comprehensive `@within` documentation that shows which functions, tags, or advancements<br>
call each function, providing clear dependency tracking and usage documentation.<br>

**🎮 Context Analysis**: The plugin intelligently extracts and preserves execution contexts<br>
from `execute` commands (such as `as @e`, `positioned`, `at`, `rotated`, `facing`, etc.)<br>
and automatically determines the execution context for functions based on their callers.

**🔧 Macro Analysis**: For macro functions (using `$(variable)` syntax), the plugin automatically<br>
detects macro variables, infers their types from function calls and storage NBT data, and generates<br>
`@args` documentation with type information. It supports both direct NBT calls and storage-based calls,<br>
with intelligent type inheritance from calling functions.

## 🔗 Dependencies
- **✅ Required**: Beet context with functions, function tags, and advancements
- **📍 Position**: Should run after all content generation but before finalization
- **🔧 Optional**: Existing function headers (will be parsed and updated)

### <u>Some Features Showcase</u>

**Example of a function being called by multiple functions with macro arguments:**<br>
<img src="img/auto.headers.macro_example.jpg">

**Example of a function being called by multiple functions with different contexts:**<br>
<img src="img/auto.headers.context_example.jpg">

**Example of a function being called by multiple macro arguments (with arguments types):**<br>
<img src="img/auto.headers.macro_types_example.jpg">

## 🎯 Purpose
- 📝 Automatically generates function documentation headers
- 🔍 Tracks function call relationships and dependencies
- 🏷️ Analyzes function tag memberships and usage
- 🎖️ Monitors advancement reward function calls
- 🔧 **Detects macro variables** and infers their types automatically
- 📊 **Generates `@args` documentation** for macro functions with type information
- 🧬 **Intelligent type inference** from NBT data, direct calls, and storage operations
- 🔄 **Type inheritance** from calling functions via `$(variable)` references
- 📝 **Preserves manual descriptions** in `@args` while auto-filling missing types
- 🎮 **Extracts execution contexts** from `execute` commands (`as`, `at`, `positioned`, `rotated`, `facing`, `in`, `anchored`, `align`)
- 🧠 **Determines function execution contexts** automatically based on caller analysis
- � Creates comprehensive `@within` and `@args` documentation

## ⚙️ Configuration

### 🎯 Basic Example Configuration
```yaml
pipeline:
  - ...
  - stewbeet.plugins.auto.headers
  - ... # Some finalization plugins

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

### 🔧 Macro Argument Analysis (NEW!)
Automatically detects and types macro function arguments:
- 🔍 **Auto-detection** - Scans function content for `$(variable)` patterns
- 📊 **Type inference from NBT** - Analyzes direct calls like `function test {x:10,y:20.5f,id:"hello"}`
- 💾 **Storage-based inference** - Parses `data modify storage` commands to extract types
- 🔄 **Type inheritance** - When `$(var)` references another function's argument, inherits the type
- 🧬 **Recursive analysis** - Follows function call chains to ensure all types are resolved
- 📝 **Description preservation** - Keeps manually written descriptions while filling missing types
- 🎯 **NBT type mapping** - Correctly identifies byte(b), short(s), int, long(l), float(f), double(d), string, compound, list
- 📋 **Order preservation** - Arguments listed in order of first appearance in the file
- 🔗 **Merge logic** - Combines inferred types with manual annotations (manual takes precedence)

#### Supported Type Inference Patterns:
```mcfunction
# Direct NBT call
function namespace:target {x:10,y:20.5f,name:"Player"}
# -> Infers: x (int), y (float), name (string)

# Storage-based call
data modify storage temp:data macro set value {dimension:"minecraft:overworld",x:0,y:64,z:0}
function namespace:teleport with storage temp:data macro
# -> Infers: dimension (string), x (int), y (int), z (int)

# Type inheritance
function caller {result:$(value)}
# If caller has @args with value (int), target inherits: result (int)
```

### 🎮 Execution Context Analysis
Intelligently analyzes and determines execution contexts:
- 🔍 **Parses `execute` commands** to extract contexts like `as @e[type=zombie]`, `positioned ~ ~1 ~`, `at @s`, `rotated 45 0`
- 🧠 **Smart selector simplification** for complex selectors with NBT data and multiple attributes
- 🔄 **Context inheritance** - functions inherit execution contexts from their callers when appropriate
- 📋 **Automatic context determination** for advancement reward functions (`as the player & at current position`)
- ⚡ **Special handling** for tick/load tags and other built-in contexts
- 📝 **Context preservation** in `@executed` header sections

### 📝 Function Header Parsing
Intelligently parses existing function headers:
- 🔍 Detects `#> function_name` header format
- 📋 Extracts existing `@within` information
- 📝 Preserves custom documentation comments
- 🔄 Separates header content from actual function code

### 🏷️ Function Tag Analysis
Analyzes function tag memberships for documentation:
- 📊 Processes all function tags in the datapack
- 🔗 Creates `#namespace:tag_name` references for tagged functions
- 📝 Handles both string and object-based tag entries
- ✅ Supports conditional tag entries with IDs

### 🎖️ Advancement Reward Tracking
Monitors advancement reward function calls:
- 🎯 Scans advancement reward sections for function calls
- 📋 Creates `advancement namespace:advancement_name` references
- 🔗 Links reward functions to their triggering advancements
- ✅ Ensures proper advancement-to-function relationship tracking

### 🔍 Function Call Analysis
Analyzes direct function calls within mcfunction files:
- 🔍 Scans each line for `function ` commands
- 🎯 Extracts called function names with quote handling
- 🔧 Captures macro parameters and scheduling information
- 🎮 **Analyzes execution contexts** from `execute` commands (`as @e`, `positioned`, `at`, `rotated`, `facing`, `in`, `anchored`, `align`)
- 📋 Intelligently parses complex selectors with NBT data and multiple attributes
- 🔄 Inherits execution contexts from calling functions when appropriate
- 📊 Prevents duplicate entries in the `@within` list

### 📄 Header Generation System
Generates comprehensive documentation headers:
- 📝 Creates standardized `#> function_name` headers
- 📋 Generates `@within` sections listing all callers
- 🔧 Preserves existing custom documentation
- ✅ Uses proper formatting with tabs and spacing

### 💾 File Writing and Updates
Updates all mcfunction files with generated headers:
- 📝 Writes updated headers to all processed functions
- 🔄 Overwrites existing files with new documentation
- 📊 Maintains clean formatting and structure
- ✅ Ensures all functions have complete documentation headers 

