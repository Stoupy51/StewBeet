// @ts-check
"use strict";

const test = require("node:test");
const assert = require("node:assert/strict");
const { projectBolt } = require("../src/boltlines");
const { tokensBack } = require("../src/semantic");

/** Index of each type in the legend these tests pretend Spyglass sent. */
const ERROR = 0, LITERAL = 1, PUNCTUATION = 2, VECTOR = 3;

/**
 * Absolute [line, character, length, type] tokens in the relative encoding the semantic tokens API uses.
 * @param {number[][]} tokens
 */
function encode(tokens) {
  const data = [];
  let [line, character] = [0, 0];
  for (const [at, from, length, type] of tokens) {
    data.push(at - line, at === line ? from - character : from, length, type, 0);
    [line, character] = [at, from];
  }
  return data;
}

/** @param {string} text @param {number[][]} tokens */
function back(text, tokens) {
  const lengths = text.split("\n").map(line => line.length);
  return tokensBack(encode(tokens), projectBolt(text), lengths, ERROR).map(token => token.slice(0, 4));
}

test("a command's tokens come back to the columns its indentation pushed it to", () => {
  const text = "for i in range(3):\n    say done";
  assert.deepEqual(back(text, [[1, 0, 3, LITERAL]]), [[1, 4, 3, LITERAL]]);
});

test("the Python bolt evaluates keeps the grammar's colour, whatever Spyglass made of its mask", () => {
  const text = "for i in range(3):\n    tp @s (i) ~ ~";
  // `tp @s ___ ~ ~`: the mask is columns 6 to 9 of the virtual line.
  assert.deepEqual(back(text, [[1, 0, 2, LITERAL], [1, 6, 3, ERROR], [1, 10, 3, VECTOR]]), [[1, 4, 2, LITERAL], [1, 14, 3, VECTOR]],
    "the mask's own token goes, and the vector after it is the author's");
  assert.deepEqual(back(text, [[1, 10, 1, ERROR]]), [], "an error after a mask is the parser lost on the stand-in");
});

test("the continuation a spread command is given has no colour to bring back", () => {
  const text = "execute\n    as @a\n    run say spread";
  // `execute \`, `as @a \`, `run say spread`: the `\` sits past the end of the source line.
  assert.deepEqual(back(text, [[0, 0, 7, LITERAL], [0, 8, 1, PUNCTUATION], [1, 0, 2, LITERAL]]), [[0, 0, 7, LITERAL], [1, 4, 2, LITERAL]]);
});

test("a value the build substituted is not coloured as what it became", () => {
  const text = "x = 2\ntp @s (x) ~ ~";
  const projection = projectBolt(text, { generated: new Map([[1, "tp @s 2 ~ ~"]]) });
  assert.equal(projection.text.split("\n")[1], "tp @s 2 ~ ~", "the projection this relies on substitutes the value");
  const tokens = tokensBack(encode([[1, 0, 2, LITERAL], [1, 6, 1, LITERAL], [1, 8, 3, VECTOR]]), projection, [5, 13], ERROR);
  assert.deepEqual(tokens.map(token => token.slice(0, 4)), [[1, 0, 2, LITERAL], [1, 10, 3, VECTOR]]);
});
