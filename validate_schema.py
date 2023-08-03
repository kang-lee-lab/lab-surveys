""" Script to validate a survey against the schema

    Make sure all your survey files are in App/static/surveys/<survey_id>

    To run in command line: 'python3 validate_schema.py <survey_id> <language>'

    Alternatively to validate all schemas, run 'python3 validate_schema.py all'
"""

import glob
import json
import logging
import os
import sys

from jsonschema import validate

from App.consts import (
    METADATA_SCHEMA_PATH,
    QUESTIONS_SCHEMA_PATH,
    RESULTS_SCHEMA_PATH,
    SURVEYS_PATH,
)


def validate_schema(survey_id: str, language: str = "EN"):
    """
    Validate a survey (metadata, questions, responses) against the schema

    Arguments:
        survey_id (str): Survey ID
        language (str): Language of the survey (EN, FR, CH, etc.)
    """
    logging.info(" -- Survey ID: %s\n -- Language: %s\n", survey_id, language)
    survey_path = os.path.join(SURVEYS_PATH, survey_id)

    with open(os.path.join(survey_path, f"metadata_{language}.json"), "r") as f:
        metadata = json.load(f)
    with open(os.path.join(METADATA_SCHEMA_PATH), "r") as f:
        metadata_schema = json.load(f)
    logging.info(" * Validating metadata JSON")
    validate(metadata, metadata_schema)
    logging.info(" * Metadata JSON is good\n")

    with open(os.path.join(survey_path, f"questions_{language}.json"), "r") as f:
        questions = json.load(f)
    with open(os.path.join(QUESTIONS_SCHEMA_PATH), "r") as f:
        questions_schema = json.load(f)
    logging.info(" * Validating questions JSON")
    validate(questions, questions_schema)
    logging.info(" * Questions JSON is good\n")

    with open(os.path.join(survey_path, f"results_{language}.json"), "r") as f:
        results = json.load(f)
    with open(os.path.join(RESULTS_SCHEMA_PATH), "r") as f:
        results_schema = json.load(f)
    logging.info(" * Validating results JSON")
    validate(results, results_schema)
    logging.info(" * Results JSON is good\n")


def validate_all():
    all_surveys = glob.glob(os.path.join(SURVEYS_PATH, "*"), recursive=True)
    for survey in all_surveys:
        validate_schema(survey_id=os.path.split(survey)[-1], language="EN")


if __name__ == "__main__":
    survey_id = sys.argv[1]

    if survey_id == "all":
        validate_all()
    else:
        language = sys.argv[2]
        validate_schema(survey_id, language)
