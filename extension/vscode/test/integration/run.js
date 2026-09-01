// @ts-check
"use strict";

// Launch the integration test in a VS Code extension host.
//   node test/integration/run.js
//
// Two traps this script exists to avoid:
//
// 1. When launched from inside VS Code's own terminal or an extension host,
//    ELECTRON_RUN_AS_NODE=1 is inherited and Code.exe then behaves as plain
//    Node, rejecting every VS Code flag with "bad option:". VSCODE_IPC_HOOK is
//    worse: it makes the launch attach to the running editor instead of
//    starting a new one. Both are cleared below.
// 2. The `code` CLI wrapper detaches, so it returns 0 immediately and the
//    result is never seen. The Electron binary is invoked directly instead.

const { spawnSync } = require("node:child_process");
const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");

const HERE = __dirname;
const EXT_ROOT = path.resolve(HERE, "..", "..");
const OUT = path.join(HERE, "result.json");

const CANDIDATES = [
  process.env.VSCODE_EXE,
  "D:\\Programs\\Microsoft VS Code\\Code.exe",
  "C:\\Program Files\\Microsoft VS Code\\Code.exe",
  path.join(os.homedir(), "AppData", "Local", "Programs", "Microsoft VS Code", "Code.exe"),
  "/usr/share/code/code",
  "/Applications/Visual Studio Code.app/Contents/MacOS/Electron",
].filter(Boolean);

const exe = CANDIDATES.find(p => p && fs.existsSync(p));
if (!exe) {
  console.error("Could not find the VS Code executable. Set VSCODE_EXE to its full path.");
  console.error("Tried:\n  " + CANDIDATES.join("\n  "));
  process.exit(1);
}

const env = { ...process.env, SB_OUT: OUT };
for (const key of Object.keys(env)) {
  if (key === "ELECTRON_RUN_AS_NODE" || key.startsWith("VSCODE_")) delete env[key];
}

// Extensions that only slow the host down or add noise to the log.
const NOISY = [
  "anthropic.claude-code", "supermaven.supermaven", "eamodio.gitlens",
  "ms-python.vscode-pylance", "ms-python.python", "donjayamanne.python-extension-pack",
  "icrawl.discord-vscode",
];

fs.rmSync(OUT, { force: true });

const args = [
  `--extensionDevelopmentPath=${EXT_ROOT}`,
  `--extensionTestsPath=${path.join(HERE, "index.js")}`,
  `--user-data-dir=${path.join(HERE, ".udd")}`,
  "--new-window", "--disable-gpu", "--disable-workspace-trust",
  ...NOISY.flatMap(id => ["--disable-extension", id]),
  path.join(HERE, "fixture"),
];

console.log(`Launching ${exe}\nA VS Code window will open, run the checks and close itself.`);
const res = spawnSync(exe, args, { env, stdio: ["ignore", "ignore", "pipe"], encoding: "utf8" });

if (!fs.existsSync(OUT)) {
  console.error(`No result written. Exit code ${res.status}.`);
  console.error((res.stderr || "").split("\n").slice(-20).join("\n"));
  process.exit(1);
}

const result = JSON.parse(fs.readFileSync(OUT, "utf8"));
for (const line of result.checks || []) console.log("  " + line);
if (result.error) console.error(result.error);
console.log(`\nVERDICT: ${result.VERDICT}`);
process.exit(String(result.VERDICT || "").startsWith("PASS") ? 0 : 1);
