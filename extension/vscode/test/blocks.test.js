// @ts-check
"use strict";

const { test } = require("node:test");
const assert = require("node:assert/strict");

const {
  findBlockOffsets,
  findClosingQuote,
  skipInterpolation,
  skipFirstArg,
  readOpeningQuote,
} = require("../src/blocks");

/** Convenience: run findBlockOffsets and return the sliced block texts. */
function blockTexts(text) {
  return findBlockOffsets(text).map(({ start, end }) => text.slice(start, end));
}

// ─── Simple blocks ───────────────────────────────────────────────────────────

test("single-line f-string, 2nd arg", () => {
  const text = 'write_function("ns:path", f"say hi")';
  assert.deepEqual(blockTexts(text), ['f"say hi"']);
});

test("single-line plain string, 1st arg (write_tick_file)", () => {
  const text = 'write_tick_file("say tick")';
  assert.deepEqual(blockTexts(text), ['"say tick"']);
});

test("triple-quoted multi-line block", () => {
  const text = 'write_function("ns:path", f"""\nsay hello\nsay world\n""")';
  assert.deepEqual(blockTexts(text), ['f"""\nsay hello\nsay world\n"""']);
});

test("triple-single-quoted block", () => {
  const text = "write_load_file(f'''\nsay load\n''')";
  assert.deepEqual(blockTexts(text), ["f'''\nsay load\n'''"]);
});

test("multiple blocks in one file", () => {
  const text = 'write_function("a", "say 1")\nwrite_tick_file("say 2")';
  assert.deepEqual(blockTexts(text), ['"say 1"', '"say 2"']);
});

test("unterminated string yields no block", () => {
  const text = 'write_function("a", f"say {oops';
  assert.deepEqual(blockTexts(text), []);
});

// ─── Interpolation handling (TODO example 1) ─────────────────────────────────

test("braces in a non-f string are not interpolations", () => {
  const text = 'write_function("a", "say {literal} text")';
  assert.deepEqual(blockTexts(text), ['"say {literal} text"']);
});

test("literal {{ }} braces in an f-string (NBT)", () => {
  const text = 'write_function("a", f"data merge entity @s {{Invulnerable:1b}}")';
  assert.deepEqual(blockTexts(text), ['f"data merge entity @s {{Invulnerable:1b}}"']);
});

test("quotes inside a single-line interpolation are skipped", () => {
  const text = `write_function("a", f"say {d['key,)']} end")`;
  assert.deepEqual(blockTexts(text), [`f"say {d['key,)']} end"`]);
});

test("f-string first arg with interpolations is skipped correctly", () => {
  const text = 'write_versioned_function(f"{ns}:v{version}/x", f"say hi")';
  assert.deepEqual(blockTexts(text), ['f"say hi"']);
});

test("nested triple-quoted f-string inside an interpolation", () => {
  const text = [
    'write_function("p", f"""',
    "{helper(f'''",
    "say inner",
    "''')}",
    "say outer",
    '""")',
  ].join("\n");
  const blocks = blockTexts(text);
  assert.equal(blocks.length, 1);
  assert.ok(blocks[0].includes("say outer"), "block must extend past the nested f-string");
  assert.ok(blocks[0].endsWith('"""'));
  assert.equal(findBlockOffsets(text)[0].end, text.lastIndexOf('"""') + 3);
});

test("TODO example 1: nested f-string in late_join_flow_lines call", () => {
  const text = `
\t\twrite_versioned_function("zombies/join_game", f"""
{late_join_flow_lines(
\tns,
\t"zombies",
\tf"{ns}.zb.in_game",
\t"No active zombies game to join!",
\t"You are already in the zombies game!",
\tf"""
scoreboard players set @s {ns}.zb.in_game 1
team join {ns}.zombies @s
scoreboard players set @s {ns}.zb.points 500
scoreboard players set @s {ns}.zb.kills 0
scoreboard players set @s {ns}.zb.downs 0
scoreboard players set @s {ns}.zb.passive 0
scoreboard players set @s {ns}.zb.ability 0
scoreboard players set @s {ns}.zb.ability_cd 0
scoreboard players set @s {ns}.mp.spectate_timer 0
scoreboard players set @s {ns}.mp.death_count 0
attribute @s minecraft:max_health base reset
attribute @s minecraft:entity_interaction_range base set 5
""",
\tf"{ns}:v{version}/zombies/respawn_tp",
\t"joined the zombies game!",
\t"dark_green",
\tpost_class_lines=f"scoreboard players operation @s {ns}.zb.prev_kills = @s {ns}.total_kills",
)}
""")
`;
  const blocks = blockTexts(text);
  assert.equal(blocks.length, 1);
  const block = blocks[0];
  assert.ok(block.startsWith('f"""'));
  // The block must NOT stop at the nested f""" — it must cover the whole call.
  assert.ok(block.includes("attribute @s minecraft:entity_interaction_range base set 5"));
  assert.ok(block.includes("post_class_lines"));
  assert.equal(findBlockOffsets(text)[0].end, text.lastIndexOf('"""') + 3);
});

// ─── Quotes in comments (TODO example 2) ─────────────────────────────────────

test("TODO example 2: quote inside a comment line does not break the block", () => {
  const text = `
\t\twrite_versioned_function("zombies/on_respawn", f"""
# Reset death counter
scoreboard players set @s {ns}.mp.death_count 0

# Increment "down count
scoreboard players add @s {ns}.zb.downs 1

# Enter downed state (revive system)
function {ns}:v{version}/zombies/revive/on_down
""")
`;
  const blocks = blockTexts(text);
  assert.equal(blocks.length, 1);
  assert.ok(blocks[0].includes('# Increment "down count'));
  assert.ok(blocks[0].includes("zombies/revive/on_down"));
  assert.equal(findBlockOffsets(text)[0].end, text.lastIndexOf('"""') + 3);
});

// ─── Unit tests for the low-level scanners ───────────────────────────────────

test("findClosingQuote: plain single-line string", () => {
  const text = '"hello" rest';
  assert.equal(findClosingQuote(text, '"', 1), 6);
});

test("findClosingQuote: escaped quote is skipped", () => {
  const text = '"he said \\"hi\\"" rest';
  assert.equal(findClosingQuote(text, '"', 1), 15);
});

test("findClosingQuote: single-line string stops at newline", () => {
  assert.equal(findClosingQuote('"abc\ndef"', '"', 1), -1);
});

test("findClosingQuote: non-f string treats braces as plain characters", () => {
  const text = '"""say {x} done""" tail';
  assert.equal(findClosingQuote(text, '"""', 3), 15);
});

test("findClosingQuote: f-string skips interpolation containing triple quotes", () => {
  const text = 'f"""{fn(f"""inner""")}outer"""';
  const close = findClosingQuote(text, '"""', 4, true);
  assert.equal(close, text.length - 3);
});

test("skipInterpolation: nested brackets and strings", () => {
  const text = `x(a, [1, 2], {"k": "v"}, f'{y}')} tail`;
  assert.equal(skipInterpolation(text, 0), text.length - 5);
});

test("skipFirstArg: simple path", () => {
  const text = '"ns:path", f"say hi")';
  const idx = skipFirstArg(text, 0);
  assert.equal(text.slice(idx, idx + 1), "f");
});

test("skipFirstArg: path with comma inside string", () => {
  const text = '"a,b", "content")';
  const idx = skipFirstArg(text, 0);
  assert.equal(text.slice(idx, idx + 1), '"');
  assert.equal(idx, 7);
});

test("skipFirstArg: no comma returns -1", () => {
  assert.equal(skipFirstArg('"only")', 0), -1);
});

test("readOpeningQuote: detects f prefix and triple quotes", () => {
  assert.deepEqual(readOpeningQuote('  f"""x', 0), {
    quoteStyle: '"""',
    quoteStart: 2,
    contentStart: 6,
    isFString: true,
  });
});

test("readOpeningQuote: rf prefix counts as f-string", () => {
  const r = readOpeningQuote('rf"x"', 0);
  assert.ok(r && r.isFString);
});

test("readOpeningQuote: non-string returns null", () => {
  assert.equal(readOpeningQuote("variable", 0), null);
});

