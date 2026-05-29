#!/bin/bash

# Build the VSCode extension package using `vsce`.
cd vscode
cp ../../docs/stewbeet_1024x1024.png ./icon.png
cp ../../python_package/LICENSE ./LICENSE
vsce package --no-dependencies

# Move the generated .vsix file to the parent directory.
mv stewbeet*.vsix StewBeet.vsix

# Open browser to the extension's marketplace page.
echo "https://marketplace.visualstudio.com/manage/publishers/stoupy"
echo "https://open-vsx.org/user-settings/extensions"

# Clean up the copied files.
rm icon.png LICENSE

