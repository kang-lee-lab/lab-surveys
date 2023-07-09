""" Script to validate a survey against the schema 

    Make sure all your survey files are in App/static/surveys/<survey_id>

    To run in command line: "python validate_schema.py <survey_id> <language>"
"""

import json
import os
import sys
from jsonschema import validate
from App.consts import SCHEMAS_PATH, SURVEYS_PATH


def validate_schema(survey_id: str, language: str = 'EN'):
    """
    Validate a survey (metadata, questions, responses) against the schema

    Arguments:
        survey_id (str): Survey ID
        language (str): Language of the survey (EN, FR, CH, etc.)
    """
    print(f' * Survey ID: {survey_id}\n * Language: {language}\n')
    survey_path = os.path.join(SURVEYS_PATH, survey_id)
    
    with open(os.path.join(survey_path, f'metadata_{language}.json'), 'r') as f:
        metadata = json.load(f)
    with open(os.path.join(SCHEMAS_PATH, 'metadata.json'), 'r') as f:
        metadata_schema = json.load(f)
    print(' * Validating metadata JSON')
    validate(metadata, metadata_schema)
    print(' * Metadata JSON is good\n')

    with open(os.path.join(survey_path, f'questions_{language}.json'), 'r') as f:
        questions = json.load(f)
    with open(os.path.join(SCHEMAS_PATH, 'questions.json'), 'r') as f:
        questions_schema = json.load(f)
    print(' * Validating questions JSON')
    validate(questions, questions_schema)
    print(' * Questions JSON is good\n')

    with open(os.path.join(survey_path, f'results_{language}.json'), 'r') as f:
        results = json.load(f)
    with open(os.path.join(SCHEMAS_PATH, 'results.json'), 'r') as f:
        results_schema = json.load(f)
    print(' * Validating results JSON')
    validate(results, results_schema)
    print(' * Results JSON is good\n')


if __name__ == '__main__':
    survey_id = sys.argv[1]
    language = sys.argv[2]
    validate_schema(survey_id, language)
