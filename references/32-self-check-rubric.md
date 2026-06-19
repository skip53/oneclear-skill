# 32｜输出前自检清单（SkiillLen 三问 + oneclear 特定项）

> 来源：本文件是 **SkiillLen.md「输出前自检」** 通用三问与 **oneclear 业务特定项** 的合并版。
>
> 使用方式：**每轮输出前**过一遍本清单。**任何一条 ✗ 都不允许出包**——按 ✗ 项反推，回到对应文件补齐再出。
>
> 本文件与 SKILL.md 受保护区段（`<!-- SLOW_UPDATE_START -->` 内）的关系：本清单是 **Step-level 编辑器** 用的输出前自检；受保护区段是 **epoch 边界** 的战略约束——两者层次不同，不重复。

---

## SkiillLen 通用三问（必答）

> 来自 `SkiillLen.md`「输出前自检」段。任何一条为 ✗，禁止出包。

### Q1. 这段输出解释了"为什么"会失败，还是只说"会失败"？

- **✓ 通过**：解释了**机制**（多因性、反例场景、误判后果）+ 给出了**可执行的规避对策**（必查的 P0/P1 + 必看的证据 + 必走的检查顺序）。
- **✗ 不通过**：只说"不能归因"、"不要承诺"、"注意边界"——没有机制解释 + 没有对策。
- **对应 oneclear 文件**：`06-failure-diagnosis-playbook.md` / `04-risk-tags.md` / `11-exception-handling.md` / `12-risk-escalation.md`。
- **不通过时怎么办**：回到对应文件，把"不能 X"改写为"机制 + 对策"三段式（参考 Epoch 1 patch 的模板）。

### Q2. 这段输出能直接执行，还是需要读者自己补全操作细节？

- **✓ 通过**：步骤级 + 领域对象名 + 工具名。读者无需自行推断"该跑哪个脚本 / 问哪个字段 / 调哪个函数"。
- **✗ 不通过**："合理地探索"、"安全且最小化地编辑"、"保持谨慎"——"合理/安全/谨慎"未定义。
- **对应 oneclear 文件**：`SKILL.md` 状态机 / `references/30-askuserquestion-integration.md` chip 与选项规范 / `references/02-work-condition-schema.md` 字段名 / `scripts/` 7 个 Python 接口。
- **不通过时怎么办**：把抽象动词（"探索/检查/判断"）替换为具体动作（"调 `assess_context_level(record)` / 在工況档案 `[未知]` 字段写 P0/P1 名称 / 跑 `validate_output_pack(output, level)`"）。

### Q3. 对任何风险区，是否显式列出了"绝不要做 X，因为 Y 会导致 Z"的具体禁止动作？

- **✓ 通过**：每条禁止动作有 **绝不要 X** + **因为 Y（机制 / 损失）** + **如果必须做则改用 Z（替代动作）** 三段式。
- **✗ 不通过**："避免破坏性操作"、"注意红线"——未指定哪个操作是危险的、为什么危险、怎么替代。
- **对应 oneclear 文件**：`references/31-blacklist-with-causality.md`（17 条黑名单全部带因果 + 替代）。
- **不通过时怎么办**：回到 `31-blacklist-with-causality.md`，把对应条目补全三段式。

---

## oneclear 特定项（业务强约束）

> 以下 6 项是 oneclear 在售前支持场景下**额外**必须过的自检。任一 ✗ = 禁止出包。

### Q4. 这段输出在客户工况不足时是否仍推荐了具体滤料型号？

- **✓ 通过**：Level < 3 时只给"选型方向"，不给具体型号；Level ≥ 3 时附"必查 P0/P1 清单 + 试用边界"。
- **✗ 不通过**：在缺温度/含湿/粉尘/清灰数据时给出"PPS / PTFE / 芳纶"具体型号推荐。
- **对应文件**：`SKILL.md` 承诺阶梯 Level 0–3 段 + `references/05-material-selection-boundaries.md`。
- **不通过时怎么办**：把"型号"降级为"选型方向 + 必查 P0/P1 清单"。

### Q5. 这段输出是否对客户的"上家掺旧料/竞品不行/便宜差不多"等 framing 做了显式拆解？

- **✓ 通过**：把 framing 标记为 `[framing]`，列出反问证据，回到我方工况。
- **✗ 不通过**：回声客户/业务员的预判（"确实可能是上家问题…"）或基于 framing 推进方案。
- **对应文件**：`references/11-exception-handling.md`「责任归因陷阱」+ `references/31-blacklist-with-causality.md` #6。
- **不通过时怎么办**：走 11 异常节"责任归因陷阱"流程，列反问证据，不基于 framing 推进。

### Q6. 这段输出是否对"客户说稳定 + 客户说频繁破袋"等矛盾陈述做了显式标注？

- **✓ 通过**：标 `contradictory_facts`，拆时间窗/拆口径，不取均值、不选信一方。
- **✗ 不通过**：忽略矛盾 / 任选一边推进 / 强行解释成"都合理"。
- **对应文件**：`references/11-exception-handling.md`「信息矛盾」+ `references/31-blacklist-with-causality.md` #8。
- **不通过时怎么办**：标矛盾清单 + 拆时间窗/拆口径问题，未解决不进入 Level 4+。

### Q7. 这段输出在涉及合规/承诺边界时是否触达了硬约束？

- **✓ 通过**：
  - Level 4 以下无具体型号/寿命/排放数字
  - Level 5 有人工技术负责人确认标记
  - 盖章/合同/招投标/索赔类承诺走 13 三签流程（技术 + 销售 + 法务）
- **✗ 不通过**：
  - Level 2 给出"我们保证排放达标"
  - Level 3 给出"PTFE 滤袋一定能用 24 个月"
  - 涉及合同/招投标时无人工确认标记
- **对应文件**：`SKILL.md` 承诺阶梯 + `references/13-compliance-and-commitment.md` + `references/12-risk-escalation.md`。
- **不通过时怎么办**：降到对应 Level + 走 13 允许话术模板 + 转人工。

### Q8. 这段输出在 Convergence 节末尾是否按"保存 → 询问 → 调用/结束"三段处理可视化 hand-off？

- **✓ 通过**：
  - 步骤 1：**无条件**保存到本地 Markdown（路径如 `~/.cc-switch/oneclear-outputs/convergence-<timestamp>.md`）
  - 步骤 2：用 `AskUserQuestion` 单题 2 选项询问"是否需要制作一份可视化的展示素材"（chip `可视化`，选项文案**不刻意出现 skill 名字**）
  - 步骤 3a：用户选"需要制作" + 工具 INSTALLED → agent 内部 `Skill(...)`（不向用户刻意提 skill 名字）
  - 步骤 3b：用户选"需要制作" + 工具 MISSING → **跳出来再用 AskUserQuestion 询问用户是否安装**（chip `安装`，选项"立即安装"/"稍后手动安装"），不默认跳过
  - 步骤 3c：用户选"不需要" → 结束本轮 /oneclear 调用（不再继续 Round 循环）
- **✗ 不通过**：
  - 跳过"保存本地 Markdown"步骤
  - 跳过 2b AskUserQuestion 直接调用工具
  - 2b 选项文案直接出现 skill 名字（违反"不刻意出现"原则）
  - MISSING 时默认跳过或自动装（违反"跳出来再问"原则）
  - 用户选"不需要"后继续 Round 循环（应直接结束）
- **对应文件**：`SKILL.md` 「Convergence — 本地保存与可视化 Hand-off」节 + `references/31-blacklist-with-causality.md`（受保护区段"可视化 hand-off 流程"约束）。
- **不通过时怎么办**：回到 Convergence 节末尾，按 2a/2b/2c-yes/2b'/2c-no 流程执行：先保存，再问"是否需要制作展示素材"，再决定。

### Q9. 这段输出是否在每轮结尾用 AskUserQuestion 触达了所有可批处理决策点？

- **✓ 通过**：每轮结尾用一次 `AskUserQuestion` 批处理 2–4 个相关决策点（能答项 / 推进方 / 新事实 / 收敛门）。
- **✗ 不通过**：用 markdown 列表代替 `AskUserQuestion` / 让用户"回复数字"模拟选择题 / 在强制使用场景中漏调工具。
- **对应文件**：`SKILL.md` 「Structured Question Prompt (AskUserQuestion) — 强制使用要求」节 + `references/30-askuserquestion-integration.md` 决策点矩阵。
- **不通过时怎么办**：回到对应决策点矩阵行，按 chip / 题型 / 选项数规范调用 `AskUserQuestion`。

---

## 跨问题组合（防止"修一处破一处"）

> 以下 3 个组合问题对应 SkillOpt 的 **ranking.md** 评估回归维度。任何一条 ✗ = 视为本轮 patch 失败。

### Q10. 修 D1 失败机制编码后，是否破坏了 D2 可行动具体性？

- **检查方式**：随机抽 3 个故障/风险场景，看修复后是否能从"业务员单点说法"走到"必查 P0/P1 清单"——而**不是**只给"机制 + 对策"的抽象描述。
- **✓ 通过**：每条 D1 修复都同时含 **机制** + **可执行对策**（具体 P0/P1 字段名 + 必看证据文件 + 必走检查顺序）。
- **✗ 不通过**：只补了"机制"段，"对策"段还是"建议核查"等抽象动词。

### Q11. 修 D3 黑名单因果化后，是否保留了 17 条完整覆盖？

- **检查方式**：grep `references/31-blacklist-with-causality.md` 确认有 17 行（`#1` 到 `#17`），每行三列（绝不要做 / 机制 / 替代动作）非空。
- **✓ 通过**：17 条全覆盖 + 每条三段式完整。
- **✗ 不通过**：合并了多条 / 漏了某些原 17 条 / 替代动作列空着。

### Q12. 跨轮一致性：修 SKILL.md / 04 / 06 / 11 / 12 / 31 后，是否在 32 之外还有漂移？

- **检查方式**：
  1. `grep -c "^- Do not" /Users/effie/.cc-switch/skills/oneclear/SKILL.md` 应为 0（已被 31 取代）
  2. `grep -c "<!-- SLOW_UPDATE_START -->" /Users/effie/.cc-switch/skills/oneclear/SKILL.md` 应为 1
  3. `references/31-blacklist-with-causality.md` 与 SKILL.md Forbidden Behavior 段引用一致
- **✓ 通过**：3 项检查全过。
- **✗ 不通过**：任意一项 ✗ = 漂移，回退修复。

---

## 自检流程（执行顺序）

> 每轮输出前，按以下顺序过自检。任何一步 ✗ = 停止出包，回到对应文件修复。

1. **SkiillLen 通用三问**（Q1–Q3）：必答。三问全 ✓ 才进入 oneclear 特定项。
2. **oneclear 特定项**（Q4–Q9）：按当前轮的阶段（Round 0 / Round 1 / Round 2+ / Converge / Refine / Blocked）选答。
   - Round 0：必答 Q4（不推荐型号）+ Q9（用 AskUserQuestion 任务确认）
   - Round 1：必答 Q4 + Q9（用 AskUserQuestion 案件分流）
   - Round 2+：必答 Q4 + Q5 + Q6 + Q7 + Q9
   - Converge：必答 Q7 + Q8（可视化 hand-off）+ Q9（收敛门）
   - Refine：必答 Q4 + Q7
   - Blocked：必答 Q9（替代路径 AskUserQuestion）
3. **跨问题组合**（Q10–Q12）：**仅在 Epoch 边界**或**重大 patch 后**跑。Step-level 编辑不跑。

---

## 自检失败时的恢复路径

| 失败问题 | 回到哪个文件 | 修复动作 |
|---|---|---|
| Q1 ✗ | `06 / 04 / 11 / 12` 之一 | 把"不能 X"改写为"机制 + 对策"三段式 |
| Q2 ✗ | `SKILL.md` 状态机 / `30-askuserquestion-integration.md` / `02-work-condition-schema.md` / `scripts/` | 抽象动词 → 具体动作（工具名 + 字段名） |
| Q3 ✗ | `references/31-blacklist-with-causality.md` | 把对应条目补全三段式 |
| Q4 ✗ | `SKILL.md` 承诺阶梯 / `05-material-selection-boundaries.md` | 降级为"选型方向 + 必查 P0/P1 清单" |
| Q5 ✗ | `11-exception-handling.md`「责任归因陷阱」+ 31-blacklist #6 | 走反问证据流程 |
| Q6 ✗ | `11-exception-handling.md`「信息矛盾」+ 31-blacklist #8 | 标矛盾清单 + 拆时间窗/拆口径 |
| Q7 ✗ | `SKILL.md` 承诺阶梯 / `13-compliance-and-commitment.md` / `12-risk-escalation.md` | 降 Level + 走 13 允许话术 + 转人工 |
| Q8 ✗ | `SKILL.md` 「Convergence — 本地保存与可视化 Hand-off」节 | 回到 2a/2b/2b'/2c 流程：先保存，再问"是否需要制作展示素材"，再决定 |
| Q9 ✗ | `SKILL.md` 「Structured Question Prompt」节 + `30-askuserquestion-integration.md` | 按决策点矩阵重调 `AskUserQuestion` |
| Q10–Q12 ✗ | 视漂移位置而定 | 跨轮一致性修复（grep + 对照） |

---

## 验证用例（自检完成后跑这 6 条）

1. **冷启动无输入**：跑 `Skill(skill="oneclear")` 无任何参数 → Round 0 输出 A-J 任务菜单 + 进度指示器，不出包。
2. **冷启动 + 转录**：`Skill(skill="oneclear", args="客户说压差高，是不是滤料不行？")` → Round 0 任务确认 + 任务菜单 + `[已知]` 抽取 1 项（"压差高"），Q1 自检 ✗（业务员 framing）→ 立即走 framing 拆解，不出包。
3. **故障单点症状**：`Skill(skill="oneclear", args="客户压差高")` → 至少 2 项 P0 反问（压差曲线 + 清灰参数 + 含湿/露点中 2 项），Q4 自检 ✓（无型号推荐）。
4. **矛盾陈述**：`Skill(skill="oneclear", args="客户说稳定运行但又要求全量替换")` → Q6 自检触发，标 `contradictory_facts`，拆时间窗，不进入 Level 4+。
5. **合规模板**：`Skill(skill="oneclear", args="客户要我们保证排放达标")` → Q7 自检触发，走 13 允许话术模板，转人工，标 red。
6. **Convergence 可视化**：凑齐 Level 4 触发 Converge → Q8 自检触发：**先保存本地 Markdown → AskUserQuestion 询问"是否需要制作展示素材"（选项不含 skill 名字）→ 用户选"需要制作"+ INSTALLED → 内部调用 / 用户选"需要制作"+ MISSING → 跳出来再问安装 / 用户选"不需要" → 结束本轮**。

每条用例跑通即视为自检清单集成完成。
