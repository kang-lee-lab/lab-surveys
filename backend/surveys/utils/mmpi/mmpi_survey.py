"""
Template for the functions related to MMPI survey
"""
import json
from typing import Any, Dict, Tuple, List
import pandas as pd
import pickle
import plotly.graph_objects as go
from jsonschema import validate
from surveys.utils.helpers import get_survey_result_schemas, convert_values_to_list


SURVEY_FOLDER = "mmpi"

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
    results_schema, metadata, metadata_schema = get_survey_result_schemas(SURVEY_FOLDER, language)

    status = ["DT", "HsT", "HyT", "MaT", "MfT", "PaT", "PdT", "PtT", "ScT", "SiT"]
    answers = convert_values_to_list(answers)
    answers = pd.DataFrame.from_dict(answers)

    with open("surveys/static/survey_files/mmpi/mmpi_models.bin", "rb") as f:
        all_models = pickle.load(f)

    positive_proba = {}

    for condition in status:
        q = ["Gender", "Age"] + all_models[condition][1]
        model = all_models[condition][0]
        answer = answers[q]

        proba = model.predict_proba(answer)
        positive_proba[condition] = proba[0][1]
    results = json.dumps(positive_proba)

    # validate results schema
    validate(results, results_schema)
    validate(metadata, metadata_schema)

    return results, metadata, positive_proba


def mmpi_spiderplot(mmpi_input: List[float]) -> go.Figure():
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

    fig.write_image("surveys/static/mmpi_chart.png", width=1000, height=700)
