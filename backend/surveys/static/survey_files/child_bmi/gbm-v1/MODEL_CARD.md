# gbm-v1 — model card

```bash
python3 train.py --data pairs --features z --model gbm --target-space dz \
                 --intervals --search --target all --version gbm-v1
```

25 seconds for all three targets, against roughly 8 minutes for svr-v3.

Gradient boosting on a **change-in-centile** target, with **conformal prediction
intervals**. Trained on the pooled panel (`data/processed/growth_pairs.csv`).

## What changed and why

**The estimator is not what improved.** On identical holdout rows:

| Target | naive centile rule | svr-v3 | **gbm-v1** |
|---|---:|---:|---:|
| height | 3.255 cm | 2.787 | **2.773** |
| weight | 4.826 kg | **4.067** | 4.160 |
| BMI | 2.229 | **1.636** | 1.675 |

A wash — gbm-v1 wins on height, loses slightly on weight and BMI, and does it
while training on **16,531 rows against svr-v3's 22,359**, because a quarter of
the training split is held back to calibrate intervals. Anyone hoping the model
class was the bottleneck should read the first column instead: *assume the child
stays on the centile they are on* is a zero-parameter rule, and every model here
beats it by well under a centimetre.

What actually improved:

1. **Intervals you can believe.** Uncalibrated quantile GBM covered 74% at a
   nominal 80%, and 55% at the longest horizons. Conformal calibration lands at
   80.0% / 79.3% / 78.8% for height / weight / BMI.
2. **20× faster to fit**, which is why this one searched all 16,531 training
   rows where the SVR had to tune on a 8,000-row subsample and refit.
3. **Delta-z target.** Delta-z has SD 0.71 and sits near zero; absolute height
   carries 12 cm of variance the model otherwise rediscovers from scratch.
   Converting back through the LMS reference injects the growth curve as known
   structure rather than something to be learned.
4. **Smaller artifacts** — 0.4–0.8 MB against 1.6–1.8 MB.

## Performance

Grouped holdout, 256 of 1,276 groups held out entirely (5,473 pairs); a group is
the school, community or child, so no child spans the split. Parameters were
chosen by grouped 5-fold CV on the training split; the holdout was scored once.

| Target | MAE | RMSE | R² | 80% interval coverage | Median width |
|---|---:|---:|---:|---:|---:|
| height | 2.77 cm | 3.95 | 0.935 | 80.0% | 8.4 cm |
| weight | 4.16 kg | 6.23 | 0.820 | 79.3% | 11.8 kg |
| BMI | 1.67 | 2.45 | 0.665 | 78.8% | 4.7 |

### Behaviour

8-year-old boy, 128 cm, 26 kg:

| Target age | 10 | 12 | 14 | 16 | 18 | 20 |
|---|---:|---:|---:|---:|---:|---:|
| Predicted | 139.5 | 150.5 | 163.2 | 172.9 | 176.2 | 176.9 |
| 80% interval | 136–143 | 146–155 | 157–169 | 165–181 | 168–184 | 169–185 |

Monotonic, decelerating into adulthood, and the interval widens with horizon the
way honest uncertainty should. Sex difference at 18 is 11.9 cm (176.2 male,
164.3 female) against roughly 13 cm in reality. Sweeping current height 110→150
cm at age 8 moves the age-18 prediction 160.0→198.3 cm, monotonically.

## Limits — read before trusting an output

**Intervals under-cover at the longest horizons.** Per horizon band, height:

| Horizon | 0–2y | 2–4y | 4–6y | 6–8y | 8–10y | 10–13y | 13y+ |
|---|---:|---:|---:|---:|---:|---:|---:|
| Coverage | 77.8% | 82.3% | 81.5% | 71.7% | 85.3% | 77.1% | **69.1%** |
| Width | 4.2 | 7.0 | 9.5 | 9.8 | 14.3 | 16.8 | 14.8 cm |

Much better than the 55% an uncalibrated quantile model managed, but 69% against
a nominal 80% is still overconfident exactly where the app's default question
lives. The cause is thin, clustered data: essentially all 13y+ pairs come from
Berkeley's 136 children, which breaks the exchangeability conformal assumes.
Treat the long-horizon interval as a lower bound on the real uncertainty.

**The parameter search chose the edge of the grid.** All three targets picked
`learning_rate=0.03`, `max_leaf_nodes=15` and `min_samples_leaf=20` — the most
conservative corner available on two of three axes. The grid boundary is
probably binding and a smaller, more regularised model may do better. Cheap to
check now that a full search costs 25 seconds.

**Target ages above 20 are clamped.** The CDC reference stops at 20.0, so the
conversion holds the reference at 20 above that. For height this is close to
harmless — adult height is essentially fixed by then. For **weight and BMI it is
wrong**: adults keep gaining and this model will not say so. Constrain the
target ages the product offers to 20 or below.

**The gains over doing almost nothing are small.** 2.77 cm against 3.26 cm for a
one-line growth-chart lookup. The remaining error is dominated by predictors
absent from every open dataset — parental height (adult height heritability is
~0.8), pubertal timing, skeletal maturity. See `data/SOURCES.md`.

**Inherited from the pooled panel**, unchanged: worse on Chinese children than a
China-only model; 13–21 year horizons rest on 136 1930s Californian children; no
parental heights; a ~0.5 z step at age 2 where the BMI reference switches from
WHO 2006 to CDC 2000.

## Deploying

`engine.py` currently builds a six-column frame and is pinned to
`MODEL_VERSION = "svr-v1"`, so nothing after v1 is live. To ship gbm-v1:

1. **`scripts/growth_model.py` must be importable.** Pickle stores a reference
   to `GrowthPredictor`, not its code, so the module has to be on `sys.path` in
   the serving environment — verified: loading without it raises
   `ModuleNotFoundError: No module named 'growth_model'`. The LMS tables
   themselves are embedded in the pickle (484 + 150 rows), so no data file is
   needed.
2. **Sex encoding**, still unfixed since svr-v2: training uses `1 = male,
   0 = female`; the app sends `1 = male, 2 = female`.
3. **Nine feature columns**, including `height_z`, `weight_z`, `bmi_z` computed
   via `scripts/lms.py`. Note these features remain unproven — they measured as
   neutral in svr-v3 — but gbm-v1 was trained with them, so they are part of
   its contract.
4. **Surface the interval.** `predict_interval(X)` returns `(low, high)` at 80%.
   Shipping the point estimate alone throws away the main thing this version
   adds.

`.predict(dataframe)` returns centimetres/kilograms/BMI units exactly as before,
so the call site does not change.

## Which model should ship?

If the product shows a single number, **svr-v3 and gbm-v1 are interchangeable on
accuracy** — pick gbm-v1 for the 20× faster retrain loop and smaller artifacts.

If the product can show a range, **gbm-v1**, because it is the only version that
knows how uncertain it is.

If neither is worth a deployment, the honest option is the **naive centile rule**
at 3.26 cm — half a centimetre worse than either model, no artifact, no pickle,
no feature contract. That it is even close is the most useful result here.
