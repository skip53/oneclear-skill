# 05｜选型承诺边界

This file controls what the Agent may say about filter-media direction.

## Information Insufficient: Do Not Recommend Material

Do not recommend specific material when any of these are missing:

- Case type is unclear.
- Industry and process section are unknown.
- Temperature range and peak temperature are unknown.
- Humidity or condensation risk is unknown for moisture-sensitive cases.
- Dust properties are unknown for blinding, abrasion, or emissions cases.
- Current material and failure evidence are missing for existing-project failures.
- Replacement goal and current-scheme stability are unknown for replacement / cost-down cases.

## Direction-Level Recommendation Allowed

The Agent may give a direction when:

- Case type is clear.
- Main work-condition risks are visible.
- Key unknowns are listed as assumptions.
- Output explicitly says that no final model is confirmed.

Allowed wording:

```text
从现有信息看，可以优先关注耐温、抗结露/抗糊袋、耐腐蚀或抗磨方向。具体材质仍需结合温度峰值、含湿量、粉尘性质和现场证据确认。
```

## Candidate Direction Allowed With Human Confirmation

The Agent may provide 1-3 candidate directions when:

- Temperature, humidity, dust, dust collector, current filter information, failure behavior, and customer target are mostly known.
- Risks are tagged.
- Evidence gaps are explicit.
- The output says the candidate plan requires technical lead confirmation.

## Always Human-Confirmed

These require human confirmation:

- Final material model.
- Service-life expectation.
- Emission guarantee.
- Full competitor replacement.
- Large project scheme.
- Warranty wording.
- Contract technical commitment.

## Forbidden Wording

Avoid absolute phrases:

- 一定能解决
- 保证寿命
- 直接换这个就行
- 肯定是材质问题
- 可以完全替代
