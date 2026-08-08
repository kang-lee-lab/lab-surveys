"""
Template for the functions related to NAFLD survey
"""
import json
import os
from typing import Any, Dict, Tuple
import pickle
import pandas as pd
import pygal
import plotly.graph_objects as go
from pygal.style import Style
from typing import Union


from jsonschema import validate

from App.consts import (
    METADATA_SCHEMA_PATH,
    QUESTIONS_SCHEMA_PATH,
    SURVEYS_PATH,
)

SURVEY_FOLDER = "nafld"
data_folder = "App/static/surveys_files/nafld"


def nafld_load_questions(language: str = "EN") -> Tuple[Dict, Dict]:
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


def nafld_calculate_results(
    answers: Dict, language: str = "EN"
) -> tuple[str, Any, float]:
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

    inputs = pd.DataFrame(answers, index=[0])  # Convert dictionary to Pandas data frame
    inputs_norm = normalize(inputs)

    with open("App/static/surveys_files/nafld/nafld_models_lr.bin", "rb") as f:
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


def z_score_norm(
    row: Union[pd.DataFrame, dict], col: int, mean: float, stdev: float
) -> float:
    """
    Z-score normalises the data given the row, column, mean and standard deviation.
    :param row: Row of the data (user inputs)
    :param col: Column number
    :param mean: Mean
    :param stdev: Standard deviation
    :return: z-score normalised value
    """
    z_score = (float(row[col]) - mean) / stdev
    return float(z_score)


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
        os.path.join(data_folder, "/nafld_models_{}.bin".format(model_type)), "rb"
    ) as f:
        all_models = pickle.load(f)

    model = all_models["models"][0]
    col = list(model.feature_names_in_)

    normalized = normalize(user_inputs)
    normalized = normalized[col]
    proba = model.predict_proba(normalized)
    predicted_label = model.predict(normalized)

    return proba, predicted_label


def nafld_features() -> list[str]:
    """
    Returns: a list of NAFLD features.
    """
    features = [
        "H cholesterol",
        "weight",
        "height",
        "Red blood cell count",
        "systolic",
        "Alanine aminotransferase",
        "The average hemoglobin concentration",
        "Triglycerides",
        "Eosinophil count",
        "diastolic",
        "Platelet count",
        "Lymphocyte count",
        "White blood cell count",
        "age",
        "Total bilirubin",
        "Cholinesterase",
        "Leucine aminopeptidase",
        "Alkaline phosphatase",
        "gender0female1male",
    ]

    return features


def nafld_chart(positive: float) -> go.Figure():
    """
    Returns: a plotly figure of NAFLD features.
    """
    p1 = round((positive * 100), 1)

    custom_style = Style(
        value_font_size=45,
        background="transparent",
        # foreground_strong="#FFFFFF",
        font_family="googlefont:Arial",
    )

    gauge = pygal.SolidGauge(  # half_pie = True,
        inner_radius=0.70,
        show_legend=False,
        style=custom_style,
        explicit_size=True,
        height=500,
        width=500,
    )

    percent_formatter = lambda x: "{:.10g}%".format(x)
    gauge.value_formatter = percent_formatter

    gauge.add("", [{"value": p1, "min_value": 0, "max_value": 100, "color": "#0000EE"}])

    gauge.render_to_png("App/static/nafld_chart.png")
