#!/bin/bash

# Build the VSCode extension package using `vsce`.
cd vscode
cp ../../docs/stewbeet_1024x1024.png ./icon.png
cp ../../python_package/LICENSE ./LICENSE

# The marketplace renders no video and leaves a bare user-attachments URL as a link, so it is
# packaged with a copy of the README whose three recordings are the GIFs under images/.
node scripts/marketplace-readme.js
vsce package --no-dependencies --readme-path README.marketplace.md

# Move the generated .vsix file to the parent directory.
mv stewbeet*.vsix StewBeet.vsix

# Open browser to the extension's marketplace page.
echo "https://marketplace.visualstudio.com/manage/publishers/stoupy"
echo "https://open-vsx.org/user-settings/extensions"

# Clean up the copied and generated files.
rm icon.png LICENSE README.marketplace.md

