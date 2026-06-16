from __future__ import annotations


def _text(record: dict[str, object]) -> str:
    return " ".join(str(value) for value in record.values() if value is not None)


def _value(record: dict[str, object], key: str) -> str:
    return str(record.get(key, "")).strip()


def _has_any(text: str, terms: list[str]) -> bool:
    return any(term in text for term in terms)


def _has_field(record: dict[str, object], keys: list[str]) -> bool:
    return any(_value(record, key) for key in keys)


def _missing_fields(record: dict[str, object], groups: dict[str, list[str]]) -> list[str]:
    return [label for label, keys in groups.items() if not _has_field(record, keys)]


def _assess_decision_chain(record: dict[str, object], text: str) -> dict[str, object]:
    role_fields = {
        "使用者": ["使用者", "现场使用者", "运行负责人", "设备负责人"],
        "技术评估人": ["技术评估人", "技术负责人", "环保负责人", "设备技术"],
        "采购负责人": ["采购负责人", "采购", "商务负责人"],
        "最终决策人": ["最终决策人", "老板", "总经理", "项目负责人"],
    }
    missing_roles = _missing_fields(record, role_fields)

    concerns: list[str] = []
    if _has_field(record, ["关键顾虑", "客户顾虑", "关注点"]):
        concerns.append(_value(record, "关键顾虑") or _value(record, "客户顾虑") or _value(record, "关注点"))
    if _has_any(text, ["降本", "便宜", "价格太高", "低价"]):
        concerns.append("降本")
    if _has_any(text, ["排放", "超低排放", "10毫克"]):
        concerns.append("排放稳定")
    if _has_any(text, ["寿命", "质保", "保用"]):
        concerns.append("寿命/质保")
    if _has_any(text, ["交期", "下周", "紧急"]):
        concerns.append("交期")

    return {
        "status": "决策链完整" if not missing_roles else "决策链缺口",
        "known_roles": [role for role in role_fields if role not in missing_roles],
        "missing_roles": missing_roles,
        "key_concerns": list(dict.fromkeys(concerns)) or ["未确认"],
    }


def _assess_quote_readiness(record: dict[str, object], text: str) -> dict[str, object]:
    quote_groups = {
        "规格": ["规格", "滤袋规格", "尺寸", "袋长", "袋径"],
        "数量": ["数量", "条数", "套数"],
    }
    missing = _missing_fields(record, quote_groups)

    has_work_condition_boundary = (
        _has_field(record, ["行业"])
        and _has_field(record, ["工艺段"])
        and (
            _has_field(record, ["常态温度", "峰值温度", "温度"])
            or _has_field(record, ["含湿量", "含湿"])
            or _has_field(record, ["粉尘性质", "粉尘"])
        )
    )
    if not has_work_condition_boundary:
        missing.append("工况边界")

    risk_notes: list[str] = []
    if "工况边界" in missing:
        risk_notes.append("技术承诺风险未排除")
    if _has_any(text, ["保证", "质保", "承诺", "投标", "招标", "盖章", "合同"]):
        risk_notes.append("报价可能连带合同/技术承诺")

    if missing:
        status = "不能正式报价"
    elif risk_notes or not _has_field(record, ["候选方向", "技术负责人确认", "人工确认"]):
        status = "只能预算报价"
    else:
        status = "可进入正式报价前人工复核"

    return {
        "status": status,
        "missing_quote_fields": list(dict.fromkeys(missing)),
        "risk_notes": list(dict.fromkeys(risk_notes)),
        "allowed_quote_depth": {
            "不能正式报价": "只能说明缺口和报价前置资料",
            "只能预算报价": "只能给预算区间或内部测算，不能作为技术承诺",
            "可进入正式报价前人工复核": "可准备正式报价资料，但仍需人工复核",
        }[status],
    }


def _assess_capability_match(record: dict[str, object], text: str) -> dict[str, object]:
    risk_map = [
        (
            ["高温", "峰值", "烧袋", "热收缩"],
            "温度风险",
            "耐温与热稳定能力",
            "耐温等级、基布结构或后处理方向待技术确认",
            ["连续/峰值温度记录", "启停和异常温度记录"],
        ),
        (
            ["含湿", "结露", "高湿", "糊袋"],
            "含湿/结露风险",
            "抗结露、易清灰和抗糊袋能力",
            "表面处理、过滤精度和清灰适配方向待技术确认",
            ["含湿量", "露点或结露记录", "压差曲线", "袋面照片"],
        ),
        (
            ["酸", "碱", "腐蚀", "HCl", "SOx", "NOx"],
            "腐蚀风险",
            "耐化学腐蚀能力",
            "耐腐蚀等级和复合结构方向待技术确认",
            ["烟气成分", "酸碱浓度", "历史腐蚀照片/样品"],
        ),
        (
            ["磨蚀", "冲刷", "迎风面", "破袋"],
            "磨蚀风险",
            "耐磨和结构强度能力",
            "增强结构、克重或安装保护方向待技术确认",
            ["破损位置比例", "入口流速", "粉尘粒径/硬度", "现场照片"],
        ),
        (
            ["火星", "烧穿", "着火", "高温颗粒"],
            "火星烧袋风险",
            "抗火星冲击和系统防护能力",
            "滤料方向必须与火星治理、预除尘或阻火措施一起确认",
            ["火星来源", "预处理措施", "烧损照片", "安环要求"],
        ),
        (
            ["清灰", "压差", "喷吹"],
            "清灰/压差风险",
            "清灰适配和低阻稳定能力",
            "过滤结构、清灰参数和设备条件需联动确认",
            ["清灰压力/周期", "压差曲线", "过滤风速", "除尘器结构"],
        ),
    ]

    matches: list[dict[str, object]] = []
    for terms, risk, ability, direction, evidence in risk_map:
        if _has_any(text, terms):
            matches.append(
                {
                    "work_condition_risk": risk,
                    "required_capability": ability,
                    "possible_direction": direction,
                    "evidence_required": evidence,
                    "forbidden_commitments": ["不确定最终型号", "不承诺寿命", "不承诺排放", "不承诺完全替代"],
                }
            )

    return {
        "status": "已形成能力匹配草稿" if matches else "缺工况风险证据",
        "matches": matches,
        "note": "能力匹配只连接风险与能力，不输出最终材料型号或效果承诺。",
    }


def _is_competitor_stable_costdown(record: dict[str, object], text: str) -> bool:
    stable_value = _value(record, "当前方案是否稳定")
    stable = "稳定" in stable_value or _has_any(text, ["现在用着稳定", "能用", "表现稳定"])
    costdown = _has_any(text, ["降本", "便宜", "价格太高", "低价", "太贵"])
    competitor = _has_any(text, ["竞品", "替换", "替代"])
    return stable and costdown and competitor


def _assess_trial_validation(record: dict[str, object], text: str) -> dict[str, object]:
    requested_trial = _has_any(text, ["试用", "小批量", "分仓", "对照"])
    stable_costdown = _is_competitor_stable_costdown(record, text)
    needed = requested_trial or stable_costdown

    if _has_any(text, ["分仓", "对照"]):
        suggested_mode = "分仓对照试用"
    elif needed:
        suggested_mode = "小批量试用"
    else:
        suggested_mode = "暂不进入试用验证"

    required_fields: list[str] = []
    if needed:
        if suggested_mode == "分仓对照试用":
            required_fields.append("试用仓/对照仓")
        else:
            required_fields.append("试用范围")
        required_fields.extend(["基线数据", "观察周期", "验收指标", "记录责任人"])

    field_groups = {
        "试用仓/对照仓": ["试用仓", "对照仓", "试用范围", "安装位置"],
        "试用范围": ["试用范围", "安装位置", "小批量数量"],
        "基线数据": ["基线数据", "当前基线", "当前寿命", "当前压差", "当前排放"],
        "观察周期": ["观察周期", "试用周期"],
        "验收指标": ["验收指标", "成功标准"],
        "记录责任人": ["记录责任人", "现场记录人"],
    }
    missing = [field for field in required_fields if not _has_field(record, field_groups[field])]

    if not needed:
        status = "未进入试用验证"
    elif missing:
        status = "试用边界待补齐"
    else:
        status = "试用计划可提交人工确认"

    return {
        "needed": needed,
        "status": status,
        "suggested_mode": suggested_mode,
        "required_fields": required_fields,
        "missing_fields": missing,
        "acceptance_indicators": ["压差趋势", "排放记录", "袋面状态", "清灰稳定性", "运行异常记录"],
        "forbidden_commitments": ["不以试用前判断替代全量效果承诺", "不承诺同等寿命", "不承诺完全替代竞品"],
    }


def _assess_competitor_position(record: dict[str, object], text: str) -> dict[str, object]:
    if not _has_any(text, ["竞品", "替换", "替代", "降本", "便宜", "太贵"]):
        return {
            "status": "未识别竞品场景",
            "recommended_posture": "不输出竞品对比",
            "required_evidence": [],
            "forbidden_commitments": ["不做无依据竞品比较"],
        }

    if _is_competitor_stable_costdown(record, text):
        return {
            "status": "竞品稳定降本",
            "recommended_posture": "需当前基线 + 小批量试用",
            "required_evidence": ["当前稳定基线", "竞品实际寿命", "当前压差/排放", "当前采购与换袋成本", "客户降本目标"],
            "forbidden_commitments": ["不直接低价打竞品", "不承诺同寿命", "不承诺完全替代"],
        }

    if _has_any(text, ["压差高", "糊袋", "破袋", "排放超标", "不稳定", "寿命短"]):
        return {
            "status": "竞品替换伴随故障",
            "recommended_posture": "先诊断故障，再讨论替换价值",
            "required_evidence": ["故障证据链", "竞品运行基线", "工况变化", "样品/照片/报告"],
            "forbidden_commitments": ["不把故障直接归因于竞品材质", "不承诺换材质一定解决"],
        }

    return {
        "status": "竞品信息待澄清",
        "recommended_posture": "先确认客户选择标准和竞品基线",
        "required_evidence": ["竞品型号/结构", "客户选择标准", "价格/寿命/排放基线", "是否接受试用"],
        "forbidden_commitments": ["不做无证据优劣比较", "不承诺完全替代"],
    }


def _assess_commercial_value(record: dict[str, object]) -> dict[str, object]:
    value_groups = {
        "当前单价": ["当前单价", "竞品价格", "采购单价"],
        "当前寿命": ["当前寿命", "实际寿命"],
        "停机/人工换袋成本": ["停机成本", "换袋人工", "人工换袋成本", "停机时间"],
        "能耗/压差成本": ["能耗", "压差成本", "当前压差"],
        "排放处罚/环保风险": ["排放处罚", "环保风险", "排放要求"],
    }
    missing = _missing_fields(record, value_groups)
    status = "可建立TCO对比" if len(missing) <= 1 else "TCO 信息不足"

    return {
        "status": status,
        "missing_value_fields": missing,
        "value_dimensions": ["滤袋单价", "实际寿命", "停机损失", "换袋人工", "压差能耗", "排放风险"],
        "calculation_boundary": "只做总使用成本口径和资料缺口，不承诺降本幅度。",
    }


def _assess_escalation_package(record: dict[str, object], text: str) -> dict[str, object]:
    escalation_terms = ["投标", "招标", "技术条款", "偏差表", "盖章承诺", "合同", "保证", "质保", "排放保证"]
    requested_high_level = _has_any(text, ["候选方案", "技术支持包", "Level 4", "Level 5"])
    required = _has_any(text, escalation_terms) or requested_high_level

    required_materials = [
        "客户需求摘要",
        "工况档案",
        "真实需求判断",
        "风险假设",
        "候选方向",
        "证据要求",
        "试用/验证边界",
        "禁止承诺项",
    ]
    material_fields = {
        "客户需求摘要": ["客户需求摘要", "客户目标", "本次目标"],
        "工况档案": ["工况档案", "行业", "工艺段"],
        "真实需求判断": ["真实需求判断", "客户想解决的问题"],
        "风险假设": ["风险假设", "初步风险标签", "风险"],
        "候选方向": ["候选方向", "候选方案"],
        "证据要求": ["证据要求", "证据包"],
        "试用/验证边界": ["试用/验证边界", "试用验证边界", "验证边界", "试用范围"],
        "禁止承诺项": ["禁止承诺项", "禁止输出", "当前禁止输出"],
    }

    return {
        "required": required,
        "human_confirmation_required": required,
        "required_roles": ["技术负责人", "销售负责人", "管理层"] if required else [],
        "role_confirmations": {
            "技术负责人": "确认候选方向、证据要求、风险假设和不可承诺边界。",
            "销售负责人": "确认决策链、采购流程、预算阶段、时间线和客户成功标准。",
            "管理层": "确认招投标、质保、排放、重大降本或合同承诺风险。",
        }
        if required
        else {},
        "required_materials": required_materials if required else [],
        "missing_materials": _missing_fields(record, material_fields) if required else [],
    }


def _assess_level_4_5_readiness(record: dict[str, object]) -> dict[str, object]:
    level_4_groups = {
        "候选方向": ["候选方向", "候选方案"],
        "证据要求": ["证据要求", "证据包"],
        "试用/验证边界": ["试用/验证边界", "试用验证边界", "验证边界", "试用范围"],
        "人工确认": ["人工确认", "技术负责人确认", "内部确认"],
    }
    level_5_groups = {
        "客户需求摘要": ["客户需求摘要", "客户目标", "本次目标"],
        "工况档案": ["工况档案", "行业"],
        "真实需求判断": ["真实需求判断", "客户想解决的问题"],
        "风险假设": ["风险假设", "初步风险标签", "风险"],
        "候选方向": ["候选方向", "候选方案"],
        "试用验证计划": ["试用验证计划", "试用计划"],
        "客户话术": ["客户话术", "客户转述版"],
        "禁止承诺项": ["禁止承诺项", "当前禁止输出"],
        "下一步行动清单": ["下一步行动清单", "下一步动作"],
        "人工确认": ["人工确认", "技术负责人确认", "内部确认"],
    }

    level_4_blockers = [f"缺{field}" for field in _missing_fields(record, level_4_groups)]
    level_5_blockers = [f"缺{field}" for field in _missing_fields(record, level_5_groups)]

    return {
        "level_4_ready": not level_4_blockers,
        "level_4_blockers": level_4_blockers,
        "level_5_ready": not level_5_blockers,
        "level_5_blockers": level_5_blockers,
        "note": "Level 4/5 只表示资料包 readiness，仍不能自动形成最终型号、寿命、排放或质保承诺。",
    }


def _build_next_actions(
    decision_chain: dict[str, object],
    quote_readiness: dict[str, object],
    trial_validation: dict[str, object],
    escalation_package: dict[str, object],
    level_4_5_readiness: dict[str, object],
) -> list[dict[str, str]]:
    actions: list[dict[str, str]] = []

    missing_roles = decision_chain["missing_roles"]
    if missing_roles:
        actions.append(
            {
                "owner": "销售负责人",
                "needed_info": "、".join(missing_roles),
                "timepoint": "下一轮客户沟通前",
                "goal": "补齐决策链和关键顾虑",
                "target_level": "Level 2",
            }
        )

    missing_quote = quote_readiness["missing_quote_fields"]
    if missing_quote:
        actions.append(
            {
                "owner": "销售负责人",
                "needed_info": "、".join(missing_quote),
                "timepoint": "报价前",
                "goal": "判断是否只能预算报价或可进入正式报价",
                "target_level": "Level 3",
            }
        )

    if trial_validation["needed"]:
        actions.append(
            {
                "owner": "销售负责人 + 技术负责人",
                "needed_info": "、".join(trial_validation["missing_fields"] or trial_validation["required_fields"]),
                "timepoint": "试用前",
                "goal": "锁定试用范围、对照基线、观察周期和验收指标",
                "target_level": "Level 4",
            }
        )

    if escalation_package["required"]:
        actions.append(
            {
                "owner": "技术负责人",
                "needed_info": "、".join(escalation_package["missing_materials"] or escalation_package["required_materials"]),
                "timepoint": "对外提交候选方案/技术标/盖章材料前",
                "goal": "完成内部升级包和人工确认",
                "target_level": "Level 4/5",
            }
        )

    if not level_4_5_readiness["level_4_ready"] and not actions:
        actions.append(
            {
                "owner": "销售负责人",
                "needed_info": "、".join(level_4_5_readiness["level_4_blockers"]),
                "timepoint": "进入候选方案前",
                "goal": "补齐 Level 4 readiness",
                "target_level": "Level 4",
            }
        )

    return actions


def assess_presales_progression(record: dict[str, object]) -> dict[str, object]:
    text = _text(record)
    decision_chain = _assess_decision_chain(record, text)
    quote_readiness = _assess_quote_readiness(record, text)
    capability_match = _assess_capability_match(record, text)
    trial_validation = _assess_trial_validation(record, text)
    competitor_position = _assess_competitor_position(record, text)
    commercial_value = _assess_commercial_value(record)
    escalation_package = _assess_escalation_package(record, text)
    level_4_5_readiness = _assess_level_4_5_readiness(record)

    return {
        "decision_chain_status": decision_chain,
        "quote_readiness": quote_readiness,
        "capability_match": capability_match,
        "trial_validation": trial_validation,
        "competitor_position": competitor_position,
        "commercial_value": commercial_value,
        "escalation_package": escalation_package,
        "next_actions": _build_next_actions(
            decision_chain,
            quote_readiness,
            trial_validation,
            escalation_package,
            level_4_5_readiness,
        ),
        "level_4_5_readiness": level_4_5_readiness,
    }
