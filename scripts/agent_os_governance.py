from __future__ import annotations


def _text(record: dict[str, str]) -> str:
    return " ".join(str(value) for value in record.values() if value is not None)


def _has_any(text: str, terms: list[str]) -> bool:
    return any(term in text for term in terms)


def _value(record: dict[str, str], key: str) -> str:
    return str(record.get(key, "")).strip()


def _assess_demand_validation(record: dict[str, str], text: str) -> dict[str, object]:
    signals: list[str] = []
    clarifications: list[str] = []

    costdown = _has_any(text, ["便宜", "降本", "价格太高", "换便宜", "低价"])
    failure = _has_any(text, ["压差高", "糊袋", "破袋", "排放超标", "寿命短", "清灰下不来", "不稳定"])
    quote_only = _has_any(text, ["报价", "报个价", "多少钱", "价格"])
    missing_goal = not _value(record, "客户想解决的问题") and not _value(record, "本次目标")

    if costdown and failure:
        signals.append("表层需求是降本，但现场仍有未解释故障")
        clarifications.append("先确认客户真正要解决的是故障恢复、寿命改善，还是单纯降本。")
    if quote_only and not _has_any(text, ["温度", "含湿", "工艺", "材质", "寿命", "排放"]):
        signals.append("客户要求报价，但缺少选型和报价所需工况")
        clarifications.append("先补行业、工艺段、规格、材质、温度、含湿、数量和目标。")
    if missing_goal:
        signals.append("客户目标未显式确认")
        clarifications.append("确认本轮目标是诊断、选型、报价、试用、索赔、替换还是技术标支持。")

    if any("表层需求" in signal for signal in signals):
        gap_level = "high"
    elif signals:
        gap_level = "medium"
    else:
        gap_level = "low"

    return {
        "gap_level": gap_level,
        "gap_signals": signals,
        "clarifications": clarifications,
    }


def _detect_exceptions(record: dict[str, str], text: str, demand_gap_signals: list[str]) -> list[str]:
    exceptions: list[str] = []
    if not _value(record, "客户原话"):
        exceptions.append("缺少客户原话")
    if _value(record, "业务员转述") and not _value(record, "客户原话"):
        exceptions.append("只有业务员转述，存在转译失真风险")
    if "表层需求是降本，但现场仍有未解释故障" in demand_gap_signals:
        exceptions.append("不能把故障问题直接转成低价替换问题")
    if _has_any(text, ["保证", "质保", "承诺", "肯定", "一定", "完全替代"]):
        exceptions.append("客户要求超出当前证据边界的确定承诺")
    if _has_any(text, ["但是", "不过", "前面说", "又说"]) and _has_any(text, ["稳定", "不稳定", "能用", "不行"]):
        exceptions.append("输入存在潜在矛盾，需要拆分已知和矛盾信息")
    return list(dict.fromkeys(exceptions))


def _detect_compliance_commitment(text: str) -> list[str]:
    flags: list[str] = []
    if _has_any(text, ["保证排放", "排放保证", "达标承诺", "10毫克以内", "超低排放"]):
        flags.append("排放保证风险")
    if _has_any(text, ["质保", "保用", "保证寿命", "用两年", "寿命差不多"]):
        flags.append("质保/寿命承诺风险")
    if _has_any(text, ["照片", "现场资料", "检测报告", "不要外传", "保密"]):
        flags.append("客户现场资料保密风险")
    if _has_any(text, ["竞品检测", "竞品样品", "竞品报告", "供应商资料"]):
        flags.append("竞品资料保密风险")
    if _has_any(text, ["投标", "招标", "技术条款", "偏差表", "盖章承诺", "合同"]):
        flags.append("招投标技术承诺风险")
    if _has_any(text, ["安全事故", "爆炸", "着火", "火星", "安环"]):
        flags.append("安环风险")
    return list(dict.fromkeys(flags))


def _detect_commercial_stage(record: dict[str, str], text: str) -> str:
    if _has_any(text, ["投标", "招标", "技术条款", "偏差表", "盖章承诺"]) or _value(record, "采购阶段") == "招标":
        return "招投标 / 技术标阶段"
    if _has_any(text, ["索赔", "质量问题", "你们袋子有问题", "赔"]):
        return "故障索赔 / 责任判断阶段"
    if _has_any(text, ["试用", "小批量", "分仓"]):
        return "试用验证阶段"
    if _has_any(text, ["竞品", "替换", "换便宜", "降本"]):
        return "竞品替换 / 降本阶段"
    if _has_any(text, ["报价", "多少钱", "价格"]):
        return "询价 / 报价前置阶段"
    if _has_any(text, ["新项目", "新建", "新上", "选型"]):
        return "技术发现 / 新项目选型阶段"
    return "商业阶段未知"


def _assess_risk_escalation(
    demand_validation: dict[str, object],
    exceptions: list[str],
    compliance_commitment: list[str],
) -> dict[str, object]:
    reasons: list[str] = []

    if demand_validation["gap_level"] == "high":
        reasons.append("客户表达需求与真实工况问题存在高 gap")
    if exceptions:
        reasons.extend(exceptions)
    if compliance_commitment:
        reasons.extend(compliance_commitment)

    no_go_terms = ["招投标技术承诺风险", "排放保证风险", "质保/寿命承诺风险"]
    if any(reason in no_go_terms for reason in reasons):
        level = "red"
    elif demand_validation["gap_level"] == "high" or exceptions:
        level = "amber"
    else:
        level = "green"

    return {"level": level, "reasons": list(dict.fromkeys(reasons))}


def _assess_case_progress(record: dict[str, str]) -> dict[str, object]:
    if _value(record, "上一轮结论") or _value(record, "新增信息"):
        return {
            "mode": "多轮补充",
            "state_action": "合并新增信息，保留上一轮未知项，重新判断 Level。",
        }
    return {
        "mode": "首轮诊断",
        "state_action": "建立初始工况档案和追问路径。",
    }


def assess_governance(record: dict[str, str]) -> dict[str, object]:
    text = _text(record)
    demand_validation = _assess_demand_validation(record, text)
    exceptions = _detect_exceptions(record, text, demand_validation["gap_signals"])
    compliance_commitment = _detect_compliance_commitment(text)
    commercial_stage = _detect_commercial_stage(record, text)
    risk_escalation = _assess_risk_escalation(demand_validation, exceptions, compliance_commitment)
    case_progress = _assess_case_progress(record)

    required_controls: list[str] = []
    if case_progress["mode"] == "多轮补充":
        required_controls.append("新增信息需要合并进工况档案")
    if compliance_commitment or risk_escalation["level"] == "red":
        required_controls.append("需要人工技术确认")
    if demand_validation["gap_level"] in {"medium", "high"}:
        required_controls.append("先澄清真实需求再推进方案")
    if not required_controls:
        required_controls.append("按当前 Level 输出下一步追问")

    return {
        "demand_validation": demand_validation,
        "exceptions": exceptions,
        "risk_escalation": risk_escalation,
        "compliance_commitment": compliance_commitment,
        "commercial_stage": commercial_stage,
        "case_progress": case_progress,
        "required_controls": list(dict.fromkeys(required_controls)),
    }
