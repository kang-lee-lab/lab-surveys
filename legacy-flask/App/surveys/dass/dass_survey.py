"""
Functions related to DASS survey
"""
import json
import os
import pickle
import pandas as pd
from typing import Dict, Tuple, Any
import plotly.graph_objects as go
import pygal
from pygal.style import Style
from jsonschema import validate

from App.consts import (
    METADATA_SCHEMA_PATH,
    QUESTIONS_SCHEMA_PATH,
    SURVEYS_PATH,
)

SURVEY_FOLDER = "dass"


def dass_load_questions(mode: str, language: str = "EN") -> Tuple[Dict, Dict]:
    """
    Function to load survey questions

    Arguments:
        mode (str): Anxiety, depression or stress
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

    if mode == "anxiety":
        del questions["questions"][9:]
    elif mode == "depression":
        del questions["questions"][3:9]
        del questions["questions"][9:]
    else:
        del questions["questions"][3:15]

    # validate questions schema
    validate(questions, questions_schema)
    validate(metadata, metadata_schema)

    return questions, metadata


def dass_calculate_results(
    answers: Dict, mode: str, language: str = "EN"
) -> tuple[str, Any, Any]:
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

    user_inputs = pd.DataFrame.from_dict(answers)

    if mode == "depression":
        with open(
            "App/static/surveys_files/dass/depression_model_moderate.bin", "rb"
        ) as f:
            model = pickle.load(f)
    elif mode == "anxiety":
        with open(
            "App/static/surveys_files/dass/anxiety_model_moderate.bin", "rb"
        ) as f:
            model = pickle.load(f)
    else:
        with open("App/static/surveys_files/dass/stress_model_moderate.bin", "rb") as f:
            model = pickle.load(f)

    proba = model[0].predict_proba(user_inputs)
    positive = proba[0][1]

    results = json.dumps(positive)

    # validate results schema
    validate(results, results_schema)
    validate(metadata, metadata_schema)

    return results, metadata, positive


def anxiety_chart(positive: float) -> go.Figure():
    """
    Function to create anxiety chart
    Args:
        positive: decimal value of the percentage of anxiety likelihood
    Returns: A figure to show percentage of anxiety likelihood.
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

    gauge.render_to_png("App/static/anxiety_moderate_chart.png")


def depression_chart(positive: float) -> go.Figure():
    """
    Function to create depression chart
    Args:
        positive: decimal value of the percentage of depression likelihood

    Returns: A figure to show percentage of depression likelihood.
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

    gauge.render_to_png("App/static/depression_moderate_chart.png")


def stress_chart(positive: float) -> go.Figure():
    """
    Function to create stress chart
    Args:
        positive: decimal value of the percentage of stress likelihood

    Returns: A figure to show percentage of stress likelihood.
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

    gauge.render_to_png("App/static/stress_moderate_chart.png")
