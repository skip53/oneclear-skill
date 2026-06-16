import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from risk_tag_rules import tag_risks


def test_tags_condensation_for_humidity_and_blinding():
    record = {"故障表现": "糊袋 压差高", "含湿量": "高", "启停频率": "频繁"}
    result = tag_risks(record)
    assert "结露 / 含湿风险" in result


def test_tags_spark_burn_risk():
    record = {"故障表现": "烧袋", "火星/高温颗粒": "有"}
    result = tag_risks(record)
    assert "火星烧袋风险" in result


def test_tags_replacement_costdown_risk():
    record = {"替换目标": "降本", "客户原话": "想换便宜点"}
    result = tag_risks(record)
    assert "替换降本风险" in result
