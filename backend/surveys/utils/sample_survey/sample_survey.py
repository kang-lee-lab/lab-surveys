"""
Demo survey: sum of two numbers plus example result types.
"""
import json
from typing import Any, Dict, Tuple

from jsonschema import validate

from surveys.utils.helpers import get_survey_result_schemas

SURVEY_FOLDER = "sample_survey"


def sample_survey_calculate_results(
    answers: Dict[str, Any], language: str = "EN"
) -> Tuple[str, Any, float, float, str]:
    """
    Compute demo results from numeric inputs.

    Returns:
        results (str): JSON string of computed values
        metadata: Survey metadata document
        scalar_score (float): Sum of Number1 and Number2
        likelihood (float): experience_rating / 10 (0–1)
        summary_text (str): Human-readable summary
    """
    results_schema, metadata, metadata_schema = get_survey_result_schemas(
        SURVEY_FOLDER, language
    )

    number1 = float(answers.get("Number1", 0))
    number2 = float(answers.get("Number2", 0))
    rating = float(answers.get("experience_rating", 0))
    gender = answers.get("gender", "")

    scalar_score = number1 + number2
    likelihood = rating / 10.0
    summary_text = (
        f"Sum of {number1:g} and {number2:g} is {scalar_score:g}. "
        f"Experience rating: {rating:g}/10."
    )
    if gender:
        summary_text += f" Gender code: {gender}."

    computed = {
        "scalar_score": scalar_score,
        "likelihood": likelihood,
        "summary": summary_text,
    }
    results = json.dumps(computed)

    validate(metadata, metadata_schema)

    return results, metadata, scalar_score, likelihood, summary_text
