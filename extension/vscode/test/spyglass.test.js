// @ts-check
"use strict";

// When the extension offers to install the language server, and when it keeps quiet.
//
// The offer is the one piece of UI that fires without being asked for, so every condition that
// suppresses it matters more than the one that shows it.

const { test } = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");

const { SPYGLASS_EXTENSION_ID, OFFER_MESSAGE, OFFER_ACTIONS, shouldOffer } = require("../src/spyglass");

/** The state in which the offer is meant to appear, so each test changes one thing. */
const RELEVANT = { installed: false, suggest: true, languageFeatures: true, asked: false, blocks: 3 };

test("a Python file with blocks and no Spyglass gets the offer", () => {
  assert.ok(shouldOffer(RELEVANT));
});

test("a file with no blocks is not what the offer is about", () => {
  assert.equal(shouldOffer({ ...RELEVANT, blocks: 0 }), false,
    "the reason to install it is the strings, so a file without any is the wrong place to ask");
});

test("nothing is offered when Spyglass is already there", () => {
  assert.equal(shouldOffer({ ...RELEVANT, installed: true }), false);
});

test("the setting is what Never writes, and it holds", () => {
  assert.equal(shouldOffer({ ...RELEVANT, suggest: false }), false);
});

test("switching the language features off silences the offer for them", () => {
  assert.equal(shouldOffer({ ...RELEVANT, languageFeatures: false }), false,
    "offering a server for features that are turned off is noise");
});

test("asking once is asking once", () => {
  assert.equal(shouldOffer({ ...RELEVANT, asked: true }), false);
});

// What the prompt says, and what the manifest promises about it

test("the message names what is missing and what still works", () => {
  assert.match(OFFER_MESSAGE, /Spyglass/, "a prompt that does not name the extension cannot be acted on");
  assert.match(OFFER_MESSAGE, /not installed/, "the reason has to be in the sentence");
  assert.equal(OFFER_ACTIONS.length, 3, "install, later, never");
});

test("the offer has a setting and a command behind it", () => {
  const manifest = JSON.parse(fs.readFileSync(path.join(__dirname, "..", "package.json"), "utf8"));

  assert.ok(manifest.contributes.configuration.properties["StewBeet.suggestSpyglass"],
    "Never writes a setting rather than a hidden flag, so it must exist to be found again");
  assert.ok(manifest.contributes.commands.some((/** @type {{command: string}} */ c) => c.command === "stewbeet.installSpyglass"),
    "someone who answered Not now needs a way back to it");
  assert.ok(!(manifest.extensionDependencies || []).includes(SPYGLASS_EXTENSION_ID),
    "a hard dependency would force the install on everyone, and everything else works without it");
});
