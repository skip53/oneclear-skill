# 24｜工况规则库使用边界

规则库来自旧项目的工况规则引擎。当前主知识库是 `references/26-work-condition-rules.json`，Python 脚本 `scripts/work_condition_rule_library.py` 只负责读取、归一化输入、求值和翻译输出。

规则库在本 Skill 中只作为风险约束、规则偏好材料/结构、系统动作和证据要求使用，不作为自动选材引擎。

## 使用定位

规则库用于：

- 识别材料阻断项：某类材料在已知工况下存在明显边界风险。
- 输出规则偏好材料/结构：例如 PPS、PTFE、PET、AC、ARAMID、PI、ePTFE_MEMBRANE、SURFACE_FILTRATION。
- 识别系统风险：过滤风速、清灰气源、火星、安环、结露等问题可能优先于滤料选择。
- 生成证据要求：需要补哪些数据才能进入候选方向或人工确认。

规则库不得用于：

- 自动推荐最终材料型号。
- 自动承诺寿命、排放、质保或替代效果。
- 用 `rule_score` 代替 Level 判断。
- 在 Level 0-3 将 `preferred_materials` 表述成最终推荐、报价承诺或客户可直接采购型号。
- 绕过技术负责人确认形成 Level 4/5 对外承诺。

## 与 Level 的关系

| Level | 规则库可做 | 规则库不可做 |
| --- | --- | --- |
| Level 0-1 | 补充追问方向和缺失证据 | 输出材料方向 |
| Level 2 | 标注风险、阻断项、规则偏好材料/结构、系统动作 | 输出候选方案 |
| Level 3 | 辅助形成规则偏好材料/结构和证据要求 | 确定最终型号或替代竞品 |
| Level 4 | 支撑候选方向包的证据和边界 | 替代人工确认 |
| Level 5 | 支撑技术支持包的风险假设和禁止承诺项 | 形成合同/质保/排放承诺 |

## 结构化规则库

`26-work-condition-rules.json` 包含：

- `schema_version`、`source_version`、`source_file`
- `field_aliases`：把中文输入、扁平字段和嵌套字段归一到旧规则引擎字段，例如 `flue_gas.temperature_normal`、`dust.stickiness`
- `default_forbidden_commitments`
- 87 条从 `rule-engine-domain/rule_engine/selectionDecisionTable.ts` 迁移的规则
- 每条规则的 `presales_outputs`：`preferred_materials`、`blocked_options`、`risk_flags`、`capability_directions`、`required_evidence`、`system_actions`、`missing_evidence_policy`

迁移后的规则类型计数：

| rule_type | 数量 |
| --- | ---: |
| hard_constraint | 24 |
| strong_preference | 38 |
| risk_warning | 18 |
| negative_bias | 3 |
| weight_adjustment | 3 |
| system_policy | 1 |

## 执行器边界

`work_condition_rule_library.py` 是执行器，不是规则来源。它负责：

- `load_rule_library()`：加载 JSON 主知识库。
- `normalize_work_condition(record)`：用 `field_aliases` 把中文输入、嵌套字段和文本线索归一到规则字段。
- `evaluate_condition_set(...)`：支持 `eq`、`neq`、`in`、`gt`、`gte`、`lt`、`lte`、`contains`、`exists` 和 `.length`。
- `assess_work_condition_rules(record)`：输出 Skill 可用的阻断项、偏好方向、风险、证据和禁止承诺项。

执行器不得在代码中新增业务分支来替代 JSON。需要调整规则时，应先更新 JSON 主知识库。

## 迁移原则

- 完整保留旧 TS 规则的 `rule_id`、`rule_type`、`priority`、`confidence`、`enabled`、`condition_set`、`effects`、`explanation_template`。
- 材料偏好规则转换为 `preferred_materials` 和 `preferred_material_reasons`；38 条 `strong_preference` 规则已转换为规则偏好材料/结构和证据要求。
- 绝对表达要降级：`mandatory`、`optimal`、`guaranteed failure` 对外应表达为“高风险 / 需验证 / 需人工确认”。
- “已确认无”与“未知”必须区分；未知不能当成无风险。
- 如果规则库和现有 Skill 判断冲突，选择更保守的承诺等级。

## 输出字段

规则库输出的核心业务字段包括：

- matched_rules
- blocked_options
- preferred_materials
- preferred_material_reasons
- risk_flags
- capability_directions
- required_evidence
- missing_evidence
- system_actions
- forbidden_commitments
- human_confirmation_required

不输出：

- final_material
- service_life
- emission_guarantee
- warranty
