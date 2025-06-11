
# 🏗️ stewbeet.plugins.finalyze.basic_datapack_structure

📄 **Source Code**: [stewbeet/plugins/finalyze/basic_datapack_structure/__init__.py](../../python_package/src/stewbeet/plugins/finalyze/basic_datapack_structure/__init__.py) 🔗

## 📋 Overview
The `finalyze.basic_datapack_structure` plugin sets up essential timing infrastructure<br>
for Minecraft datapacks by creating timer systems for different intervals. It automatically<br>
detects existing versioned timing functions and generates the necessary tick-based<br>
logic to call them at proper intervals with optimized load distribution.

## 🎯 Purpose
- ⏰ Sets up basic timing infrastructure for datapacks
- 🔄 Creates timer systems for different intervals (tick_2, second, second_5, minute)
- 📊 Implements scoreboard-based timing logic
- ⚡ Optimizes load distribution with offset timing
- 🎯 Automatically detects existing timing functions
- 🏗️ Provides foundation for datapack timing systems

## 🔗 Dependencies
- **✅ Required**: Project ID and version in context
- **✅ Required**: Beet context for function detection
- **🔧 Optional**: Versioned timing functions (tick_2, second, second_5, minute)
- **📋 Related**: Works with versioned function system

## ⚙️ Configuration

### 🎯 Basic Configuration
```yaml
# No specific configuration required - automatically detects timing functions
# Creates timer infrastructure for any existing versioned functions:
# {namespace}:v{version}/tick_2     - Every 2 ticks (0.1 seconds)
# {namespace}:v{version}/second     - Every second
# {namespace}:v{version}/second_5   - Every 5 seconds
# {namespace}:v{version}/minute     - Every minute
```

### 📋 Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `tick_2` | function | Auto-detected | Function called every 2 ticks (0.1 seconds) |
| `second` | function | Auto-detected | Function called every second (20 ticks) |
| `second_5` | function | Auto-detected | Function called every 5 seconds (100 ticks) |
| `minute` | function | Auto-detected | Function called every minute (1200 ticks) |
| Timer Offset | automatic | Enabled | Offset timing for better load distribution |

## ✨ Features

### 🔍 Automatic Function Detection
Scans for existing versioned timing functions in the datapack: [`#L33-L37`](../../python_package/src/stewbeet/plugins/finalyze/basic_datapack_structure/__init__.py#L33-L37)
- 📁 Detects `v{version}/tick_2` functions for high-frequency timing
- ⏱️ Identifies `v{version}/second` functions for per-second execution
- 🕐 Finds `v{version}/second_5` functions for 5-second intervals
- ⏰ Locates `v{version}/minute` functions for minute-based timing

### 📊 Timer Reset System
Implements proper timer initialization for each detected function: [`#L40-L63`](../../python_package/src/stewbeet/plugins/finalyze/basic_datapack_structure/__init__.py#L40-L63)
- 🔄 Resets `#tick_2` timer to 1 for immediate first execution
- ⏱️ Initializes `#second` timer to 0 for standard counting
- 🕐 Sets `#second_5` timer to -10 for offset execution
- ⏰ Resets `#minute` timer to 1 for proper timing

### ⚡ Load Distribution Optimization
Uses offset timing to distribute computational load: [`#L54-L56, #L84-L85`](../../python_package/src/stewbeet/plugins/finalyze/basic_datapack_structure/__init__.py#L54-L56)
- 🎯 `tick_2` executes at 3+ ticks instead of 2 for offset
- 🕐 `second_5` starts at -10 to spread load (90+ ticks instead of 100)
- ⚡ Prevents multiple timers from executing simultaneously
- 📈 Improves server performance by avoiding tick spikes

### 🔢 Scoreboard Timer Logic
Creates efficient scoreboard-based timing system: [`#L66-L75`](../../python_package/src/stewbeet/plugins/finalyze/basic_datapack_structure/__init__.py#L66-L75)
- 📊 Increments timer scoreboards each tick
- 🎯 `#tick_2` increments for 2-tick timing
- ⏱️ `#second` increments for 20-tick (1 second) timing
- 🕐 `#second_5` increments for 100-tick (5 second) timing
- ⏰ `#minute` increments for 1200-tick (1 minute) timing

### 🎯 Conditional Function Execution
Implements threshold-based function calling: [`#L78-L85`](../../python_package/src/stewbeet/plugins/finalyze/basic_datapack_structure/__init__.py#L78-L85)
- 🔄 Calls `tick_2` when score reaches 3+ (offset timing)
- ⏱️ Executes `second` when score reaches 20+ (1 second)
- 🕐 Triggers `second_5` when score reaches 90+ (offset 5 ticks)
- ⏰ Invokes `minute` when score reaches 1200+ (1 minute)

### 🏗️ Tick File Integration
Integrates timing logic into the main tick function: [`#L88-L89`](../../python_package/src/stewbeet/plugins/finalyze/basic_datapack_structure/__init__.py#L88-L89)
- 📝 Prepends timer logic to existing tick functions
- 🔧 Ensures timing infrastructure runs before other tick logic
- ⚡ Maintains proper execution order for dependent systems
- 🎯 Provides foundation for all datapack timing needs 

