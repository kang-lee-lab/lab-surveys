"""
Central registry of survey JSON paths and helpers to list surveys by category.
"""
from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional

# Route id -> survey definition JSON (same paths as former get_survey_file_path).
# Order is preserved for stable API output.
SURVEY_JSON_PATHS: Dict[str, str] = {
    "asq": "surveys/static/survey_files/asq/asq.json",
    "child_bmi": "surveys/static/survey_files/child_bmi/child_bmi.json",
    "depression_moderate": "surveys/static/survey_files/dass/depression_moderate.json",
    "anxiety_moderate": "surveys/static/survey_files/dass/anxiety_moderate.json",
    "stress_moderate": "surveys/static/survey_files/dass/stress_moderate.json",
    "mmpi": "surveys/static/survey_files/mmpi/mmpi.json",
    "nafld": "surveys/static/survey_files/nafld/nafld.json",
    "manga": "surveys/static/survey_files/manga/manga.json",
    "anxiety_multiclass": "surveys/static/survey_files/dass_multiclass/anxiety_multiclass.json",
    "sample_survey": "surveys/static/survey_files/sample_survey/sample_survey.json",
}

# Matches surveys/static/schemas/metadata.json survey_type enum
CATEGORY_ORDER = ["physical", "psychological", "physiological", "other"]


def get_survey_file_path(survey_folder: str) -> str:
    try:
        return SURVEY_JSON_PATHS[survey_folder]
    except KeyError as exc:
        raise ValueError("Invalid survey type") from exc


def _load_json(rel_path: str) -> Dict[str, Any]:
    with open(rel_path, "r", encoding="utf-8") as f:
        return json.load(f)


def _description_from_survey(survey: Dict[str, Any]) -> Optional[str]:
    desc = survey.get("description")
    if isinstance(desc, dict):
        parts = [v for v in desc.values() if isinstance(v, str) and v.strip()]
        return "\n".join(parts) if parts else None
    if isinstance(desc, str):
        return desc
    return None


def _submission_hints(survey: Dict[str, Any], route_id: str) -> Dict[str, Any]:
    """How to call POST /surveys/results for this survey (survey + optional mode)."""
    sid = survey.get("survey_id") or route_id
    mode = survey.get("survey_mode")
    if sid == "dass":
        return {"survey": "dass", "mode": mode}
    if sid == "dass_multiclass":
        return {"survey": "dass_multiclass", "mode": mode}
    if route_id == "child_bmi":
        return {"survey": "child_bmi"}
    return {"survey": route_id}


def build_survey_catalog() -> Dict[str, Any]:
    by_category: Dict[str, List[Dict[str, Any]]] = {c: [] for c in CATEGORY_ORDER}

    for route_id, json_rel in SURVEY_JSON_PATHS.items():
        survey = _load_json(json_rel)
        meta_path = os.path.join(os.path.dirname(json_rel), "metadata_EN.json")
        metadata: Dict[str, Any] = {}
        if os.path.isfile(meta_path):
            metadata = _load_json(meta_path)

        survey_type = metadata.get("survey_type") or "other"
        if survey_type not in by_category:
            survey_type = "other"

        title = survey.get("title") or metadata.get("full_name") or route_id
        description = metadata.get("description") or _description_from_survey(survey)

        mode = survey.get("survey_mode")
        if isinstance(mode, str) and not mode.strip():
            mode = None

        entry: Dict[str, Any] = {
            "route_id": route_id,
            "survey_id": metadata.get("survey_id") or survey.get("survey_id") or route_id,
            "title": title,
            "short_name": metadata.get("short_name") if metadata else None,
            "full_name": metadata.get("full_name") if metadata else None,
            "description": description,
            "survey_mode": mode,
            "display": metadata.get("display", False) if metadata else False,
            "submit": _submission_hints(survey, route_id),
        }
        if metadata:
            entry["has_results"] = metadata.get("has_results", True)
            if "is_machine_learning" in metadata:
                entry["is_machine_learning"] = metadata["is_machine_learning"]
        else:
            entry["has_results"] = False
        # Drop keys with None values for a cleaner payload
        entry = {k: v for k, v in entry.items() if v is not None}
        by_category[survey_type].append(entry)

    return {
        "by_category": by_category,
        "category_order": list(CATEGORY_ORDER),
    }
