# 09｜输出模板

Default response must contain three parts.

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
