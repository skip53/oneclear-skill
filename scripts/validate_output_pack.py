from __future__ import annotations

import re


REQUIRED_SECTIONS = {
    "缺少工况档案草稿": "工况档案草稿",
    "缺少追问清单": "追问清单",
    "缺少初步诊断摘要": "初步诊断摘要",
}

REQUIRED_GOVERNANCE_FIELDS = {
    "缺少真实需求判断": "真实需求判断",
    "缺少异常状态": "异常状态",
    "缺少风险升级等级": "风险升级等级",
    "缺少合规/承诺边界": "合规/承诺边界",
    "缺少商业/采购阶段": "商业/采购阶段",
    "缺少案件状态": "案件状态",
}

OVERCOMMIT_TERMS = [
    "保证寿命",
    "寿命保证",
    "保证排放",
    "排放保证",
    "保证达标",
    "一定达标",
    "质保承诺",
    "承诺质保",
    "完全替代",
    "无需试用",
    "不用试用",
    "直接全量替换",
    "直接全量切换",
    "直接换这个",
    "最终型号",
    "最终方案",
    "一定能解决",
    "肯定是材质问题",
]
COMMITMENT_BOUNDARY_MARKERS = ["禁止承诺", "不承诺", "不得", "不做", "不可", "不能", "禁止", "不直接"]
SPECIFIC_RECOMMEND_RE = re.compile(
    r"(推荐|建议|可以|可|优先|直接)\s*(使用|用|换|选)?\s*"
    r"(PPS|PTFE|P84|芳纶|涤纶|玻纤|玻璃纤维|亚克力|丙纶)(覆膜)?",
    re.IGNORECASE,
)
LEVEL_4_REQUIRED_MARKERS = {
    "Level 4 缺少候选方向": ["候选方向", "候选方案"],
    "Level 4 缺少证据要求": ["证据要求", "证据包"],
    "Level 4 缺少试用/验证边界": ["试用/验证边界", "试用验证边界", "验证边界", "试用范围"],
    "Level 4 缺少人工确认提示": ["人工确认", "技术负责人确认", "需人工确认"],
}
LEVEL_5_REQUIRED_MARKERS = {
    "Level 5 缺少客户需求摘要": ["客户需求摘要"],
    "Level 5 缺少工况档案": ["工况档案"],
    "Level 5 缺少真实需求判断": ["真实需求判断"],
    "Level 5 缺少风险假设": ["风险假设"],
    "Level 5 缺少候选方向": ["候选方向", "候选方案"],
    "Level 5 缺少试用验证计划": ["试用验证计划", "试用计划"],
    "Level 5 缺少人工确认提示": ["人工确认", "技术负责人确认", "需人工确认"],
    "Level 5 缺少客户话术": ["客户话术", "客户转述版"],
    "Level 5 缺少禁止承诺项": ["禁止承诺项"],
    "Level 5 缺少下一步行动清单": ["下一步行动清单"],
}


def _has_specific_material_recommendation(output: str) -> bool:
    return bool(SPECIFIC_RECOMMEND_RE.search(output))


def _contains_any(output: str, markers: list[str]) -> bool:
    return any(marker in output for marker in markers)


def _has_overcommitment(output: str) -> bool:
    for line in output.splitlines():
        if any(marker in line for marker in COMMITMENT_BOUNDARY_MARKERS):
            continue
        if any(term in line for term in OVERCOMMIT_TERMS):
            return True
    return False


def validate_output_pack(output: str, level: int) -> dict[str, object]:
    issues: list[str] = []
    for issue, marker in REQUIRED_SECTIONS.items():
        if marker not in output:
            issues.append(issue)
    for issue, marker in REQUIRED_GOVERNANCE_FIELDS.items():
        if marker not in output:
            issues.append(issue)

    if level <= 2:
        if _has_overcommitment(output) or _has_specific_material_recommendation(output):
            issues.append("Level 2 禁止具体推荐或寿命承诺")
    elif level == 3:
        if _has_overcommitment(output) or _has_specific_material_recommendation(output):
            issues.append("Level 3 禁止具体材料推荐或确定效果承诺")
    elif level == 4:
        for issue, markers in LEVEL_4_REQUIRED_MARKERS.items():
            if not _contains_any(output, markers):
                issues.append(issue)
        if _has_overcommitment(output):
            issues.append("Level 4/5 禁止寿命、排放、质保、替代或最终型号承诺")
    elif level >= 5:
        for issue, markers in LEVEL_5_REQUIRED_MARKERS.items():
            if not _contains_any(output, markers):
                issues.append(issue)
        if _has_overcommitment(output):
            issues.append("Level 4/5 禁止寿命、排放、质保、替代或最终型号承诺")

    return {"ok": not issues, "issues": issues}
