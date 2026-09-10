"""
Serving wrapper for the growth models.

Why a wrapper rather than a bare estimator. The gbm-v1 models predict a child's
*change in centile* (Delta-z), not their height in centimetres, because that
target is far better conditioned — Delta-z has SD 0.71 and sits near zero,
where absolute height carries 12 cm of variance the model would have to
rediscover from scratch. Turning the prediction back into centimetres needs the
LMS growth reference, so something has to hold both the estimator and the
reference and expose one `predict`.

That something is this class, and it keeps the serving contract identical to
svr-v1/v2/v3: `pickle.load(...)` then `.predict(dataframe)` returning
centimetres, kilograms or BMI units. `engine.py` needs no arithmetic of its own.

The LMS tables are embedded in the pickle rather than read from disk, so a
deployed artifact carries its own reference and cannot silently drift if the
`data/external/` copy changes or is missing.

They are stored as plain numpy arrays, deliberately, not as the pandas frames
they are built from. pandas does not promise pickle compatibility across major
versions and 2.x -> 1.x commonly breaks, while the serving containers pin
pandas 1.4.3 against training's 2.3.3. Float arrays and nested dicts survive
that gap; a pickled BlockManager does not.

⚠️  Unpickling requires this module to be importable — pickle stores a reference
to the class, not its code. Ship `scripts/growth_model.py` alongside the model
files and make sure it is on `sys.path` in the serving environment. Everything
else it needs (numpy, pandas, scikit-learn) is already a serving dependency.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

# Mirrors lms._MEASURES. Duplicated deliberately: this module must stand alone
# in the serving environment without dragging in the training-side code.
_SUFFIX = {"height": "ht", "weight": "wt", "bmi": "bmi"}


def _as_arrays(table):
    """
    Flattens an LMS reference frame into {(measure, sex): (years, L, M, S)}.

    Done once at construction so the pickle holds only float arrays. Rows where
    a measure is undefined (CDC has no BMI under 2) are dropped per measure
    rather than per table, so each measure keeps its own age range.
    """
    if table is None:
        return None
    if isinstance(table, dict):
        return table                    # already flattened

    out = {}
    for measure, suffix in _SUFFIX.items():
        cols = [f"L.{suffix}", f"M.{suffix}", f"S.{suffix}"]
        if not all(c in table.columns for c in cols):
            continue
        for sex_code in (1.0, 2.0):
            sub = table[(table["sex"] == sex_code) & table[f"M.{suffix}"].notna()]
            sub = sub.sort_values("years")
            if sub.empty:
                continue
            out[(measure, sex_code)] = (
                np.ascontiguousarray(sub["years"].to_numpy(float)),
                np.ascontiguousarray(sub[cols[0]].to_numpy(float)),
                np.ascontiguousarray(sub[cols[1]].to_numpy(float)),
                np.ascontiguousarray(sub[cols[2]].to_numpy(float)),
            )
    return out


class GrowthPredictor:
    """An estimator plus the growth reference needed to interpret its output."""

    def __init__(self, estimator, measure: str, target_space: str,
                 features: list, lms_primary, lms_fallback=None,
                 conformal: dict | None = None):
        self.estimator = estimator
        self.measure = measure                 # height | weight | bmi
        self.target_space = target_space       # cm | dz
        self.features = list(features)
        self.lms_primary = _as_arrays(lms_primary)      # CDC 2000
        self.lms_fallback = _as_arrays(lms_fallback)    # WHO 2006, BMI under 2
        self.conformal = conformal or {}

    # -- reference arithmetic ------------------------------------------------

    def _lms(self, table, age: np.ndarray, sex: np.ndarray, measure: str):
        """Interpolates L, M and S at each (age, sex). NaN where undefined."""
        L = np.full(age.shape, np.nan)
        M = np.full(age.shape, np.nan)
        S = np.full(age.shape, np.nan)
        if table is None:
            return L, M, S

        for model_code, ref_code in ((1.0, 1.0), (0.0, 2.0)):
            ref = table.get((measure, ref_code))
            if ref is None:
                continue
            years, l_, m_, s_ = ref
            m = (sex == model_code) & np.isfinite(age) \
                & (age >= years[0]) & (age <= years[-1])
            if not m.any():
                continue
            L[m] = np.interp(age[m], years, l_)
            M[m] = np.interp(age[m], years, m_)
            S[m] = np.interp(age[m], years, s_)
        return L, M, S

    def _reference_age(self, age: np.ndarray) -> np.ndarray:
        """
        Clamps the lookup age to the reference's upper bound (20.0 years).

        For height this is close to harmless — adult height is essentially fixed
        after 18-20, so holding the reference at 20 is the right shape. For
        weight and BMI it is a real limitation: adults keep gaining, and this
        model will not say so. Constrain the target ages the product offers to
        20 or below, or treat anything above it as "adult" rather than as a
        specific age.
        """
        tops = [v[0][-1] for (meas, _), v in self.lms_primary.items()
                if meas == self.measure]
        return np.minimum(age, max(tops)) if tops else age

    def _lms_filled(self, age: np.ndarray, sex: np.ndarray, measure: str):
        """L, M, S from the primary reference, with the fallback filling gaps."""
        L, M, S = self._lms(self.lms_primary, age, sex, measure)
        if self.lms_fallback is not None:
            gap = np.isnan(M)
            if gap.any():
                L2, M2, S2 = self._lms(self.lms_fallback, age, sex, measure)
                L = np.where(gap, L2, L)
                M = np.where(gap, M2, M)
                S = np.where(gap, S2, S)
        return L, M, S

    def _to_measure(self, z: np.ndarray, age: np.ndarray, sex: np.ndarray) -> np.ndarray:
        """z -> centimetres/kilograms/BMI, via X = M (1 + L S z)^(1/L)."""
        age = self._reference_age(age)
        L, M, S = self._lms_filled(age, sex, self.measure)
        near0 = np.abs(L) < 1e-7
        base = 1.0 + L * S * z
        safe = np.where(near0 | (base > 0), np.where(near0, 1.0, base), np.nan)
        return np.where(near0, M * np.exp(S * z),
                        M * np.power(safe, 1.0 / np.where(near0, 1.0, L)))

    def zscore(self, measure: str, value, age_years, sex_model) -> np.ndarray:
        """
        Forward transform: a measurement's centile for that age and sex.

        Exposed because the models take z-scores as *inputs*, so a caller has to
        be able to produce them. The embedded tables cover height, weight and
        BMI, so any of the three can be asked for regardless of which target
        this particular artifact predicts — one loaded model is enough to build
        the whole feature row.
        """
        value = pd.to_numeric(pd.Series(value), errors="coerce").to_numpy(float)
        age = pd.to_numeric(pd.Series(age_years), errors="coerce").to_numpy(float)
        sex = pd.to_numeric(pd.Series(sex_model), errors="coerce").to_numpy(float)

        # `measure` is passed down rather than stashed on self: these objects are
        # cached per process and Django serves requests concurrently, so mutating
        # instance state here would race between threads.
        L, M, S = self._lms_filled(age, sex, measure)
        near0 = np.abs(L) < 1e-7
        ratio = np.where(np.isfinite(M) & (M > 0) & (value > 0), value / M, np.nan)
        with np.errstate(invalid="ignore"):
            return np.where(near0, np.log(ratio) / S,
                            (np.power(ratio, np.where(near0, 1.0, L)) - 1.0) / (L * S))

    # -- prediction ----------------------------------------------------------

    def _frame(self, X) -> pd.DataFrame:
        if not isinstance(X, pd.DataFrame):
            X = pd.DataFrame(X, columns=self.features)
        missing = [c for c in self.features if c not in X.columns]
        if missing:
            raise ValueError(f"missing feature columns: {missing}")
        return X

    def predict(self, X) -> np.ndarray:
        """Predicted measurement at the target age, in real units."""
        X = self._frame(X)
        raw = self.estimator.predict(X[self.features])
        if self.target_space == "cm":
            return raw

        z0 = pd.to_numeric(X[f"{self.measure}_z"], errors="coerce").to_numpy(float)
        age = pd.to_numeric(X["Age to predict"], errors="coerce").to_numpy(float)
        sex = pd.to_numeric(X["Sex"], errors="coerce").to_numpy(float)
        return self._to_measure(z0 + raw, age, sex)

    def predict_interval(self, X):
        """
        Returns (low, high) for the nominal level the model was calibrated at.

        Conformal, and conditioned on the prediction horizon rather than global:
        error at a 1-year horizon and at a 15-year horizon differ by a factor of
        four, so one width would be far too wide for the first and far too
        narrow for the second — which is exactly how the uncalibrated quantile
        model failed, covering 55% at long horizons against a nominal 80%.

        Widths are applied in z-space and converted, so the interval is
        asymmetric in centimetres the way the growth reference is.
        """
        if not self.conformal:
            raise ValueError("this model was not calibrated for intervals")

        X = self._frame(X)
        raw = self.estimator.predict(X[self.features])
        horizon = (pd.to_numeric(X["Age to predict"], errors="coerce")
                   - pd.to_numeric(X["Current age"], errors="coerce")).to_numpy(float)

        edges = np.asarray(self.conformal["bin_edges"], float)
        widths = np.asarray(self.conformal["widths"], float)
        idx = np.clip(np.searchsorted(edges, horizon, side="right") - 1,
                      0, len(widths) - 1)
        w = widths[idx]

        if self.target_space == "cm":
            return raw - w, raw + w

        z0 = pd.to_numeric(X[f"{self.measure}_z"], errors="coerce").to_numpy(float)
        age = pd.to_numeric(X["Age to predict"], errors="coerce").to_numpy(float)
        sex = pd.to_numeric(X["Sex"], errors="coerce").to_numpy(float)
        return (self._to_measure(z0 + raw - w, age, sex),
                self._to_measure(z0 + raw + w, age, sex))
