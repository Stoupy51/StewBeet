#!/bin/bash

# Build the VSCode extension package using `vsce`.
cd vscode
cp ../../docs/stewbeet_256x256.png ./icon.png
cp ../../python_package/LICENSE ./LICENSE
vsce package --no-dependencies

# Move the generated .vsix file to the parent directory.
mv *.vsix ../

# Publish the extension to the marketplace using `vsce publish`.
#vsce publish --no-dependencies

# Clean up the copied files.
rm icon.png LICENSE

