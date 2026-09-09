// @ts-check
"use strict";

// Block detection and colouring against two real StewBeet projects.
//
// machines.test.js takes SimplEnergy's machine setup apart shape by shape. This file covers what
// that one does not reach: StardustFragment, which is three times the size and older in style,
// and the helpers other than `write_function`. Each case cites the file and line it came from.
//
// The two sweeps at the end run over whatever of those projects is on this machine, and skip
// when neither is. They are a net rather than a assertion about any one line: a change that
// breaks detection wholesale, or a grammar rule that never closes, shows up there first.

const { test } = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");

const { findBlockOffsets, findInterpolationSpans } = require("../src/blocks");
const { load, scopesOf } = require("./textmate.js");

const COMMAND = "keyword.control.flow.mcfunction";

const PROJECTS = [
  ["SimplEnergy", "d:/advanced_desktop/SimplEnergy/src"],
  ["StardustFragment", "d:/advanced_desktop/StardustFragment/src"],
];

/** The commands a block covers, which is what a projection hands to the language server. */
function contentsOf(source) {
  return findBlockOffsets(source).map(b => source.slice(b.contentStart, b.contentEnd));
}

/** @param {string} dir @returns {string[]} */
function pythonUnder(dir) {
  if (!fs.existsSync(dir)) return [];
  return fs.readdirSync(dir, { withFileTypes: true }).flatMap(entry => {
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) return entry.name === "__pycache__" ? [] : pythonUnder(full);
    return entry.name.endsWith(".py") ? [full] : [];
  });
}

// StardustFragment, which uses raw strings and macros that SimplEnergy does not

test("snipers.py:133 a raw one-line string holding a macro line", () => {
  const source = 'write_function(f"{ns}:utils/snipers/block_particles", r"""$particle block{block_state:"$(block)"} $(x) $(y) $(z) 0.1 0.1 0.1 1 10 force @a[distance=..128]""")';
  const [content] = contentsOf(source);
  assert.ok(content.startsWith("$particle"), `the whole macro line is the block, got ${JSON.stringify(content)}`);
  assert.ok(content.endsWith("@a[distance=..128]"),
    "the closing quotes sit on the same line, and the block must stop at them");
});

test("snipers.py:133 a raw string has no interpolations, whatever its braces look like", () => {
  const source = 'write_function("ns:x", r"""$particle block{block_state:"$(block)"} $(x) 1 force @a""")';
  const [block] = findBlockOffsets(source);
  assert.deepEqual(findInterpolationSpans(source, block), [],
    "`r` means no f-string, so `{block_state:...}` is NBT and masking it would corrupt the command");
});

test("remaining.py:128 a raw multi-line macro carrying JSON", () => {
  const source = [
    'write_function(f"{ns}:utils/use_durability/item_modifier", r"""',
    '$item modify entity @s $(slot) {"function": "minecraft:set_damage","damage": $(use_durability),"add": true}',
    '""")',
  ].join("\n");
  const [content] = contentsOf(source);
  assert.ok(content.includes('"minecraft:set_damage"'),
    "double quotes inside a triple-double-quoted string are content, not the end of it");
  assert.ok(!content.includes("write_function"), "and the call must not leak into the block");
});

test("remaining.py:257 a one-line block whose JSON carries quotes and an escape", () => {
  const source = 'write_function(f"{ns}:utils/home_travel_staff/fail", """tellraw @s {"text":"Teleportation cancelled!","color":"red"}\\nplaysound entity.villager.no ambient @s""")';
  const [content] = contentsOf(source);
  assert.ok(content.startsWith("tellraw @s"), content);
  assert.ok(content.includes('"color":"red"'), "the JSON is part of the command");
  assert.ok(content.includes("playsound"), "the literal \\n escape does not end the block");
});

test("ultimate_dragon.py:48 a single-quoted f-string body with a selector interpolation", () => {
  const source = 'write_function(f"{ns}:mobs/remove_bossbars", f"execute unless entity @e[tag={ns}.dragon] run bossbar set {ns}:ultimate_dragon players")';
  const [content] = contentsOf(source);
  assert.equal(content, "execute unless entity @e[tag={ns}.dragon] run bossbar set {ns}:ultimate_dragon players");

  const [block] = findBlockOffsets(source);
  const spans = findInterpolationSpans(source, block);
  assert.equal(spans.length, 2, `both {ns} uses are interpolations, got ${JSON.stringify(spans)}`);
  assert.equal(source.slice(spans[0].start, spans[0].end), "{ns}",
    "the one inside the selector bracket counts too");
});

test("ultimate_dragon.py:51 a helper that is not a write_ function is left alone", () => {
  const source = 'write_advancement(f"{ns}:technical/used_lingering_potion", {\n    "criteria": {}\n})';
  assert.deepEqual(findBlockOffsets(source), [],
    "write_advancement takes JSON, and reading it as commands would colour every advancement");
});

test("dimensions.py:44 write_versioned_function takes a bare name as its path", () => {
  const source = 'write_versioned_function("minute", f"""\n# Make sure dimensions are still built\nfunction {ns}:dimensions/ensure_built\n""")';
  const [content] = contentsOf(source);
  assert.ok(content.includes("function {ns}:dimensions/ensure_built"),
    "the first argument is a version name rather than a resource location, and is still skipped");
});

// SimplEnergy, for the helpers whose content is the first argument

test("remaining.py:29 write_load_file puts the commands first, with a keyword argument after", () => {
  const source = [
    'write_load_file(f"""',
    "scoreboard objectives add {ns}.right_click minecraft.used:minecraft.warped_fungus_on_a_stick",
    "team modify {ns}.green color green",
    '""", prepend=True)',
  ].join("\n");
  const [content] = contentsOf(source);
  assert.ok(content.includes("scoreboard objectives add"), content);
  assert.ok(!content.includes("prepend"), "the trailing keyword argument is Python, not a command");
});

test("remaining.py:40 write_tick_file is a first-argument helper too", () => {
  const source = 'write_tick_file(f"""\n# Increase every tick the elevator time\nscoreboard players add #elevator_time {ns}.data 1\n""")';
  assert.equal(findBlockOffsets(source).length, 1);
});

test("pulverizer.py:106 a function joined out of a list appended to in a loop", () => {
  const source = [
    "\tprogressions_gui: list[str] = []",
    "\tfor i, progression in enumerate(progressions_cmd):",
    "\t\tif i == 0:",
    '\t\t\tprogressions_gui.append(f"$execute if score #progression {ns}.data matches ..0 run item replace block ~ ~ ~ container.$(slot) with {CUSTOM_ITEM_VANILLA}")',
    "\t\telse:",
    '\t\t\tprogressions_gui.append(f"$execute if score #progression {ns}.data matches {gui_min}.. run item replace block ~ ~ ~ container.$(slot) with {CUSTOM_ITEM_VANILLA}")',
    '\twrite_function(funcs["gui_progression"], "\\n".join(progressions_gui))',
  ].join("\n");

  const contents = contentsOf(source);
  assert.equal(contents.length, 2, `both appended commands, got ${JSON.stringify(contents)}`);
  assert.ok(contents.every(c => c.startsWith("$execute if score #progression")), contents.join(" | "));
  assert.ok(!contents.some(c => c === "\\n"), "the join separator is not one of the commands");
});

test("ultimate_dragon.py:170 a list literal joined inside the call itself", () => {
  const source = [
    'write_function(f"{ns}:mobs/ultimate_dragon/summon_end_crystals", "\\n".join([',
    '\tf"execute in {ns}:ultimate run summon minecraft:end_crystal {coords}"',
    "\tfor coords in [",
    '\t\t"12 76 -40", "33 103 -25"',
    "\t]",
    "]))",
  ].join("\n");

  assert.deepEqual(contentsOf(source), ["execute in {ns}:ultimate run summon minecraft:end_crystal {coords}"],
    "the comprehension's element is the command; the coordinates it loops over and the separator are not");
});

test("remaining.py:45 a version name that looks like a path is still a version name", () => {
  const source = 'write_versioned_function("tick_2", f"""\nexecute as @a[tag=!global.ignore.gui] at @s run function {ns}:utils/passive_offhand\n""")';
  const [content] = contentsOf(source);
  assert.ok(content.trim().startsWith("execute as @a"), content);
});

// The same lines, through the grammar

test("a raw block is coloured, like an f-string one", async t => {
  const engine = await load("source.python");
  if (typeof engine === "string") return t.skip(engine);

  for (const prefix of ["", "f", "r", "rf", "fr"]) {
    const lines = engine.tokenize(`write_function("ns:x", ${prefix}"""\nsay hello\n""")\n`);
    assert.ok(scopesOf(lines, "say")?.includes(COMMAND),
      `a ${prefix || "plain"}-prefixed block lost its colours, and blocks.js accepts all of these`);
  }
});

test("a macro line inside a raw block keeps the command colour", async t => {
  const engine = await load("source.python");
  if (typeof engine === "string") return t.skip(engine);

  const lines = engine.tokenize('write_function("ns:x", r"""\n$particle block{block_state:"$(block)"} $(x) 1 force @a\n""")\n');
  const dollar = lines.flat().find(token => token.text === "$");
  assert.ok(dollar, "the macro marker should be tokenized");
  assert.ok(dollar.scopes.some(s => s.includes("mcfunction")),
    "a macro line is still mcfunction, not Python");
});

// Sweeps over whatever is on this machine

test("every block found in both projects is well formed", t => {
  const files = PROJECTS.flatMap(([, dir]) => pythonUnder(dir));
  if (files.length === 0) return t.skip("neither project is on this machine");

  let total = 0;
  for (const file of files) {
    const text = fs.readFileSync(file, "utf8");
    const blocks = findBlockOffsets(text);
    total += blocks.length;

    let previousEnd = -1;
    for (const block of blocks) {
      const where = `${path.basename(file)} at ${block.start}`;
      assert.ok(block.start < block.contentStart, `${where}: content starts before the quote`);
      assert.ok(block.contentStart <= block.contentEnd, `${where}: content ends before it starts`);
      assert.ok(block.contentEnd < block.end, `${where}: content runs past the closing quote`);
      assert.ok(block.end <= text.length, `${where}: block runs past the file`);
      assert.ok(block.start >= previousEnd, `${where}: blocks overlap, so a projection would double-write`);
      previousEnd = block.end;
    }
  }
  assert.ok(total > 200, `expected the corpus to hold hundreds of blocks, found ${total}`);
});

test("no rule of ours runs away over a whole file", async t => {
  const engine = await load("source.python");
  if (typeof engine === "string") return t.skip(engine);

  const files = PROJECTS.flatMap(([, dir]) => pythonUnder(dir));
  if (files.length === 0) return t.skip("neither project is on this machine");

  const worst = [];
  for (const file of files) {
    const lines = engine.tokenize(fs.readFileSync(file, "utf8"));
    // Only the scopes this extension owns. MagicPython's `meta.function-call.python` legitimately
    // covers 200 consecutive lines in these projects, where a definitions file passes one dict
    // literal to one call, and policing that would be policing Python's grammar rather than ours.
    let run = 0, longest = 0, scope = "";
    let previous = null;
    for (const line of lines) {
      const ours = line.length
        ? line[0].scopes.find(s => s.includes("mcfunction") || s.includes("stewbeet")) ?? null
        : null;
      run = ours && ours === previous ? run + 1 : 1;
      previous = ours;
      if (run > longest) { longest = run; scope = String(ours); }
    }
    if (longest >= 120) worst.push(`${path.basename(file)}: ${longest} lines in ${scope}`);
  }
  assert.deepEqual(worst, [], "a rule whose end never matches turns the rest of a file into one colour");
});

test("a command inside a block is coloured somewhere in every file that has one", async t => {
  const engine = await load("source.python");
  if (typeof engine === "string") return t.skip(engine);

  const files = PROJECTS.flatMap(([, dir]) => pythonUnder(dir));
  if (files.length === 0) return t.skip("neither project is on this machine");

  const silent = [];
  for (const file of files) {
    const text = fs.readFileSync(file, "utf8");
    if (findBlockOffsets(text).length === 0) continue;
    const coloured = engine.tokenize(text).flat()
      .some(token => token.scopes.some(scope => scope.endsWith(".mcfunction")));
    if (!coloured) silent.push(path.basename(file));
  }
  assert.deepEqual(silent, [],
    "these files hold blocks the finder sees and the grammar colours nothing in, so the two disagree");
});


// The showcase project, which ships in this repo and is what the README's recordings come from

/** 1-based line of an offset, which is what demo/README.md's takes name. @param {string} text @param {number} offset */
function lineOf(text, offset) {
  return text.slice(0, offset).split("\n").length;
}

test("the demo project holds the blocks its recording script names", () => {
  const demo = path.resolve(__dirname, "..", "demo", "src");
  /** Call line of every block, as demo/README.md tells the recorder to find them. */
  const calls = (name) => {
    const text = fs.readFileSync(path.join(demo, name), "utf8");
    return findBlockOffsets(text).map(block => lineOf(text, block.callStart));
  };

  // Two of machines.py's blocks are the variable and the `+=` onto it, both consumed by line 35.
  assert.deepEqual(calls("machines.py"), [12, 23, 35, 35]);
  // turbine.py line 22 is a `Function([...])`, whose two entries are two blocks on one call.
  assert.deepEqual(calls("turbine.py"), [9, 16, 22, 22, 26]);
});
