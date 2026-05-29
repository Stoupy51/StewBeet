
#> _your_namespace:v3.0.0/unload_with_libraries
#
# @within	#_your_namespace:unload_with_libraries
#
# Be careful this can lead to issues if a library is used by another pack and had some data stored
#

# Unload the pack itself
function _your_namespace:v3.0.0/unload

# Unload libraries
function #common_signals:unload
function #smart_ore_generation:unload

