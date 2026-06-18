# Changelog

All notable changes to OneClear will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.4.1] - 2026-06-18

### Changed (via darwin-skill auto-optimization)
- **dim4 检查点**: 加 7 个 🔴/🛑/CHECKPOINT 显性视觉标记于 7 个关键决策点
  - `Interactive Operating Flow` 入口门: 🛑 STOP
  - `Round 0 — Task Menu`: 🔴 CHECKPOINT 0
  - `Round 1` 案件分流 AskUserQuestion: 🛑 STOP
  - `Convergence` 收敛门: 🔴 CHECKPOINT
  - `Level 4/5` 输出限制: 🔴 CHECKPOINT 人工确认门
  - `Blocked` 异常终止: 🛑 STOP 替代路径门
  - `Forbidden Behavior`: 🔴 CHECKPOINT 黑名单 4 段式承认门
- **dim1 Frontmatter**: 加 16 个中英文触发词到 `triggers:` 字段
  - 10 中文: 工业除尘 / 滤袋 / 滤料 / 袋式除尘器 / 压差高 / 糊袋 / 破袋 / 询价 / 投标 / 试用 / 替换降本
  - 6 英文: filter bag / baghouse / dust collector / differential pressure / trial validation / ...

### Quality Score (darwin-skill 9-dim rubric)
- 总分: 81.1 → **83.0** (+1.9, +2.3%)
- dim4: 7/6 → **9/6** (+2)
- dim1: 6/7 → **7/7** (+1)
- 其余 7 维度不变

### Optimization Process
- 2 rounds, 3 commits, 0 revert
- 0 changes to SLOW_UPDATE protected section
- 0 changes to references/ files
- HL-4 cap signal triggered (consecutive Δ < 2.0), break to Phase 3

### Commits (since v0.1.4)
- `e97774c` — optimize oneclear: dim4 加 7 个显性视觉标记
- `5b43cd8` — resolve UU: integrate dim4 markers + author SLOW_UPDATE段
- `5b4648e` — optimize oneclear: dim1 加 16 个中英文触发词

## [0.1.4] - 2025

Initial tagged release. See git history for full log.