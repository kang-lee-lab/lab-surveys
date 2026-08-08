"""
Template for the functions related to Child BMI survey
"""
import json
import os
import pickle
import pandas as pd
from typing import Any, Dict, Tuple

from jsonschema import validate

from App.consts import (
    METADATA_SCHEMA_PATH,
    QUESTIONS_SCHEMA_PATH,
    SURVEYS_PATH,
)

SURVEY_FOLDER = "childbmi"


def childbmi_load_questions(language: str = "EN") -> Tuple[Dict, Dict]:
    """
    Function to load survey questions

    Arguments:
        language (str): Language of the website
    Outputs:
        questions (Dict): Survey questions json formatted according to the schema
        metadata (Dict): Survey metadata json formatted according to the schema
    """
    with open(
        os.path.join(SURVEYS_PATH, SURVEY_FOLDER, f"questions_{language}.json"), "r"
    ) as f:
        questions = json.load(f)
    with open(os.path.join(QUESTIONS_SCHEMA_PATH), "r") as f:
        questions_schema = json.load(f)

    with open(
        os.path.join(SURVEYS_PATH, SURVEY_FOLDER, f"metadata_{language}.json"), "r"
    ) as f:
        metadata = json.load(f)
    with open(os.path.join(METADATA_SCHEMA_PATH), "r") as f:
        metadata_schema = json.load(f)

    # validate questions schema
    validate(questions, questions_schema)
    validate(metadata, metadata_schema)

    return questions, metadata


def childbmi_calculate_results(
    answers: Dict, language: str = "EN"
) -> tuple[str, Any, Any, Any, Any]:
    """
    Function to calculate results for the ChildBMI survey

    Arguments:
        answers (Dict): Survey answers
        language (str): Language of the website
    Outputs:
        results (Dict): Survey results json formatted according to the schema
        metadata (Dict): Survey metadata json formatted according to the schema
        pred_height (float): Predicted height
        pred_weight (float): Predicted weight
        pred_bmi (float): Predicted BMI
    """
    with open(
        os.path.join(SURVEYS_PATH, SURVEY_FOLDER, f"results_{language}.json"), "r"
    ) as f:
        results_schema = json.load(f)

    with open(
        os.path.join(SURVEYS_PATH, SURVEY_FOLDER, f"metadata_{language}.json"), "r"
    ) as f:
        metadata = json.load(f)
    with open(os.path.join(METADATA_SCHEMA_PATH), "r") as f:
        metadata_schema = json.load(f)

    with open("App/static/surveys_files/childbmi/childbmi_model_height.bin", "rb") as f:
        height_model = pickle.load(f)
        pred_height = height_model.predict(pd.DataFrame(answers)).tolist()[0]
    with open("App/static/surveys_files/childbmi/childbmi_model_weight.bin", "rb") as f:
        weight_model = pickle.load(f)
        pred_weight = weight_model.predict(pd.DataFrame(answers)).tolist()[0]
    with open("App/static/surveys_files/childbmi/childbmi_model_bmi.bin", "rb") as f:
        bmi_model = pickle.load(f)
        pred_bmi = bmi_model.predict(pd.DataFrame(answers)).tolist()[0]

    results = json.dumps(pred_bmi)

    # validate results schema
    validate(results, results_schema)
    validate(metadata, metadata_schema)

    return results, metadata, pred_height, pred_weight, pred_bmi
