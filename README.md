<sub>🌐 <b>中文</b></sub>

<div align="center">

# OneClear

> *「一句转述进去，一份可推进的售前判断出来。」*

[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![npm](https://img.shields.io/npm/v/oneclear)](https://www.npmjs.com/package/oneclear)
[![Agent Skill](https://img.shields.io/badge/Skill-Claude%20%7C%20Codex%20%7C%20Cursor-blueviolet)](https://skills.sh)

<br>

**工业除尘滤料售前技术支持的 Agent Skill。**

<br>

客户只说「压差高」「寿命短」「竞品太贵」——技术支持的第一遍工作是：
听转述、挑真实工况问题、判断信息够不够、决定现在能说什么、必须先问什么。

OneClear 把这段过程结构化成**多轮状态机**：每轮 3-7 个追问，信息攒够才出结论，Level 不够不承诺。

```bash
npx oneclear install
```

Claude Code · Codex · OpenCode · Cursor 跨 agent 通用。

</div>

---

## 安装

推荐用 Skills CLI：

```bash
npx skills add skip53/oneclear-skill
```

npm fallback：

```bash
npx oneclear install                          # 安装到所有支持的 agent
npx oneclear install --target claude          # 只装 Claude Code
npx oneclear install --target codex,cursor    # 多选
```

装好后，在 agent 里用 `$oneclear` 触发。

---

## 解决什么问题

| 坑 | 表现 | 后果 |
|---|---|---|
| 表层诉求当真实需求 | "客户说便宜点" → 直接降配 | 寿命缩短、排放超标、客户投诉 |
| 信息不足就下判断 | 没有压差曲线就给选型方向 | 把责任和风险一起背了 |
| 节奏失控 | 一次问十个问题，或者什么都不问就出报告 | 客户流失或错误承诺 |

---

## 怎么工作

不是一次性报告，是**多轮来回**——每轮更新进度、重评 Level，信息够了才收敛。

<div align="center">
<img src="https://raw.githubusercontent.com/skip53/oneclear-skill/main/docs/flow-overview.jpg" width="700" alt="OneClear 多轮状态机流程">
</div>

---

## 判断深度（Level 0–5）

Level 决定「能说到哪」。每轮都会重评；信息不够，Level 上不去，承诺边界卡住。

<div align="center">
<img src="https://raw.githubusercontent.com/skip53/oneclear-skill/main/docs/flow-levels.png" width="800" alt="Level 0–5 判断深度">
</div>

| Level | 触发条件 | 能说的边界 |
|---|---|---|
| 0 | 基本信息不足，无法分流 | 只问最小澄清问题 |
| 1 | 可分流，工况未建档 | 给案件类型和追问路径 |
| 2 | 可初步诊断，缺证据 | 给风险标签和证据需求 |
| 3 | 主要工况齐，缺细节 | 给材质方向，不定具体型号 |
| 4 | 工况基本完整 | 给 1-3 个候选方向 + 验证边界，需人工确认 |
| 5 | 全部字段齐备 | 完整技术支持包：需求摘要、试用计划、下一步 |

---

## 能力一览

| 能力 | 输出 | 典型用途 |
|---|---|---|
| **任务菜单识别** | A-J 任务清单 + 推荐默认 | 先确认做什么，再开始分析 |
| **多轮推进** | Round 0 → Round N → Convergence | 按轮收集，避免一次问爆 |
| **进度可视** | 第 X 轮 / 预计 N 轮 · Level L | 实时知道进度和剩余缺口 |
| **工况档案** | 已知 / 未知 / 矛盾三态标注 | 把零散转述结构化 |
| **真实需求判断** | 表层诉求 vs 真实工况问题 vs 商业目标 | 识别「要便宜」背后的真实风险 |
| **风险标签** | 温度、含湿、腐蚀、磨蚀、糊袋、火星等 | 让销售不遗漏关键风险 |
| **追问清单** | 3-7 问，含内部技术版 + 客户转述版 | 知道下一句该问什么、怎么问 |
| **报价准备度** | 不可报价 / 预算报价 / 候选正式报价 | 防止「先报个价」变成技术承诺 |
| **Level 4/5 支持包** | 候选方向、证据需求、试用边界、禁止承诺 | 竞品替换、试用验证、招投标 |

---

## 触发示例

冷启动：

```
$oneclear
```

→ 弹出 A-J 任务菜单，选完立刻建档。

粘贴转述：

```
$oneclear 客户说水泥窑尾滤袋半年就压差高，清灰下不来，
怀疑材料质量有问题，销售想直接给替换方案。
```

→ 自动识别「旧项目故障」，弹菜单确认后进入 Round 1。

替换 / 降本场景：

```
$oneclear 客户现在用竞品 PTFE 覆膜袋，觉得价格高，想换便宜一点。
工况只知道是垃圾焚烧，排放要求 10mg 以下。
```

→ 默认「替换 / 降本」，Round 2 重点问当前基线和试用边界。

---

## 核心机制

### 先问任务菜单，再做一切分析

即使用户一次粘贴了完整对话，也先抽取 P0 推荐默认任务、确认后再开始诊断。避免「报价需求」和「选型需求」被混在一起处理。

### 脚本是护栏，不是裁判

`scripts/` 里的确定性检查器负责分类、缺失字段检查、风险标签和规则库校验，不输出最终型号 / 寿命 / 排放承诺。与参考文档冲突时，取更严格的边界。

### 黑名单必须讲因果

`references/31-blacklist-with-causality.md` 里 17 条禁止动作，每条都标注机制 / 损失 / 替代方案。违反时必须显式说明，不能悄悄绕过。

### 可视化是解耦的可选项

收敛后先无条件保存本地 Markdown，再问是否需要可视化。工具已装好才调用，没装会问是否安装，不会自作主张。

---

## 局限性

- OneClear 不替代专家签字、现场检查、实验室检测或合同技术承诺。
- 信息不足时降级为追问和风险提示，不强行推荐具体材料型号。
- 工况规则库主要覆盖常见粉尘场景，特殊化学品 / 高温熔融场景须人工审核。
- 竞品对比基于规格参数评估，不基于实验室数据，结论仅供参考。

---

## 仓库结构

```
oneclear/
├── SKILL.md                          # Skill 主入口（agent 读这里）
├── bin/oneclear.js                   # CLI 安装器入口
├── lib/installer.js                  # 安装逻辑
├── references/                       # 知识库（00-32）
│   ├── 26-work-condition-rules.json  # 工况规则库主体
│   ├── 27-interactive-round-protocol.md
│   ├── 31-blacklist-with-causality.md
│   └── 32-self-check-rubric.md
├── scripts/                          # 确定性护栏脚本
│   ├── classify_case_type.py
│   ├── presales_progression.py
│   └── work_condition_rule_library.py
└── examples/                         # 端到端场景示例（7 个）
```

---

## License

[MIT License](LICENSE) · 自由使用、修改、分发，包括商业用途。
