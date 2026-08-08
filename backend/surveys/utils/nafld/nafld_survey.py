"""
Template for the functions related to NAFLD survey
"""
import json
import os
from typing import Any, Dict
import pickle
import pandas as pd
from typing import Union, Tuple
from surveys.utils.helpers import z_score_norm
from surveys.utils.helpers import get_survey_result_schemas, calculate_bmi, convert_values_to_floats

from jsonschema import validate

SURVEY_FOLDER = "nafld"
data_folder = "surveys/static/survey_files/nafld"

def nafld_calculate_results(
    answers: Dict, language: str = "EN"
) -> Tuple[str, Any, float]:
    """
    Function to calculate results for a survey

    Arguments:
        answers (Dict): Survey answers
        language (str): Language of the website
    Outputs:
        results (Dict): Survey results json formatted according to the schema
        metadata (Dict): Survey metadata json formatted according to the schema
        positive (float): Probability of having NAFLD
    """
    results_schema, metadata, metadata_schema = get_survey_result_schemas(SURVEY_FOLDER, language)
    answers["bmi"] = calculate_bmi(answers["weight"], answers["height"])
    converted_answers = convert_values_to_floats(answers)
    inputs = pd.DataFrame(converted_answers, index=[0])  # Convert dictionary to Pandas data frame
    inputs_norm = normalize(inputs)

    with open("surveys/static/survey_files/nafld/nafld_models_lr.bin", "rb") as f:
        all_models = pickle.load(f)

    model = all_models["models"][0]
    col = list(model.feature_names_in_)
    inputs_norm = inputs_norm[col]  # Matching features

    proba = model.predict_proba(inputs_norm)
    positive = proba[0][1]

    results = json.dumps(positive)

    # validate results schema
    validate(results, results_schema)
    validate(metadata, metadata_schema)

    return results, metadata, positive

def normalize(user_inputs: Union[pd.DataFrame, dict]) -> Union[pd.DataFrame, dict]:
    """
    Z-score normalizes the user input with mean and standard deviation of the data
    from nafld_mean_std.csv.
    :param user_inputs: pandas dataframe or dictionary containing the user's input for their
                  biomarkers in the 20 top features of NAFLD.
    :return: pandas dataframe containing the z-score normalized user input.
    """
    mean_std = pd.read_csv(os.path.join(data_folder, "nafld_mean_std.csv"))

    for col in user_inputs:
        if col != "gender0female1male":
            mean = float(mean_std["{}_mean".format(col)])
            stdev = float(mean_std["{}_stdev".format(col)])
            user_inputs["{}_norm".format(col)] = user_inputs.apply(
                lambda row: z_score_norm(row, col, mean, stdev), axis=1
            )
            user_inputs = user_inputs.drop([col], axis=1)

    return user_inputs


def run_model(model_type, user_inputs: pd.DataFrame):
    """
    Runs the specified model to generate the likelihood of NAFLD.
    It will normalize the user input using z score with mean and standard
    deviation of the data from NAFLD_filtered.csv.

    Parameters
    ----------
    model_type : Type of model ('lr', 'rf', 'svm', 'xgb', 'mlp', 'nb')
    user_inputs : pandas dataframe containing the user's input for their
                  biomarkers in the 20 top features of NAFLD.

    Returns
    -------
    Probability of being positive in NAFLD

    """
    with open(
        os.path.join(data_folder, "nafld_models_{}.bin".format(model_type)), "rb"
    ) as f:
        all_models = pickle.load(f)

    model = all_models["models"][0]
    col = list(model.feature_names_in_)

    normalized = normalize(user_inputs)
    normalized = normalized[col]
    proba = model.predict_proba(normalized)
    predicted_label = model.predict(normalized)

    return proba, predicted_label
