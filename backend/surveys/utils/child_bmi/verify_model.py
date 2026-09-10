"""
Pre-deploy check for the Child BMI model.

Run this after replacing the artifacts and before shipping. It imports the real
serving module and exercises the real code path, so it catches the failures that
actually happen with a model swap — a scikit-learn version that cannot unpickle
the artifact, a feature contract that drifted, a sex mapping that got dropped —
rather than testing a reimplementation of them.

Deliberately free of Django, so it runs in a bare container or a virtualenv that
has only the model's own dependencies, and from any working directory:

    python backend/surveys/utils/child_bmi/verify_model.py

Exits non-zero on the first failure, so it can gate a deployment.
"""
import os
import sys
from pathlib import Path

# The Django project root — the directory `surveys` lives in.
PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

# helpers.get_survey_result_schemas opens "surveys/static/..." relative to the
# process working directory, so this has to run from the project root. Changing
# into it here means the check works from anywhere rather than failing on a
# path lookup that has nothing to do with the model.
os.chdir(PROJECT_ROOT)

from surveys.utils.child_bmi.child_bmi_survey import (  # noqa: E402
    FEATURE_ORDER,
    MODEL_DIR,
    MODEL_VERSION,
    _build_features,
    child_bmi_calculate_results,
)

BASE = {"Sex": "1", "Height": "128", "Weight": "26",
        "Current age": "8", "Age to predict": "18"}

_failures = []


def check(label: str, ok: bool, detail: str = "") -> None:
    print(f"  {'PASS' if ok else 'FAIL'}  {label}{'  ' + detail if detail else ''}")
    if not ok:
        _failures.append(label)


def main() -> int:
    print(f"model {MODEL_VERSION} from {MODEL_DIR}")

    import sklearn
    print(f"scikit-learn {sklearn.__version__}\n")

    # Unpickling is the step most likely to break on a version change, and it
    # fails at import of the wrapper class rather than at predict.
    _, _, height, weight, bmi, intervals = child_bmi_calculate_results(BASE, "EN")
    check("artifacts unpickle and predict", True, f"{height:.1f} cm, {weight:.1f} kg")

    row = _build_features(BASE)
    check("feature contract matches", list(row.columns) == FEATURE_ORDER,
          f"{len(row.columns)} columns")

    check("height is plausible", 100 < height < 220, f"{height:.1f} cm")
    check("weight is plausible", 10 < weight < 150, f"{weight:.1f} kg")
    check("BMI is derived from the predicted pair",
          abs(bmi - weight / ((height / 100) ** 2)) < 1e-9)

    # The bug that shipped in svr-v1: sex was in the feature list but had almost
    # no effect, and a mis-mapped value made girls taller than boys.
    female = child_bmi_calculate_results({**BASE, "Sex": "2"}, "EN")[2]
    check("sex is used and girls are shorter", female < height - 3,
          f"male {height:.1f} vs female {female:.1f}")

    # The defect svr-v2's model card warned about: predictions that did not rise
    # with the target age, because no training row had a short horizon.
    ages = [10, 12, 14, 16, 18, 20]
    heights = [child_bmi_calculate_results({**BASE, "Age to predict": str(a)}, "EN")[2]
               for a in ages]
    check("prediction rises with target age",
          all(b > a for a, b in zip(heights, heights[1:])),
          " -> ".join(f"{h:.0f}" for h in heights))

    # Taller children must be predicted taller, all else equal.
    short = child_bmi_calculate_results({**BASE, "Height": "115", "Weight": "21"}, "EN")[2]
    tall = child_bmi_calculate_results({**BASE, "Height": "140", "Weight": "32"}, "EN")[2]
    check("responds to current height", tall > short + 5,
          f"{short:.1f} vs {tall:.1f}")

    if intervals:
        h = intervals["height"]
        check("interval brackets the point estimate",
              h["low"] < height < h["high"],
              f"[{h['low']:.1f}, {h['high']:.1f}] at {h['confidence']:.0%}")

        near = child_bmi_calculate_results({**BASE, "Age to predict": "10"}, "EN")[5]
        check("interval widens with the horizon",
              (h["high"] - h["low"]) > (near["height"]["high"] - near["height"]["low"]))
    else:
        print("  NOTE  this model reports no intervals (pre-gbm-v1)")

    print()
    if _failures:
        print(f"{len(_failures)} check(s) failed: {', '.join(_failures)}")
        return 1
    print("all checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
