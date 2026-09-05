// @ts-check
"use strict";

// Which .mcfunction files are bolt, and what the extension is allowed to do about it.
//
// The detector decides whether a file is taken away from Spyglass, so precision is what these
// tests are about. A missed bolt file is the status quo; a false positive costs a working
// vanilla file its completion and its diagnostics.

const { test } = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const { looksLikeBolt, isBuildOutput, SCAN_LIMIT } = require("../src/bolt.js");

const ROOT = path.join(__dirname, "..");

// Detection

test("bolt detection fires on what Spyglass cannot parse", () => {
  for (const source of [
    "for i in range(1, 6):\n    say hi\n",
    "from lib:helpers import thing\n",
    "import demo:helper\n",
    "def build(self):\n    say hi\n",
    "x = 3\nsay hi\n",
    "self.value += 1\n",
    "execute as @a:\n    say hi\n",
    "function demo:inner:\n    say hi\n",
    'enchantment ns:name {\n    "anvil_cost": 1\n}\n',
  ]) {
    assert.ok(looksLikeBolt(source), `not detected: ${JSON.stringify(source)}`);
  }
});

test("bolt detection leaves vanilla mcfunction alone", () => {
  for (const source of [
    "say hello\n",
    "execute as @a at @s run function ns:inner\n",
    "scoreboard players set #x obj 1\n",
    "data merge entity @s {NoAI:1b}\n",
    "return run function ns:other\n",
    "# for i in range(3):\n",
    "$say hello $(name)\n",
    'tellraw @a {"text":"hi"}\n',
    "execute if score #a obj = #b obj run say tie\n",
    "say Warning: something\n",
    "execute store result score #h ns.data run data get entity @s Pos[1]\n",
  ]) {
    assert.equal(looksLikeBolt(source), false, `false positive: ${JSON.stringify(source)}`);
  }
});

test("a file the build wrote is never bolt, whatever it holds", () => {
  assert.equal(looksLikeBolt("say hi\n## sourceMappingURL=x.mcfunction.map\n"), false,
    "the discovery comment marks output, which belongs to Spyglass");
  assert.equal(looksLikeBolt("for i in range(3):\n    say hi\n## sourceMappingURL=x.mcfunction.map\n"), false,
    "and it wins over every other signal, because mecha has already compiled this");
});

test("detection stops at a bounded number of lines", () => {
  const padding = "say hi\n".repeat(SCAN_LIMIT + 50);
  assert.equal(looksLikeBolt(padding + "for i in range(3):\n"), false,
    "a file this long is not worth scanning to prove a negative");
  assert.ok(looksLikeBolt("for i in range(3):\n" + padding),
    "and the limit does not hide a construct near the top");
});

test("a build output path is recognised whatever the slashes", () => {
  assert.ok(isBuildOutput("D:/proj/build/datapack/data/ns/function/x.mcfunction", ["D:/proj/build"]));
  assert.ok(isBuildOutput("D:\\proj\\build\\datapack\\x.mcfunction", ["D:/proj/build/"]));
  assert.equal(isBuildOutput("D:/proj/src/data/ns/function/x.mcfunction", ["D:/proj/build"]), false);
  assert.equal(isBuildOutput("D:/proj/src/x.mcfunction", []), false);
});

// The corpus, which is what the precision claim rests on

test("no generated function in this repository is read as bolt", () => {
  const tests = path.join(ROOT, "..", "..", "python_package", "tests");
  /** @param {string} dir @returns {string[]} */
  const walk = dir => (fs.existsSync(dir) ? fs.readdirSync(dir, { withFileTypes: true }).flatMap(entry => {
    const full = path.join(dir, entry.name);
    return entry.isDirectory() ? walk(full) : (entry.name.endsWith(".mcfunction") ? [full] : []);
  }) : []);

  // Only what a build wrote: the fixture sources under src/ are bolt on purpose.
  const generated = walk(tests).filter(file => file.replace(/\\/g, "/").includes("/build/"));
  assert.ok(generated.length > 100, `expected a real corpus, found ${generated.length} generated functions`);

  const wrong = generated.filter(file => looksLikeBolt(fs.readFileSync(file, "utf8")));
  assert.deepEqual(wrong, [], "a false positive here takes a vanilla file away from Spyglass");
});

test("the fixture that is bolt in a .mcfunction is read as bolt", () => {
  const hello = path.join(ROOT, "..", "..", "python_package", "tests",
    "plugin_25_sniffer_mecha_bolt", "src", "data", "tns", "function", "hello.mcfunction");
  assert.ok(fs.existsSync(hello), "the minimal template's example is the fixture for this");
  assert.ok(looksLikeBolt(fs.readFileSync(hello, "utf8")));
});

// What the manifest promises about a bolt document

test("the extension owns bolt navigation but not the mcfunction language", () => {
  const manifest = JSON.parse(fs.readFileSync(path.join(ROOT, "package.json"), "utf8"));

  assert.ok(manifest.contributes.languages.some((/** @type {{id: string}} */ l) => l.id === "bolt"),
    "the language id is what lets any server select the file");
  assert.ok(!manifest.contributes.languages.some((/** @type {{id: string}} */ l) => l.id === "mcfunction"),
    "FR-015: ownership is partitioned by file, and Spyglass owns mcfunction");
  assert.ok(manifest.activationEvents.includes("onLanguage:bolt"),
    "a bolt file gets lenses and header links, so the extension has to wake for it");
  assert.ok(manifest.contributes.configuration.properties["StewBeet.boltInMcfunction"],
    "taking a file away from Spyglass is the kind of thing that needs a switch");
});

test("the Spyglass-backed providers stay on Python", () => {
  const source = fs.readFileSync(path.join(ROOT, "src", "extension.js"), "utf8");
  const start = source.indexOf("function registerLanguageFeatures");
  const body = source.slice(start, source.indexOf("\n}", start));
  assert.ok(!/language:\s*["']bolt["']/.test(body),
    "completion, hover and signature help need a compiler-backed server for bolt, which this is not");
});

// Telling Spyglass to skip the file, which is the half a language id cannot do

test("an exclusion is added without disturbing the rest of the config", () => {
  const { withExclusions } = require("../src/bolt.js");
  const existing = {
    env: { dependencies: ["@vanilla-datapack"], exclude: ["build/**"] },
    somethingElse: { kept: true },
  };
  const updated = withExclusions(existing, ["src/a.mcfunction"]);
  assert.deepEqual(updated.env.exclude, ["build/**", "src/a.mcfunction"]);
  assert.deepEqual(updated.env.dependencies, ["@vanilla-datapack"], "the project's own settings survive");
  assert.deepEqual(updated.somethingElse, { kept: true });
});

test("a config with nothing in it still gets a well-formed exclude", () => {
  const { withExclusions } = require("../src/bolt.js");
  assert.deepEqual(withExclusions({}, ["a.mcfunction"]), { env: { exclude: ["a.mcfunction"] } });
});

test("adding an exclusion that is already there changes nothing", () => {
  const { withExclusions } = require("../src/bolt.js");
  assert.equal(withExclusions({ env: { exclude: ["a.mcfunction"] } }, ["a.mcfunction"]), null,
    "null is what stops the command rewriting the file on every invocation");
});

test("the pattern is relative to the project root, with forward slashes", () => {
  const { excludePatternFor } = require("../src/bolt.js");
  const root = path.join("D:", "proj");
  const file = path.join(root, "data", "ns", "function", "x.mcfunction");
  assert.equal(excludePatternFor(root, file), "data/ns/function/x.mcfunction",
    "Spyglass matches a forward-slash relative path whatever the platform");
});

test("an existing Spyglass config is preferred over creating a new one", () => {
  const { spyglassConfigPath, SPYGLASS_CONFIG_NAMES } = require("../src/bolt.js");
  const os = require("node:os");
  const root = fs.mkdtempSync(path.join(os.tmpdir(), "stewbeet-spyglassrc-"));
  assert.equal(path.basename(spyglassConfigPath(root)), ".spyglassrc.json", "the default when there is none");

  fs.writeFileSync(path.join(root, "spyglass.json"), "{}");
  assert.equal(path.basename(spyglassConfigPath(root)), "spyglass.json", "never a second config beside the real one");
  assert.equal(SPYGLASS_CONFIG_NAMES[0], "spyglass.json", "Spyglass's own precedence order, kept");
});

test("writing the exclusion round-trips through a real file", () => {
  const { addExclusions } = require("../src/bolt.js");
  const os = require("node:os");
  const root = fs.mkdtempSync(path.join(os.tmpdir(), "stewbeet-spyglassrc-"));
  const file = path.join(root, "data", "ns", "function", "x.mcfunction");

  const first = addExclusions(root, [file]);
  assert.ok(first, "the first call writes");
  assert.deepEqual(JSON.parse(fs.readFileSync(first.path, "utf8")),
    { env: { exclude: ["data/ns/function/x.mcfunction"] } });

  assert.equal(addExclusions(root, [file]), null, "the second call has nothing to do");
});
