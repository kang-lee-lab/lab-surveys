"""
Template for the functions related to Child BMI survey
"""
import json
import pickle
import pandas as pd
from typing import Any, Dict, Tuple
from jsonschema import validate
from surveys.utils.helpers import get_survey_result_schemas, convert_values_to_list, calculate_bmi

SURVEY_FOLDER = "child_bmi"

def child_bmi_calculate_results(
    answers: Dict, language: str = "EN"
) -> Tuple[str, Any, Any, Any, Any]:
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
    results_schema, metadata, metadata_schema = get_survey_result_schemas(SURVEY_FOLDER, language)
    answers["BMI"] = calculate_bmi(answers["Weight"], answers["Height"])
    # convert dictionary so all values are in a list
    # this must be done in order to use pd.DataFrame
    converted_dictionary = convert_values_to_list(answers)

    with open("surveys/static/survey_files/child_bmi/childbmi_model_height.bin", "rb") as f:
        height_model = pickle.load(f)
        pred_height = height_model.predict(pd.DataFrame(converted_dictionary)).tolist()[0]
    with open("surveys/static/survey_files/child_bmi/childbmi_model_weight.bin", "rb") as f:
        weight_model = pickle.load(f)
        pred_weight = weight_model.predict(pd.DataFrame(converted_dictionary)).tolist()[0]
    with open("surveys/static/survey_files/child_bmi/childbmi_model_bmi.bin", "rb") as f:
        bmi_model = pickle.load(f)
        pred_bmi = bmi_model.predict(pd.DataFrame(converted_dictionary)).tolist()[0]

    results = json.dumps(pred_bmi)

    # validate results schema
    validate(results, results_schema)
    validate(metadata, metadata_schema)

    return results, metadata, pred_height, pred_weight, pred_bmi
