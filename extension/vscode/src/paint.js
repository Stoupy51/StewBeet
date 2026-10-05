// @ts-check
"use strict";

// Colours for the blocks no grammar rule can reach.
//
// The injection grammar colours a block from the lines around its opening quote: a write_* call, a
// variable annotated McFunction. A block handed to a function or a class of the project's own, or
// to a variable nothing annotates, is found by reading the whole file, which a grammar cannot do,
// so VS Code shows it as a plain string. This paints those blocks with the colours the grammar
// would have given them: the same grammar, run by vscode-textmate, the engine VS Code itself uses,
// against the theme in use and the author's own token colour customizations.

const fs = require("fs");
const path = require("path");

// Required lazily, so everything but the adapter at the bottom loads under plain `node --test`.
/** @returns {typeof import("vscode")} */
function api() {
  return require("vscode");
}

const SYNTAXES = path.join(__dirname, "..", "syntaxes");

/** The scope the injection opens around a block it colours. */
const INJECTED = "meta.embedded.block.mcfunction.stewbeet";

/** A call the injection colours whatever string it is handed, put in front of a block's own opening quote. */
const PRELUDE = 'write_function("", ';

/** VS Code's `editor.foreground` for a theme that sets none, by `uiTheme`. */
const DEFAULT_FOREGROUND = { "vs-dark": "#BBBBBB", vs: "#333333", "hc-black": "#FFFFFF", "hc-light": "#292929" };

/** The scopes each shorthand of `editor.tokenColorCustomizations` stands for, in the order VS Code applies them. */
const CUSTOMIZATION_GROUPS = {
  comments: ["comment", "punctuation.definition.comment"],
  strings: ["string", "meta.embedded.assembly"],
  keywords: ["keyword - keyword.operator", "keyword.control", "storage", "storage.type"],
  numbers: ["constant.numeric"],
  types: ["entity.name.type", "entity.name.class", "support.type", "support.class"],
  functions: ["entity.name.function", "support.function"],
  variables: ["variable", "entity.name.variable"],
};

/** Blocks remembered by `paintsOf` before the memo starts over, which a long session of edits would otherwise grow without end. */
const MEMO_LIMIT = 5000;

/** Bits of a token's metadata, from vscode-textmate's `EncodedTokenMetadata`. */
const FONT_STYLE_MASK = 0b00000000000000000111100000000000;
const FONT_STYLE_OFFSET = 11;
const FOREGROUND_MASK = 0b00000000111111111000000000000000;
const FOREGROUND_OFFSET = 15;

// Engine

/** @type {Promise<{ vsctm: any, registry: any }> | null} */
let engine = null;

/**
 * The TextMate registry with MagicPython, this extension's grammars and the injection, wired as VS Code wires them.
 * Created once, since the regex engine can be loaded only once per process.
 * @param {string} pythonGrammar  Path of MagicPython.tmLanguage.json, which ships inside VS Code.
 */
function createEngine(pythonGrammar) {
  engine ??= (async () => {
    const vsctm = require("vscode-textmate");
    const oniguruma = require("vscode-oniguruma");
    await oniguruma.loadWASM(fs.readFileSync(require.resolve("vscode-oniguruma/release/onig.wasm")).buffer);
    /** @type {Record<string, string>} */
    const files = {
      "source.python": pythonGrammar,
      "source.mcfunction.embedded": path.join(SYNTAXES, "mcfunction-embedded.tmLanguage.json"),
      "stewbeet.mcfunction-injection": path.join(SYNTAXES, "mcfunction-injection.tmLanguage.json"),
      "source.bolt": path.join(SYNTAXES, "bolt.tmLanguage.json"),
    };
    const registry = new vsctm.Registry({
      onigLib: Promise.resolve({
        createOnigScanner: (/** @type {string[]} */ sources) => new oniguruma.OnigScanner(sources),
        createOnigString: (/** @type {string} */ text) => new oniguruma.OnigString(text),
      }),
      loadGrammar: (/** @type {string} */ scope) => Promise.resolve(
        files[scope] ? vsctm.parseRawGrammar(fs.readFileSync(files[scope], "utf8"), files[scope]) : null),
      getInjections: (/** @type {string} */ scope) => (scope === "source.python" ? ["stewbeet.mcfunction-injection"] : undefined),
    });
    return { vsctm, registry };
  })();
  return engine;
}

// Painting (pure but for the engine)

/**
 * Each run of a block the grammar leaves plain, with the style the grammar would have given it.
 *
 * Whether the grammar reaches a block is asked of the grammar itself, from the line of the call or
 * assignment the block belongs to. A block it does not reach is tokenized as the second argument of
 * a write_* call, which is a place the injection always colours, so every scope it gets is the one
 * a coloured block has.
 *
 * @param {{ vsctm: any, python: any }} tokenizer  `python` is the source.python grammar, with a theme set.
 * @param {string} text  The Python document.
 * @param {{ start:number, contentStart:number, contentEnd:number, callStart?:number }[]} blocks
 * @param {Map<string, { line:number, from:number, to:number, metadata:number }[]>} memo  Each block's paints by its text,
 *   so a keystroke pays for the block it changed. Only valid for the theme it was filled under.
 * @returns {{ line:number, from:number, to:number, metadata:number }[]}
 */
function paintsOf(tokenizer, text, blocks, memo = new Map()) {
  const lines = text.split("\n");
  const starts = [0];
  for (const line of lines) starts.push(starts[starts.length - 1] + line.length + 1);
  /** @param {number} offset */
  const positionOf = offset => {
    let line = 0;
    while (starts[line + 1] <= offset) line++;
    return { line, character: offset - starts[line] };
  };

  return blocks.flatMap(block => {
    if (block.contentEnd <= block.contentStart) return [];
    const from = positionOf(Math.min(block.callStart ?? block.start, block.start)).line;
    // Lines counted from `from`, so a block that only moved is found again.
    const [open, content, end] = [block.start, block.contentStart, block.contentEnd]
      .map(offset => positionOf(offset)).map(({ line, character }) => ({ line: line - from, character }));
    const window = lines.slice(from, end.line + from + 1);
    const key = `${open.line},${open.character},${content.line},${content.character},${end.line},${end.character}\n${window.join("\n")}`;
    if (!memo.has(key)) memo.set(key, reachedByGrammar(tokenizer, window, content) ? [] : paintBlock(tokenizer, window, open, content, end));
    return (memo.get(key) ?? []).map(paint => ({ ...paint, line: paint.line + from }));
  });
}

/**
 * A block's paints, tokenized as the second argument of a write_* call.
 * @param {{ vsctm: any, python: any }} tokenizer
 * @param {string[]} lines
 * @param {{ line:number, character:number }} open  Its prefix or opening quote.
 * @param {{ line:number, character:number }} content  Its first command character.
 * @param {{ line:number, character:number }} end  Just past its last command character.
 */
function paintBlock({ vsctm, python }, lines, open, content, end) {
  const paints = [];
  let state = vsctm.INITIAL;
  for (let line = open.line; line <= end.line; line++) {
    const shift = line === open.line ? PRELUDE.length - open.character : 0;
    const source = line === open.line ? PRELUDE + lines[line].slice(open.character) : lines[line];
    const { tokens, ruleStack } = python.tokenizeLine2(source, state);
    state = ruleStack;
    const lower = line === content.line ? content.character : 0;
    const upper = line === end.line ? end.character : lines[line].length;
    for (let i = 0; i < tokens.length; i += 2) {
      const tokenFrom = Math.max(lower, tokens[i] - shift);
      const tokenTo = Math.min(upper, (i + 2 < tokens.length ? tokens[i + 2] : source.length) - shift);
      if (tokenTo > tokenFrom) paints.push({ line, from: tokenFrom, to: tokenTo, metadata: tokens[i + 1] });
    }
  }
  return paints;
}

/**
 * Whether the grammar colours a block, read off the first character of its commands.
 * @param {{ vsctm: any, python: any }} tokenizer
 * @param {string[]} lines  From the line the call or assignment the block belongs to starts on.
 * @param {{ line:number, character:number }} content  Where its commands start.
 */
function reachedByGrammar({ vsctm, python }, lines, content) {
  let state = vsctm.INITIAL;
  for (let line = 0; line <= content.line + 1 && line < lines.length; line++) {
    const { tokens, ruleStack } = python.tokenizeLine(lines[line], state);
    state = ruleStack;
    const first = tokens.find((/** @type {{ startIndex:number, endIndex:number }} */ token) =>
      (line > content.line || token.endIndex > content.character) && lines[line].slice(token.startIndex, token.endIndex).trim());
    if (line >= content.line && first) return first.scopes.includes(INJECTED);
  }
  return true;
}

/**
 * The colour and font style of a token's metadata.
 * @param {number} metadata
 * @param {string[]} colorMap  From the registry the theme was set on.
 * @returns {{ color: string, fontStyle: number }}
 */
function styleOf(metadata, colorMap) {
  return {
    color: colorMap[(metadata & FOREGROUND_MASK) >>> FOREGROUND_OFFSET],
    fontStyle: (metadata & FONT_STYLE_MASK) >>> FONT_STYLE_OFFSET,
  };
}

// Themes (pure)

/**
 * JSON with the comments and trailing commas a theme file is allowed.
 * @param {string} source
 *
 * >>> parseJsonc('{ "a": [1, 2,], // note\n "b": "x//y", /* c *\/ }')
 * { a: [1, 2], b: "x//y" }
 */
function parseJsonc(source) {
  let out = "";
  for (let i = 0; i < source.length; i++) {
    const char = source[i];
    if (char === '"') {
      const close = closingQuote(source, i);
      out += source.slice(i, close + 1);
      i = close;
    } else if (char === "/" && source[i + 1] === "/") {
      while (i + 1 < source.length && source[i + 1] !== "\n") i++;
    } else if (char === "/" && source[i + 1] === "*") {
      i = source.indexOf("*/", i + 2) + 1;
      if (i === 0) break;
    } else if (char !== "," || !/^\s*(?:\/\/[^\n]*\s*|\/\*[\s\S]*?\*\/\s*)*[}\]]/.test(source.slice(i + 1))) {
      out += char;
    }
  }
  return JSON.parse(out);
}

/** @param {string} source @param {number} open */
function closingQuote(source, open) {
  let i = open + 1;
  while (i < source.length && source[i] !== '"') i += source[i] === "\\" ? 2 : 1;
  return i;
}

/**
 * A theme file's TextMate rules and colours, its `include` chain first, as VS Code merges them.
 * @param {string} file
 * @param {(content: string, file: string) => any} parsePlist  Reads a `.tmTheme`, which is a plist.
 * @returns {{ rules: any[], colors: Record<string, string> }}
 */
function readTheme(file, parsePlist) {
  const content = fs.readFileSync(file, "utf8");
  const theme = file.endsWith(".json") ? parseJsonc(content) : parsePlist(content, file);
  const base = theme.include ? readTheme(path.join(path.dirname(file), theme.include), parsePlist) : { rules: [], colors: {} };
  const own = typeof theme.tokenColors === "string"
    ? readTheme(path.join(path.dirname(file), theme.tokenColors), parsePlist).rules
    : theme.tokenColors ?? theme.settings ?? [];
  return { rules: [...base.rules, ...own], colors: { ...base.colors, ...theme.colors } };
}

/**
 * The rules `editor.tokenColorCustomizations` adds after the theme's: the general ones, then the sections naming the theme, merged as VS Code merges them.
 * @param {Record<string, any>} customizations
 * @param {string} settingsId  The theme's id, or its label when it has none, which is all a `[Theme Name]` section is matched against.
 */
function customRules(customizations, settingsId) {
  return [customizations, forTheme(customizations, settingsId)].flatMap(section => [
    ...Object.entries(CUSTOMIZATION_GROUPS).filter(([group]) => section[group]).flatMap(([group, scopes]) =>
      scopes.map(scope => ({ scope, settings: typeof section[group] === "string" ? { foreground: section[group] } : section[group] }))),
    ...(Array.isArray(section.textMateRules) ? section.textMateRules.filter((/** @type {any} */ rule) => rule.scope && rule.settings) : []),
  ]);
}

/**
 * The `[Theme Name]` sections of a customization setting that name the theme, merged into one: a later value wins and lists are joined.
 * A name may start or end with `*`, and several may share one key, as in `[Monokai][*Modern]`.
 * @param {Record<string, any>} customizations
 * @param {string} settingsId
 * @returns {Record<string, any>}
 *
 * >>> forTheme({ "[Monokai][*Modern]": { comments: "#000" }, "[Default Dark Modern]": { strings: "#111" } }, "Dark Modern")
 * { comments: "#000" }
 */
function forTheme(customizations, settingsId) {
  /** @type {Record<string, any>} */
  const merged = {};
  for (const [key, section] of Object.entries(customizations)) {
    if (!/^\[.*\]$/.test(key) || !section || typeof section !== "object" || Array.isArray(section)) continue;
    if (![...key.matchAll(/\[(.+?)\]/g)].some(([, name]) => namesTheme(name, settingsId))) continue;
    for (const [field, value] of Object.entries(section)) {
      merged[field] = Array.isArray(merged[field]) && Array.isArray(value) ? [...merged[field], ...value] : value || merged[field];
    }
  }
  return merged;
}

/**
 * Whether one name of a `[...]` key is the theme's: the same id, or a `*` at either end standing for the rest of it.
 * @param {string} name
 * @param {string} settingsId
 */
function namesTheme(name, settingsId) {
  const [first, last] = [name.startsWith("*"), name.endsWith("*")];
  return name === settingsId
    || (first && last && settingsId.includes(name.slice(1, -1)))
    || (last && settingsId.startsWith(name.slice(0, -1)))
    || (first && settingsId.endsWith(name.slice(1)));
}

/**
 * Every rule VS Code sets on its tokenizer for a theme, in its order: the default colours, the theme's rules, then the author's.
 * @param {{ rules: any[], colors: Record<string, string> }} theme
 * @param {string} uiTheme  `vs-dark`, `vs`, `hc-black` or `hc-light`.
 * @param {any[]} custom  From `customRules`.
 * @param {Record<string, string>} colorCustomizations  `workbench.colorCustomizations`, resolved for this theme.
 */
function themeRules(theme, uiTheme, custom, colorCustomizations) {
  const colors = { ...theme.colors, ...colorCustomizations };
  const foreground = colors["editor.foreground"] ?? DEFAULT_FOREGROUND[/** @type {keyof typeof DEFAULT_FOREGROUND} */ (uiTheme)] ?? DEFAULT_FOREGROUND["vs-dark"];
  return [
    { settings: { foreground, background: colors["editor.background"] } },
    ...[...theme.rules, ...custom].filter(rule => rule && rule.scope && rule.settings),
  ];
}

// Adapter

/**
 * Paint the blocks no grammar rule reaches in every Python editor, and keep them painted across edits and theme changes.
 *
 * Nothing is painted until the theme is read, and nothing at all when it cannot be: an unpainted
 * block is what VS Code shows anyway, and a wrong colour is worse than none.
 *
 * @param {import("vscode").ExtensionContext} context
 * @param {(text: string) => { start:number, contentStart:number, contentEnd:number, callStart?:number }[]} blocksOf
 */
function registerPainting(context, blocksOf) {
  const vscode = api();
  /** @type {{ vsctm: any, python: any, colorMap: string[] } | null} */
  let tokenizer = null;
  /** One decoration type per colour and font style. @type {Map<string, import("vscode").TextEditorDecorationType>} */
  const styles = new Map();
  /** See `paintsOf`, emptied with every theme. @type {Map<string, any[]>} */
  const memo = new Map();

  /** @param {import("vscode").TextEditor} editor */
  function paint(editor) {
    if (editor.document.languageId !== "python") return;
    /** @type {Map<string, import("vscode").Range[]>} */
    const ranges = new Map([...styles.keys()].map(key => [key, []]));
    if (tokenizer) {
      if (memo.size > MEMO_LIMIT) memo.clear();
      const text = editor.document.getText();
      for (const { line, from, to, metadata } of paintsOf(tokenizer, text, blocksOf(text), memo)) {
        const { color, fontStyle } = styleOf(metadata, tokenizer.colorMap);
        const key = `${color}|${fontStyle}`;
        if (!styles.has(key)) styles.set(key, decorationFor(color, fontStyle));
        ranges.set(key, [...(ranges.get(key) ?? []), new vscode.Range(line, from, line, to)]);
      }
    }
    for (const [key, list] of ranges) editor.setDecorations(/** @type {any} */ (styles.get(key)), list);
  }

  /** @param {string} color @param {number} fontStyle */
  function decorationFor(color, fontStyle) {
    return vscode.window.createTextEditorDecorationType({
      color,
      fontStyle: fontStyle & 1 ? "italic" : "normal",
      fontWeight: fontStyle & 2 ? "bold" : "normal",
      textDecoration: [fontStyle & 4 ? "underline" : "", fontStyle & 8 ? "line-through" : ""].join(" ").trim() || "none",
    });
  }

  async function loadTheme() {
    try {
      const pythonGrammar = path.join(vscode.extensions.getExtension("vscode.python")?.extensionPath ?? "", "syntaxes", "MagicPython.tmLanguage.json");
      const { vsctm, registry } = await createEngine(pythonGrammar);
      const found = activeTheme(vscode);
      if (!found) {
        tokenizer = null;
      } else {
        const workbench = vscode.workspace.getConfiguration("workbench");
        const editor = vscode.workspace.getConfiguration("editor");
        const colorCustomizations = workbench.get("colorCustomizations") ?? {};
        const custom = customRules(editor.get("tokenColorCustomizations") ?? {}, found.settingsId);
        const colors = { ...colorCustomizations, ...forTheme(colorCustomizations, found.settingsId) };
        registry.setTheme({ settings: themeRules(readTheme(found.file, vsctm.parseRawGrammar), found.uiTheme, custom, colors) });
        tokenizer = { vsctm, python: await registry.loadGrammar("source.python"), colorMap: registry.getColorMap() };
      }
    } catch (e) {
      console.debug("[StewBeet] could not read the colour theme, blocks no grammar reaches stay unpainted", e);
      tokenizer = null;
    }
    for (const style of styles.values()) style.dispose();
    styles.clear();
    memo.clear();
    vscode.window.visibleTextEditors.forEach(paint);
  }

  context.subscriptions.push(
    vscode.window.onDidChangeActiveColorTheme(loadTheme),
    vscode.workspace.onDidChangeConfiguration(e => {
      if (e.affectsConfiguration("editor.tokenColorCustomizations") || e.affectsConfiguration("workbench.colorCustomizations")) loadTheme();
    }),
    vscode.window.onDidChangeVisibleTextEditors(editors => editors.forEach(paint)),
    vscode.workspace.onDidChangeTextDocument(e => {
      for (const editor of vscode.window.visibleTextEditors) if (editor.document === e.document) paint(editor);
    }),
    { dispose: () => styles.forEach(style => style.dispose()) },
  );
  loadTheme();
}

/**
 * The theme file in use, found among the themes every installed extension contributes.
 * @param {typeof import("vscode")} vscode
 * @returns {{ file: string, uiTheme: string, settingsId: string } | null}
 */
function activeTheme(vscode) {
  const workbench = vscode.workspace.getConfiguration("workbench");
  const kind = vscode.window.activeColorTheme.kind;
  const preferred = { 1: "preferredLightColorTheme", 2: "preferredDarkColorTheme", 3: "preferredHighContrastColorTheme", 4: "preferredHighContrastLightColorTheme" };
  const setting = vscode.workspace.getConfiguration("window").get("autoDetectColorScheme")
    ? preferred[/** @type {1 | 2 | 3 | 4} */ (kind)] : "colorTheme";
  const wanted = workbench.get(setting);
  for (const extension of vscode.extensions.all) {
    for (const theme of extension.packageJSON?.contributes?.themes ?? []) {
      if ((theme.id ?? theme.label) !== wanted) continue;
      return { file: path.join(extension.extensionPath, theme.path), uiTheme: theme.uiTheme, settingsId: theme.id ?? theme.label };
    }
  }
  return null;
}

module.exports = {
  createEngine, paintsOf, styleOf, parseJsonc, readTheme, customRules, forTheme, themeRules, registerPainting, activeTheme,
};
