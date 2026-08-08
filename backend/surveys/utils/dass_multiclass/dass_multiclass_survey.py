"""
Functions related to DASS multiclass survey
"""
import pandas as pd
from typing import Dict, Any, Tuple
import plotly.graph_objects as go
from jsonschema import validate
from surveys.utils.helpers import get_survey_result_schemas
import joblib

SURVEY_FOLDER = "dass_multiclass"

def dass_multiclass_calculate_results(
    answers: Dict, mode: str, language: str = "EN"
) -> Tuple[str, Any, Any]:
    """
    Function to calculate results for a survey

    Arguments:
        answers (Dict): Survey answers
        language (str): Language of the website
        mode (str): anxiety-multiclass
    Outputs:
        results (Dict): Survey results json formatted according to the schema
        metadata (Dict): Survey metadata json formatted according to the schema
        positive (Any): decimal value of the percentage of anxiety/depression/stress likelihood
    """
    results_schema, metadata, metadata_schema = get_survey_result_schemas(SURVEY_FOLDER, language)

    if mode == 'anxiety-multiclass':
        model_path = "surveys/static/survey_files/dass_multiclass/model.h5"  # Use the appropriate file path
        with open(model_path, "rb") as f:
            loaded_model = joblib.load(f)
    else:
        raise Exception("This mode is not valid for the DASS multiclass survey.")
    
    # Define the columns
    cols = [
        'Q4A_0', 'Q4A_1', 'Q4A_2', 'Q4A_3',
        'Q7A_0', 'Q7A_1', 'Q7A_2', 'Q7A_3',
        'Q9A_0', 'Q9A_1', 'Q9A_2', 'Q9A_3',
        'Q20A_0', 'Q20A_1', 'Q20A_2', 'Q20A_3',
        'Q25A_0', 'Q25A_1', 'Q25A_2', 'Q25A_3',
        'Q28A_0', 'Q28A_1', 'Q28A_2', 'Q28A_3',
        'Q36A_0', 'Q36A_1', 'Q36A_2', 'Q36A_3',
        'Q40A_0', 'Q40A_1', 'Q40A_2', 'Q40A_3',
        'Q41A_0', 'Q41A_1', 'Q41A_2', 'Q41A_3'
    ]

    # Initialize an empty dictionary with all columns set to 0
    features_df = {col: 0 for col in cols}
    # Populate the dictionary based on the answers
    for question, answer in answers.items():
        base_col = f'{question}A_'
        features_df[base_col + answer] = 1

    # Convert the dictionary to a DataFrame
    selected_features = pd.DataFrame([features_df])


    # Duplicate the single-row input to make it appear as multiple rows
    duplicated_features = pd.concat([selected_features]*5, axis=0)

    # Convert test features to the appropriate format if needed
    test_features_np = duplicated_features.copy()

    # Compatibility patch for legacy trained model expecting Q30A_* instead of Q20A_*
    rename_map = {
        "Q20A_0": "Q30A_0",
        "Q20A_1": "Q30A_1",
        "Q20A_2": "Q30A_2",
        "Q20A_3": "Q30A_3",
    }
    test_features_np = test_features_np.rename(columns=rename_map)

    # Reorder columns to match model training
    try:
        test_features_np = test_features_np[loaded_model.feature_names_in_]
    except Exception as e:
        print(f"Column order alignment skipped: {e}")

    # Now make predictions
    predictions = loaded_model.predict(test_features_np)

    # Extract the prediction for the original single row
    single_row_prediction = predictions[0]

    # If you need probabilities, use predict_proba method (if supported by your model)
    probabilities = loaded_model.predict_proba(test_features_np)

    single_row_probabilities = probabilities[0]
    
    results = single_row_probabilities.tolist()

    # validate results schema
    validate(results, results_schema)
    validate(metadata, metadata_schema)
    
    # severity_level: in the results, the index of the highest value is the severity level
    severity_level = results.index(max(results))
    
    # classification, where severity level 0 is normal, 1 is mild, 2 is moderate, 3 is severe, and 4 is extremely severe
    classification = ['normal', 'mild', 'moderate', 'severe', 'extremely severe']
    rank = classification[severity_level]

    return results, metadata, severity_level, rank




# sample
# answers = {'Q4': '2', 'Q7': '1', 'Q9': '0', 'Q20': '2', 'Q25': '1', 'Q28': '1', 'Q30': '2', 'Q40': '1', 'Q41': '2'}
# dass_multiclass_calculate_results(answers, 'anxiety-multiclass')