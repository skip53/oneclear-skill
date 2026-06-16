const assert = require("node:assert/strict");
const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");
const test = require("node:test");

const {
  installSkill,
  resolveTargets,
  SKILL_PAYLOAD_PATHS,
} = require("../lib/installer");

function makeTempHome() {
  return fs.mkdtempSync(path.join(os.tmpdir(), "oneclear-install-"));
}

test("resolveTargets defaults to Codex and Claude skill directories", () => {
  const homeDir = makeTempHome();
  const projectDir = fs.mkdtempSync(path.join(os.tmpdir(), "oneclear-project-"));

  assert.deepEqual(resolveTargets({ target: "all", homeDir, projectDir }), [
    {
      name: "codex",
      directory: path.join(homeDir, ".codex", "skills", "oneclear"),
    },
    {
      name: "claude",
      directory: path.join(homeDir, ".claude", "skills", "oneclear"),
    },
    {
      name: "opencode",
      directory: path.join(homeDir, ".config", "opencode", "skills", "oneclear"),
    },
    {
      name: "cursor",
      directory: path.join(projectDir, ".cursor", "skills", "oneclear"),
    },
  ]);
});

test("resolveTargets still supports the legacy both alias for Codex and Claude", () => {
  const homeDir = makeTempHome();

  assert.deepEqual(resolveTargets({ target: "both", homeDir }), [
    {
      name: "codex",
      directory: path.join(homeDir, ".codex", "skills", "oneclear"),
    },
    {
      name: "claude",
      directory: path.join(homeDir, ".claude", "skills", "oneclear"),
    },
  ]);
});

test("installSkill supports OpenCode and Cursor targets", () => {
  const homeDir = makeTempHome();
  const projectDir = fs.mkdtempSync(path.join(os.tmpdir(), "oneclear-project-"));

  const result = installSkill({
    target: "opencode,cursor",
    homeDir,
    projectDir,
    force: false,
    dryRun: false,
  });

  assert.deepEqual(
    result.installed.map((entry) => entry.directory),
    [
      path.join(homeDir, ".config", "opencode", "skills", "oneclear"),
      path.join(projectDir, ".cursor", "skills", "oneclear"),
    ]
  );
  for (const installTarget of result.installed) {
    assert.match(
      fs.readFileSync(path.join(installTarget.directory, "SKILL.md"), "utf8"),
      /^---\nname: oneclear/m
    );
  }
});

test("installSkill copies only the skill payload into selected target", () => {
  const homeDir = makeTempHome();

  const result = installSkill({
    target: "codex",
    homeDir,
    force: false,
    dryRun: false,
  });

  const installDir = path.join(homeDir, ".codex", "skills", "oneclear");

  assert.equal(result.installed.length, 1);
  assert.equal(result.installed[0].directory, installDir);
  for (const payloadPath of SKILL_PAYLOAD_PATHS) {
    assert.equal(fs.existsSync(path.join(installDir, payloadPath)), true);
  }
  assert.equal(fs.existsSync(path.join(installDir, "package.json")), false);
  assert.equal(fs.existsSync(path.join(installDir, "bin")), false);
  assert.equal(fs.existsSync(path.join(installDir, "lib")), false);
  assert.equal(fs.existsSync(path.join(installDir, "scripts", "__pycache__")), false);
});

test("installSkill refuses to overwrite an existing install without force", () => {
  const homeDir = makeTempHome();
  const installDir = path.join(homeDir, ".claude", "skills", "oneclear");
  fs.mkdirSync(installDir, { recursive: true });
  fs.writeFileSync(path.join(installDir, "SKILL.md"), "local edit\n");

  assert.throws(
    () => installSkill({ target: "claude", homeDir, force: false }),
    /already exists/
  );
  assert.equal(fs.readFileSync(path.join(installDir, "SKILL.md"), "utf8"), "local edit\n");
});

test("installSkill overwrites an existing install when force is true", () => {
  const homeDir = makeTempHome();
  const installDir = path.join(homeDir, ".claude", "skills", "oneclear");
  fs.mkdirSync(installDir, { recursive: true });
  fs.writeFileSync(path.join(installDir, "stale.txt"), "remove me\n");

  installSkill({ target: "claude", homeDir, force: true });

  assert.equal(fs.existsSync(path.join(installDir, "stale.txt")), false);
  assert.match(fs.readFileSync(path.join(installDir, "SKILL.md"), "utf8"), /^---\nname: oneclear/m);
});

test("installSkill dry run reports targets without writing files", () => {
  const homeDir = makeTempHome();

  const result = installSkill({ target: "codex", homeDir, dryRun: true });

  assert.equal(result.installed.length, 0);
  assert.equal(result.planned.length, 1);
  assert.equal(
    fs.existsSync(path.join(homeDir, ".codex", "skills", "oneclear")),
    false
  );
});

test("package files list excludes generated cache directories", () => {
  const packageJson = require("../package.json");

  assert.equal(packageJson.files.includes("scripts"), false);
  assert.equal(packageJson.files.some((entry) => entry.endsWith("__pycache__")), false);
  assert.equal(packageJson.files.includes("scripts/classify_case_type.py"), true);
  assert.equal(packageJson.files.includes("scripts/work_condition_rule_library.py"), true);
});
