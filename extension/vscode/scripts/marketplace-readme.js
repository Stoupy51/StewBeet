// @ts-check
"use strict";

// The marketplace renders no video and leaves a bare user-attachments URL as a link, so the copy it
// is packaged with keeps that link and puts the GIF of the same take under it. Generated rather than
// kept by hand, because a README the maintainer never reads is a README that drifts.
//
//   node scripts/marketplace-readme.js && vsce package --readme-path README.marketplace.md

const fs = require("fs");
const path = require("path");

const RAW = "https://raw.githubusercontent.com/Stoupy51/StewBeet/refs/heads/main/extension/vscode/images";

/** Each recording, by the URL that embeds it on GitHub. */
const RECORDINGS = [
  {
    url: "https://github.com/user-attachments/assets/18b87420-9b65-4971-8c51-e72eae709e65",
    gif: "stewbeet.gif",
    alt: "Completion and navigation inside a block",
  },
  {
    url: "https://github.com/user-attachments/assets/57fd9d18-1643-45bc-8257-4942865c9be4",
    gif: "bolt.gif",
    alt: "The Bolt language, with completion and ctrl+click on its commands",
  },
  {
    url: "https://github.com/user-attachments/assets/92a49027-a47a-49f5-aa6a-2236f975bc25",
    gif: "beet.gif",
    alt: "Errors and navigation in a plain beet plugin",
  },
];

const source = path.join(__dirname, "..", "README.md");
const target = path.join(__dirname, "..", "README.marketplace.md");

let text = fs.readFileSync(source, "utf8");
for (const { url, gif, alt } of RECORDINGS) {
  if (!text.includes(url)) throw new Error(`${url} is gone from README.md, so ${gif} would be dropped without a word`);
  text = text.replace(url, `[Watch this as a video, in better quality](${url})\n\n![${alt}](${RAW}/${gif})`);
}

fs.writeFileSync(target, text);
console.log(`wrote ${path.basename(target)} with ${RECORDINGS.length} recordings swapped for GIFs`);
