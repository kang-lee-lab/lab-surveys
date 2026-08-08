"""
Template for the functions related to the ASQ (Average Stress Quotient) survey.
"""
import json
from typing import Any, Dict, Tuple, List
from jsonschema import validate
from surveys.utils.helpers import get_survey_result_schemas, convert_list_values_to_floats
from surveys.utils.asq.calculate import pipeline

SURVEY_FOLDER = "asq"

def asq_calculate_results(
    answers: Dict[str, Any], language: str = "EN"
) -> Tuple[str, Any, float]:
    """
    Function to calculate results for the ASQ survey.

    Arguments:
        answers (dict): Survey answers keyed by HRV measure ID
        language (str): Language of the website
    Outputs:
        results (str): Survey results json formatted according to the schema
        metadata (Any): Survey metadata json formatted according to the schema
        asq_result (float): ASQ result
        sq_result (dict): SQ1-6 results
    """
    results_schema, metadata, metadata_schema = get_survey_result_schemas(SURVEY_FOLDER, language)
    ordered_asq_data = get_ordered_asq_data(answers)
    asq_data_floats = convert_list_values_to_floats(ordered_asq_data)
    asq_result, sq_result = pipeline(asq_data_floats)

    results = json.dumps(asq_result)
    # validate results schema
    validate(results, results_schema)
    validate(metadata, metadata_schema)

    return results, metadata, asq_result, sq_result

def get_ordered_asq_data(answers) -> List[float]:
    ordered_data = [
        answers["MHR"],
        answers["SDHR"],
        answers["max_RR_interval"],
        answers["min_RR_interval"],
        answers["mean_RR_interval"],
        answers["median_RR_interval"],
        answers["SDNN"],
        answers["NN50"],
        answers["pNN50"],
        answers["RMSSD"],
        answers["VLF"],
        answers["LF"],
        answers["HF"],
        answers["total"],
        answers["VLF_peak"],
        answers["LF_peak"],
        answers["HF_peak"],
        answers["VLF_percent"],
        answers["LF_percent"],
        answers["HF_percent"],
        answers["LF_nu"],
        answers["HF_nu"],
        answers["LF_HF"],
        answers["SD1"],
        answers["SD2"],
        answers["SD1_SD2"],
        answers["alpha"],
        answers["alpha1"],
        answers["alpha2"],
    ]
    return ordered_data
