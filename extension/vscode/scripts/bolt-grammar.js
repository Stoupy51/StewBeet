// @ts-check
"use strict";

// The root commands the Bolt grammar colours as commands, regenerated from the command tree mecha ships
// for a Minecraft version. A line the last build compiled is a command whatever this list says, so
// the list only decides colours and the guess made before any build.
//
//   node scripts/bolt-grammar.js <mecha>/resources/26_3.json
//
// `python -c "import mecha, os; print(os.path.dirname(mecha.__file__))"` prints where mecha is installed.

const fs = require("fs");
const path = require("path");

/** Root commands bolt reads as Python, so they open no command line. */
const PYTHON_KEYWORDS = new Set(["return"]);

const GRAMMAR = path.join(__dirname, "..", "syntaxes", "bolt.tmLanguage.json");

/** The alternation of root commands inside the command-statement rule. */
const ALTERNATION = /(\(\?=\^\(\[ \\t\]\*\)\()([a-z0-9|_-]+)(\))/;

const [treePath] = process.argv.slice(2);
if (!treePath) throw new Error("usage: node scripts/bolt-grammar.js <path to a mecha command tree, e.g. resources/26_3.json>");

const tree = JSON.parse(fs.readFileSync(treePath, "utf8"));
const commands = Object.keys(tree.children)
  .filter(name => !PYTHON_KEYWORDS.has(name))
  .sort((a, b) => b.length - a.length || a.localeCompare(b));

const grammar = JSON.parse(fs.readFileSync(GRAMMAR, "utf8"));
const rule = grammar.repository["command-statement"];
if (!ALTERNATION.test(rule.begin)) throw new Error("the command-statement rule no longer opens with the alternation this script rewrites");
const previous = new Set(ALTERNATION.exec(rule.begin)?.[2].split("|"));
rule.begin = rule.begin.replace(ALTERNATION, `$1${commands.join("|")}$3`);
fs.writeFileSync(GRAMMAR, `${JSON.stringify(grammar, null, 2)}\n`);

const added = commands.filter(name => !previous.has(name));
const removed = [...previous].filter(name => !commands.includes(name));
console.log(`${commands.length} root commands, added: ${added.join(", ") || "none"}, removed: ${removed.join(", ") || "none"}`);
