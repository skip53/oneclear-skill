# 15｜多轮案件推进协议

> 本文件已被 `references/27-interactive-round-protocol.md` 重构为"Round 0 → Round N → Convergence → Refinement → Blocked"的状态机。本文件保留历史背景与每轮处理原则,作为详细参考。

这个 skill 不是只能做一轮。它按案件状态推进,每一轮都更新工况档案、重新评估承诺等级,并显示进度。

## 与新交互式协议的对应关系

| 新协议(27) | 历史协议(15) | 备注 |
|---|---|---|
| Round 0 任务菜单 | — | 新增,在所有诊断之前先确认任务 |
| Round 1 Intake & Routing | intake 状态 | 抽取 P0 + 分流 |
| Round 2+ Progressive Discovery | discovery 状态 | 补 P1,每轮重评 Level |
| Convergence Output Pack | diagnosis / direction / candidate-review / support-pack | 按 Level 出包 |
| Refinement Update Pack | 多轮合并 | 收敛后增量更新 |
| Blocked | blocked | 异常终止 |

详细每轮做什么 / 不做什么 / 怎么输出,见 `references/27-interactive-round-protocol.md`。

## 每轮输入

多轮输入可能包含:

- 上一轮 Agent 输出。
- 业务员补充的信息。
- 客户新的原话。
- 新的照片、样品、压差曲线、检测报告或竞品资料。
- 内部技术人员的确认。

## 每轮处理原则

1. 保留上一轮结论。
2. 标注本轮新增信息。
3. 合并到工况档案。
4. 标注仍缺信息。
5. 识别新矛盾、新风险、新异常。
6. 重新判断 Level。
7. 决定继续追问、进入试用建议、升级人工确认,还是形成技术支持包。
8. **不重复问已答字段**(新协议补充)。
9. **每轮输出进度条**(新协议补充)。

## 案件状态(与新协议保持一致)

| 状态 | 含义 | 下一步 |
|---|---|---|
| intake | 首轮输入,信息未结构化 | 建档、分流、最小追问 |
| discovery | 已分流但缺关键 P0/P1 | 继续追问 |
| diagnosis | 可初步诊断但不可选型 | 要证据、列假设 |
| direction | 可给方向但不可确定型号 | 方向建议、试用前条件 |
| candidate-review | 有候选方向但需人工确认 | 技术负责人确认 |
| support-pack | 可形成技术支持包 | 输出客户需求、风险、建议、下一步 |
| blocked | 缺关键数据或风险过高 | 停止承诺,给替代路径 |

## 输出新增字段

多轮案件输出应加入:

- 案件状态。
- 上一轮结论。
- 本轮新增信息。
- 本轮更新后的未知项。
- Level 是否变化,以及变化原因。
- 本轮下一步动作。

进度条格式定义见 `references/29-progress-visibility.md`。

## 关闭追问条件

只有满足以下条件,才能减少追问并进入方向/候选方案:

- Case type 清楚。
- P0 数据完整。
- 关键 P1 数据足以支持当前 Level。
- 风险和异常已标注。
- 商业阶段和客户成功标准明确。
- 没有未处理的 Red/No-Go 风险。

任务-目标 Level 映射见 `references/28-task-menu.md`。

## 超过 7 轮的强制收敛

如果对话达到 7 轮仍未达到任务目标 Level,自动收敛,显式列出仍未解决的字段,告知业务员"等数据齐再来",不要无限循环。强制收敛后,如有新数据,进入 Refinement 阶段。