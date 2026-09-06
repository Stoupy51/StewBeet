// @ts-check
"use strict";

// Block detection against the shapes a real project actually writes.
//
// Every case below is lifted from SimplEnergy's `src/utils/machines.py`, which is 328 lines of
// StewBeet in production use and exercises more of the finder than anything written to order:
// paths that are call chains, paths that are f-string subscripts, NBT braces doubled inside an
// f-string, annotated lists built by appending, and plain lists that must be left alone.
//
// The cited line numbers are where each shape sits in that file, so a case that stops making
// sense can be checked against the original.

const { test } = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");

const { findBlockOffsets, findInterpolationSpans } = require("../src/blocks");
const { load, scopesOf } = require("./textmate.js");

const COMMAND = "keyword.control.flow.mcfunction";

/** The commands a block covers, which is what a projection hands to the language server. */
function contentsOf(source) {
  return findBlockOffsets(source).map(b => source.slice(b.contentStart, b.contentEnd));
}

// Paths, which is where skipFirstArg earns its keep

test("machines.py:29 a path that is a method call on a constructor", () => {
  const source = 'write_function(BlockFunctions("solar_panel").second, "say hi")';
  assert.deepEqual(contentsOf(source), ["say hi"],
    "the path argument holds quotes and parentheses, and skipping it must not stop at either");
});

test("machines.py:30 a call-chain path with an inline triple-quoted body", () => {
  const source = [
    'write_function(BlockFunctions("solar_panel").place_secondary, """',
    "# Fix scale",
    "data modify entity @s transformation.scale[1] set value 1.005f",
    '""")',
  ].join("\n");
  const [content] = contentsOf(source);
  assert.ok(content.includes("data modify entity @s transformation.scale[1]"), content);
  assert.ok(!content.includes("place_secondary"), "the path must not leak into the commands");
});

test("machines.py:77 a path that is a subscript", () => {
  const source = 'write_function(funcs["stop"], f"""\nsay stopped\n""")';
  assert.deepEqual(contentsOf(source), ["\nsay stopped\n"]);
});

test("machines.py:84 a path that is a subscript holding an f-string", () => {
  const source = 'write_function(funcs[f"consume_{item}"], f"""\nsay consumed\n""")';
  assert.deepEqual(contentsOf(source), ["\nsay consumed\n"],
    "the interpolation inside the path argument must not be read as the content");
});

test("machines.py:169 an attribute path and a bare-name path both work", () => {
  assert.equal(findBlockOffsets('write_function(funcs.tick, "say a")').length, 1);
  assert.equal(findBlockOffsets('write_function(funcs["work"], "say b")').length, 1);
});

// Content shapes

test("machines.py:25 an annotated variable whose first line is a comment", () => {
  const source = [
    'content: McFunction = f"""# Produce Energy depending on the power of daylight sensor',
    "execute if predicate {ns}:check_daylight_power run scoreboard players operation @s energy.storage += @s {ns}.energy_rate",
    '"""',
    "write_function(BlockFunctions(\"solar_panel\").second, content)",
  ].join("\n");
  const [content] = contentsOf(source);
  assert.ok(content.startsWith("# Produce Energy"),
    "a comment on the opening line is part of the block, not a reason to skip it");
  assert.ok(content.includes("execute if predicate"), content);
});

test("machines.py:48 an annotated variable assigned an empty string still reaches its call", () => {
  const source = [
    'redstone_generator: McFunction = ""',
    'write_function(funcs.second, redstone_generator)',
  ].join("\n");
  assert.deepEqual(contentsOf(source), [""],
    "an empty block is a block: it is where the author will type, and completion must work there");
});

test("machines.py:56 doubled braces in an f-string are NBT, not interpolation", () => {
  const line = 'execute if data block ~ ~ ~ {{Items:[{{Slot:0b,id:"minecraft:redstone"}}],lit_time_remaining:0s}} run say hi';
  const source = `content: McFunction = f"""\n${line}\n"""\nwrite_function(funcs.second, content)`;
  const [block] = findBlockOffsets(source);
  const spans = findInterpolationSpans(source.slice(block.contentStart, block.contentEnd), true);
  assert.deepEqual(spans, [],
    "`{{` is an escaped brace, so masking it as an interpolation would corrupt the NBT");
});

test("machines.py:56 a real interpolation beside doubled braces is still found", () => {
  const source = [
    'write_function(funcs.second, f"""',
    'execute if data block ~ ~ ~ {{Slot:0b}} run function {funcs["consume"]}',
    '""")',
  ].join("\n");
  const [block] = findBlockOffsets(source);
  const spans = findInterpolationSpans(source, block);
  assert.equal(spans.length, 1, `expected one interpolation, got ${JSON.stringify(spans)}`);
  assert.equal(source.slice(spans[0].start, spans[0].end), '{funcs["consume"]}',
    "the escaped brace is skipped and the computed path is the only thing masked");
});

// Lists, where the annotation is the whole difference

test("machines.py:170 an annotated list is coloured but is not a block", () => {
  // The two halves of the extension disagree here, and it is worth pinning rather than
  // discovering. The grammar colours a `list[McFunction]` and every append onto it, because the
  // annotation says what they are. The block finder does not, because it only claims content
  // that reaches a call it knows, and this list reaches `write_function` as one joined string
  // many lines later. So these entries get colours, and not completion.
  const source = [
    "output_list: list[McFunction] = []",
    `output_list.append('data modify entity @s item.components."minecraft:custom_data".itemio.ioconfig append value {"Slot":0b}')`,
  ].join("\n");
  assert.deepEqual(findBlockOffsets(source), [],
    "following the join is what completion here would need, and the finder does not do it");
});

test("machines.py:124 a plain list of strings is left alone", () => {
  const source = [
    "machine_gui: list[str] = []",
    `machine_gui.append(f'execute if score @s energy.storage matches ..0 run say hi')`,
  ].join("\n");
  assert.deepEqual(findBlockOffsets(source), [],
    "list[str] is not list[McFunction], and colouring it would colour every list in the file");
});

test("machines.py:170 the grammar does colour an annotated list's entries", async t => {
  const engine = await load("source.python");
  if (typeof engine === "string") return t.skip(engine);

  const lines = engine.tokenize([
    "output_list: list[McFunction] = []",
    `output_list.append('data modify entity @s item.components."minecraft:custom_data" set value 1')`,
    `machine_gui.append('execute if score @s energy.storage matches ..0 run say hi')`,
    "",
  ].join("\n"));

  assert.ok(scopesOf(lines, "data")?.includes(COMMAND),
    "the annotated list's append is a command, which is the half the grammar owns");
  assert.equal((scopesOf(lines, "execute") ?? []).includes(COMMAND), false,
    "and an append onto a name that was never annotated ends the run");
});

// What the grammar makes of the same shapes

test("the real file tokenizes without a runaway scope", async t => {
  const engine = await load("source.python");
  if (typeof engine === "string") return t.skip(engine);

  const real = "d:/advanced_desktop/SimplEnergy/src/utils/machines.py";
  if (!fs.existsSync(real)) return t.skip(`${real} is not on this machine`);

  const lines = engine.tokenize(fs.readFileSync(real, "utf8"));
  // A begin pattern whose end never matches turns the rest of the file into one scope.
  let run = 0, longest = 0, worst = "";
  let previous = null;
  for (const line of lines) {
    const scope = line.length ? line[0].scopes[1] ?? line[0].scopes[0] : null;
    run = scope && scope === previous ? run + 1 : 1;
    previous = scope;
    if (run > longest) { longest = run; worst = String(scope); }
  }
  assert.ok(longest < 60, `${longest} consecutive lines in ${worst}, which looks like a rule that never closed`);
});

test("a command inside an annotated variable is coloured in the real file's idiom", async t => {
  const engine = await load("source.python");
  if (typeof engine === "string") return t.skip(engine);

  const source = [
    'content: McFunction = f"""# Produce Energy',
    "execute if predicate {ns}:check_daylight_power run scoreboard players operation @s energy.storage += @s {ns}.energy_rate",
    '"""',
    'write_function(BlockFunctions("solar_panel").second, content)',
  ].join("\n");
  const lines = engine.tokenize(source);
  assert.ok(scopesOf(lines, "execute")?.includes(COMMAND), "the annotated block must colour its commands");
  assert.ok(scopesOf(lines, "write_function")?.every(s => !s.includes("mcfunction")),
    "and the call below it is Python, not part of the block");
});

// beet's own writers, through the grammar

test("a Function assigned into the pack is coloured", async t => {
  const engine = await load("source.python");
  if (typeof engine === "string") return t.skip(engine);

  for (const source of [
    'ctx.data.functions["ns:x"] = Function("say hi")',
    'ctx.data["ns"].functions["x"] = Function("say hi")',
    'ctx.data[Function]["ns:x"] = Function("say hi")',
    'ctx.data.functions["ns:x"] = Function("""\nsay hi\n""")',
    'ctx.data.functions["ns:x"] = Function(["say hi", "say other"])',
    'ctx.data.functions["ns:x"].append("say hi")',
  ]) {
    const lines = engine.tokenize(source + "\n");
    assert.ok(scopesOf(lines, "say")?.includes(COMMAND), `not coloured: ${JSON.stringify(source)}`);
  }
});

test("a bare Function call is left as Python", async t => {
  const engine = await load("source.python");
  if (typeof engine === "string") return t.skip(engine);

  const lines = engine.tokenize('func = Function("say hi")\n');
  assert.equal((scopesOf(lines, "say") ?? []).includes(COMMAND), false,
    "the class name alone appears in unrelated Python, and claiming it would colour that too");
});

test("an assignment does not swallow the Python after it", async t => {
  const engine = await load("source.python");
  if (typeof engine === "string") return t.skip(engine);

  const lines = engine.tokenize('ctx.data.functions["ns:x"] = Function("say hi")\nvalue = 3\n');
  assert.ok(scopesOf(lines, "=")?.includes("keyword.operator.assignment.python"),
    "the block closes at its quote, so the next line is Python again");
});

test("a list of commands closes its brackets, so nothing renders as unmatched", async t => {
  const engine = await load("source.python");
  if (typeof engine === "string") return t.skip(engine);

  // The `say` rule ends an inline embed at whatever closes it. A quote followed by `]` was not
  // one of those, so the last entry swallowed the bracket and the paren after it, and VS Code
  // coloured the opening `([` as unmatched.
  const source = 'ctx.data.functions["ns:x"] = Function(["say from list one", "say from list two"])\n';
  const flat = engine.tokenize(source).flat();

  const closing = flat.filter(token => token.text === "]" || token.text === ")");
  assert.equal(closing.length, 2, `expected one ] and one ), got ${JSON.stringify(closing.map(c => c.text))}`);
  for (const token of closing) {
    assert.ok(!token.scopes.some(scope => scope.startsWith("string.")),
      `${token.text} is inside ${token.scopes[token.scopes.length - 1]}, so its opener reads as unmatched`);
  }

  // Both entries still hold commands, which is what the leak was hiding.
  const says = flat.filter(token => token.text === "say" && token.scopes.includes(COMMAND));
  assert.equal(says.length, 2, "each entry is a command of its own");
});

test("a list of commands with a trailing comma closes too", async t => {
  const engine = await load("source.python");
  if (typeof engine === "string") return t.skip(engine);

  const source = 'ctx.data.functions["ns:x"] = Function([\n    "say one",\n    "say two",\n])\nvalue = 3\n';
  const lines = engine.tokenize(source);
  assert.ok(scopesOf(lines, "=")?.includes("keyword.operator.assignment.python"),
    "a list written across lines must still close, or the rest of the file is one string");
  assert.equal(lines.flat().filter(t => t.text === "say" && t.scopes.includes(COMMAND)).length, 2);
});
