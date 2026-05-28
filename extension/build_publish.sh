#!/bin/bash

# Build the VSCode extension package using `vsce`.
cd vscode
vsce package --no-dependencies

# Move the generated .vsix file to the parent directory.
mv *.vsix ../

# Publish the extension to the marketplace using `vsce publish`.
# TODO

