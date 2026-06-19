# 09｜输出模板

Default response must contain three parts. 本文件按「**模板字段 + 字段说明 + 工具/命令级如何填**」组织——读完一份，就知道**每个字段填什么**、**怎么从工況档案抽取**、**用什么工具验证**。

> 通用原则：模板不是装饰——每个字段都是**人工 / 客户决策的依据**。**字段为空 = 决策依据缺失 = 不能进入下一轮**。

## 一、工况档案草稿

```markdown
## 一、工况档案草稿

- 问题类型：
- 当前 Level：
- 客户原话：
- 业务员转述：
- 真实需求判断：
- 异常状态：
- 风险升级等级：
- 合规/承诺边界：
- 商业/采购阶段：
- 案件状态：

### 已知信息

- [已知]

### 未知关键信息

- [未知]

### 矛盾信息

- [矛盾]

### 初步风险标签

- [风险]

### 当前允许输出

-

### 当前禁止输出

-
```

## 二、追问清单

```markdown
## 二、追问清单

### 内部技术版

1. 问题：
   - 优先级：
   - 为什么问：

### 客户转述版

1. 可直接发给客户的话：
```

## 三、初步诊断摘要

```markdown
## 三、初步诊断摘要

- 当前判断：
- 真实工况问题假设：
- 主要风险：
- 需求 gap：
- 异常 / 合规 / 商业阶段：
- 现在不能下结论的原因：
- 下一步动作：
- 下一步行动清单：
  - 负责人：
  - 需补资料：
  - 时间点：
  - 推进目标：
  - 目标 Level：
```

## Level-Specific Output Limits

- Level 0: only clarification questions and missing-context explanation.
- Level 1: case type, routing path, work-condition draft.
- Level 2: risk tags, preliminary cause hypotheses, evidence needs.
- Level 3: selection direction only, no final model.
- Level 4: candidate directions with human-confirmation requirement.
- Level 5: technical-support pack with risk assumptions and next actions.

Level 0-3 do not need a full presales progression package unless the user explicitly asks for quote readiness, competitor response, trial planning, tender support, or next-action ownership.

## 四、售前推进判断（Level 4/5 或明确要求时）

```markdown
## 四、售前推进判断

- 决策链状态：
- 报价 readiness：
- 滤料能力匹配：
- 试用/验证边界：
- 竞品应对：
- 商业价值量化：
- 内部升级包：
- 人工确认：
- 禁止承诺项：
- 下一步行动清单：
```

## 规则库命中（触发工况规则库时）

```markdown
## 规则库命中

- matched_rules：
- blocked_options：
- preferred_materials：
- preferred_material_reasons：
- risk_flags：
- capability_directions：
- required_evidence：
- missing_evidence：
- system_actions：
- forbidden_commitments：
- human_confirmation_required：
```

规则库可以输出 `preferred_materials`，含义是“规则偏好材料/结构”，不是最终型号或合同承诺。不得把 `blocked_options` 的反面解释成推荐项，也不得输出最终型号、寿命、排放或质保承诺。

## Level 4 Required Fields

- 候选方向 / 候选方案。
- 证据要求。
- 试用/验证边界。
- 人工确认提示。

## Level 5 Required Fields

- 客户需求摘要。
- 工况档案。
- 真实需求判断。
- 风险假设。
- 候选方向 / 候选方案。
- 试用验证计划。
- 客户话术。
- 禁止承诺项。
- 下一步行动清单。

## Governance Fields

- 真实需求判断: compare expressed demand, real work-condition problem, and commercial target.
- 异常状态: mark missing customer words, unroutable case, contradictions, evidence gaps, overcommitment requests, claim pressure, or full replacement pressure.
- 风险升级等级: green, amber, red, or no-go.
- 合规/承诺边界: emissions, safety, warranty, contract, tender, customer-site data, or competitor-data boundaries.
- 商业/采购阶段: quote-before-discovery, new-project selection, failure claim, competitor replacement, trial validation, tender, or repeat order.
- 案件状态: intake, discovery, diagnosis, direction, candidate-review, support-pack, or blocked.

---

## 如何填（工具/命令级指引）

> 每段给一段**可被 agent 直接调用的命令或脚本**，让模板字段从"占位"变成"自动填"。

### 1. 已知信息 / 未知关键信息 / 矛盾信息

- **如何填**：
  - 每轮用户回复后，**逐句拆分**到 02-work-condition-schema.md 的 8 大块
  - 已知字段标 `[已知] <field>: <value>`
  - 未知字段标 `[未知] <field>: <为什么这轮问>`
  - 矛盾字段标 `[矛盾] <field>: <两个说法的对比> — 影响: <为什么不能下结论>`
- **工具**：
  - `scripts/agent_os_governance.py:assess_governance(record)` — 自动检测矛盾 / 表层需求与工况冲突
  - `scripts/check_context_completeness.py:assess_context_level(record)` — 自动评估 Level 0-3
- **验证**：跑 `validate_output_pack.py:validate_output_pack(output, level)` — 检查必含字段

### 2. 初步风险标签

- **如何填**：
  - 触发信号 + 缺失证据，按 04-risk-tags.md 10 类逐一检查
  - 风险标签标 `[风险] <风险类别>: <触发信号 + 缺失证据>`
- **工具**：`scripts/risk_tag_rules.py:tag_risks(record)` — 关键字匹配自动标 10 类风险
- **验证**：风险标签数 ≥ 0 是合法；不标 = 未触风险（仍合法）

### 3. 当前允许输出 / 当前禁止输出

- **如何填**：
  - 查 SKILL.md 承诺阶梯 Level 0-5 → 当前 Level 允许/禁止
  - 查 31-blacklist-with-causality.md 17 条 → 触达的红线
  - 查 13-compliance-and-commitment.md 7 类 → 触达的合规边界
- **工具**：人工判断（Agent 内部查表）
- **验证**：禁止输出必须覆盖所有触达的黑名单条目

### 4. 真实需求判断

- **如何填**：走 10-true-demand-validation.md — 拆 3 层（表层需求 / 真实工况 / 商业目标）
- **工具**：`scripts/agent_os_governance.py:assess_governance(record)` — 自动检测需求 gap
- **验证**：3 层都被显式标注（不能只填 1 层）

### 5. 风险升级等级

- **如何填**：走 12-risk-escalation.md — 9 Red + 4 No-Go 触发条件
- **工具**：`scripts/agent_os_governance.py:assess_governance(record)` — 自动评估
- **验证**：标 red/no-go 时必须同时输出"触发原因 + 不能承诺 + 替代路径"

### 6. 合规/承诺边界

- **如何填**：走 13-compliance-and-commitment.md 7 类
- **工具**：`scripts/agent_os_governance.py:assess_governance(record)` — 自动检测合规触达
- **验证**：触达任一合规 → 走 13 + 12 red 升级

### 7. 商业/采购阶段

- **如何填**：走 14-commercial-procurement-context.md 8 阶段
- **工具**：`scripts/agent_os_governance.py:assess_governance(record)` — 自动检测商业阶段
- **验证**：阶段判断与 Level 评估一致

### 8. 案件状态

- **如何填**：按 Round 推进更新（intake → discovery → diagnosis → direction → candidate-review → support-pack → blocked）
- **工具**：`scripts/check_context_completeness.py:assess_context_level(record)` — 输出 Level 0-3
- **验证**：每轮 Round 标题 + 案件状态一致

---

## 跨字段通用检查清单

> 任何字段填写前，先过这 4 条。

1. **字段是否从工況档案抽取**？是 → 通过；凭空填 → 必须重做。
2. **字段是否有工具/脚本支撑**？是 → 通过；纯靠人工判断 → 标 `[待证]`。
3. **字段是否触达黑名单**？是 → 走 31 + 12 red 升级。
4. **字段是否被 validate_output_pack 校验通过**？是 → 输出；否 → 重做。
