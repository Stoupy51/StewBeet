// @ts-check
"use strict";

// What a datapack parser is shown of a bolt file.
//
// Two properties matter more than any single case. Lines stay in lockstep, so a position on
// screen is the same position in the projection, and a Python line is empty, so forwarding from
// one answers nothing. Everything else is about keeping a real bolt file parseable enough for
// the rest of its line to still be understood.

const { test } = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");

const { projectBolt, commandsOf, commandBlocks, keptPart, maskPython } = require("../src/boltlines");
const { toVirtual, toPython } = require("../src/projection");

/** The projected lines of a source, which is what Spyglass reads. @param {string} source */
function projected(source) {
  return projectBolt(source).text.split("\n");
}

/** Only the lines that survived, by 1-based line number. @param {string} source */
function kept(source) {
  return projected(source)
    .map((line, index) => (line.trim() ? [index + 1, line] : null))
    .filter(entry => entry !== null);
}

// Commands and Python

test("a command line is kept, and every line around it is blank", () => {
  const source = [
    "from lib:xp import XP",
    "",
    "class Gui:",
    "    def open(self):",
    "        say hello",
    "        item = 3",
    "        item modify entity @s weapon.mainhand voltaic:sharpen",
    "        return item",
  ].join("\n");

  assert.deepEqual(kept(source), [
    [5, "say hello"],
    [7, "item modify entity @s weapon.mainhand voltaic:sharpen"],
  ]);
});

test("the projection has exactly as many lines as the source", () => {
  const source = "say a\n\nfor i in range(3):\n    say b\n";
  assert.equal(projected(source).length, source.split("\n").length);
});

test("a command keeps its own line and loses its indentation", () => {
  const { text, table } = projectBolt("class A:\n    def b(self):\n        say deep\n");
  assert.equal(text.split("\n")[2], "say deep");
  assert.deepEqual(table.get(2), [{ start: 0, pythonWidth: 8, virtualWidth: 0 }],
    "the table is what gives the eight columns back to every range coming home");
});

test("a nesting statement is the command it opens", () => {
  assert.deepEqual(keptPart("    function voltaic:gui/open:"),
    { start: 4, text: "function voltaic:gui/open", partial: false });
  assert.deepEqual(keptPart("append function voltaic:tick:"),
    { start: 7, text: "function voltaic:tick", partial: false },
    "`append` is mecha's word, not a command's, so the projection starts at `function`");
  assert.equal(keptPart("execute as @a at @s:")?.text, "execute as @a at @s");
});

test("a macro line is kept whole, since Python starts no statement with a dollar", () => {
  assert.deepEqual(keptPart("    $say $(name)"), { start: 4, text: "$say $(name)", partial: false });
});

test("a command being typed is kept, and a Python keyword is not", () => {
  assert.deepEqual(keptPart("    exe"), { start: 4, text: "exe", partial: true },
    "completion is wanted most on the word that is not a command yet");
  assert.equal(keptPart("    pass"), null);
  assert.equal(keptPart("    return"), null);
  assert.equal(keptPart("    gui = Gui(machine)"), null);
  assert.equal(keptPart("    @cached_property"), null);
});

// A first word mecha does not know

test("a misspelled command reaches the parser, which is the only way it is ever flagged", () => {
  assert.deepEqual(keptPart("    playound minecraft:block.barrel.open block @s"),
    { start: 4, text: "playound minecraft:block.barrel.open block @s", partial: false });
  assert.equal(keptPart("    sya hello")?.text, "sya hello", "two letters swapped is what a typo mostly is");
  assert.equal(keptPart("    tellra @a hi")?.text, "tellra @a hi");
});

test("a word that is no typo of a command is left to mecha, one letter being the whole licence", () => {
  for (const line of [
    "    raw f\"say {message}\"",                          // bolt's own
    "    append function_tag name {\"values\": [entry]}",  // a mecha contrib
    "    damage_type BEHEAD_DAMAGE_TYPE {",               // a nested resource
    "    duels_map elven_cave {",                         // a project's own macro
    "    hotbar_with_slots_modify {\"function\": \"set\"}",
    "        rotated as @s",                              // a subcommand of an execute block
    "        on attacker",
    "        positioned BOX_COORDS",
    "        store result score #count temp",
  ]) {
    assert.equal(keptPart(line), null, `${line.trim()} is legal bolt, and an unknown command to a parser`);
  }
});

test("Python that starts with a lowercase word is not read as a misspelled command", () => {
  for (const line of [
    "gui = Gui(machine)",
    "machine, other = pair",
    "self.path = f\"voltaic:gui/{machine}\"",
    "value += 1",
    "machine in MACHINES",
    "helpers.write(machine)",
    "raise ValueError(machine)",
    "del gui",
    "type Alias = int",
    "gui(machine)",
    "say (event, elem.tag, elem.attrib)",
    "date in seen",
    "text is None",
  ]) {
    assert.equal(keptPart(line), null, line);
  }
});

test("the prose of a docstring is never a command, whatever its first word is", () => {
  const source = [
    "def open(self):",
    "    \"\"\" Open the interface.",
    "",
    "    list the machines it knows about",
    "    \"\"\"",
    "    say hi",
  ].join("\n");
  assert.deepEqual([...commandsOf(source).keys()], [5],
    "`list the machines` has the exact shape of a command, and the quotes are all that say it is not");
});

test("a partial command answers completion and no diagnostic", () => {
  const { masked } = projectBolt("class A:\n    exe\n");
  assert.deepEqual(masked.get(1), [{ start: 0, end: 3 }],
    "what a parser says about three letters is about how far the author has got");
});

// Blocks, which are what a keystroke reparses

test("consecutive commands are one block and a Python line starts another", () => {
  const source = [
    "function a:",        // 0
    "    say one",        // 1
    "    say two",        // 2
    "",                   // 3
    "for i in range(2):", // 4
    "    say three",      // 5
  ].join("\n");
  assert.deepEqual(commandBlocks(commandsOf(source)), [{ from: 0, to: 2 }, { from: 5, to: 5 }]);
});

test("a file of scattered commands is served as a bounded number of documents", () => {
  const source = Array.from({ length: 60 }, (_, i) => `say ${i}\nx = ${i}`).join("\n");
  const blocks = commandBlocks(commandsOf(source));
  assert.ok(blocks.length <= 8, `${blocks.length} documents is a round trip each on every pass`);
  assert.equal(blocks[0].from, 0);
  assert.equal(blocks[blocks.length - 1].to, 118);
});

test("a block projects its own run and nothing else", () => {
  const source = "say one\n\nsay two\n";
  const { text } = projectBolt(source, { from: 2, to: 2 });
  assert.deepEqual(text.split("\n"), ["", "", "say two", ""]);
});

// What the build resolved

test("a build gives a Python path back its real value, which is what makes it clickable", () => {
  const source = "for machine in MACHINES:\n    execute as @a run function gui.open\n";
  const generated = new Map([[1, "execute as @a run function voltaic:gui/furnace/open"]]);
  const { text, table, masked } = projectBolt(source, { generated });

  assert.equal(text.split("\n")[1], "execute as @a run function voltaic:gui/furnace/open");
  assert.equal(masked.get(1), undefined, "nothing is a placeholder once the build has answered");

  // The column of the `g` of `gui.open`, which has to land on the resolved path.
  const onPath = toVirtual({ line: 1, character: source.split("\n")[1].indexOf("gui.open") }, table);
  assert.equal(text.split("\n")[1].slice(onPath.character), "voltaic:gui/furnace/open");
  assert.deepEqual(toPython(onPath, table).character, source.split("\n")[1].indexOf("gui.open"));
});

test("without a build the same path is a mask, and the mask explains the line", () => {
  const { text, masked } = projectBolt("execute as @a run function gui.open\n");
  assert.equal(text.split("\n")[0], "execute as @a run function ________");
  assert.deepEqual(masked.get(0), [{ start: 27, end: 35 }]);
});

test("a resource location after `function` is left alone", () => {
  assert.equal(maskPython("function voltaic:gui/open").text, "function voltaic:gui/open");
  assert.equal(maskPython("function #voltaic:tick").text, "function #voltaic:tick");
});

// The Python a command line carries

test("a prefixed string is masked, and a command's own quotes are not", () => {
  assert.equal(maskPython('function f"{self.path}/open"').text, "function ___________________");
  assert.equal(maskPython('tellraw @a {"text":"hi"}').text, 'tellraw @a {"text":"hi"}',
    "an NBT string is the command's, and masking it would take the command with it");
});

test("a call is masked, so the rest of the line is still a command", () => {
  const masked = maskPython("execute if predicate has_item(self.item) run function ns:x").text;
  assert.equal(masked, "execute if predicate ___________________ run function ns:x");
  assert.ok(masked.endsWith("run function ns:x"), "which is the half worth keeping");
});

test("a selector is not read as a call, and a macro is not read as one either", () => {
  assert.equal(maskPython("clear @s (-self.item) 1").text, "clear @s ____________ 1");
  assert.equal(maskPython("give @s (self.output_item)").text, "give @s __________________");
  assert.equal(maskPython("$say $(name)").text, "$say $(name)");
});

test("an unbalanced parenthesis costs its own line and no more", () => {
  const masked = maskPython("give @s (self.item").text;
  assert.equal(masked, "give @s __________");
});

// Against the demo, which is a real bolt module

test("the demo's bolt module projects to its commands and nothing else", () => {
  const module = path.join(__dirname, "..", "demo", "src", "data", "voltaic", "module", "gui.bolt");
  const lines = kept(fs.readFileSync(module, "utf8"));

  assert.ok(lines.every(([, line]) => !/^\s/.test(String(line))), "every kept line starts at column 0");
  assert.ok(lines.some(([, line]) => line === "playsound minecraft:block.barrel.open block @s ~ ~ ~ 0.6 1.4"));
  assert.ok(lines.some(([, line]) => String(line).startsWith("function ___")),
    "the f-string path is masked, since no build has resolved it here");
  assert.ok(!lines.some(([, line]) => /class |def |for |= Gui/.test(String(line))),
    "and no Python reached the parser");
});

// The columns, which is what a dedent costs and the table pays back

test("a position on a dedented line survives the round trip", () => {
  const { table } = projectBolt("class A:\n    def b(self):\n        function ns:one\n");

  // Python column 17 is the `n` of `ns:one`, eight columns into a line indented by eight.
  const virtual = toVirtual({ line: 2, character: 17 }, table);
  assert.deepEqual(virtual, { line: 2, character: 9 }, "which is where Spyglass sees that token");
  assert.deepEqual(toPython(virtual, table), { line: 2, character: 17 });
});

test("a position inside the indentation lands at the start of the command", () => {
  const { table } = projectBolt("class A:\n    say hi\n");
  assert.deepEqual(toVirtual({ line: 1, character: 2 }, table), { line: 1, character: 0 });
});
