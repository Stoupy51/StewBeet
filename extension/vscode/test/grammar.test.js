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
