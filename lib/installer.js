const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");

const SKILL_NAME = "oneclear";
const PACKAGE_ROOT = path.resolve(__dirname, "..");
const SKILL_PAYLOAD_PATHS = [
  "SKILL.md",
  "agents",
  "examples",
  "references",
  "scripts",
];

const SKIP_NAMES = new Set([".DS_Store", "__pycache__"]);

function normalizeTargetList(target) {
  if (Array.isArray(target)) {
    return target.flatMap(normalizeTargetList);
  }

  return String(target)
    .split(",")
    .map((entry) => entry.trim().toLowerCase())
    .filter(Boolean);
}

function resolveTargets({
  target = "all",
  homeDir = os.homedir(),
  projectDir = process.cwd(),
} = {}) {
  const normalizedTargets = normalizeTargetList(target);
  const targets = {
    codex: {
      name: "codex",
      directory: path.join(homeDir, ".codex", "skills", SKILL_NAME),
    },
    claude: {
      name: "claude",
      directory: path.join(homeDir, ".claude", "skills", SKILL_NAME),
    },
    opencode: {
      name: "opencode",
      directory: path.join(homeDir, ".config", "opencode", "skills", SKILL_NAME),
    },
    cursor: {
      name: "cursor",
      directory: path.join(projectDir, ".cursor", "skills", SKILL_NAME),
    },
  };

  if (normalizedTargets.includes("all")) {
    return [targets.codex, targets.claude, targets.opencode, targets.cursor];
  }
  if (normalizedTargets.includes("both")) {
    return [targets.codex, targets.claude];
  }

  const resolved = [];
  for (const normalized of normalizedTargets) {
    if (!targets[normalized]) {
      throw new Error("Invalid target. Use codex, claude, opencode, cursor, both, or all.");
    }
    resolved.push(targets[normalized]);
  }

  return resolved;
}

function ensureSourcePayload(sourceRoot = PACKAGE_ROOT) {
  for (const payloadPath of SKILL_PAYLOAD_PATHS) {
    const absolutePath = path.join(sourceRoot, payloadPath);
    if (!fs.existsSync(absolutePath)) {
      throw new Error(`Package is missing required skill payload: ${payloadPath}`);
    }
  }
}

function copyRecursive(source, destination) {
  const name = path.basename(source);
  if (SKIP_NAMES.has(name)) {
    return;
  }

  const stat = fs.statSync(source);
  if (stat.isDirectory()) {
    fs.mkdirSync(destination, { recursive: true });
    for (const entry of fs.readdirSync(source)) {
      copyRecursive(path.join(source, entry), path.join(destination, entry));
    }
    return;
  }

  if (stat.isFile()) {
    fs.mkdirSync(path.dirname(destination), { recursive: true });
    fs.copyFileSync(source, destination);
  }
}

function installSkill({
  target = "both",
  homeDir = os.homedir(),
  projectDir = process.cwd(),
  force = false,
  dryRun = false,
  sourceRoot = PACKAGE_ROOT,
} = {}) {
  ensureSourcePayload(sourceRoot);
  const targets = resolveTargets({ target, homeDir, projectDir });
  const result = { planned: [], installed: [] };

  for (const installTarget of targets) {
    result.planned.push(installTarget);
    if (fs.existsSync(installTarget.directory) && !force) {
      throw new Error(
        `${installTarget.directory} already exists. Re-run with --force to overwrite it.`
      );
    }
  }

  if (dryRun) {
    return result;
  }

  for (const installTarget of targets) {
    fs.rmSync(installTarget.directory, { recursive: true, force: true });
    fs.mkdirSync(installTarget.directory, { recursive: true });

    for (const payloadPath of SKILL_PAYLOAD_PATHS) {
      copyRecursive(
        path.join(sourceRoot, payloadPath),
        path.join(installTarget.directory, payloadPath)
      );
    }

    result.installed.push(installTarget);
  }

  return result;
}

module.exports = {
  installSkill,
  resolveTargets,
  SKILL_NAME,
  SKILL_PAYLOAD_PATHS,
};
