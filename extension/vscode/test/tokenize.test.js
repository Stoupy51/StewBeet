// @ts-check
"use strict";

// Tokenization tests, run through the same TextMate engine VS Code uses, with the real Python
// grammar the injection targets. grammar.test.js checks that the grammars are well-formed;
// this checks what they actually produce, which is the only way to catch a rule that never
// fires or one whose end pattern swallows the quote closing the embed.
//
// Needs `npm install` for vscode-textmate and vscode-oniguruma, and a VS Code install to read
// MagicPython from. Missing either, every test here skips rather than fails: the suite reports
// what it could not check instead of pretending it passed.

const { test } = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");

const SYNTAXES = path.join(__dirname, "..", "syntaxes");

/** VS Code ships MagicPython inside its own install, under a version-stamped directory. */
function findPythonGrammar() {
  const roots = [
    process.env.VSCODE_EXE && path.dirname(process.env.VSCODE_EXE),
    "D:\\Programs\\Microsoft VS Code",
    "C:\\Program Files\\Microsoft VS Code",
    path.join(os.homedir(), "AppData", "Local", "Programs", "Microsoft VS Code"),
    "/usr/share/code",
    "/Applications/Visual Studio Code.app/Contents/Resources",
  ].filter(Boolean);
  const tail = path.join("resources", "app", "extensions", "python", "syntaxes", "MagicPython.tmLanguage.json");
  for (const root of roots) {
    const direct = path.join(String(root), tail);
    if (fs.existsSync(direct)) return direct;
    // Some installs interpose a version-stamped directory between the root and `resources`.
    for (const entry of fs.existsSync(String(root)) ? fs.readdirSync(String(root)) : []) {
      const nested = path.join(String(root), entry, tail);
      if (fs.existsSync(nested)) return nested;
    }
  }
  return null;
}

/** @returns {Promise<{ tokenize: (source: string) => { text: string, scopes: string[] }[][] } | string>} */
async function loadEngine() {
  let vsctm, oniguruma;
  try {
    vsctm = require("vscode-textmate");
    oniguruma = require("vscode-oniguruma");
  } catch {
    return "vscode-textmate and vscode-oniguruma are not installed; run `npm install`";
  }
  const python = findPythonGrammar();
  if (!python) return "no VS Code install found to read MagicPython from; set VSCODE_EXE";

  await oniguruma.loadWASM(fs.readFileSync(require.resolve("vscode-oniguruma/release/onig.wasm")).buffer);
  const files = {
    "source.python": python,
    "source.mcfunction.embedded": path.join(SYNTAXES, "mcfunction-embedded.tmLanguage.json"),
    "stewbeet.mcfunction-injection": path.join(SYNTAXES, "mcfunction-injection.tmLanguage.json"),
  };
  const registry = new vsctm.Registry({
    onigLib: Promise.resolve({
      createOnigScanner: (/** @type {string[]} */ s) => new oniguruma.OnigScanner(s),
      createOnigString: (/** @type {string} */ s) => new oniguruma.OnigString(s),
    }),
    loadGrammar: (/** @type {string} */ scope) => Promise.resolve(
      files[scope] ? vsctm.parseRawGrammar(fs.readFileSync(files[scope], "utf8"), files[scope]) : null,
    ),
    getInjections: (/** @type {string} */ scope) => (scope === "source.python" ? ["stewbeet.mcfunction-injection"] : undefined),
  });
  const grammar = await registry.loadGrammar("source.python");

  return {
    tokenize(source) {
      let state = vsctm.INITIAL;
      return source.split("\n").map(line => {
        const result = grammar.tokenizeLine(line, state);
        state = result.ruleStack;
        return result.tokens
          .map((/** @type {{ startIndex: number, endIndex: number, scopes: string[] }} */ t) =>
            ({ text: line.substring(t.startIndex, t.endIndex), scopes: t.scopes }))
          .filter((/** @type {{ text: string }} */ t) => t.text.trim());
      });
    },
  };
}

const engine = loadEngine();

/** Scopes of the first token whose text is exactly `word`, across every line. */
function scopesOf(lines, word) {
  for (const line of lines) {
    const hit = line.find(t => t.text === word);
    if (hit) return hit.scopes;
  }
  return null;
}

/** Run `body` with a tokenizer, or skip when the engine could not be built. */
function tokenizerTest(name, source, body) {
  test(name, async t => {
    const ready = await engine;
    if (typeof ready === "string") return t.skip(ready);
    body(ready.tokenize(source), assert);
  });
}

// A command is coloured wherever the embed starts

tokenizerTest(
  "an annotated inline string colours its command",
  'c: McFunction = "say hello"\n',
  lines => {
    assert.ok(scopesOf(lines, "say")?.includes("keyword.control.flow.mcfunction"),
      "say must be the command keyword, not a bare name");
  },
);

tokenizerTest(
  "a write_* inline string colours its command",
  'write_function("probe:x", "say hello")\n',
  lines => {
    assert.ok(scopesOf(lines, "say")?.includes("keyword.control.flow.mcfunction"),
      "the inline write_* form must colour commands too");
  },
);

tokenizerTest(
  "an inline resource location is a function name",
  'e: McFunction = "function ns:path/to/fn"\n',
  lines => {
    assert.ok(scopesOf(lines, "function")?.includes("keyword.control.flow.mcfunction"));
    assert.ok(scopesOf(lines, "ns:path/to/fn")?.includes("entity.name.function.mcfunction"));
  },
);

tokenizerTest(
  "a block still colours its commands",
  'block: McFunction = """\nsay hello\nfunction ns:other\n"""\n',
  lines => {
    assert.ok(scopesOf(lines, "say")?.includes("keyword.control.flow.mcfunction"));
    assert.ok(scopesOf(lines, "ns:other")?.includes("entity.name.function.mcfunction"));
  },
);

// The embed ends where the Python string ends

tokenizerTest(
  "an inline say does not swallow the quote that closes the string",
  'c: McFunction = "say hello"\nplain = "ordinary python"\n',
  lines => {
    const after = scopesOf(lines, "ordinary python") ?? [];
    assert.ok(!after.some(s => s.includes("mcfunction")),
      `the embed leaked into the next line: ${after.join(" ")}`);
  },
);

tokenizerTest(
  "a block line ending in a quote does not end the block early",
  'block: McFunction = """\nexecute as @a run say ends with "hi"\nfunction ns:after\n"""\n',
  lines => {
    assert.ok(scopesOf(lines, "ns:after")?.includes("entity.name.function.mcfunction"),
      "the line after a quoted say must still be read as a command");
  },
);

// Everything else stays Python

tokenizerTest(
  "another annotation is left alone",
  'notes: str = "this must stay plain Python"\n',
  lines => {
    const scopes = scopesOf(lines, "this must stay plain Python") ?? [];
    assert.ok(!scopes.some(s => s.includes("mcfunction")), scopes.join(" "));
  },
);

// Appends to an annotated variable (FR-022 + FR-023)

tokenizerTest(
  "a += onto an annotated variable is coloured too",
  'content: McFunction = """\nsay one\n"""\ncontent += """\nsay two\n"""\n',
  lines => {
    const says = lines.flat().filter(t => t.text === "say");
    assert.equal(says.length, 2, "both blocks should contribute a say");
    for (const say of says) {
      assert.ok(say.scopes.includes("keyword.control.flow.mcfunction"),
        `an appended block must colour like the first: ${say.scopes.join(" ")}`);
    }
  },
);

tokenizerTest(
  "a += onto a different name is left alone",
  'first: McFunction = "say first"\nsecond += "not mine"\n',
  lines => {
    const scopes = scopesOf(lines, "not mine") ?? [];
    assert.ok(!scopes.some(s => s.includes("mcfunction")),
      `only the annotated name may carry its appends: ${scopes.join(" ")}`);
  },
);

tokenizerTest(
  "a blank line between the assignment and its append is tolerated",
  'gap: McFunction = "say gap"\n\ngap += "say later"\n',
  lines => {
    const says = lines.flat().filter(t => t.text === "say");
    assert.equal(says.length, 2, "the blank line must not end the variable's run");
  },
);

tokenizerTest(
  "an append inside a function body works at that indentation",
  'def build():\n\tbody: McFunction = "say one"\n\tbody += "say two"\n\tother = "plain"\n',
  lines => {
    assert.equal(lines.flat().filter(t => t.text === "say").length, 2);
    const plain = scopesOf(lines, "plain") ?? [];
    assert.ok(!plain.some(s => s.includes("mcfunction")), `the run must end at the next statement: ${plain.join(" ")}`);
  },
);

tokenizerTest(
  "the variable's run ends at the call that consumes it",
  'content: McFunction = "say one"\nwrite_function("ns:x", content)\nafter = "plain python"\n',
  lines => {
    const after = scopesOf(lines, "plain python") ?? [];
    assert.ok(!after.some(s => s.includes("mcfunction")), after.join(" "));
  },
);

// A list annotated list[McFunction] (FR-023)

tokenizerTest(
  "appends onto an annotated list are coloured, across a branch",
  'def build(m):\n\tout: list[McFunction] = []\n\tif m == "x":\n\t\tout.append("say one")\n\t\tout.append("say two")\n\telse:\n\t\tout.append("say three")\n',
  lines => {
    assert.equal(lines.flat().filter(t => t.text === "say").length, 3,
      "a branch between the declaration and its appends must not end the run");
    for (const say of lines.flat().filter(t => t.text === "say")) {
      assert.ok(say.scopes.includes("keyword.control.flow.mcfunction"), say.scopes.join(" "));
    }
  },
);

tokenizerTest(
  "an append onto a different list is left alone, and ends the run",
  'out: list[McFunction] = []\nout.append("say mine")\nother.append("not mine")\nout.append("not mine either")\n',
  lines => {
    assert.equal(lines.flat().filter(t => t.text === "say").length, 1);
    for (const text of ["not mine", "not mine either"]) {
      const scopes = scopesOf(lines, text) ?? [];
      assert.ok(!scopes.some(s => s.includes("mcfunction")), `${text}: ${scopes.join(" ")}`);
    }
  },
);

tokenizerTest(
  "a list literal's entries are commands",
  'literal: list[McFunction] = [\n\t"say one",\n\t\'say two\',\n]\ntail = "plain python"\n',
  lines => {
    assert.equal(lines.flat().filter(t => t.text === "say").length, 2);
    const tail = scopesOf(lines, "plain python") ?? [];
    assert.ok(!tail.some(s => s.includes("mcfunction")), `the literal leaked: ${tail.join(" ")}`);
  },
);

tokenizerTest(
  "a plain list annotation is left alone",
  'notes: list[str] = []\nnotes.append("say nothing")\n',
  lines => {
    const scopes = scopesOf(lines, "say nothing") ?? [];
    assert.ok(!scopes.some(s => s.includes("mcfunction")), scopes.join(" "));
  },
);

tokenizerTest(
  "an append carrying quoted NBT keeps the whole command",
  'out: list[McFunction] = []\nout.append(\'data modify entity @s foo.components."minecraft:custom_data" set value {"Slot":0b}\')\nafter = "plain python"\n',
  lines => {
    assert.ok(scopesOf(lines, "data")?.includes("keyword.control.flow.mcfunction"));
    const after = scopesOf(lines, "plain python") ?? [];
    assert.ok(!after.some(s => s.includes("mcfunction")), `quoted NBT leaked: ${after.join(" ")}`);
  },
);
