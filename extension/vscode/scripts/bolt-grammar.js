// @ts-check
"use strict";

// The root commands the Bolt grammar colours as commands, regenerated from every command tree mecha ships.
// The union covers every Minecraft version a project may target, so `replaceitem` stays a command in a
// 1.16 pack. A line the last build compiled is a command whatever this list says, so the list only
// decides colours and the guess made before any build. `.github/workflows/bolt-grammar.yml` runs it
// against each new mecha release.
//
//   node scripts/bolt-grammar.js <mecha>/resources
//
// `python -c "import mecha, os; print(os.path.dirname(mecha.__file__))"` prints where mecha is installed.

const fs = require("fs");
const path = require("path");

/** Root commands bolt reads as Python, so they open no command line. */
const PYTHON_KEYWORDS = new Set(["return"]);

const GRAMMAR = path.join(__dirname, "..", "syntaxes", "bolt.tmLanguage.json");

/** The alternation of root commands inside the command-statement rule. */
const ALTERNATION = /(\(\?=\^\(\[ \\t\]\*\)\()([a-z0-9|_-]+)(\))/;

/** A command tree, named after its version (`1_21_5.json`, `26_3.json`), beside mecha's other resources. */
const TREE_FILE = /^\d+(_\d+)*\.json$/;

const [resources] = process.argv.slice(2);
if (!resources) throw new Error("usage: node scripts/bolt-grammar.js <mecha>/resources");

const trees = fs.readdirSync(resources).filter(name => TREE_FILE.test(name));
if (trees.length === 0) throw new Error(`no command tree in ${resources}`);
const roots = new Set(trees.flatMap(name => Object.keys(JSON.parse(fs.readFileSync(path.join(resources, name), "utf8")).children)));
const commands = [...roots]
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
console.log(`${commands.length} root commands from ${trees.length} trees, added: ${added.join(", ") || "none"}, removed: ${removed.join(", ") || "none"}`);
