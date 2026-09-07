// @ts-check
"use strict";

// Offering the language server the string blocks need, once, and never again once it is declined.
//
// Spyglass is a soft dependency on purpose: the grammar, the decorations, the lenses and every
// source-map jump work without it. What does not work is the half a reader assumes is there,
// completion and errors inside the strings, and nothing in the UI says why. This is that missing
// sentence, shown where it is relevant and settled either way with one click.
//
// Free of any "vscode" dependency, so the decision is testable under plain `node --test`.

// Constants

/** Marketplace id of the language server that answers for mcfunction. */
const SPYGLASS_EXTENSION_ID = "SPGoding.datapack-language-server";

/** What the prompt says. Named here so a test can hold it to naming the extension and the reason. */
const OFFER_MESSAGE =
  "These mcfunction strings can have completion, hover and error checking, from the Spyglass " +
  "language server. It is not installed, so they are highlighted and navigable but not checked.";

/** Labels of the three answers, in the order they are shown. */
const OFFER_ACTIONS = ["Install Spyglass", "Not now", "Never"];

// Deciding

/**
 * Whether to offer the install for a document, given everything already known about the session.
 *
 * @param {object} state
 * @param {boolean} state.installed         Spyglass is already there, so there is nothing to offer.
 * @param {boolean} state.suggest           The `suggestSpyglass` setting, which "Never" turns off.
 * @param {boolean} state.languageFeatures  Offering a server for features that are switched off is noise.
 * @param {boolean} state.asked             Already asked in this session.
 * @param {number}  state.blocks            Blocks in the document, which is what makes it relevant.
 * @returns {boolean}
 */
function shouldOffer(state) {
  if (state.installed || !state.suggest || !state.languageFeatures || state.asked) return false;
  return state.blocks > 0;
}

module.exports = {
  SPYGLASS_EXTENSION_ID,
  OFFER_MESSAGE,
  OFFER_ACTIONS,
  shouldOffer,
};
