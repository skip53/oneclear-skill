import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from presales_progression import assess_presales_progression


def test_quote_readiness_blocks_formal_quote_without_specs_quantity_or_work_condition():
    record = {
        "客户原话": "先报个价，看看多少钱。",
        "项目类型": "新项目选型",
        "行业": "水泥",
    }

    result = assess_presales_progression(record)

    assert result["quote_readiness"]["status"] == "不能正式报价"
    assert "规格" in result["quote_readiness"]["missing_quote_fields"]
    assert "数量" in result["quote_readiness"]["missing_quote_fields"]
    assert "工况边界" in result["quote_readiness"]["missing_quote_fields"]
    assert "技术承诺风险未排除" in result["quote_readiness"]["risk_notes"]


def test_competitor_stable_costdown_requires_current_baseline_and_small_trial():
    record = {
        "客户原话": "竞品袋子现在用着稳定，就是价格太高，想换便宜一点降本。",
        "项目类型": "替换 / 降本",
        "行业": "水泥",
        "当前方案是否稳定": "稳定",
        "替换目标": "降本",
    }

    result = assess_presales_progression(record)

    assert result["competitor_position"]["status"] == "竞品稳定降本"
    assert result["competitor_position"]["recommended_posture"] == "需当前基线 + 小批量试用"
    assert "当前稳定基线" in result["competitor_position"]["required_evidence"]
    assert result["trial_validation"]["needed"] is True
    assert result["trial_validation"]["suggested_mode"] == "小批量试用"


def test_trial_validation_generates_required_fields_for_bay_trial():
    record = {
        "客户原话": "客户想先分仓试用，和原来的袋子对比一下压差和排放。",
        "项目类型": "替换 / 降本",
        "行业": "钢铁",
        "试用方式": "分仓试用",
    }

    result = assess_presales_progression(record)

    assert result["trial_validation"]["needed"] is True
    assert result["trial_validation"]["suggested_mode"] == "分仓对照试用"
    assert "试用仓/对照仓" in result["trial_validation"]["required_fields"]
    assert "基线数据" in result["trial_validation"]["required_fields"]
    assert "观察周期" in result["trial_validation"]["required_fields"]
    assert "验收指标" in result["trial_validation"]["required_fields"]


def test_tender_or_sealed_commitment_generates_escalation_package():
    record = {
        "客户原话": "下周投标，需要技术标、偏差表和盖章承诺，最好写保证排放10毫克以内。",
        "采购阶段": "招标",
        "本次目标": "技术标支持",
    }

    result = assess_presales_progression(record)

    assert result["escalation_package"]["required"] is True
    assert result["escalation_package"]["human_confirmation_required"] is True
    assert "技术负责人" in result["escalation_package"]["required_roles"]
    assert "销售负责人" in result["escalation_package"]["required_roles"]
    assert "管理层" in result["escalation_package"]["required_roles"]
    assert "禁止承诺项" in result["escalation_package"]["required_materials"]


def test_level_4_5_readiness_fails_without_evidence_or_human_confirmation():
    record = {
        "客户原话": "客户要候选方案和技术支持包。",
        "项目类型": "新项目选型",
        "行业": "水泥",
        "工况档案": "已有初稿",
        "候选方向": "候选方向A",
        "证据要求": "",
        "人工确认": "",
    }

    result = assess_presales_progression(record)

    assert result["level_4_5_readiness"]["level_4_ready"] is False
    assert result["level_4_5_readiness"]["level_5_ready"] is False
    assert "缺证据要求" in result["level_4_5_readiness"]["level_4_blockers"]
    assert "缺人工确认" in result["level_4_5_readiness"]["level_4_blockers"]
