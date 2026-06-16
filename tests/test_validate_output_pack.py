import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from validate_output_pack import validate_output_pack


GOOD_OUTPUT = """
## 一、工况档案草稿
- 当前 Level：Level 2
- 真实需求判断：表层需求与真实问题一致
- 异常状态：无
- 风险升级等级：amber
- 合规/承诺边界：不承诺寿命
- 商业/采购阶段：技术发现
- 案件状态：diagnosis
## 二、追问清单
1. 问题：压差曲线有没有？
## 三、初步诊断摘要
- 当前判断：只能初步判断
"""


def test_validates_three_part_output():
    result = validate_output_pack(GOOD_OUTPUT, level=2)
    assert result["ok"] is True
    assert result["issues"] == []


def test_flags_missing_sections():
    result = validate_output_pack("只有一段话", level=1)
    assert result["ok"] is False
    assert "缺少工况档案草稿" in result["issues"]


def test_flags_missing_governance_fields():
    output = """
## 一、工况档案草稿
- 当前 Level：Level 2
## 二、追问清单
1. 问题：压差曲线有没有？
## 三、初步诊断摘要
- 当前判断：只能初步判断
"""
    result = validate_output_pack(output, level=2)
    assert result["ok"] is False
    assert "缺少真实需求判断" in result["issues"]
    assert "缺少异常状态" in result["issues"]
    assert "缺少风险升级等级" in result["issues"]
    assert "缺少合规/承诺边界" in result["issues"]
    assert "缺少商业/采购阶段" in result["issues"]
    assert "缺少案件状态" in result["issues"]


def test_flags_overcommit_for_low_level():
    result = validate_output_pack(GOOD_OUTPUT + "推荐使用PPS，保证寿命。", level=2)
    assert result["ok"] is False
    assert "Level 2 禁止具体推荐或寿命承诺" in result["issues"]


def test_flags_specific_material_recommendation_for_level_3():
    result = validate_output_pack(GOOD_OUTPUT + "推荐使用PPS。", level=3)
    assert result["ok"] is False
    assert "Level 3 禁止具体材料推荐或确定效果承诺" in result["issues"]


def test_flags_common_specific_material_wording_for_level_3():
    outputs = [
        "建议用PPS。",
        "推荐使用 PPS。",
        "推荐使用玻纤。",
        "建议使用PTFE覆膜。",
        "可以用芳纶。",
    ]
    for output in outputs:
        result = validate_output_pack(GOOD_OUTPUT + output, level=3)
        assert result["ok"] is False
        assert "Level 3 禁止具体材料推荐或确定效果承诺" in result["issues"]


LEVEL_4_OUTPUT = GOOD_OUTPUT + """
## 四、售前推进判断
- 候选方向：方向A / 方向B，均需人工确认。
- 证据要求：温度、含湿、压差曲线、现场照片、当前基线。
- 试用/验证边界：仅限分仓或小批量验证，不做全量替换承诺。
- 人工确认：技术负责人确认后才能对外使用。
"""


LEVEL_5_OUTPUT = GOOD_OUTPUT + """
## 四、技术支持包
- 客户需求摘要：客户希望在排放稳定前提下降低总使用成本。
- 工况档案：已整理行业、工艺段、温度、含湿、粉尘、当前滤袋。
- 真实需求判断：不是单纯低价，而是稳定前提下的总成本优化。
- 风险假设：温度波动、含湿和压差变化仍需验证。
- 候选方向：方向A / 方向B，等待技术负责人确认。
- 试用验证计划：分仓对照，记录压差、排放、外观和运行周期。
- 客户话术：建议先按试用边界对齐验收口径。
- 禁止承诺项：不承诺寿命、排放、完全替代或质保。
- 下一步行动清单：销售补齐决策链，技术负责人确认候选方向。
"""


def test_level_4_requires_trial_or_validation_boundary():
    output = LEVEL_4_OUTPUT.replace("- 试用/验证边界：仅限分仓或小批量验证，不做全量替换承诺。\n", "")
    result = validate_output_pack(output, level=4)
    assert result["ok"] is False
    assert "Level 4 缺少试用/验证边界" in result["issues"]


def test_level_5_requires_next_actions_and_forbidden_commitments():
    output = LEVEL_5_OUTPUT.replace("- 下一步行动清单：销售补齐决策链，技术负责人确认候选方向。\n", "")
    output = output.replace("- 禁止承诺项：不承诺寿命、排放、完全替代或质保。\n", "")
    result = validate_output_pack(output, level=5)
    assert result["ok"] is False
    assert "Level 5 缺少下一步行动清单" in result["issues"]
    assert "Level 5 缺少禁止承诺项" in result["issues"]


def test_level_4_flags_overcommit_even_when_candidate_direction_is_allowed():
    output = LEVEL_4_OUTPUT + """
- 候选方向：PPS / PTFE，仅作为技术负责人确认前的候选方向。
- 但销售可以对客户说保证寿命，并且完全替代竞品后直接全量替换。
"""
    result = validate_output_pack(output, level=4)

    assert result["ok"] is False
    assert "Level 4/5 禁止寿命、排放、质保、替代或最终型号承诺" in result["issues"]


def test_level_5_requires_human_confirmation_prompt():
    output = LEVEL_5_OUTPUT.replace("，等待技术负责人确认", "")
    output = output.replace("，技术负责人确认候选方向", "")

    result = validate_output_pack(output, level=5)

    assert result["ok"] is False
    assert "Level 5 缺少人工确认提示" in result["issues"]


def test_level_5_flags_emission_or_warranty_commitments():
    output = LEVEL_5_OUTPUT + "\n- 客户话术补充：可以保证排放达标，并提供质保承诺。\n"
    result = validate_output_pack(output, level=5)

    assert result["ok"] is False
    assert "Level 4/5 禁止寿命、排放、质保、替代或最终型号承诺" in result["issues"]


def test_level_5_allows_candidate_material_direction_with_boundaries():
    output = GOOD_OUTPUT + """
## 四、技术支持包
- 客户需求摘要：客户希望在排放稳定前提下降低总使用成本。
- 工况档案：已整理行业、工艺段、温度、含湿、粉尘、当前滤袋。
- 真实需求判断：不是单纯低价，而是稳定前提下的总成本优化。
- 风险假设：温度波动、含湿和压差变化仍需验证。
- 候选方向：PPS / PTFE，仅作为候选材料方向。
- 试用验证计划：分仓对照，记录压差、排放、外观和运行周期。
- 试用/验证边界：不直接全量切换，先小批量验证。
- 人工确认：技术负责人确认后才能对外作为候选方案。
- 客户话术：建议先按试用边界对齐验收口径。
- 禁止承诺项：不承诺寿命、排放、完全替代或质保。
- 下一步行动清单：销售补齐决策链，技术负责人确认候选方向。
"""

    result = validate_output_pack(output, level=5)

    assert result["ok"] is True
    assert result["issues"] == []
