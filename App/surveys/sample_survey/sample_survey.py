"""
Template for the functions related to each survey
"""
import json
import os
from typing import Dict, Tuple

from jsonschema import validate

from App.consts import (
    METADATA_SCHEMA_PATH,
    QUESTIONS_SCHEMA_PATH,
    RESULTS_SCHEMA_PATH,
    SURVEYS_PATH,
)

SURVEY_FOLDER = "sample_survey"


def load_questions(language: str = "EN") -> Tuple[Dict, Dict]:
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

    # TODO: Add your code to load questions (e.g. all questions, random questions, question sets)

    # validate questions schema
    validate(questions, questions_schema)
    validate(metadata, metadata_schema)

    return questions, metadata


def calculate_results(answers: Dict, language: str = "EN") -> Tuple[Dict, Dict]:
    """
    Function to calculate results for a survey

    Arguments:
        answers (Dict): Survey answers
        language (str): Language of the website
    Outputs:
        results (Dict): Survey results json formatted according to the schema
        metadata (Dict): Survey metadata json formatted according to the schema
    """
    results = {}
    with open(os.path.join(RESULTS_SCHEMA_PATH), "r") as f:
        results_schema = json.load(f)

    with open(
        os.path.join(SURVEYS_PATH, SURVEY_FOLDER, f"metadata_{language}.json"), "r"
    ) as f:
        metadata = json.load(f)
    with open(os.path.join(METADATA_SCHEMA_PATH), "r") as f:
        metadata_schema = json.load(f)

    # TODO: Add your code to calculate the results (can return no results)

    # validate results schema
    validate(results, results_schema)
    validate(metadata, metadata_schema)

    return results, metadata
