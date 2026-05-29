#!/bin/bash

# Build the VSCode extension package using `vsce`.
cd vscode
cp ../../docs/stewbeet_256x256.png ./icon.png
cp ../../python_package/LICENSE ./LICENSE
vsce package --no-dependencies
rm icon.png LICENSE

# Move the generated .vsix file to the parent directory.
mv *.vsix ../

# Publish the extension to the marketplace using `vsce publish`.
# TODO

