import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from agent_os_governance import assess_governance


def test_detects_high_demand_gap_when_surface_request_conflicts_with_failure():
    record = {
        "客户原话": "袋子半年压差高，清灰下不来，能不能直接换个便宜点的？",
        "客户表达的需求": "换便宜",
        "故障表现": "压差高",
        "当前方案是否稳定": "不稳定",
    }
    result = assess_governance(record)
    assert result["demand_validation"]["gap_level"] == "high"
    assert "表层需求是降本，但现场仍有未解释故障" in result["demand_validation"]["gap_signals"]
    assert "不能把故障问题直接转成低价替换问题" in result["exceptions"]


def test_flags_commitment_and_compliance_risks():
    record = {
        "客户原话": "能不能保证排放10毫克以内，质保两年？照片和竞品检测报告不要外传。",
        "排放要求": "10mg/Nm3",
        "目标寿命": "24个月",
        "现场照片/样品/报告": "客户照片和竞品检测报告",
    }
    result = assess_governance(record)
    assert "排放保证风险" in result["compliance_commitment"]
    assert "质保/寿命承诺风险" in result["compliance_commitment"]
    assert "客户现场资料保密风险" in result["compliance_commitment"]
    assert "竞品资料保密风险" in result["compliance_commitment"]
    assert result["risk_escalation"]["level"] == "red"


def test_detects_tender_procurement_stage_and_human_confirmation_need():
    record = {
        "客户原话": "这个项目下周投标，需要技术条款、偏差表和盖章承诺。",
        "采购阶段": "招标",
        "本次目标": "投标技术文件",
    }
    result = assess_governance(record)
    assert result["commercial_stage"] == "招投标 / 技术标阶段"
    assert "招投标技术承诺风险" in result["compliance_commitment"]
    assert "需要人工技术确认" in result["required_controls"]


def test_detects_multiround_case_update():
    record = {
        "客户原话": "补充一下，现场温度160度，含湿高，压差曲线稍后发。",
        "上一轮结论": "旧项目故障 Level 1，需补温度、含湿、压差曲线",
        "新增信息": "温度160度，含湿高",
    }
    result = assess_governance(record)
    assert result["case_progress"]["mode"] == "多轮补充"
    assert "新增信息需要合并进工况档案" in result["required_controls"]
