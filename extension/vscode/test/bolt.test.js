// @ts-check
"use strict";

// Tokenization tests for the `bolt` grammar, run through the same TextMate engine VS Code uses.
// Bolt is Python with command statements interleaved, so almost every test here is about the line
// between the two: a head that is also an identifier, a head that is also a keyword, and an
// argument that is a Python expression rather than a resource location.
//
// The engine skips when MagicPython or the npm dev dependencies are missing, and a run that
// reports skips has verified nothing.

const { test } = require("node:test");
const assert = require("node:assert/strict");
const { load, scopesOf } = require("./textmate.js");

const engine = load("source.bolt");

/** Run `body` with a tokenizer, or skip when the engine could not be built. */
function boltTest(name, source, body) {
  test(name, async t => {
    const ready = await engine;
    if (typeof ready === "string") return t.skip(ready);
    body(ready.tokenize(source), assert);
  });
}

const COMMAND = "keyword.control.flow.mcfunction";

// Python stays Python

boltTest(
  "a class and a def keep Python's scopes",
  "class Ammo(Component):\n    def build(self):\n        pass\n",
  lines => {
    assert.ok(scopesOf(lines, "class")?.includes("storage.type.class.python"));
    assert.ok(scopesOf(lines, "def")?.includes("storage.type.function.python"));
    assert.ok(scopesOf(lines, "Ammo")?.includes("entity.name.type.class.python"));
  },
);

boltTest(
  "a plain Python import is left alone",
  "from functools import cached_property\n",
  lines => {
    assert.ok(scopesOf(lines, "from")?.includes("keyword.control.import.python"));
    assert.equal(scopesOf(lines, "functools")?.includes("entity.name.function.mcfunction"), false,
      "a dotted Python module must not be read as a resource location");
  },
);

// Commands are commands

boltTest(
  "a say statement is a command",
  "say hello\n",
  lines => assert.ok(scopesOf(lines, "say")?.includes(COMMAND)),
);

boltTest(
  "a command keeps its selector and its numbers",
  "setblock -1 2 3 stone\nexecute as @a run say hi\n",
  lines => {
    assert.ok(scopesOf(lines, "setblock")?.includes(COMMAND), "a negative coordinate is not Python");
    assert.ok(scopesOf(lines, "@a")?.includes("support.class.mcfunction"));
  },
);

boltTest(
  "an indented command inside a def is still a command",
  "def build(self):\n    scoreboard players add #x obj 1\n",
  lines => assert.ok(scopesOf(lines, "scoreboard")?.includes(COMMAND)),
);

// The collisions, which are the whole difficulty

boltTest(
  "return is Python, never the command",
  "return x\n",
  lines => {
    assert.ok(scopesOf(lines, "return")?.includes("keyword.control.flow.python"));
    assert.equal(scopesOf(lines, "return")?.includes(COMMAND), false);
  },
);

boltTest(
  "a head used as an assignment target is Python",
  "item = 3\ntime -= 1\ndata = {}\n",
  lines => {
    for (const name of ["item", "time", "data"]) {
      assert.equal(scopesOf(lines, name)?.includes(COMMAND), false, `${name} was assigned to, so it is a name`);
    }
    assert.ok(scopesOf(lines, "=")?.includes("keyword.operator.assignment.python"));
    assert.ok(scopesOf(lines, "-=")?.includes("keyword.operator.assignment.python"));
  },
);

boltTest(
  "the same head followed by an argument is the command",
  "item modify entity @s weapon.mainhand foo\n",
  lines => assert.ok(scopesOf(lines, "item")?.includes(COMMAND)),
);

boltTest(
  "a head used as a call or an attribute is Python",
  "list(x)\ntime.sleep(1)\n",
  lines => {
    assert.equal(scopesOf(lines, "list")?.includes(COMMAND), false);
    assert.equal(scopesOf(lines, "time")?.includes(COMMAND), false);
  },
);

boltTest(
  "a head used as an annotated name is Python",
  "test: int = 3\n",
  lines => assert.equal(scopesOf(lines, "test")?.includes(COMMAND), false),
);

// Bolt's own forms

boltTest(
  "a namespaced import colours the resource location",
  "from server:core import SERVER_TICK\n",
  lines => {
    assert.ok(scopesOf(lines, "server:core")?.includes("entity.name.function.mcfunction"));
    assert.ok(scopesOf(lines, "import")?.includes("keyword.control.import.python"));
  },
);

boltTest(
  "a relative import colours its target",
  "from ./type import Component\n",
  lines => assert.ok(scopesOf(lines, "./type")?.includes("entity.name.function.mcfunction")),
);

boltTest(
  "a bare namespaced import colours its target",
  "import demo:helper as _\n",
  lines => assert.ok(scopesOf(lines, "demo:helper")?.includes("entity.name.function.mcfunction")),
);

boltTest(
  "an append nesting head is a command on both words",
  "append function PLAYER_TICK:\n",
  lines => {
    assert.ok(scopesOf(lines, "append")?.includes(COMMAND));
    assert.ok(scopesOf(lines, "function")?.includes(COMMAND));
  },
);

boltTest(
  "a nesting argument that is a Python expression keeps Python's scopes",
  "function self.tick_reload:\n    say hi\n",
  lines => {
    assert.ok(scopesOf(lines, "function")?.includes(COMMAND));
    assert.ok(scopesOf(lines, "self")?.includes("variable.language.special.self.python"),
      "the argument is an attribute access, not a resource location");
  },
);

boltTest(
  "a nesting argument that is a resource location is one",
  "function demo:helper/inner:\n    say hi\n",
  lines => assert.ok(scopesOf(lines, "demo:helper/inner")?.includes("entity.name.function.mcfunction")),
);

boltTest(
  "a call inside a command argument is Python",
  "execute if predicate has_item_predicate(self.item.conditional_dict()) run function demo:x\n",
  lines => {
    assert.ok(scopesOf(lines, "execute")?.includes(COMMAND));
    assert.ok(scopesOf(lines, "has_item_predicate")?.includes("entity.name.function.python"),
      "a bare `(` after a word never happens in mcfunction, so it is a call");
    assert.ok(scopesOf(lines, "conditional_dict")?.some(s => s.endsWith(".python")),
      "and the nested call is Python too");
  },
);

// Recovery, which is what a runaway rule breaks

boltTest(
  "a command does not swallow the Python that follows it",
  "say hello\nx = 3\n",
  lines => {
    assert.ok(scopesOf(lines, "say")?.includes(COMMAND));
    assert.ok(scopesOf(lines, "=")?.includes("keyword.operator.assignment.python"),
      "the command block must close at the end of its line");
  },
);

boltTest(
  "an unbalanced parenthesis costs one line, not the rest of the file",
  "say hello foo(bar\nclass Later:\n    pass\n",
  lines => assert.ok(scopesOf(lines, "class")?.includes("storage.type.class.python"),
    "the call rule must end at the line end as well as at its closing paren"),
);

boltTest(
  "a multi-line resource command recovers when its braces balance",
  'advancement demo:x {\n    "criteria": {}\n}\nclass Later:\n    pass\n',
  lines => assert.ok(scopesOf(lines, "class")?.includes("storage.type.class.python")),
);

// Step D contributes a grammar and an id, and nothing else

test("nothing in the extension selects a bolt document", () => {
  const fs = require("node:fs");
  const path = require("node:path");
  const root = path.join(__dirname, "..");
  const manifest = JSON.parse(fs.readFileSync(path.join(root, "package.json"), "utf8"));

  assert.ok(!manifest.activationEvents.includes("onLanguage:bolt"),
    "a grammar needs no activation, and waking up for a file we do nothing with is pure cost");
  assert.ok(manifest.contributes.languages.some(l => l.id === "bolt"), "the language id is the deliverable");
  assert.ok(!manifest.contributes.languages.some(l => l.id === "mcfunction"),
    "FR-015: ownership is partitioned by file, and Spyglass owns mcfunction");

  const sources = fs.readdirSync(path.join(root, "src")).filter(f => f.endsWith(".js"));
  for (const file of sources) {
    const text = fs.readFileSync(path.join(root, "src", file), "utf8");
    assert.ok(!/language:\s*["']bolt["']/.test(text), `${file} registers a provider for bolt`);
    assert.ok(!/languageId\s*[=!]==\s*["']bolt["']/.test(text), `${file} reacts to a bolt document`);
  }
});
