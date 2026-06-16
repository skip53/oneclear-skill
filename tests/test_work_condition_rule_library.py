import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from collections import Counter

from work_condition_rule_library import (
    assess_work_condition_rules,
    evaluate_condition_set,
    load_rule_library,
    normalize_work_condition,
)


def test_json_rule_library_loads_full_source_rule_set():
    library = load_rule_library()
    rules = library["rules"]

    assert library["source_version"] == "2026-04-application-only"
    assert len(rules) == 87
    assert Counter(rule["rule_type"] for rule in rules) == {
        "hard_constraint": 24,
        "strong_preference": 38,
        "risk_warning": 18,
        "negative_bias": 3,
        "weight_adjustment": 3,
        "system_policy": 1,
    }
    assert all("presales_outputs" in rule for rule in rules)


def test_ac_is_blocked_above_normal_temperature_limit():
    result = assess_work_condition_rules({
        "常态温度": "126",
        "烟气成分": [],
        "腐蚀成分状态": "已确认无",
    })

    assert "RULE_011_TEMP_AC_PROHIBITED" in result["matched_rules"]
    assert "AC" in result["blocked_options"]
    assert "AC" not in result["preferred_materials"]


def test_condition_evaluator_supports_length_in_contains_exists_and_neq():
    normalized = normalize_work_condition({
        "烟气成分": [],
        "腐蚀成分状态": "已确认无",
        "粉尘粘性": "高",
        "除尘器类型": "水平滤筒",
        "露点": "88",
    })

    assert evaluate_condition_set(normalized, [
        {"field_path": "flue_gas.corrosive_components.length", "operator": "lte", "value": 0},
        {"field_path": "dust.stickiness", "operator": "in", "values": ["medium", "high"]},
        {"field_path": "dust_collector.type", "operator": "contains", "value": "水平"},
        {"field_path": "flue_gas.dew_point", "operator": "exists"},
        {"field_path": "dust.stickiness", "operator": "neq", "value": "low"},
    ])


def test_blocks_material_options_without_recommending_final_material():
    record = {
        "行业": "垃圾焚烧",
        "常态温度": "165",
        "烟气成分": ["HF", "SO2"],
        "含氧量": "14",
        "含湿量": "12",
        "露点": "95",
    }

    result = assess_work_condition_rules(record)

    assert "PET" in result["blocked_options"]
    assert "PPS" in result["blocked_options"]
    assert "GLASS_FIBER" in result["blocked_options"]
    assert "HF 玻纤腐蚀/断裂风险" in result["risk_flags"]
    assert "高氧+含硫 PPS 氧化/硫化风险" in result["risk_flags"]
    assert "结露窗口风险" in result["risk_flags"]
    assert result["human_confirmation_required"] is True
    assert "PTFE" in result["preferred_materials"]
    assert "PET" not in result["preferred_materials"]
    assert "PPS" not in result["preferred_materials"]
    assert "GLASS_FIBER" not in result["preferred_materials"]
    assert "不得把规则命中解释为最终型号推荐" in result["forbidden_commitments"]


def test_system_risks_require_system_actions_before_material_upgrade():
    record = {
        "客户原话": "压差高，糊袋，喷吹气源含水，过滤风速1.7，粉尘粘性高。",
        "过滤风速": 1.7,
        "粉尘粘性": "高",
        "清灰方式": "脉冲",
        "清灰气源含水": "是",
    }

    result = assess_work_condition_rules(record)

    assert "高过滤风速寿命折损风险" in result["risk_flags"]
    assert "高粘性粉尘深层糊袋风险" in result["risk_flags"]
    assert "脉冲气源含水直接糊袋风险" in result["risk_flags"]
    assert "DEEP_NEEDLE_FELT" in result["blocked_options"]
    assert "先核算过滤风速/过滤面积，再讨论滤料升级" in result["system_actions"]
    assert "气源干燥/除油状态" in result["required_evidence"]


def test_missing_corrosion_is_distinguished_from_confirmed_no_corrosion():
    unknown_record = {
        "常态温度": "90",
        "腐蚀成分状态": "未知",
    }
    confirmed_none_record = {
        "常态温度": "90",
        "烟气成分": [],
        "腐蚀成分状态": "已确认无",
    }

    unknown = assess_work_condition_rules(unknown_record)
    confirmed_none = assess_work_condition_rules(confirmed_none_record)

    assert "腐蚀成分未知" in unknown["missing_evidence"]
    assert "腐蚀成分未知" not in confirmed_none["missing_evidence"]


def test_explosive_or_spark_signals_require_safety_validation_not_material_only_answer():
    record = {
        "行业": "生物质锅炉",
        "粉尘是否爆炸": "是",
        "客户原话": "现场有火星，之前烧袋。",
    }

    result = assess_work_condition_rules(record)

    assert "防静电系统验证要求" in result["risk_flags"]
    assert "火星烧穿风险" in result["risk_flags"]
    assert "先确认火星捕集/阻火/安环措施，不承诺滤料单独解决" in result["system_actions"]
    assert "安环措施/火星来源" in result["required_evidence"]


def test_strong_preference_rules_output_preferred_materials_without_final_model():
    record = {
        "行业": "水泥窑尾",
        "常态温度": "150",
        "含氧量": "6",
        "烟气成分": [],
        "腐蚀成分状态": "已确认无",
        "粉尘磨蚀性": "高",
        "粉尘粒径": "粗颗粒",
        "客户目标": ["性价比", "低能耗"],
        "清灰方式": "脉冲",
        "客户原话": "希望低能耗，压差别太高。",
    }

    result = assess_work_condition_rules(record)

    assert result["strong_preference_rules_migrated"] == 38
    assert "RULE_105_MID_TEMP_PPS_PREFERENCE" in result["matched_rules"]
    assert "RULE_110_CEMENT_POWER_STEEL_PPS" in result["matched_rules"]
    assert "RULE_004_HIGH_ABRASION_FIBER_PRIORITY" in result["matched_rules"]
    assert "PPS" in result["preferred_materials"]
    assert "ARAMID" in result["preferred_materials"]
    assert "FIBER_TYPE_BASE_FABRIC" in result["preferred_materials"]
    assert "LOW_RESISTANCE_SURFACE_FILTER" in result["preferred_materials"]
    assert "PPS" in result["preferred_material_reasons"]
    assert "RULE_105_MID_TEMP_PPS_PREFERENCE" in result["preferred_material_reasons"]["PPS"]
    assert "final_material" not in result


def test_surface_filtration_preference_group_maps_to_evidence_requirements():
    record = {
        "客户原话": "现场糊袋、压差高，粉尘很细且有油，排放偶尔穿透，客户要求超低排放。",
        "粉尘粘性": "中",
        "粉尘吸湿性": "高",
        "粉尘粒径": "超细",
        "故障表现": ["糊袋", "排放穿透"],
        "客户目标": ["超低排放"],
        "清灰方式": "脉冲",
    }

    result = assess_work_condition_rules(record)

    assert "RULE_003A_MEMBRANE_BAG_CLOGGING_PAIN" in result["matched_rules"]
    assert "RULE_020_ULTRA_FINE_EPTFE_MEMBRANE" in result["matched_rules"]
    assert "RULE_021_OIL_BEARING_MEMBRANE" in result["matched_rules"]
    assert "RULE_056A_EMISSION_BREAKTHROUGH_MEMBRANE" in result["matched_rules"]
    assert "MEMBRANE_OR_GRADIENT" in result["preferred_materials"]
    assert "ePTFE_MEMBRANE" in result["preferred_materials"]
    assert "WATER_OIL_REPELLENT_MEMBRANE" in result["preferred_materials"]
    assert "PTFE" in result["preferred_materials"]
    assert "粉尘粒径" in result["required_evidence"]
    assert "排放记录/验收方法" in result["required_evidence"]


def test_low_temperature_cost_rule_outputs_pet_as_preferred_not_final_material():
    record = {
        "常态温度": "90",
        "烟气成分": [],
        "腐蚀成分状态": "已确认无",
        "客户目标": ["性价比"],
        "客户原话": "低温无腐蚀，预算敏感，希望性价比高。",
    }

    result = assess_work_condition_rules(record)

    assert "RULE_010_LOW_TEMP_NO_CORROSION_COST_PET" in result["matched_rules"]
    assert "PTFE_MAIN" in result["blocked_options"]
    assert "PET" in result["preferred_materials"]
    assert "PET" in result["preferred_material_reasons"]
    assert "final_material" not in result


def test_blocked_options_remove_conflicting_preferred_materials():
    result = assess_work_condition_rules({
        "行业": "水泥窑尾",
        "常态温度": "150",
        "含氧量": "14",
        "烟气成分": ["SO2"],
        "腐蚀成分状态": "已确认",
    })

    assert "RULE_001A_PPS_HIGH_OXYGEN_SULFUR_BLOCK" in result["matched_rules"]
    assert "RULE_110_CEMENT_POWER_STEEL_PPS" in result["matched_rules"]
    assert "PPS" in result["blocked_options"]
    assert "PPS" not in result["preferred_materials"]
