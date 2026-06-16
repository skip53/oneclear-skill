from __future__ import annotations

import json
import re
from collections.abc import Iterable
from functools import lru_cache
from pathlib import Path
from typing import Any


RULE_LIBRARY_PATH = Path(__file__).resolve().parents[1] / "references" / "26-work-condition-rules.json"
NUMBER_RE = re.compile(r"-?\d+(?:\.\d+)?")


@lru_cache(maxsize=1)
def load_rule_library() -> dict[str, Any]:
    with RULE_LIBRARY_PATH.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _add(target: list[str], values: Iterable[str]) -> None:
    for value in values:
        if value and value not in target:
            target.append(value)


def _set_path(target: dict[str, Any], field_path: str, value: Any) -> None:
    current = target
    segments = field_path.split(".")
    for segment in segments[:-1]:
        current = current.setdefault(segment, {})
    current[segments[-1]] = value


def _lookup_path(source: dict[str, Any], field_path: str) -> Any:
    if field_path in source:
        return source[field_path]

    current: Any = source
    for segment in field_path.split("."):
        if segment == "length":
            if isinstance(current, (str, list, tuple, set, dict)):
                return len(current)
            return None
        if not isinstance(current, dict) or segment not in current:
            return None
        current = current[segment]
    return current


def _path_exists(source: dict[str, Any], field_path: str) -> bool:
    if field_path in source:
        return source[field_path] not in (None, "")

    current: Any = source
    for segment in field_path.split("."):
        if not isinstance(current, dict) or segment not in current:
            return False
        current = current[segment]
    return current not in (None, "")


def _is_present(value: Any) -> bool:
    return value is not None and value != ""


def _collect_alias_values(record: dict[str, Any], aliases: list[str]) -> list[Any]:
    values: list[Any] = []
    for alias in aliases:
        value = _lookup_path(record, alias)
        if _is_present(value):
            values.append(value)
    return values


def _first_alias_value(record: dict[str, Any], aliases: list[str]) -> Any:
    values = _collect_alias_values(record, aliases)
    return values[0] if values else None


def _record_text(record: dict[str, Any]) -> str:
    values: list[str] = []

    def walk(value: Any) -> None:
        if isinstance(value, dict):
            for item in value.values():
                walk(item)
        elif isinstance(value, (list, tuple, set)):
            for item in value:
                walk(item)
        elif value is not None:
            values.append(str(value))

    walk(record)
    return " ".join(values)


def _as_string(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, str):
        stripped = value.strip()
        return stripped or None
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return str(value)
    return None


def _as_number(value: Any) -> float | None:
    if isinstance(value, bool) or value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        match = NUMBER_RE.search(value.replace(",", ""))
        if match:
            return float(match.group(0))
    return None


def _as_bool(value: Any) -> bool | None:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {"true", "1", "yes", "y", "on", "是", "有", "存在", "爆炸"}:
            return True
        if normalized in {"false", "0", "no", "n", "off", "否", "无", "不存在"}:
            return False
    return None


def _as_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        parts = [value]
        for separator in ["、", ",", "，", "/", ";", "；", "\n"]:
            expanded: list[str] = []
            for part in parts:
                expanded.extend(part.split(separator))
            parts = expanded
        return [part.strip() for part in parts if part.strip()]
    if isinstance(value, Iterable) and not isinstance(value, (bytes, dict)):
        return [str(item).strip() for item in value if str(item).strip()]
    return [str(value).strip()]


def _collect_list(record: dict[str, Any], aliases: list[str]) -> list[str]:
    values: list[str] = []
    for value in _collect_alias_values(record, aliases):
        _add(values, _as_list(value))
    return values


def _as_level(value: Any) -> str | None:
    text = _as_string(value)
    if not text:
        return None
    normalized = text.lower()
    if "high" in normalized or "高" in normalized or "强" in normalized:
        return "high"
    if "medium" in normalized or "mid" in normalized or "中" in normalized:
        return "medium"
    if "low" in normalized or "低" in normalized or "弱" in normalized:
        return "low"
    return None


def _as_orientation(value: Any) -> str | None:
    text = _as_string(value)
    if not text:
        return None
    normalized = text.lower()
    if "horizontal" in normalized or "水平" in normalized or "横" in normalized:
        return "horizontal"
    if "vertical" in normalized or "垂直" in normalized or "竖" in normalized:
        return "vertical"
    return None


def _as_pressure_drop_behavior(value: Any) -> str | None:
    text = _as_string(value)
    if not text:
        return None
    normalized = text.lower()
    if "骤降" in normalized or "plunge" in normalized or "sudden drop" in normalized:
        return "plunge"
    if "阶梯" in normalized or "step" in normalized:
        return "stepwise_rise"
    if "高位" in normalized or "升高" in normalized or "persistent" in normalized or "压差" in normalized:
        return "persistent_high"
    return None


def _as_hopper_status(value: Any) -> str | None:
    text = _as_string(value)
    if not text:
        return None
    normalized = text.lower()
    if "不畅" in normalized or "堵" in normalized or "restricted" in normalized or "blocked" in normalized:
        return "restricted"
    if "回落" in normalized or "fallback" in normalized:
        return "fallback_risk"
    if "正常" in normalized or "normal" in normalized:
        return "normal"
    return None


def _normalize_for_comparison(value: Any) -> Any:
    if isinstance(value, str):
        normalized = value.strip()
        bool_value = _as_bool(normalized)
        return bool_value if bool_value is not None else normalized
    return value


def _values_equal(left: Any, right: Any) -> bool:
    left_normalized = _normalize_for_comparison(left)
    right_normalized = _normalize_for_comparison(right)
    return left_normalized == right_normalized


def _contains(container: Any, needle: Any) -> bool:
    if needle is None:
        return False
    needle_text = str(needle)
    if isinstance(container, str):
        return needle_text in container
    if isinstance(container, Iterable) and not isinstance(container, (bytes, dict)):
        for item in container:
            item_text = str(item)
            if item_text == needle_text or needle_text in item_text or item_text in needle_text:
                return True
        return False
    return False


def _condition_fields_present(normalized: dict[str, Any], condition_set: list[dict[str, Any]]) -> bool:
    return all(_lookup_path(normalized, condition["field_path"].replace(".length", "")) is not None for condition in condition_set)


def evaluate_condition_set(normalized_record: dict[str, Any], condition_set: list[dict[str, Any]]) -> bool:
    if not condition_set:
        return False

    for condition in condition_set:
        field_value = _lookup_path(normalized_record, condition["field_path"])
        operator = condition["operator"]

        if operator == "eq":
            if not _values_equal(field_value, condition.get("value")):
                return False
        elif operator == "neq":
            if _values_equal(field_value, condition.get("value")):
                return False
        elif operator == "in":
            allowed = condition.get("values") or []
            if isinstance(field_value, Iterable) and not isinstance(field_value, (str, bytes, dict)):
                if not any(_values_equal(item, allowed_item) for item in field_value for allowed_item in allowed):
                    return False
            elif not any(_values_equal(field_value, allowed_item) for allowed_item in allowed):
                return False
        elif operator in {"gt", "gte", "lt", "lte"}:
            left = _as_number(field_value)
            right = _as_number(condition.get("value"))
            if left is None or right is None:
                return False
            if operator == "gt" and not left > right:
                return False
            if operator == "gte" and not left >= right:
                return False
            if operator == "lt" and not left < right:
                return False
            if operator == "lte" and not left <= right:
                return False
        elif operator == "contains":
            if not _contains(field_value, condition.get("value")):
                return False
        elif operator == "exists":
            if field_value in (None, ""):
                return False
        else:
            return False

    return True


def _corrosion_confirmed_empty(record: dict[str, Any]) -> bool:
    text = str(
        _first_alias_value(record, ["腐蚀成分状态", "烟气成分状态", "corrosive_components_status"]) or ""
    )
    return "已确认无" in text or "无腐蚀" in text


def _infer_terms(raw_text: str, terms: list[str]) -> list[str]:
    return [term for term in terms if term in raw_text]


def normalize_work_condition(record: dict[str, Any]) -> dict[str, Any]:
    library = load_rule_library()
    aliases: dict[str, list[str]] = library["field_aliases"]
    raw_text = _record_text(record)
    normalized: dict[str, Any] = {}

    industry_values = _collect_alias_values(record, aliases["industry_process"])
    industry_texts = [_as_string(value) for value in industry_values]
    industry = " ".join(dict.fromkeys(text for text in industry_texts if text))
    if industry:
        _set_path(normalized, "industry_process", industry)

    objectives = _collect_list(record, aliases["objectives"])
    _add(objectives, _infer_terms(raw_text, ["超低排放", "低能耗", "性价比", "降本"]))
    if objectives:
        _set_path(normalized, "objectives", objectives)

    pain_points = _collect_list(record, aliases["pain_points"])
    _add(
        pain_points,
        _infer_terms(
            raw_text,
            [
                "糊袋",
                "堵袋",
                "排放超标",
                "穿透",
                "局部磨损",
                "局部磨蚀",
                "磨穿",
                "硬饼",
                "板结",
                "油",
                "结晶",
                "盐析",
                "压差",
                "火星",
                "烧袋",
                "清灰频繁",
                "浓度高",
                "启停",
            ],
        ),
    )
    if pain_points:
        _set_path(normalized, "pain_points", pain_points)

    for field_path in [
        "flue_gas.temperature_normal",
        "flue_gas.temperature_instant",
        "flue_gas.humidity",
        "flue_gas.dew_point",
        "flue_gas.oxygen_content",
        "dust_collector.filter_velocity",
        "dust_collector.airflow",
        "dust_collector.design_pressure",
        "metadata.completeness_score",
    ]:
        value = _as_number(_first_alias_value(record, aliases[field_path]))
        if value is not None:
            _set_path(normalized, field_path, value)

    corrosive_values = _collect_alias_values(record, aliases["flue_gas.corrosive_components"])
    if corrosive_values:
        components: list[str] = []
        for value in corrosive_values:
            _add(components, _as_list(value))
        _set_path(normalized, "flue_gas.corrosive_components", components)
    elif _corrosion_confirmed_empty(record):
        _set_path(normalized, "flue_gas.corrosive_components", [])

    for field_path in [
        "dust.type",
        "dust.particle_size",
        "dust_collector.type",
        "dust_collector.cleaning_method",
        "dust_collector.cleaning_frequency",
        "dust_collector.support_structure_quality",
        "constraints.material_specified",
        "constraints.brand_specified",
        "constraints.delivery_deadline",
        "constraints.budget",
    ]:
        value = _as_string(_first_alias_value(record, aliases[field_path]))
        if value:
            _set_path(normalized, field_path, value)

    if _lookup_path(normalized, "dust.particle_size") is None:
        if "超细" in raw_text:
            _set_path(normalized, "dust.particle_size", "超细")
        elif "细" in raw_text:
            _set_path(normalized, "dust.particle_size", "细")
        elif "粗" in raw_text:
            _set_path(normalized, "dust.particle_size", "粗")

    for field_path in [
        "dust.abrasiveness",
        "dust.stickiness",
        "dust.hygroscopicity",
        "dust_collector.pleat_spacing_level",
        "dust_collector.air_leakage_level",
        "operation.start_stop_frequency",
        "operation.temperature_fluctuation_level",
    ]:
        value = _as_level(_first_alias_value(record, aliases[field_path]))
        if value:
            _set_path(normalized, field_path, value)

    if _lookup_path(normalized, "dust.stickiness") is None:
        if any(term in raw_text for term in ["粘性高", "很粘", "糊袋", "堵袋"]):
            _set_path(normalized, "dust.stickiness", "high")
        elif "粘" in raw_text:
            _set_path(normalized, "dust.stickiness", "medium")

    if _lookup_path(normalized, "dust.abrasiveness") is None:
        if any(term in raw_text for term in ["强磨蚀", "磨蚀性高", "磨穿"]):
            _set_path(normalized, "dust.abrasiveness", "high")
        elif any(term in raw_text for term in ["磨蚀", "冲刷"]):
            _set_path(normalized, "dust.abrasiveness", "medium")

    if _lookup_path(normalized, "dust.hygroscopicity") is None:
        if any(term in raw_text for term in ["吸湿", "盐析", "结晶", "板结"]):
            _set_path(normalized, "dust.hygroscopicity", "high")

    orientation = _as_orientation(_first_alias_value(record, aliases["dust_collector.installation_orientation"]))
    if orientation:
        _set_path(normalized, "dust_collector.installation_orientation", orientation)

    hopper_status = _as_hopper_status(_first_alias_value(record, aliases["dust_collector.hopper_discharge_status"]))
    if hopper_status:
        _set_path(normalized, "dust_collector.hopper_discharge_status", hopper_status)

    pressure_drop = _as_pressure_drop_behavior(_first_alias_value(record, aliases["symptoms.pressure_drop_behavior"]))
    if not pressure_drop and "压差" in raw_text:
        pressure_drop = "persistent_high"
    if pressure_drop:
        _set_path(normalized, "symptoms.pressure_drop_behavior", pressure_drop)

    bool_fields = [
        "dust.explosive",
        "cleaning.compressed_air.moisture_contamination",
        "cleaning.compressed_air.oil_contamination",
        "operation.cold_spot_present",
        "symptoms.emission_breakthrough",
        "symptoms.local_abrasion",
        "symptoms.bag_clogging",
        "symptoms.hardcake",
    ]
    for field_path in bool_fields:
        value = _as_bool(_first_alias_value(record, aliases[field_path]))
        if value is not None:
            _set_path(normalized, field_path, value)

    inferred_bools = {
        "cleaning.compressed_air.moisture_contamination": ["气源含水", "压缩空气含水"],
        "cleaning.compressed_air.oil_contamination": ["气源含油", "压缩空气含油"],
        "operation.cold_spot_present": ["冷点", "结露"],
        "symptoms.emission_breakthrough": ["排放超标", "穿透"],
        "symptoms.local_abrasion": ["局部磨损", "局部磨蚀", "磨穿"],
        "symptoms.bag_clogging": ["糊袋", "堵袋"],
        "symptoms.hardcake": ["硬饼", "板结"],
    }
    for field_path, terms in inferred_bools.items():
        if _lookup_path(normalized, field_path) is None:
            _set_path(normalized, field_path, any(term in raw_text for term in terms))

    if _lookup_path(normalized, "operation.start_stop_frequency") is None and "频繁启停" in raw_text:
        _set_path(normalized, "operation.start_stop_frequency", "high")
    if _lookup_path(normalized, "operation.temperature_fluctuation_level") is None and "温度波动" in raw_text:
        _set_path(normalized, "operation.temperature_fluctuation_level", "high")

    certifications = _collect_list(record, aliases["constraints.certifications_required"])
    if certifications:
        _set_path(normalized, "constraints.certifications_required", certifications)

    if _lookup_path(normalized, "constraints.budget") is None and any(term in raw_text for term in ["预算敏感", "成本敏感", "低价", "性价比"]):
        _set_path(normalized, "constraints.budget", "敏感")

    if _lookup_path(normalized, "metadata.completeness_score") is None:
        completeness_keys = [
            "dust.type",
            "flue_gas.temperature_normal",
            "flue_gas.humidity",
            "flue_gas.corrosive_components",
            "dust_collector.cleaning_method",
            "objectives",
        ]
        missing = [field_path for field_path in completeness_keys if not _path_exists(normalized, field_path)]
        score = round(((len(completeness_keys) - len(missing)) / len(completeness_keys)) * 100)
        _set_path(normalized, "metadata.completeness_score", max(0, min(100, score)))
        _set_path(normalized, "metadata.missing_fields", missing)

    return normalized


def _missing_evidence(record: dict[str, Any], normalized: dict[str, Any]) -> list[str]:
    missing: list[str] = []
    if _lookup_path(normalized, "flue_gas.corrosive_components") is None and not _corrosion_confirmed_empty(record):
        missing.append("腐蚀成分未知")
    return missing


def _ordered_rules(rules: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(
        (rule for rule in rules if rule.get("enabled", True)),
        key=lambda rule: (-rule["priority"], -rule["confidence"], rule["rule_id"]),
    )


def assess_work_condition_rules(record: dict[str, Any]) -> dict[str, Any]:
    library = load_rule_library()
    normalized = normalize_work_condition(record)

    matched_rules: list[str] = []
    matched_rule_set: set[str] = set()
    blocked_options: list[str] = []
    preferred_materials: list[str] = []
    preferred_material_reasons: dict[str, list[str]] = {}
    risk_flags: list[str] = []
    capability_directions: list[str] = []
    required_evidence: list[str] = []
    system_actions: list[str] = []

    for rule in _ordered_rules(library["rules"]):
        if any(dependency not in matched_rule_set for dependency in rule.get("depends_on", [])):
            continue
        if any(rule_id in matched_rule_set for rule_id in rule.get("mutually_exclusive_with", [])):
            continue
        if not _condition_fields_present(normalized, rule["condition_set"]):
            continue
        if not evaluate_condition_set(normalized, rule["condition_set"]):
            continue

        rule_id = rule["rule_id"]
        matched_rules.append(rule_id)
        matched_rule_set.add(rule_id)
        outputs = rule.get("presales_outputs", {})

        _add(blocked_options, outputs.get("blocked_options", []))
        _add(risk_flags, outputs.get("risk_flags", []))
        _add(capability_directions, outputs.get("capability_directions", []))
        _add(required_evidence, outputs.get("required_evidence", []))
        _add(system_actions, outputs.get("system_actions", []))

        for effect in rule.get("effects", []):
            if effect.get("type") == "block_option" and effect.get("option"):
                _add(blocked_options, [effect["option"]])
            elif effect.get("type") == "system_action" and effect.get("action"):
                _add(system_actions, [str(effect["action"])])

        rule_preferred = list(outputs.get("preferred_materials", []))
        for effect in rule.get("effects", []):
            if effect.get("type") == "preference_hit" and effect.get("option"):
                _add(rule_preferred, [effect["option"]])

        for material in rule_preferred:
            if material not in preferred_materials:
                preferred_materials.append(material)
            preferred_material_reasons.setdefault(material, [])
            if rule_id not in preferred_material_reasons[material]:
                preferred_material_reasons[material].append(rule_id)

    effective_preferred_materials = [material for material in preferred_materials if material not in blocked_options]
    effective_preferred_material_reasons = {
        material: preferred_material_reasons[material]
        for material in effective_preferred_materials
        if material in preferred_material_reasons
    }

    return {
        "rule_set_version": library["schema_version"],
        "source_version": library["source_version"],
        "strong_preference_rules_migrated": sum(
            1 for rule in library["rules"] if rule["rule_type"] == "strong_preference"
        ),
        "matched_rules": matched_rules,
        "blocked_options": blocked_options,
        "preferred_materials": effective_preferred_materials,
        "preferred_material_reasons": effective_preferred_material_reasons,
        "risk_flags": risk_flags,
        "capability_directions": capability_directions,
        "required_evidence": required_evidence,
        "missing_evidence": _missing_evidence(record, normalized),
        "system_actions": system_actions,
        "human_confirmation_required": bool(blocked_options or risk_flags or system_actions),
        "forbidden_commitments": library["default_forbidden_commitments"],
        "commitment_boundary": "规则库只用于风险阻断、证据要求和能力方向，不输出最终材料型号、寿命、排放、质保或竞品替代承诺。",
    }
