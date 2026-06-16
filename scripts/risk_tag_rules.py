from __future__ import annotations


def _contains(record: dict[str, str], terms: list[str]) -> bool:
    text = " ".join(str(value) for value in record.values())
    return any(term in text for term in terms)


def tag_risks(record: dict[str, str]) -> list[str]:
    risks: list[str] = []
    if _contains(record, ["峰值", "高温", "烧", "收缩"]):
        risks.append("温度风险")
    if _contains(record, ["含湿", "结露", "糊袋", "压差高", "频繁启停", "启停频率"]):
        risks.append("结露 / 含湿风险")
    if _contains(record, ["水解", "高湿", "变脆"]):
        risks.append("水解风险")
    if _contains(record, ["氧化", "含氧"]):
        risks.append("氧化风险")
    if _contains(record, ["酸", "碱", "腐蚀", "HCl", "SOx", "NOx"]):
        risks.append("酸碱腐蚀风险")
    if _contains(record, ["磨蚀", "冲刷", "迎风面", "局部破"]):
        risks.append("粉尘磨蚀风险")
    if _contains(record, ["粘", "油", "糊袋"]):
        risks.append("粘性 / 油性糊袋风险")
    if _contains(record, ["火星", "高温颗粒", "烧袋", "烧穿"]):
        risks.append("火星烧袋风险")
    if _contains(record, ["清灰", "压差", "喷吹"]):
        risks.append("清灰 / 压差风险")
    if _contains(record, ["降本", "便宜", "替换", "竞品"]):
        risks.append("替换降本风险")
    return list(dict.fromkeys(risks))
