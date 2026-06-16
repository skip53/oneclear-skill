import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from check_context_completeness import assess_context_level


def test_level_0_when_case_type_missing():
    record = {"客户原话": "", "项目类型": "", "行业": ""}
    result = assess_context_level(record)
    assert result["level"] == 0
    assert "客户原话" in result["missing_p0"]


def test_level_0_when_case_type_cannot_be_routed():
    record = {
        "客户原话": "客户说这个能不能做，帮忙看看",
        "项目类型": "信息不足，无法分流",
        "行业": "水泥",
    }
    result = assess_context_level(record)
    assert result["level"] == 0
    assert result["missing_p1"] == ["项目类型无法识别"]
    assert "最小澄清问题" in result["allowed_outputs"]


def test_level_1_for_failure_with_basic_problem_but_missing_diagnostic_context():
    record = {
        "客户原话": "袋子半年压差高",
        "项目类型": "旧项目故障",
        "行业": "水泥",
        "工艺段": "窑尾",
        "故障表现": "压差高",
    }
    result = assess_context_level(record)
    assert result["level"] == 1
    assert "现场照片/样品/报告" in result["missing_p1"]


def test_level_2_for_new_project_missing_customer_targets():
    record = {
        "客户原话": "窑尾新项目选型",
        "项目类型": "新项目选型",
        "行业": "水泥",
        "工艺段": "窑尾",
        "常态温度": "160",
        "峰值温度": "190",
        "含湿量": "已确认",
        "粉尘性质": "细粉",
        "除尘器类型": "袋式",
    }
    result = assess_context_level(record)
    assert result["level"] == 2
    assert "排放要求" in result["missing_p1"]
    assert "目标寿命" in result["missing_p1"]


def test_level_3_when_new_project_key_conditions_and_targets_present():
    record = {
        "客户原话": "窑尾新项目选型，要求10毫克以内，用两年",
        "项目类型": "新项目选型",
        "行业": "水泥",
        "工艺段": "窑尾",
        "常态温度": "160",
        "峰值温度": "190",
        "含湿量": "已确认",
        "粉尘性质": "细粉",
        "除尘器类型": "袋式",
        "排放要求": "10mg/Nm3",
        "目标寿命": "24个月",
    }
    result = assess_context_level(record)
    assert result["level"] == 3
    assert "可给选型方向" in result["allowed_outputs"][0]


def test_level_2_for_failure_missing_pressure_cleaning_and_work_condition_evidence():
    record = {
        "客户原话": "袋子半年压差高",
        "项目类型": "旧项目故障",
        "行业": "水泥",
        "工艺段": "窑尾",
        "故障表现": "压差高",
        "当前材质": "PPS",
        "使用时长": "半年",
        "故障位置/比例": "中上部，约10%",
        "常态温度": "160",
        "含湿量": "已确认",
        "近期工况变化": "近期原料含湿升高",
        "现场照片/样品/报告": "已有照片",
    }
    result = assess_context_level(record)
    assert result["level"] == 2
    assert "压差曲线" in result["missing_p1"]
    assert "清灰参数" in result["missing_p1"]


def test_level_3_for_complete_existing_failure_context():
    record = {
        "客户原话": "袋子半年压差高",
        "项目类型": "旧项目故障",
        "行业": "水泥",
        "工艺段": "窑尾",
        "故障表现": "压差高",
        "当前材质": "PPS",
        "使用时长": "半年",
        "故障位置/比例": "中上部，约10%",
        "常态温度": "160",
        "含湿量": "已确认",
        "清灰参数": "脉冲0.3MPa，每20分钟",
        "压差曲线": "有近三个月曲线",
        "近期工况变化": "近期原料含湿升高",
        "现场照片/样品/报告": "已有照片",
    }
    result = assess_context_level(record)
    assert result["level"] == 3
    assert result["missing_p1"] == []


def test_level_3_for_complete_replacement_context():
    record = {
        "客户原话": "想替换竞品袋子降本",
        "项目类型": "替换 / 降本",
        "行业": "水泥",
        "当前材质": "PTFE覆膜",
        "当前寿命": "18个月",
        "替换目标": "降本",
        "当前方案是否稳定": "稳定",
    }
    result = assess_context_level(record)
    assert result["level"] == 3
    assert result["missing_p1"] == []
