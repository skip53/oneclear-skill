import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from classify_case_type import classify_case_type


def test_classifies_new_project_selection():
    result = classify_case_type("客户是水泥厂新项目，窑尾除尘问用什么滤袋")
    assert result["case_type"] == "新项目选型"
    assert result["confidence"] >= 0.5


def test_classifies_existing_failure():
    result = classify_case_type("客户说袋子半年就压差高，清灰下不来，是不是质量问题")
    assert result["case_type"] == "旧项目故障"
    assert "压差" in result["signals"]


def test_classifies_replacement_costdown():
    result = classify_case_type("现在用竞品PTFE覆膜袋太贵，想换便宜点")
    assert result["case_type"] == "替换 / 降本"
    assert "便宜" in result["signals"]


def test_classifies_insufficient_context():
    result = classify_case_type("客户问这个能不能做，帮忙看看")
    assert result["case_type"] == "信息不足，无法分流"
    assert result["confidence"] < 0.5
