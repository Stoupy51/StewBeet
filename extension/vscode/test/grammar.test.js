// @ts-check
"use strict";

// Sanity tests for the TextMate grammars. Full tokenization would require an
// Oniguruma-backed harness (vscode-tmgrammar-test); these tests validate the
// JSON structure and the regexes that fixed the known highlighting bugs
// (regexes checked here are JS-compatible subsets of Oniguruma).

const { test } = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");

const SYNTAXES = path.join(__dirname, "..", "syntaxes");

const embedded = JSON.parse(fs.readFileSync(path.join(SYNTAXES, "mcfunction-embedded.tmLanguage.json"), "utf8"));
const injection = JSON.parse(fs.readFileSync(path.join(SYNTAXES, "mcfunction-injection.tmLanguage.json"), "utf8"));

// ─── Structure ───────────────────────────────────────────────────────────────

test("grammar files are valid JSON with expected scope names", () => {
  assert.equal(embedded.scopeName, "source.mcfunction.embedded");
  assert.equal(injection.scopeName, "stewbeet.mcfunction-injection");
  assert.equal(injection.injectionSelector, "L:source.python");
});

test("every regex in both grammars compiles as a RegExp", () => {
  const keys = new Set(["match", "begin", "end"]);
  const walk = (node, file) => {
    if (Array.isArray(node)) return node.forEach(n => walk(n, file));
    if (node && typeof node === "object") {
      for (const [k, v] of Object.entries(node)) {
        if (keys.has(k) && typeof v === "string") {
          assert.doesNotThrow(() => new RegExp(v), `invalid regex in ${file}: ${v}`);
        } else {
          walk(v, file);
        }
      }
    }
  };
  walk(embedded, "mcfunction-embedded");
  walk(injection, "mcfunction-injection");
});

// ─── Comment patterns must swallow quotes (TODO example 2) ───────────────────

test("line comment pattern consumes a double quote", () => {
  const pattern = embedded.repository.comments.patterns.find(p => p.match && p.match.includes("^\\s*#(?!\\{)"));
  assert.ok(pattern, "line comment pattern not found");
  const re = new RegExp(pattern.match);
  const line = '# Increment "down count';
  const m = line.match(re);
  assert.ok(m);
  assert.equal(m[0], line, "comment must extend past the quote to end of line");
});

test("inline comment pattern consumes a double quote", () => {
  const pattern = embedded.repository.comments_inline.patterns.find(p => p.match);
  assert.ok(pattern, "inline comment pattern not found");
  const re = new RegExp(pattern.match);
  const line = '# has "quotes" inside';
  const m = line.match(re);
  assert.ok(m);
  assert.equal(m[0], line);
});

test("line comment pattern still stops at a literal \\n escape", () => {
  const pattern = embedded.repository.comments.patterns.find(p => p.match && p.match.includes("^\\s*#(?!\\{)"));
  const re = new RegExp(pattern.match);
  const m = "# hello \\nworld".match(re);
  assert.ok(m);
  assert.equal(m[0], "# hello ");
});

// ─── say blocks must not swallow the end of the Python string ────────────────
//
// A begin/end rule hides the parent injection's end pattern from the tokenizer,
// so a say block ending only at "\n" ate the closing quote, the ")", and every
// following line of the file.

test("both say rules end at more than a real newline", () => {
  const ends = embedded.repository.say.patterns.map(p => p.end);
  assert.equal(ends.length, 2);
  for (const end of ends) {
    assert.notEqual(end, "\\n", "say must not end on a bare newline (swallows the closing quote)");
    assert.ok(end.includes("(?=\\\\n)"), "say must stop before a literal \\n escape");
  }
});

test("say end matches where the mcfunction line really ends", () => {
  const [lineStart, afterRun] = embedded.repository.say.patterns.map(p => new RegExp(p.end));
  const cases = [
    // [line, index the say block must end at]
    ['execute if score #spam ns.data matches 1 run say every minute\\n")', 61],  // literal \n escape
    ['execute run say hi")', 18],                                               // closing quote + call paren
    ['execute run say hi""")', 18],                                             // triple-quoted string
    ["execute run say hi''')", 18],
    ['execute run say hi", prepend=True)', 18],                                 // quote, then kwargs
  ];
  for (const [line, expected] of cases) {
    for (const re of [lineStart, afterRun]) {
      const m = re.exec(line);
      assert.ok(m, `no end match in ${JSON.stringify(line)}`);
      assert.equal(m.index, expected, `wrong end position in ${JSON.stringify(line)}`);
    }
  }
});

test("say end does not fire early on quotes inside a multiline block", () => {
  for (const p of embedded.repository.say.patterns) {
    const re = new RegExp(p.end);
    for (const line of ["say Don't panic\n", 'say Hello "world" bye\n']) {
      const m = re.exec(line);
      assert.ok(m);
      assert.equal(m.index, line.length - 1, `say must run to the newline in ${JSON.stringify(line)}`);
    }
  }
});

// ─── Triple-quote string rules must exist before single-quote ones ──────────

test("literals define triple-quote rules before single-quote rules", () => {
  const patterns = embedded.repository.literals.patterns;
  const idxOf = begin => patterns.findIndex(p => p.begin === begin);
  const tripleDouble = idxOf('"""');
  const tripleSingle = idxOf("'''");
  const singleDouble = idxOf('"');
  const singleSingle = idxOf("'");
  assert.ok(tripleDouble !== -1, 'missing """ rule in #literals');
  assert.ok(tripleSingle !== -1, "missing ''' rule in #literals");
  assert.ok(tripleDouble < singleDouble, '""" rule must come before " rule');
  assert.ok(tripleSingle < singleSingle, "''' rule must come before ' rule");
});

// ─── Injection rules cover all write_* function forms ────────────────────────

test("injection grammar covers all six write_* functions", () => {
  const text = JSON.stringify(injection);
  for (const fn of [
    "write_function",
    "write_versioned_function",
    "write_scheduled_function",
    "write_load_file",
    "write_unload_file",
    "write_tick_file",
  ]) {
    assert.ok(text.includes(fn), `injection grammar missing ${fn}`);
  }
});
