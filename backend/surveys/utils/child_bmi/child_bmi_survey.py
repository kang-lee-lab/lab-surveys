"""
Functions related to the Child BMI survey.

Height and weight are served by svr-v2 (see MODEL_VERSION below); BMI is still
the original svr-v1 artifact, because BMI is close to unpredictable from this
data — R2 0.359, where simply predicting the training mean already gets within
0.7 of svr-v2's error. Retraining it would be churn without a real gain.

Four things in here are deliberate and easy to undo by accident:

1.  Sex is remapped. Callers send 1 = male, 2 = female (see child_bmi.json), but
    the models were trained on `gender_1`, which is 1 = male, 0 = female. With
    svr-v1 this mismatch was harmless because the model barely used sex — the
    measured cost was 0.01 cm. svr-v2 does use sex, and feeding it 2 predicted a
    *taller* result for girls than for boys. Remapping here rather than in each
    client keeps one place responsible for matching the model's contract.

2.  Features are built as floats. `convert_values_to_list` in helpers casts every
    value with `int()`, so 110.6 cm became 110 and an age of 5.5 became 5. The
    models were trained on the raw survey floats, so truncating at inference
    disagreed with training. That helper is shared by the other surveys, so it is
    left alone and bypassed here instead.

3.  Column order is explicit. scikit-learn validates feature names *and their
    order* on predict. Previously the order came from whatever order the caller
    happened to put keys in the request JSON, which worked only by luck.

4.  Models are cached per process. They were being unpickled from disk on every
    request.
"""
import json
import pickle
from pathlib import Path
from typing import Any, Dict, Tuple

import pandas as pd
from jsonschema import validate

from surveys.utils.helpers import get_survey_result_schemas, calculate_bmi

SURVEY_FOLDER = "child_bmi"

# Reported to callers so a stored prediction can be attributed to the model that
# produced it. Bump this whenever a .bin in this folder is replaced.
MODEL_VERSION = "svr-v2-height-weight"

# Must match `feature_names_in_` on the pickled estimators, in this order.
FEATURE_ORDER = ["Sex", "Height", "Weight", "Current age", "Age to predict", "BMI"]

# Resolved from this file rather than the process working directory, which the
# previous relative path depended on.
MODEL_DIR = Path(__file__).resolve().parents[2] / "static" / "survey_files" / SURVEY_FOLDER

_MODEL_CACHE: Dict[str, Any] = {}


def _load_model(name: str):
    """Loads and caches one estimator. `name` is height, weight or bmi."""
    if name not in _MODEL_CACHE:
        with open(MODEL_DIR / f"childbmi_model_{name}.bin", "rb") as f:
            _MODEL_CACHE[name] = pickle.load(f)
    return _MODEL_CACHE[name]


def _build_features(answers: Dict) -> pd.DataFrame:
    """
    Turns survey answers into the single-row frame the models expect.

    Accepts either sex convention: 1 stays male, and anything else (2 from the
    survey, or 0 from the training data) becomes female. That keeps existing
    clients working while matching what the models were trained on.
    """
    height = float(answers["Height"])
    weight = float(answers["Weight"])

    row = {
        "Sex": 1.0 if float(answers["Sex"]) == 1 else 0.0,
        "Height": height,
        "Weight": weight,
        "Current age": float(answers["Current age"]),
        "Age to predict": float(answers["Age to predict"]),
        # Recomputed rather than trusted from the request so it always agrees
        # with the height and weight actually being used.
        "BMI": calculate_bmi(weight, height),
    }
    return pd.DataFrame([row])[FEATURE_ORDER]


def child_bmi_calculate_results(
    answers: Dict, language: str = "EN"
) -> Tuple[str, Any, Any, Any, Any]:
    """
    Calculates results for the ChildBMI survey.

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
    results_schema, metadata, metadata_schema = get_survey_result_schemas(
        SURVEY_FOLDER, language
    )

    features = _build_features(answers)

    pred_height = float(_load_model("height").predict(features)[0])
    pred_weight = float(_load_model("weight").predict(features)[0])
    pred_bmi = float(_load_model("bmi").predict(features)[0])

    results = json.dumps(pred_bmi)

    # validate results schema
    validate(results, results_schema)
    validate(metadata, metadata_schema)

    return results, metadata, pred_height, pred_weight, pred_bmi
