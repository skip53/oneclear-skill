# 25｜工况规则库迁移摘要与使用边界

本文件记录 `rule-engine-domain` 到 Skill 结构化规则库的迁移摘要。规则主源是 `references/26-work-condition-rules.json`，本文件不再维护独立规则表。

## 迁移范围

已迁移旧规则引擎 `selectionDecisionTable.ts` 中的 87 条规则：

| rule_type | 数量 | 售前用途 |
| --- | ---: | --- |
| hard_constraint | 24 | 材料阻断、红色风险、系统前置条件 |
| strong_preference | 38 | 规则偏好材料/结构、候选方向入口 |
| risk_warning | 18 | 运行风险、系统风险、证据要求 |
| negative_bias | 3 | 降低默认 PTFE / PPS 倾向，防止信息不足时过度推荐 |
| weight_adjustment | 3 | 保留来源规则的权重语义，售前侧只转成风险/系统动作参考 |
| system_policy | 1 | 低能耗等目标触发系统协同动作 |

## 典型输出

规则命中后可进入以下字段：

- `blocked_options`：例如 PET、PPS、AC、P84、GLASS_FIBER、DEEP_NEEDLE_FELT、PTFE_MAIN。
- `preferred_materials`：例如 PET、PPS、PTFE、AC、ARAMID、PI、ePTFE_MEMBRANE、MEMBRANE_OR_GRADIENT、SURFACE_FILTRATION。
- `risk_flags`：例如结露窗口、高氧含硫 PPS 风险、HF 玻纤腐蚀、气源含水糊袋、火星烧穿。
- `capability_directions`：例如表面过滤、耐 HF 腐蚀、抗结露/疏水/保温协同、阻燃/抗火星系统协同。
- `required_evidence`：例如温度曲线、含湿/露点、完整烟气成分、粉尘粘性、袋面照片、压差曲线。
- `system_actions`：例如先核算过滤风速/过滤面积、先处理气源干燥/除油、先确认防静电和安环措施。

## 使用边界

这些命中可以作为候选讨论入口，但不能直接写成：

- 最终型号
- 寿命承诺
- 排放保证
- 质保承诺
- 完全替代竞品
- 无需试用或直接全量替换

若材料同时出现在 `blocked_options` 和 `preferred_materials`，执行器必须从 `preferred_materials` 中移除该材料。

## 与 Level 的关系

| Level | 可使用规则库的方式 | 禁止 |
| --- | --- | --- |
| Level 0-1 | 追问和缺失证据 | 材料方向 |
| Level 2 | 风险、阻断项、系统动作 | 候选方案或具体推荐 |
| Level 3 | 规则偏好材料/结构和验证方向 | 最终型号、替代竞品 |
| Level 4 | 候选方向包中的证据、边界、人工确认项 | 无人工确认的方案承诺 |
| Level 5 | 技术支持包中的风险假设、试用计划、禁止承诺项 | 合同、寿命、排放、质保承诺 |

## 使用话术

```text
规则库命中了若干风险边界和规则偏好材料。preferred_materials 可以作为候选讨论入口，但不能直接推出最终型号、寿命、排放或质保承诺。
```

```text
这个风险更像系统条件优先问题，建议先补过滤风速、清灰气源、温度/露点和现场照片，再讨论候选滤料方向。
```
