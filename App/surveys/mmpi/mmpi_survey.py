"""
Template for the functions related to MMPI survey
"""
import json
import os
from typing import Any, Dict, Tuple
import pandas as pd
import pickle
import plotly.graph_objects as go
from jsonschema import validate

from App.consts import (
    METADATA_SCHEMA_PATH,
    QUESTIONS_SCHEMA_PATH,
    SURVEYS_PATH,
)

SURVEY_FOLDER = "mmpi"


def mmpi_load_questions(language: str = "EN") -> Tuple[Dict, Dict]:
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


def mmpi_calculate_results(
    answers: Dict, language: str = "EN"
) -> Tuple[str, Any, Dict]:
    """
    Function to calculate results for a survey

    Arguments:
        answers (Dict): Survey answers
        language (str): Language of the website
    Outputs:
        results (Dict): Survey results json formatted according to the schema
        metadata (Dict): Survey metadata json formatted according to the schema
        positive_proba (Dict): Survey results in a dictionary format
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

    status = ["DT", "HsT", "HyT", "MaT", "MfT", "PaT", "PdT", "PtT", "ScT", "SiT"]
    answers = pd.DataFrame.from_dict(answers)

    with open("App/static/surveys_files/mmpi/mmpi_models.bin", "rb") as f:
        all_models = pickle.load(f)

    positive_proba = {}

    for condition in status:
        q = all_models[condition][1]
        q = ["Gender", "Age"] + q
        model = all_models[condition][0]

        answer = answers[q]

        proba = model.predict_proba(answer)
        positive_proba[condition] = proba[0][1]

    results = json.dumps(positive_proba)

    # validate results schema
    validate(results, results_schema)
    validate(metadata, metadata_schema)

    return results, metadata, positive_proba


def mmpi_questions() -> list[int]:
    """
    Returns: list of mmpi questions.
    """
    questions = [
        2,
        3,
        6,
        7,
        8,
        9,
        12,
        18,
        21,
        22,
        23,
        24,
        27,
        32,
        33,
        35,
        37,
        38,
        42,
        51,
        57,
        63,
        64,
        67,
        68,
        71,
        76,
        82,
        84,
        91,
        93,
        94,
        97,
        102,
        103,
        106,
        107,
        110,
        117,
        119,
        120,
        122,
        123,
        124,
        127,
        128,
        134,
        141,
        145,
        152,
        155,
        157,
        163,
        164,
        167,
        168,
        170,
        175,
        177,
        178,
        179,
        181,
        187,
        192,
        201,
        202,
        220,
        224,
        229,
        230,
        231,
        234,
        238,
        245,
        267,
        268,
        272,
        278,
        279,
        281,
        289,
        292,
        296,
        298,
        301,
        315,
        316,
        318,
        321,
        324,
        339,
        342,
        346,
        350,
        358,
        360,
        370,
        383,
        471,
        527,
    ]

    return questions


def mmpi_spiderplot(mmpi_input: list[float]) -> go.Figure():
    """
    Draws spiderplot given a list of MMPI data.
    Returns: spiderplot of mmpi statuses.
    """
    fig = go.Figure(
        data=go.Scatterpolar(
            r=mmpi_input,
            theta=[
                "Hypochondriasis",
                "Depression",
                "Hysteria",
                "Psychopathic Deviate",
                "Masculinity",
                "Paranoia",
                "Psychasthenia",
                "Schizophrenia",
                "Hypomania",
                "Social Introversion",
            ],
            fill="toself",
        )
    )

    # Change background color for different ranges
    values = [10, 10, 10, 10, 10, 10, 10, 10, 10, 10]
    colors = [
        "rgba(0, 141, 25, 0.8)",
        "rgba(38, 189, 0, 0.8)",
        "rgba(75, 228, 0, 0.8)",
        "rgba(112, 255, 0, 0.8)",
        "rgba(167, 255, 0, 0.8)",
        "rgba(222, 255, 0, 0.8)",
        "rgba(255, 204, 0, 0.8)",
        "rgba(255, 153, 0, 0.8)",
        "rgba(255, 102, 0, 0.8)",
        "rgba(255, 51, 0, 0.8)",
    ]

    for t in range(0, len(colors)):
        fig.add_trace(
            go.Barpolar(
                r=[values[t]],
                width=360,
                marker_color=[colors[t]],
                opacity=0.6,
                name="Range " + str(t + 1),
                showlegend=False,
            )
        )
        t = t + 1

    # Add values as labels to each coordinate
    for i, theta in enumerate(fig.data[0].theta):
        fig.add_trace(
            go.Scatterpolar(
                r=[mmpi_input[i] + 5],
                theta=[theta],
                mode="text",
                text=str(mmpi_input[i]) + "%",
                textfont=dict(size=12, color="black"),
                showlegend=False,
            )
        )

    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100]),
        ),
        showlegend=False,
    )

    fig.write_image("App/static/mmpi_chart.png", width=1000, height=700)
