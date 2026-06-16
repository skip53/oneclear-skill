from __future__ import annotations


NEW_PROJECT_KEYWORDS = ["新项目", "新上", "新建", "选型", "用什么", "设计院", "新增"]
FAILURE_KEYWORDS = ["糊袋", "破袋", "压差", "排放超标", "寿命短", "不耐用", "清灰", "烧袋", "变硬", "腐蚀"]
REPLACEMENT_KEYWORDS = ["替换", "换便宜", "便宜", "降本", "竞品", "太贵", "同等寿命", "PTFE覆膜"]


def _matches(text: str, keywords: list[str]) -> list[str]:
    return [keyword for keyword in keywords if keyword in text]


def classify_case_type(text: str) -> dict[str, object]:
    normalized = text.strip()
    scores = {
        "新项目选型": _matches(normalized, NEW_PROJECT_KEYWORDS),
        "旧项目故障": _matches(normalized, FAILURE_KEYWORDS),
        "替换 / 降本": _matches(normalized, REPLACEMENT_KEYWORDS),
    }
    best_type, signals = max(scores.items(), key=lambda item: len(item[1]))
    if not signals:
        return {
            "case_type": "信息不足，无法分流",
            "confidence": 0.0,
            "signals": [],
            "clarifying_questions": [
                "这是新项目选型、旧项目故障，还是替换现有滤袋？",
                "有没有客户原话或聊天记录？",
                "现场行业和工艺段是什么？",
            ],
        }

    total_signal_count = sum(len(value) for value in scores.values())
    confidence = len(signals) / max(total_signal_count, 1)
    if len(signals) == 1 and len(normalized) < 16:
        confidence = min(confidence, 0.4)

    return {
        "case_type": best_type,
        "confidence": round(confidence, 2),
        "signals": signals,
        "clarifying_questions": [],
    }
