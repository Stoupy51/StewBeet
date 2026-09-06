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
const bolt = JSON.parse(fs.readFileSync(path.join(SYNTAXES, "bolt.tmLanguage.json"), "utf8"));

// Structure

test("grammar files are valid JSON with expected scope names", () => {
  assert.equal(embedded.scopeName, "source.mcfunction.embedded");
  assert.equal(injection.scopeName, "stewbeet.mcfunction-injection");
  assert.equal(bolt.scopeName, "source.bolt");
  // The span scope is excluded so the Python this grammar includes cannot re-enter it.
  assert.equal(injection.injectionSelector, "L:source.python -meta.mcfunction-span.stewbeet");
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
  walk(bolt, "bolt");
});

// The bolt grammar

test("bolt is Python first, with commands as the exception", () => {
  const includes = bolt.patterns.map(p => p.include);
  assert.deepEqual(includes, ["#module-import", "#nesting-statement", "#command-statement", "source.python"]);
  assert.equal(includes.indexOf("source.python"), includes.length - 1,
    "Python must come last, or it claims every line before a command rule is tried");
});

test("bolt command bodies are handed to the mcfunction grammar rather than described again", () => {
  const bodies = JSON.stringify(bolt.repository["command-statement"].patterns);
  assert.ok(bodies.includes("source.mcfunction.embedded#root"), "SC-003: no mcfunction syntax is authored here");
});

test("the command heads are mecha's own, with return withheld", () => {
  const heads = bolt.repository["command-statement"].begin.match(/\((?:[a-z-]+\|)+[a-z-]+\)/)[0].slice(1, -1).split("|");
  assert.equal(heads.length, 91, "mecha's tree has 92 roots and `return` is dropped");
  assert.ok(!heads.includes("return"), "return is Python's keyword first");
  for (const head of ["execute", "function", "say", "scoreboard", "item", "ban-ip"]) {
    assert.ok(heads.includes(head), `${head} is missing from the generated set`);
  }
  assert.ok(bolt.repository["command-statement"].comment.includes("Regenerate with:"),
    "the set is derived from mecha, so the command that derives it must be recorded");
});

test("a command head only opens a command when what follows is not Python", () => {
  const begin = new RegExp(bolt.repository["command-statement"].begin);
  for (const line of ["say hello", "    item modify entity @s", "setblock -1 2 3 stone", "function demo:x:"]) {
    assert.ok(begin.test(line), line);
  }
  for (const line of ["item = 3", "time -= 1", "list(x)", "data.get(k)", "test: int = 3", "item, other = 1, 2"]) {
    assert.ok(!begin.test(line), line);
  }
});

test("every bolt rule that opens a block can close it on the same line", () => {
  for (const name of ["nesting-statement", "command-statement", "python-call"]) {
    const rule = bolt.repository[name];
    assert.ok(rule.end.includes("$"), `${name} must be able to end at the line end`);
  }
});

// Comment patterns must swallow quotes (TODO example 2)

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

// Comments must not swallow the end of an inline write_* call
//
// write_versioned_function("ns/tick", "# Hijacked map tick (no-op placeholder)")
// used to highlight the trailing `")` as part of the comment, because the
// comment pattern ran to end of line regardless of the Python string ending.

const COMMENT_PATTERNS = () => [
  ["line", embedded.repository.comments.patterns.find(p => p.match && p.match.includes("^\\s*#(?!\\{)"))],
  ["inline", embedded.repository.comments_inline.patterns.find(p => p.match)],
];

test("comment patterns stop before the quote closing an inline write_* call", () => {
  const cases = [
    // [mcfunction content + python tail, what the comment must cover]
    ['# Hijacked map tick (no-op placeholder)")', "# Hijacked map tick (no-op placeholder)"],
    ["# Hijacked map tick (no-op placeholder)')", "# Hijacked map tick (no-op placeholder)"],
    ['# Some comment", prepend=True)', "# Some comment"],
    ['# Some comment", overwrite=True, tags=["ns:my_tag"])', "# Some comment"],
    ['# Trailing spaces after paren")  ', "# Trailing spaces after paren"],
    // Quotes inside the comment must not be mistaken for the closing quote.
    [`# Override with 'name' or "name" field")`, `# Override with 'name' or "name" field`],
  ];
  for (const [name, pattern] of COMMENT_PATTERNS()) {
    assert.ok(pattern, `${name} comment pattern not found`);
    const re = new RegExp(pattern.match);
    for (const [line, expected] of cases) {
      const m = line.match(re);
      assert.ok(m, `${name}: no match in ${JSON.stringify(line)}`);
      assert.equal(m[0], expected, `${name}: wrong end in ${JSON.stringify(line)}`);
    }
  }
});

test("comment patterns still run to end of line inside a multiline block", () => {
  const cases = [
    "# Reset the counter (per player)",       // parenthesis, but no closing quote
    '# Increment "down count',                 // lone quote
    "# Kill entities (tagged) then continue",
    // Prose whose quotes happen to be followed by a parenthesis at end of line:
    // the tail between quote and ")" is not a Python argument list, so it stays a comment.
    `# Read display name (default to weapon_id, override with 'name' or "name" field)`,
    '# Set the "flag" then reset (x)',
    "# Toggle 'debug' mode (owner only)",
    '# Store as "value" (integer)',
  ];
  for (const [name, pattern] of COMMENT_PATTERNS()) {
    const re = new RegExp(pattern.match);
    for (const line of cases) {
      const m = line.match(re);
      assert.ok(m, `${name}: no match in ${JSON.stringify(line)}`);
      assert.equal(m[0], line, `${name}: comment must reach end of line in ${JSON.stringify(line)}`);
    }
  }
});

test("block comment begin stops before the quote closing an inline write_* call", () => {
  const pattern = embedded.repository.comments.patterns.find(p => p.begin && p.begin.includes("#[>!#]"));
  assert.ok(pattern, "block comment pattern not found");
  const re = new RegExp(pattern.begin);
  const m = '#> Hijacked map (placeholder)")'.match(re);
  assert.ok(m);
  assert.equal(m[0], "#> Hijacked map (placeholder)");
  assert.equal(m[2], " Hijacked map (placeholder)");
});

// say blocks must not swallow the end of the Python string
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
    for (const line of [
      "say Don't panic\n",
      'say Hello "world" bye\n',
      'say Hello "world" (bye)\n',   // quote then paren at end of line, but not a Python arg tail
      "say Press 'F' to pay respects (now)\n",
    ]) {
      const m = re.exec(line);
      assert.ok(m);
      assert.equal(m.index, line.length - 1, `say must run to the newline in ${JSON.stringify(line)}`);
    }
  }
});

// Triple-quote string rules must exist before single-quote ones

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

// Injection rules cover all write_* function forms

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

// The McFunction annotation rule (FR-023)

/** The rule owning an annotated variable and every append to it. */
const annotationRule = injection.repository["stewbeet-mcfunction-string"].patterns
  .find(p => typeof p.begin === "string" && p.begin.includes("McFunction"));

/** Its nested string rules: four quote styles for the assignment, four for `+=`. */
const valueRules = annotationRule ? annotationRule.patterns : [];

const TRIPLE_DOUBLE = '(\\"\\"\\")';
const TRIPLE_SINGLE = "(''')";
const SINGLE_DOUBLE = '(\\")';
const SINGLE_SINGLE = "(')";

test("the annotation rule owns the assignment and every append", () => {
  assert.ok(annotationRule, "no McFunction rule in the injection grammar");
  assert.equal(valueRules.length, 9, "four quote styles for `=`, four for `+=`, then Python");
  assert.equal(valueRules.at(-1).include, "source.python",
    "the span must fall back to Python, or the lines it covers lose their own colours");
  assert.equal(annotationRule.name, "meta.mcfunction-span.stewbeet", "the span needs the excluded scope");
  assert.ok(annotationRule.end.includes("\\1"),
    "the end must backreference the annotated name, or the rule runs to the end of the file");
});

test("the annotation rule matches the shapes an author writes", () => {
  const begin = new RegExp(annotationRule.begin);
  for (const shape of ["content: McFunction = ", "c:McFunction=", "_body2 :  McFunction  =  "]) {
    assert.ok(begin.test(shape), shape);
  }
});

test("the annotation rule leaves every other annotation alone", () => {
  const begin = new RegExp(annotationRule.begin);
  for (const shape of ["notes: str = ", "content = ", "content: MyMcFunction = ", "content: McFunctions = "]) {
    assert.ok(!begin.test(shape), shape);
  }
});

test("every quote style is covered, triple before single", () => {
  const idxOf = quote => valueRules.findIndex(p => p.begin.endsWith(quote));
  assert.ok(idxOf(TRIPLE_DOUBLE) !== -1 && idxOf(TRIPLE_SINGLE) !== -1, "missing a triple-quote rule");
  assert.ok(idxOf(TRIPLE_DOUBLE) < idxOf(SINGLE_DOUBLE), "triple-double must come before single-double");
  assert.ok(idxOf(TRIPLE_SINGLE) < idxOf(SINGLE_SINGLE), "triple-single must come before single-single");
});

test("a value rule ends at the quote, with no call parenthesis to close", () => {
  for (const rule of valueRules.filter(r => r.end)) {
    // The write_* rules capture the call's closing `)` as group 2. An assignment has none.
    assert.deepEqual(Object.keys(rule.endCaptures), ["1"], `${rule.begin} should end at the quote alone`);
    assert.equal(rule.contentName, "source.mcfunction.embedded");
  }
});

test("inline value rules use the inline flavour of the embedded grammar", () => {
  for (const rule of valueRules.filter(r => r.name)) {
    const wanted = rule.name.includes(".inline.")
      ? "source.mcfunction.embedded#root-inline"
      : "source.mcfunction.embedded#root";
    assert.equal(rule.patterns[0].include, wanted, rule.begin);
  }
});

test("the embedded grammar carries an inline flavour for say", () => {
  assert.ok(embedded.repository["root-inline"], "missing #root-inline");
  assert.ok(embedded.repository["say-inline"], "missing #say-inline");
  const inline = embedded.repository["say-inline"].patterns;
  const block = embedded.repository["say"].patterns;
  // An inline say ends wherever the embed around it does, which a block say must not do.
  // Two ways beyond the block rule's own: the quote that ends the line, and the quote that ends
  // an entry of a list of commands, followed by a comma or the closing bracket.
  const INLINE_ENDS = [
    "|(?=[\\\"'][ \\t]*,?[ \\t]*$)",
    "|(?=[\\\"'][ \\t]*[,\\]])",
  ];
  assert.equal(inline.length, block.length, "every say rule needs both flavours");
  for (const [i, rule] of inline.entries()) {
    assert.equal(rule.end, block[i].end + INLINE_ENDS.join(""),
      "an inline say is the block rule plus every way an embed can close");
    assert.ok(!rule.end.includes("\t"), "use the \\t escape, not a literal tab");
  }
  for (const rule of block) {
    for (const ending of INLINE_ENDS) {
      assert.ok(!rule.end.includes(ending),
        "a block say must not end at a quote, or `say something \"quoted\"` would end the block early");
    }
  }
});

/** The rule owning a list annotated list[McFunction] and every append onto it. */
const listRule = injection.repository["stewbeet-mcfunction-string"].patterns
  .find(p => typeof p.begin === "string" && p.begin.includes("list"));

test("the list rule owns the literal and every append", () => {
  assert.ok(listRule, "no list[McFunction] rule in the injection grammar");
  assert.equal(listRule.patterns.length, 6, "a list literal, four quote styles of append, then Python");
  assert.equal(listRule.patterns.at(-1).include, "source.python",
    "the span must fall back to Python, or the lines it covers lose their own colours");
  assert.equal(listRule.name, "meta.mcfunction-span.stewbeet", "the span needs the excluded scope");
  assert.ok(listRule.end.includes("\\1"), "the end must backreference the annotated name");
  assert.ok(listRule.end.includes("append"), "an append onto the name must not end the run");
});

test("the list rule holds its run open across a branch", () => {
  for (const keyword of ["if", "elif", "else", "for", "while", "try", "except", "with"]) {
    assert.ok(listRule.end.includes(keyword),
      `${keyword} must not end the run, or appends inside a branch lose their colours`);
  }
});

test("the list rule matches only a list of McFunction", () => {
  const begin = new RegExp(listRule.begin);
  for (const shape of ["out: list[McFunction] = ", "out:list[ McFunction ]= "]) {
    assert.ok(begin.test(shape), shape);
  }
  for (const shape of ["notes: list[str] = ", "out: list[MyMcFunction] = ", "out: McFunction = "]) {
    assert.ok(!begin.test(shape), shape);
  }
});

// The grammar and the block finder must agree on what opens a block

test("both halves accept the same string prefixes", () => {
  const { stringPrefixAt } = require("../src/blocks");
  const patterns = JSON.stringify(injection).match(/\(\[rRbBuUfF\]\{0,2\}\)/g) ?? [];
  assert.ok(patterns.length > 20,
    `the grammar should carry the widened prefix on every rule, found ${patterns.length}`);
  assert.equal(JSON.stringify(injection).includes('"(f?)"'), false,
    "an f-only prefix leaves r-strings uncoloured, which is what StardustFragment writes");

  // What blocks.js accepts is the contract, since it decides where completion and diagnostics go.
  const group = new RegExp(`^${patterns[0]}$`);
  for (const prefix of ["", "f", "F", "r", "R", "b", "u", "rf", "fr", "rb", "br"]) {
    const accepted = prefix === "" || stringPrefixAt(`${prefix}"""x`, prefix.length) === prefix;
    assert.equal(group.test(prefix), accepted,
      `the grammar and blocks.js disagree about the prefix ${JSON.stringify(prefix)}`);
  }
  assert.equal(group.test("xyz"), false, "and neither accepts three letters");
});
