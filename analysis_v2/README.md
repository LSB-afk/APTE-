# APTE submission-grade reanalysis

This pipeline replaces the previous internal exploratory design with a
four-way, independent analysis:

1. train (50%),
2. validation (15%),
3. SHAP screening (15%),
4. independent confirmation and final natural-prevalence test (20%).

The pipeline restores weekend, pavement, and sex variables that had previously
been removed using full-dataset target associations. Day/night is excluded by
an outcome-independent structural rule because the lighting variable contains a
daytime-specific category. The resulting fixed predictor set contains 17
pre-accident categorical variables.

Run from the repository root:

```powershell
$env:UV_CACHE_DIR = Join-Path (Get-Location) '.uv-cache'
uv run --no-project `
  --with pandas --with numpy --with scipy --with scikit-learn `
  --with xgboost --with shap --with statsmodels `
  --with imbalanced-learn --with matplotlib --with pyarrow `
  python analysis_v2/submission_analysis.py
```

All outputs are written to `submission_outputs_v2/`.

The casualty-count negative-binomial analysis is intentionally excluded because
the repository does not contain the incident-level casualty-count source needed
for independent reproduction.
