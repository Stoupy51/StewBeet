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


// Every head mecha knows, not just the handful worth naming
//
// These assert on `meta.command.bolt`, the scope this grammar's own rule opens, rather than on
// the keyword colour inside it. Colouring the head is the embedded mcfunction grammar's job, and
// it does not handle a hyphen: `ban-ip` is a command line whose head reads as a name. That is a
// limitation of the vendored grammar, not of the rule that decides what a command line is.

/** Either rule that claims a line as a command. `function` belongs to the nesting rule, which
 *  runs first because it offers the argument to Python when it is not a resource location. */
const COMMAND_SCOPES = ["meta.command.bolt", "meta.nesting.bolt"];
const opensCommand = token => COMMAND_SCOPES.some(scope => token.scopes.includes(scope));

boltTest(
  "every root command literal opens a command",
  // Built from the grammar's own set, so this cannot drift from what the rule matches.
  (() => {
    const fs = require("node:fs");
    const path = require("node:path");
    const grammar = JSON.parse(fs.readFileSync(
      path.join(__dirname, "..", "syntaxes", "bolt.tmLanguage.json"), "utf8"));
    const heads = grammar.repository["command-statement"].begin
      .match(/\((?:[a-z-]+\|)+[a-z-]+\)/)[0].slice(1, -1).split("|");
    return heads.map(head => `${head} argument`).join("\n") + "\n";
  })(),
  lines => {
    const missed = lines.filter(l => l.length).filter(l => !opensCommand(l[0]));
    assert.deepEqual(missed.map(l => l[0].text), [],
      "these heads are in the generated set but their line does not open a command");
  },
);

boltTest(
  "a hyphenated head still opens a command line",
  "ban-ip someone\nsave-all\npardon-ip someone\n",
  lines => {
    for (const line of lines.filter(l => l.length)) {
      assert.ok(opensCommand(line[0]),
        `${line[0].text} did not open a command, so the alternation cut it short`);
    }
  },
);

boltTest(
  "a word that merely starts with a head is not a command",
  "saying hello\nfunctional = 3\nitemise()\ntagged: int = 1\n",
  lines => {
    for (const line of lines.filter(l => l.length)) {
      assert.equal(opensCommand(line[0]), false, `${line[0].text} must not open a command`);
    }
  },
);

boltTest(
  "a head indented inside nested blocks is still a command",
  "class A:\n    def build(self):\n        if x:\n            for i in y:\n                summon marker ~ ~ ~\n",
  lines => assert.ok(scopesOf(lines, "summon")?.includes(COMMAND),
    "indentation depth must not matter, since bolt nests freely"),
);
