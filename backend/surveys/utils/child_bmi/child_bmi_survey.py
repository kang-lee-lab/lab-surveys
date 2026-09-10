"""
Functions related to the Child BMI survey.

Height and weight are served by gbm-v1. BMI is DERIVED from those two
predictions rather than predicted by its own model — see point 5 below.

Six things in here are deliberate and easy to undo by accident:

1.  Sex is remapped. Callers send 1 = male, 2 = female (see child_bmi.json), but
    the models were trained on `gender_1`, which is 1 = male, 0 = female. With
    svr-v1 this mismatch was harmless because the model barely used sex — the
    measured cost was 0.01 cm. Every model since does use sex, and feeding it 2
    predicted a *taller* result for girls than for boys. Remapping here rather
    than in each client keeps one place responsible for matching the model's
    contract.

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

5.  BMI is computed from the predicted height and weight, not from a third model.
    The three targets are predicted independently, so a separately predicted BMI
    did not have to agree with the height and weight shown beside it. On a
    grouped holdout that disagreement averaged 0.48 BMI points and reached 2.57.
    Deriving it is consistent by construction.

    childbmi_model_bmi.bin is shipped but not loaded, so the two approaches can
    still be compared without recovering a file from git history.

6.  gbm-v1 predicts a *change in centile*, not centimetres, and needs three
    extra input features. Both facts are handled by the artifact itself — see
    below.

## What changed moving from svr-v2 to gbm-v1

**Nine features, not six.** The three new ones are the child's current height,
weight and BMI expressed as CDC-2000 z-scores. `_build_features` computes them
from the loaded artifact, which carries its own copy of the growth reference —
there is no data file to deploy and nothing to keep in sync.

**The artifact is a wrapper, not a bare estimator.** `GrowthPredictor.predict`
still takes a DataFrame and still returns centimetres or kilograms, so the call
site is unchanged, but unpickling it needs `growth_model` to be importable.
Pickle stores a reference to the class, not its code. The module sits next to
this file and is registered under its bare name in `sys.modules` below, because
that is the name recorded when the model was trained.

**Predictions now carry an uncertainty range.** gbm-v1 is calibrated so that an
80% interval contains the true value about 80% of the time; the svr models had
no such guarantee and were quietly overconfident. The interval widens with the
prediction horizon, from roughly ±2 cm at one year to ±7 cm at ten.

**Target ages above 20 are clamped** to 20 by the artifact, because the growth
reference stops there. For height that is close to harmless — adult height is
essentially fixed by 18-20. For weight it is a real limitation: adults keep
gaining and this model will not say so.

## Rolling back

`MODEL_SUBDIR = None` restores svr-v2 from the files beside this folder, but the
feature contract differs, so `FEATURE_ORDER` and `_build_features` must go back
with it. Prefer `git revert` of this file over editing it by hand.
"""
import json
import pickle
import sys
from pathlib import Path
from typing import Any, Dict, Tuple

import pandas as pd
from jsonschema import validate

from surveys.utils.helpers import get_survey_result_schemas, calculate_bmi

# Pickle recorded this class as `growth_model.GrowthPredictor` — the module name
# it had at training time. Registering the packaged copy under that bare name
# lets the artifact unpickle without a stray top-level module on the path.
from surveys.utils.child_bmi import growth_model as _growth_model

sys.modules.setdefault("growth_model", _growth_model)

SURVEY_FOLDER = "child_bmi"

# Reported to callers so a stored prediction can be attributed to the model that
# produced it. Bump this whenever the artifacts are replaced.
MODEL_VERSION = "gbm-v1"

# Versioned subfolder of the survey's static directory. None means "the files
# directly in that directory", which is where svr-v2 still lives.
MODEL_SUBDIR = "gbm-v1"

# Must match `features` on the pickled wrapper, in this order. The three
# z-scores are the child's *current* measurements relative to CDC 2000, not
# anything about the prediction.
FEATURE_ORDER = [
    "Sex",
    "Height",
    "Weight",
    "Current age",
    "Age to predict",
    "BMI",
    "height_z",
    "weight_z",
    "bmi_z",
]

# Resolved from this file rather than the process working directory, which the
# previous relative path depended on.
MODEL_DIR = Path(__file__).resolve().parents[2] / "static" / "survey_files" / SURVEY_FOLDER
if MODEL_SUBDIR:
    MODEL_DIR = MODEL_DIR / MODEL_SUBDIR

_MODEL_CACHE: Dict[str, Any] = {}


def _load_model(name: str):
    """Loads and caches one model. `name` is height or weight; BMI is derived."""
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

    The z-scores come from the height artifact, which embeds the full CDC 2000
    and WHO 2006 tables and can score any of the three measurements — so one
    loaded model is enough to build the whole row, whichever target is being
    predicted with it.
    """
    height = float(answers["Height"])
    weight = float(answers["Weight"])
    current_age = float(answers["Current age"])
    sex = 1.0 if float(answers["Sex"]) == 1 else 0.0
    # Recomputed rather than trusted from the request so it always agrees with
    # the height and weight actually being used.
    bmi = calculate_bmi(weight, height)

    reference = _load_model("height")

    def z(measure: str, value: float) -> float:
        return float(reference.zscore(measure, [value], [current_age], [sex])[0])

    row = {
        "Sex": sex,
        "Height": height,
        "Weight": weight,
        "Current age": current_age,
        "Age to predict": float(answers["Age to predict"]),
        "BMI": bmi,
        "height_z": z("height", height),
        "weight_z": z("weight", weight),
        "bmi_z": z("bmi", bmi),
    }
    return pd.DataFrame([row])[FEATURE_ORDER]


def _interval(model, features: pd.DataFrame) -> Dict[str, float]:
    """
    The calibrated range for one prediction, or None if this artifact has none.

    Returned as a plain dict so it survives JSON serialisation unchanged, and so
    an uncalibrated model (svr-v2, on rollback) simply yields nothing rather
    than raising.
    """
    if not getattr(model, "conformal", None):
        return None
    low, high = model.predict_interval(features)
    return {
        "low": float(low[0]),
        "high": float(high[0]),
        "confidence": float(1.0 - model.conformal["alpha"]),
    }


def child_bmi_calculate_results(
    answers: Dict, language: str = "EN"
) -> Tuple[str, Any, Any, Any, Any, Any]:
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
        intervals (Dict): Calibrated ranges for height and weight, or None for a
            model that was not calibrated
    """
    results_schema, metadata, metadata_schema = get_survey_result_schemas(
        SURVEY_FOLDER, language
    )

    features = _build_features(answers)

    height_model = _load_model("height")
    weight_model = _load_model("weight")

    pred_height = float(height_model.predict(features)[0])
    pred_weight = float(weight_model.predict(features)[0])
    # Derived so the three numbers cannot contradict one another. calculate_bmi
    # takes weight first.
    pred_bmi = float(calculate_bmi(pred_weight, pred_height))

    height_range = _interval(height_model, features)
    weight_range = _interval(weight_model, features)
    intervals = None
    if height_range or weight_range:
        intervals = {"height": height_range, "weight": weight_range}

    results = json.dumps(pred_bmi)

    # validate results schema
    validate(results, results_schema)
    validate(metadata, metadata_schema)

    return results, metadata, pred_height, pred_weight, pred_bmi, intervals
