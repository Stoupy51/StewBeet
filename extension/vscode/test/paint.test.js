// @ts-check
"use strict";

const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");
const { findBlockOffsets } = require("../src/blocks");
const { createEngine, paintsOf, styleOf, parseJsonc, readTheme, customRules, themeRules } = require("../src/paint");
const { findPythonGrammar } = require("./textmate");

const SOURCE = [
  "@dataclass",
  "class Bonus:",
  "    name: str",
  "    commands: McFunction",
  "",
  'Bonus(name="speed", commands="""',
  "say hi",
  '""")',
  'write_function("a:b", """',
  "say covered",
  '""")',
].join("\n");

test("a block only the whole file reveals is painted as the grammar paints the others, and those are left alone", async (t) => {
  const python = findPythonGrammar();
  if (!python) return t.skip("no VS Code install found to read MagicPython from");
  const { vsctm, registry } = await createEngine(python);
  registry.setTheme({ settings: [
    { settings: { foreground: "#111111" } },
    { scope: "keyword.control.flow.mcfunction", settings: { foreground: "#FF0000", fontStyle: "italic" } },
  ] });
  const tokenizer = { vsctm, python: await registry.loadGrammar("source.python") };

  const paints = paintsOf(tokenizer, SOURCE, findBlockOffsets(SOURCE));
  assert.deepEqual([...new Set(paints.map(paint => paint.line))], [6], "the Bonus field, and not the write_function block the grammar colours");
  const say = paints.find(paint => paint.from === 0);
  assert.deepEqual(say && { to: say.to, ...styleOf(say.metadata, registry.getColorMap()) }, { to: 3, color: "#FF0000", fontStyle: 1 });
  assert.ok(paints.every(paint => paint.from >= 0 && paint.to <= "say hi".length), "nothing outside the commands, quotes included");
});

test("a theme file may carry comments and trailing commas", () => {
  assert.deepEqual(parseJsonc('{ "a": [1, 2,], // note\n "b": "x//y,]", /* c */ }'), { a: [1, 2], b: "x//y,]" });
});

test("a theme's include chain comes first, and a tokenColors path is read", () => {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), "stewbeet-theme-"));
  fs.writeFileSync(path.join(root, "base.json"), JSON.stringify({ colors: { "editor.foreground": "#010101" }, tokenColors: [{ scope: "a", settings: {} }] }));
  fs.writeFileSync(path.join(root, "rules.json"), JSON.stringify({ tokenColors: [{ scope: "b", settings: {} }] }));
  fs.writeFileSync(path.join(root, "theme.json"), '{ "include": "./base.json", "tokenColors": "./rules.json", // own\n }');
  const theme = readTheme(path.join(root, "theme.json"), () => ({}));
  assert.deepEqual({ scopes: theme.rules.map(rule => rule.scope), colors: theme.colors }, { scopes: ["a", "b"], colors: { "editor.foreground": "#010101" } });
  fs.rmSync(root, { recursive: true, force: true });
});

test("the author's customizations follow the theme's rules, general ones first, as VS Code applies them", () => {
  const custom = customRules({
    keywords: "#AAAAAA",
    textMateRules: [{ scope: "x", settings: { foreground: "#BBBBBB" } }],
    "[Default Dark Modern]": { comments: "#000000" },
    "[*Modern]": { textMateRules: [{ scope: "y", settings: { foreground: "#CCCCCC" } }] },
    "[Monokai][Dark*]": { textMateRules: [{ scope: "z", settings: { foreground: "#DDDDDD" } }] },
  }, "Dark Modern");
  assert.deepEqual(custom.map(rule => [rule.scope, rule.settings.foreground]), [
    ["keyword - keyword.operator", "#AAAAAA"], ["keyword.control", "#AAAAAA"], ["storage", "#AAAAAA"], ["storage.type", "#AAAAAA"],
    ["x", "#BBBBBB"], ["y", "#CCCCCC"], ["z", "#DDDDDD"],
  ], "a section named after the theme's id before VS Code renamed it applies to nothing, in VS Code as here");

  const rules = themeRules({ rules: [{ scope: "a", settings: {} }, { settings: {} }], colors: {} }, "vs", custom, {});
  assert.deepEqual(rules[0].settings.foreground, "#333333", "VS Code's own default for a light theme that sets none");
  assert.equal(rules.length, 1 + 1 + custom.length, "a rule with no scope is the theme's default, which VS Code ignores");
});
