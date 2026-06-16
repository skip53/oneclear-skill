# OneClear

> 把销售转述、客户原话、现场工况和报价压力，整理成一份可推进、可追问、可控风险的工业除尘滤料售前判断。

OneClear 是一个面向工业除尘滤料售前技术支持的 Agent Skill。它不是通用销售话术工具，而是帮助 Claude Code、Codex、OpenCode、Cursor 等 agent 处理真实售前场景中的复杂输入：客户只说“压差高”“寿命短”“竞品太贵”“能不能报价”，销售只转述半句话，但技术支持必须先判断真实工况问题、缺失信息、风险边界和下一步追问。

## Interactive by Design (交互式)

OneClear 现在以**多轮状态机**运行，而不是一次性分析：

```text
Round 0  任务识别（Task Menu）         → 1 个菜单问题，确认要做什么
Round 1  建档与分流（Intake）          → 抽 P0 + 分流 + 风险标签
Round 2  主动追问 P1（Discovery）      → 3-7 个问题 + 进度条
...                                       每轮重评 Level
Round N  收敛（Convergence）           → Level 达标才出完整诊断包
Optional Refine 更新包                  → 收敛后增量更新
Blocked  异常终止                       → 风险红线触发，显式升级
```

每轮响应都包含：

- **进度条**（第 X 轮 / 预计 N 轮 · 当前 Level L）
- **已知 ✅ / 未知 ❌ / 矛盾 ⚠️** 三段式现状
- **本轮追问**（内部技术版 + 客户转述版，3-7 个）
- **本案承诺红线**（持续更新）
- **下一步动作**

详细协议见 `references/27-interactive-round-protocol.md`、任务菜单见 `references/28-task-menu.md`、进度显示格式见 `references/29-progress-visibility.md`。

> 关键不变量：oneclear **永远先问任务菜单**，再做任何分析。即使用户一次粘贴了完整对话，也会先确认任务类型，再抽取事实、列缺失字段。

```bash
npx skills add skip53/oneclear-skill
```

安装后可通过 `$oneclear` 调用。

---

## Install

推荐使用 Skills CLI 从 GitHub 安装：

```bash
npx skills add skip53/oneclear-skill
```

只安装到指定 agent 时，可使用 Skills CLI 的 agent 参数，例如：

```bash
npx skills add skip53/oneclear-skill -a claude-code
npx skills add skip53/oneclear-skill -a codex
npx skills add skip53/oneclear-skill -a opencode
npx skills add skip53/oneclear-skill -a cursor
```

非交互安装：

```bash
npx skills add skip53/oneclear-skill --skill oneclear -g -a claude-code -y
```

---

## npm Installer Fallback

OneClear 也提供 npm fallback 安装器：

```bash
npx oneclear install
```

默认安装到：

| Agent | 安装位置 |
|---|---|
| Codex | `~/.codex/skills/oneclear` |
| Claude Code | `~/.claude/skills/oneclear` |
| OpenCode | `~/.config/opencode/skills/oneclear` |
| Cursor | 当前项目的 `.cursor/skills/oneclear` |

指定目标：

```bash
npx oneclear install --target codex
npx oneclear install --target claude
npx oneclear install --target opencode
npx oneclear install --target cursor
npx oneclear install --target codex,cursor
```

Cursor 默认安装到当前目录下的 `.cursor/skills/oneclear`；如需指定项目目录：

```bash
npx oneclear install --target cursor --project-dir /path/to/project
```

已有安装时覆盖：

```bash
npx oneclear install --force
```

预览安装位置，不写入文件：

```bash
npx oneclear install --dry-run
```

不要使用 `npx install oneclear`。在 npm/npx 语义中，这会尝试运行名为 `install` 的包或命令，而不是运行 `oneclear`。正确形式是：

```bash
npx oneclear install
```

---

## What It Does

| 能力 | 输出 | 典型用途 |
|---|---|---|
| **任务菜单识别** | A-J 任务清单 + 推荐默认 | 确认业务员要做什么，再做任何分析 |
| **多轮状态机推进** | Round 0 → Round N → Convergence | 任务分阶段、按轮收集信息、避免一次性输入 |
| **进度条显示** | 第 X 轮 / 预计 N 轮 · Level L | 让业务员实时知道自己在哪、还差什么 |
| 工况档案整理 | 八块工况档案草稿 | 把零散客户原话、销售转述、已知/未知/矛盾信息结构化 |
| 案件分流 | A-H 任务类型 + Level 0-5 评估 | 避免还没搞清楚问题就进入报价或选型 |
| 真实需求判断 | 表层诉求 vs 真实工况问题 vs 商业目标 | 识别“想便宜一点”背后的稳定性、寿命、排放或停机风险 |
| 风险标签 | 温度、含湿、腐蚀、磨蚀、糊袋、火星、清灰、压差等 | 提醒销售不要遗漏关键风险 |
| 追问清单 | 3-7 个 P0/P1 问题，含内部技术版和客户转述版 | 让销售知道下一轮该问什么、怎么问 |
| 报价准备度 | 不可报价 / 预算报价 / 人工确认后正式报价候选 | 防止“先报个价”变成技术承诺 |
| Level 4/5 售前包 | 候选方向、证据要求、试用边界、禁止承诺、人工确认 | 支撑竞品替换、试用验证、招投标、复杂项目推进 |

---

## Example Prompts

### 冷启动（无内容）

```text
$oneclear
```

→ oneclear 直接呈现任务菜单 A-J，让业务员选任务类型，再开始 Round 1。

### 一次性粘贴（快进到 Round 1）

```text
$oneclear
客户是湖南橘子洲水泥股份有限公司，窑尾袋收尘器工况…
[粘贴完整业务员转述]
```

→ oneclear 抽取 P0，推荐默认任务（通常是 B 旧项目故障或 C 替换），呈现任务菜单让业务员确认/修改，然后立刻进入 Round 2 列出仍未缺的 P1。

### 多轮推进（推荐用法）

```text
第 1 轮：$oneclear
业务员：客户水泥窑尾滤袋半年糊袋
oneclear：Round 0 任务菜单 → 选 B → Round 1 列出 8 块档案草稿 + 5 个 P0/P1 问题

第 2 轮：业务员回答部分问题
oneclear：第 2 轮 / 预计 4 轮 · Level 2，列出剩余 3 个 P1 + 进度

第 3 轮：业务员补充压差曲线和现场照片
oneclear：第 3 轮 / 预计 1 轮 · Level 3，已知 11/12，重评风险

第 4 轮：业务员补完最后 1 个字段
oneclear：Convergence · Level 3，输出完整诊断包（工况档案 + 追问 + 诊断 + 红线）
```

### 不同任务类型的示例

```text
$oneclear 客户说水泥窑尾滤袋半年就压差高，清灰下不来，怀疑我们材料质量有问题。销售想让我直接给替换方案。
```
→ 默认任务：B 旧项目故障；如果业务员选 "C 替换/降本" 会追问"当前方案是否稳定"。

```text
$oneclear 客户现在用竞品 PTFE 覆膜袋，觉得价格高，想换便宜一点。工况只知道是垃圾焚烧，排放要求 10mg 以下。
```
→ 默认任务：C 替换/降本；Round 2 重点问当前基线、试用边界。

```text
$oneclear 这是一个新建项目，客户问我们能不能直接报价。已知温度 160-190℃，粉尘细，含湿没说，目标寿命两年。
```
→ 默认任务：A 新项目选型；如果业务员选 "D 报价准备" 会先评估报价 readiness。

```text
$oneclear 客户要试用我们一批，分两个仓对比。
```
→ 默认任务：E 试用验证；Round 1 重点问试用范围、对照基线、验收指标。

---

## Core Mechanics

### 1. 先判断真实问题，再谈方案

OneClear 的最高优先级是：

```text
客户问题真实 > 技术方案可行 > 商业价值明确 > 风险透明 > 推进成交
```

它会先区分客户原话、销售转述、已知事实、未知事实和矛盾点，而不是把“客户想报价”“客户说质量问题”“客户要便宜”直接当成真实需求。

### 2. 先确认任务，再启动诊断

OneClear **永远先问任务菜单**。即使用户一次粘贴了完整对话，也会先抽取 P0 推荐默认任务，让业务员确认/修改，再开始诊断。这避免了"客户问报价"和"客户要选型"被混在一起处理。

### 3. 用 Round 控制节奏

每轮 3-7 个问题，最多 7 轮强制收敛。每轮显示进度（第 X 轮 / 预计 N 轮 · Level L · 已知/未知/矛盾），业务员随时知道自己在哪。

### 4. 用 Level 控制承诺边界

OneClear 使用 0-5 级判断梯度：

| Level | 含义 | 输出边界 |
|---|---|---|
| 0 | 无法分流 | 只能问最小澄清问题 |
| 1 | 可分流，不可诊断 | 可给案件类型和追问路径 |
| 2 | 可初步诊断，不可选型 | 可给风险标签和证据需求 |
| 3 | 可给选型方向，不可确定型号 | 可谈方向，不给最终型号 |
| 4 | 可给候选方案，需人工确认 | 可给 1-3 个候选方向和验证边界 |
| 5 | 可形成技术支持包 | 可形成客户需求摘要、风险假设、候选方向、试用计划和下一步动作 |

### 3. 脚本只做护栏，不替代专家判断

`scripts/` 中包含确定性检查器，用来辅助分类、缺失字段检查、风险标签、输出包校验和规则库评估。脚本输出不是最终选型授权；当脚本和参考文档冲突时，取更严格的承诺边界。

### 4. 售前推进和技术判断放在同一张图里

OneClear 不只判断材料，还会检查决策链、报价准备度、竞品压力、试用验证边界、商业价值量化和内部升级包需求。目标是让销售下一步能推进，而不是拿到一份无法对外使用的技术碎片。

### 5. 每轮边界严格守住

- 不重复问已答字段
- 不超过 7 轮
- 越过任务目标 Level 才收敛
- 触发 Blocked 条件立即停止技术追问

---

## Works With

推荐通过 `npx skills add skip53/oneclear-skill` 安装，Skills CLI 会处理多 agent 兼容。OneClear 当前面向：

| Agent | 推荐方式 | 备注 |
|---|---|---|
| Claude Code | `npx skills add skip53/oneclear-skill -a claude-code` | 也支持 npm fallback 到 `~/.claude/skills/oneclear` |
| Codex | `npx skills add skip53/oneclear-skill -a codex` | 也支持 npm fallback 到 `~/.codex/skills/oneclear` |
| OpenCode | `npx skills add skip53/oneclear-skill -a opencode` | npm fallback 到 `~/.config/opencode/skills/oneclear` |
| Cursor | `npx skills add skip53/oneclear-skill -a cursor` | npm fallback 到当前项目 `.cursor/skills/oneclear` |

---

## Limitations

- OneClear 不替代最终专家签字、现场检查、实验室检测、合同技术承诺或质保承诺。
- 信息不足时，它会降级为追问和风险提示，不会强行推荐具体材料型号。
- 对排放、寿命、替换效果、竞品优劣、招投标响应等内容，会保留人工确认和禁止承诺项。
- npm fallback 的 Cursor 安装是项目级安装；如果希望跨项目复用，优先使用 `npx skills add ...` 的全局安装能力。

---

## Repository Structure

```text
oneclear-skill/
├── SKILL.md                  # Skill 主入口，定义触发条件、流程、承诺边界
├── agents/
│   └── openai.yaml           # Agent UI 元数据
├── references/               # 售前判断知识库与流程参考
│   ├── 00-agent-os-framework.md
│   ├── 02-work-condition-schema.md
│   ├── 09-output-templates.md
│   ├── 17-quote-readiness.md
│   ├── 23-level-4-5-delivery-pack.md
│   └── 26-work-condition-rules.json
├── scripts/                  # 确定性护栏脚本
│   ├── classify_case_type.py
│   ├── check_context_completeness.py
│   ├── risk_tag_rules.py
│   ├── agent_os_governance.py
│   ├── presales_progression.py
│   ├── work_condition_rule_library.py
│   └── validate_output_pack.py
├── examples/                 # 典型售前输入和输出示例
├── bin/oneclear.js            # npm fallback CLI
├── lib/installer.js           # npm fallback 安装器
└── tests/                     # Node installer tests + Python guardrail tests
```

---

## Development

```bash
npm test
python3 -c "import pathlib; print('Run Python tests with the local lightweight runner used in this repo')"
npm pack --dry-run
```

The npm package is a fallback installer. The primary distribution path is the GitHub skill repository:

```bash
npx skills add skip53/oneclear-skill
```

---

## License

MIT License.
