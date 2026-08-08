import pandas as pd
from typing import Union, Any, Tuple, List, Dict
import json
import os

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

def get_survey_result_schemas(survey_folder: str, language: str) -> Tuple[Any, Any, Any]:
    METADATA_SCHEMA_PATH = os.path.join("surveys/static/schemas", "metadata.json")
    SURVEY_PATH = os.path.join("surveys/static", "survey_files")

    with open(
        os.path.join(SURVEY_PATH, survey_folder, f"results_{language}.json"), "r"
    ) as f:
        results_schema = json.load(f)

    with open(
        os.path.join(SURVEY_PATH, survey_folder, f"metadata_{language}.json"), "r"
    ) as f:
        metadata = json.load(f)

    with open(METADATA_SCHEMA_PATH, "r") as f:
        metadata_schema = json.load(f)

    return results_schema, metadata, metadata_schema

def convert_values_to_list(d: Dict[Any, Any]) -> Dict[Any, List[Any]]:
    converted = {}
    for key in d:
        converted[key] = [int(d[key])]
    return converted

def convert_values_to_floats(d: Dict[Any, Any]) -> Dict[Any, float]:
    converted = {}
    for key in d:
        converted[key] = float(d[key])
    return converted

def convert_list_values_to_floats(l: List[Any]) -> List[float]:
    list_of_floats = []
    for item in l:
        list_of_floats.append(float(item))
    return list_of_floats

def calculate_bmi(weight: float, height: float) -> float:
    return float(weight)/ ((float(height)/100) ** 2)