from __future__ import annotations


BASE_P0 = ["客户原话", "项目类型", "行业"]
NEW_PROJECT_P1 = ["工艺段", "常态温度", "峰值温度", "含湿量", "粉尘性质", "除尘器类型", "排放要求", "目标寿命"]
FAILURE_P1 = [
    "工艺段",
    "故障表现",
    "当前材质",
    "使用时长",
    "故障位置/比例",
    "常态温度",
    "含湿量",
    "清灰参数",
    "压差曲线",
    "近期工况变化",
    "现场照片/样品/报告",
]
REPLACEMENT_P1 = ["当前材质", "当前寿命", "替换目标", "当前方案是否稳定"]


def _missing(record: dict[str, str], keys: list[str]) -> list[str]:
    return [key for key in keys if not str(record.get(key, "")).strip()]


def assess_context_level(record: dict[str, str]) -> dict[str, object]:
    missing_p0 = _missing(record, BASE_P0)
    if missing_p0:
        return {
            "level": 0,
            "missing_p0": missing_p0,
            "missing_p1": [],
            "allowed_outputs": ["最小澄清问题", "信息缺口说明"],
            "forbidden_outputs": ["滤料方向", "材质建议", "报价建议", "寿命承诺"],
        }

    case_type = record.get("项目类型", "")
    if case_type == "新项目选型":
        missing_p1 = _missing(record, NEW_PROJECT_P1)
    elif case_type == "旧项目故障":
        missing_p1 = _missing(record, FAILURE_P1)
    elif case_type == "替换 / 降本":
        missing_p1 = _missing(record, REPLACEMENT_P1)
    else:
        return {
            "level": 0,
            "missing_p0": [],
            "missing_p1": ["项目类型无法识别"],
            "allowed_outputs": ["最小澄清问题", "信息缺口说明"],
            "forbidden_outputs": ["滤料方向", "材质建议", "报价建议", "寿命承诺"],
        }

    if len(missing_p1) >= 4:
        level = 1
        allowed = ["问题类型判断", "对应追问路径", "工况档案草稿"]
        forbidden = ["具体原因判断", "具体材料建议", "方案承诺"]
    elif missing_p1:
        level = 2
        allowed = ["风险标签", "初步归因假设", "证据需求"]
        forbidden = ["具体滤料推荐", "承诺换材质可解决"]
    else:
        level = 3
        allowed = ["可给选型方向，但不可确定型号"]
        forbidden = ["唯一推荐型号", "确定寿命", "确定替代竞品"]

    return {
        "level": level,
        "missing_p0": [],
        "missing_p1": missing_p1,
        "allowed_outputs": allowed,
        "forbidden_outputs": forbidden,
    }
