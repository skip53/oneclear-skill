#!/usr/bin/env node

const { installSkill } = require("../lib/installer");

function printHelp() {
  console.log(`OneClear skill installer

Usage:
  oneclear install [--target codex|claude|opencode|cursor|both|all] [--project-dir <path>] [--force] [--dry-run]
  oneclear --help

Examples:
  npx oneclear install
  npx oneclear install --target codex,cursor
  npx oneclear install --target opencode
  npx oneclear install --target claude --force

Note:
  Use "npx oneclear install", not "npx install oneclear".
`);
}

function parseInstallArgs(args) {
  const options = {
    target: "all",
    force: false,
    dryRun: false,
  };

  for (let index = 0; index < args.length; index += 1) {
    const arg = args[index];

    if (arg === "--force") {
      options.force = true;
    } else if (arg === "--dry-run") {
      options.dryRun = true;
    } else if (arg === "--target") {
      const value = args[index + 1];
      if (!value) {
        throw new Error("--target requires codex, claude, opencode, cursor, both, or all.");
      }
      options.target = value;
      index += 1;
    } else if (arg.startsWith("--target=")) {
      options.target = arg.slice("--target=".length);
    } else if (arg === "--project-dir") {
      const value = args[index + 1];
      if (!value) {
        throw new Error("--project-dir requires a path.");
      }
      options.projectDir = value;
      index += 1;
    } else if (arg.startsWith("--project-dir=")) {
      options.projectDir = arg.slice("--project-dir=".length);
    } else {
      throw new Error(`Unknown option: ${arg}`);
    }
  }

  return options;
}

function main(argv = process.argv.slice(2)) {
  const command = argv[0];

  if (!command || command === "--help" || command === "-h") {
    printHelp();
    return 0;
  }

  if (command !== "install") {
    console.error(`Unknown command: ${command}`);
    printHelp();
    return 1;
  }

  try {
    const options = parseInstallArgs(argv.slice(1));
    const result = installSkill(options);
    const action = options.dryRun ? "Would install" : "Installed";

    for (const installTarget of options.dryRun ? result.planned : result.installed) {
      console.log(`${action} OneClear for ${installTarget.name}: ${installTarget.directory}`);
    }

    return 0;
  } catch (error) {
    console.error(`oneclear: ${error.message}`);
    return 1;
  }
}

if (require.main === module) {
  process.exitCode = main();
}

module.exports = { main, parseInstallArgs };
