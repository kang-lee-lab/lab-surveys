"""
Functions related to DASS survey
"""
import json
import pickle
import pandas as pd
from typing import Dict, Any, Tuple
import plotly.graph_objects as go
from jsonschema import validate
from surveys.utils.helpers import get_survey_result_schemas, convert_values_to_list

SURVEY_FOLDER = "dass"

def dass_calculate_results(
    answers: Dict, mode: str, language: str = "EN"
) -> Tuple[str, Any, Any]:
    """
    Function to calculate results for a survey

    Arguments:
        answers (Dict): Survey answers
        language (str): Language of the website
        mode (str): Depression, anxiety or stress
    Outputs:
        results (Dict): Survey results json formatted according to the schema
        metadata (Dict): Survey metadata json formatted according to the schema
        positive (Any): decimal value of the percentage of anxiety/depression/stress likelihood
    """
    results_schema, metadata, metadata_schema = get_survey_result_schemas(SURVEY_FOLDER, language)
    converted_answers = convert_values_to_list(answers)
    user_inputs = pd.DataFrame.from_dict(converted_answers)

    if mode == 'depression':
        with open("surveys/static/survey_files/dass/depression_model_moderate.bin", "rb") as f:
                model = pickle.load(f)
    elif mode == 'anxiety':
        with open("surveys/static/survey_files/dass/anxiety_model_moderate.bin", "rb") as f:
                model = pickle.load(f)
    elif mode == 'stress':
        with open("surveys/static/survey_files/dass/stress_model_moderate.bin", "rb") as f:
                model = pickle.load(f)    
    else:
        raise Exception("This mode is not valid for the DASS survey.")
    
    proba = model[0].predict_proba(user_inputs)
    positive = proba[0][1]
    results = json.dumps(positive)

    # validate results schema
    validate(results, results_schema)
    validate(metadata, metadata_schema)

    return results, metadata, positive