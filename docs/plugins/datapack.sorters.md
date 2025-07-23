
# 🔢 stewbeet.plugins.datapack.sorters

📄 **Source Code**: [stewbeet/plugins/datapack/sorters/__init__.py](../../python_package/stewbeet/plugins/datapack/sorters/__init__.py) 🔗<br>
📄 **Source Code**: [stewbeet/plugins/datapack/sorters/constants.py](../../python_package/stewbeet/plugins/datapack/sorters/constants.py) 🔗<br>
📄 **Source Code**: [stewbeet/plugins/datapack/sorters/extend_datapack.py](../../python_package/stewbeet/plugins/datapack/sorters/extend_datapack.py) 🔗<br>
📄 **Source Code**: [stewbeet/plugins/datapack/sorters/match.py](../../python_package/stewbeet/plugins/datapack/sorters/match.py) 🔗<br>
📄 **Source Code**: [stewbeet/plugins/datapack/sorters/quick_sort.py](../../python_package/stewbeet/plugins/datapack/sorters/quick_sort.py) 🔗<br>
📄 **Source Code**: [stewbeet/plugins/datapack/sorters/selection_sort.py](../../python_package/stewbeet/plugins/datapack/sorters/selection_sort.py) 🔗<br>

## 💻 Credits
**Author**: [Darukshock](https://github.com/Darukshock) - Original implementation of the quick sort algorithm

## 📋 Overview
The `datapack.sorters` plugin generates efficient sorting functions for Minecraft datapacks.<br>
It creates optimized mcfunction files at compile time that can sort lists stored in NBT storage<br>
using configurable algorithms (Quick Sort and Selection Sort), with support for custom comparison<br>
keys, scaling factors, and performance optimizations tailored for Minecraft's execution environment.

## 🔗 Dependencies
- **✅ Required**: Beet context with datapack namespace support
- **📍 Position**: Can run at any point during compilation
- **🔧 Extension**: Requires `stewbeet.plugins.datapack.sorters.extend_datapack` to register sorter namespace

### <u>Quick Example</u>

**Sorters are declared in the `sorters` registry under `data/<namespace>`, like so:**<br>
`data/<namespace>/sorter/<sorter_name>.json`<br>
<img src="img/datapack.sorters.registry.jpg">

**Alternatively, they can be generated with python:**<br>
<img src="img/datapack.sorters.generate_sort.jpg">

**The list can now be sorted:**<br>
<img src="img/datapack.sorters.mcfunction.jpg">

## 🎯 Purpose
- 🚀 Generate high-performance sorting functions for NBT storage lists
- 🎯 Support multiple sorting algorithms optimized for Minecraft's execution model
- 📊 Handle complex data structures with configurable comparison keys
- ⚡ Provide in-place sorting with minimal memory overhead
- 🔧 Enable precision control through scaling for decimal values
- 📈 Support partial sorting with element limits for performance optimization

## ⚙️ Configuration

### 📋 Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `algorithm` | string | **Required** | Sorting algorithm to use: `"selection_sort"` (recommended) or `"quick_sort"` |
| `functions_location` | string | **Required** | Namespaced function ID where sorting functions are generated |
| `to_sort` | object | **Required** | Storage location containing `storage` and `target` keys |
| `to_sort.storage` | string | **Required** | Storage namespace (e.g., `"switch:stats"`) |
| `to_sort.target` | string | **Required** | NBT path to the list (e.g., `"all.modes.sheepwars.played"`) |
| `key` | string | **Required** | Key within each list element to compare for sorting |
| `scale` | integer | `1` | Optional: Scaling factor for numeric values (`negative for descending order`) |
| `limit` | integer | `null` | Optional: Maximum elements to sort (selection_sort only) |

**⚡ Performance Note**: Selection sort significantly outperforms quick sort in Minecraft's storage environment due to quick sort's heavy reliance on macro expansions. Each recursive call in quick sort generates multiple macro invocations for parameter passing and storage manipulation, creating substantial overhead that negates the theoretical O(n log n) advantage. Selection sort's straightforward O(n²) approach with minimal macro usage proves more efficient for typical Minecraft datapack sorting operations.

### 🎯 Basic Example Configuration
```yaml
require:
  - ...
  - stewbeet.plugins.datapack.sorters.extend_datapack # Required: register "data/<namespace>/sorter/" as a custom resource
  - ...

pipeline:
  - ...
  - stewbeet.plugins.datapack.sorters  # Place this plugin in the pipeline
  - ...  # Other plugins follow
```

### 📝 Example Sorter Configuration
```json
{
	"algorithm": "selection_sort",
	"functions_location": "switch:stats/minigame/sort_leaderboard",
	"to_sort": {
		"storage": "switch:stats",
		"target": "all.modes.sheepwars.played"
	},
	"key": "count",
	"scale": 100,
	"limit": 10
}
```


## ✨ Features

### 🎛️ Algorithm Selection System
Provides two optimized sorting algorithms:
- 🥇 **Selection Sort** - Recommended algorithm with better performance in Minecraft
- ⚡ **Quick Sort** - Alternative algorithm using recursive function calls and macros
- � **Algorithm Routing** - Automatic selection based on configuration
- 📊 **Performance Optimization** - Algorithms tailored for Minecraft's execution model

### 📦 Extended Datapack Support
Enhanced namespace functionality for sorter configurations:
- 🗄️ **Custom Resource Type** - Sorter objects defined at `data/<namespace>/sorter/path.json`
- 📁 **Namespace Extension** - Automatic registration of sorter file types
- 🔧 **File Processing** - JSON-based configuration with validation
- ✅ **Multi-Datapack Support** - Independent configurations prevent conflicts

### 🔢 Advanced Scaling System
Flexible numeric processing for different data types:
- � **Precision Control** - Scale factor for decimal precision (e.g., `1000` for 3 decimal places)
- 🔄 **Reverse Sorting** - Negative scale values for descending order
- 🎯 **Integer Optimization** - Direct comparison for whole numbers
- 📊 **Float Support** - Scaled comparison for floating-point values

### ⚡ Selection Sort Implementation
Optimized selection sort with advanced features:
- 🔍 **Minimum Finding** - Efficient linear search for smallest elements
- 📋 **Array Manipulation** - Proper NBT storage handling with temporary arrays
- 🚀 **Partial Sorting** - Optional limit parameter for top-N sorting
- 💾 **Memory Efficient** - In-place sorting with minimal storage overhead
- 🔄 **Element Movement** - Atomic operations for moving sorted elements

### � Quick Sort Implementation
Recursive quick sort with macro-based partitioning:
- 📊 **Pivot Selection** - Last element as pivot for partitioning
- � **Recursive Calls** - Function-based recursion with macro parameters
- ⚖️ **Partitioning Logic** - Efficient element comparison and swapping
- 📈 **Divide and Conquer** - Classic quick sort algorithm adaptation
- ⚠️ **Performance Note** - Less efficient than selection sort due to macro overhead

### 📝 Configuration Validation
Comprehensive input validation and error handling:
- ✅ **Type Checking** - Validates all configuration parameters
- 🔍 **Required Fields** - Ensures all mandatory options are provided
- 📋 **Format Validation** - Checks storage paths and function locations
- 🛡️ **Error Prevention** - Prevents invalid configurations from processing

### 🏗️ Function Generation System
Dynamic mcfunction file creation:
- 📄 **Multi-Function Output** - Generates complete sorting function sets
- � **Macro Integration** - Uses storage macros for dynamic parameters
- 📊 **Scoreboard Management** - Temporary objectives for sorting operations
- 🗄️ **Storage Cleanup** - Automatic cleanup of temporary storage after sorting

### 💾 Memory Management
Efficient storage utilization during sorting:
- 🔄 **Temporary Storage** - Uses `sorter:temp` namespace for operations
- 📋 **Array Copying** - Safe duplication of original arrays
- 🧹 **Cleanup Operations** - Removes temporary data after completion
- ⚡ **Minimal Footprint** - Optimized storage usage patterns

