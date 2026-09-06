// @ts-check
"use strict";

// The bolt language configuration, which nothing exercised before.
//
// VS Code reads these regexes and never reports a bad one: a wrong indentation rule silently
// indents the wrong lines forever. They are checked here against the shapes a bolt file holds.

const { test } = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");

const ROOT = path.join(__dirname, "..");
const config = JSON.parse(fs.readFileSync(path.join(ROOT, "bolt-language-configuration.json"), "utf8"));
const manifest = JSON.parse(fs.readFileSync(path.join(ROOT, "package.json"), "utf8"));

test("the configuration is the one the manifest points at", () => {
  const bolt = manifest.contributes.languages.find((/** @type {{id: string}} */ l) => l.id === "bolt");
  assert.equal(bolt.configuration, "./bolt-language-configuration.json");
  assert.ok(fs.existsSync(path.join(ROOT, bolt.configuration)), "a dangling path leaves the language with no config at all");
});

test("comments are hash, which is what ctrl+/ inserts", () => {
  assert.equal(config.comments.lineComment, "#");
  assert.ok(!config.comments.blockComment, "bolt has no block comment, and offering one would insert nonsense");
});

test("every regex in the configuration compiles", () => {
  for (const [key, value] of Object.entries(config.indentationRules ?? {})) {
    assert.doesNotThrow(() => new RegExp(String(value)), `${key} is not a valid regex`);
  }
  for (const rule of config.onEnterRules ?? []) {
    for (const key of ["beforeText", "afterText", "previousLineText"]) {
      if (rule[key]) assert.doesNotThrow(() => new RegExp(rule[key]), `${key} is not a valid regex`);
    }
  }
});

test("a line that opens a block increases the indent", () => {
  const increase = new RegExp(config.indentationRules.increaseIndentPattern);
  for (const line of [
    "def build(self):",
    "class Ammo(Component):",
    "for i in range(1, 6):",
    "if x > 2:",
    "else:",
    "    append function PLAYER_TICK:",
    "    function self.tick_reload:",
    "execute as @a at @s:",
    "with ctx.override():",
    "    try:",
    "def build(self):  # a trailing comment must not stop it",
  ]) {
    assert.ok(increase.test(line), `should open a block: ${JSON.stringify(line)}`);
  }
});

test("an ordinary line does not increase the indent", () => {
  const increase = new RegExp(config.indentationRules.increaseIndentPattern);
  for (const line of [
    "say hello",
    "x = 3",
    "function demo:helper",
    "execute as @a run say hi",
    "from server:core import SERVER_TICK",
    "    self.reload_score -= 1",
    "",
    "    ",
    "# a comment ending in a colon:",
    'say Warning: something',
  ]) {
    assert.equal(increase.test(line), false, `should not open a block: ${JSON.stringify(line)}`);
  }
});

test("a continuation keyword decreases the indent", () => {
  const decrease = new RegExp(config.indentationRules.decreaseIndentPattern);
  for (const line of ["else:", "    elif x:", "except ValueError:", "finally:"]) {
    assert.ok(decrease.test(line), `should dedent: ${JSON.stringify(line)}`);
  }
  for (const line of ["def build(self):", "say hello", "if x:"]) {
    assert.equal(decrease.test(line), false, `should not dedent: ${JSON.stringify(line)}`);
  }
});

test("a terminating statement outdents the next line", () => {
  const rule = config.onEnterRules.find((/** @type {any} */ r) => r.action && r.action.indent === "outdent");
  const before = new RegExp(rule.beforeText);
  for (const line of ["    return x", "    pass", "        break", "    continue", "    raise ValueError()"]) {
    assert.ok(before.test(line), `should outdent after: ${JSON.stringify(line)}`);
  }
  for (const line of ["    say hello", "    returned = 3", "    passing = True"]) {
    assert.equal(before.test(line), false, `should not outdent after: ${JSON.stringify(line)}`);
  }
});

test("brackets and pairs cover what bolt actually writes", () => {
  const opens = config.brackets.map((/** @type {string[]} */ pair) => pair[0]);
  assert.deepEqual(opens.sort(), ["(", "[", "{"], "NBT, JSON and selectors all need these");

  const closing = Object.fromEntries(config.autoClosingPairs.map(
    (/** @type {{open: string, close: string}} */ p) => [p.open, p.close]));
  assert.equal(closing['"""'], '"""', "a docstring is the first thing a bolt component writes");
  assert.equal(closing["'''"], "'''");
  assert.equal(closing['"'], '"');

  const triple = config.autoClosingPairs.findIndex((/** @type {{open: string}} */ p) => p.open === '"""');
  const single = config.autoClosingPairs.findIndex((/** @type {{open: string}} */ p) => p.open === '"');
  assert.ok(triple < single, "the triple quote must be offered before the single one, or it never matches");
});
