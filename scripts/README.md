# Scripts

This directory contains the Python scripts included in the **Bologna Rooftop Solar Potential Mapping with Machine Learning** research repository.

The scripts cover the main modelling, validation, interpretation, sensitivity-analysis, and selected GIS-to-Python integration stages used in the research workflow.

The principal working coordinate reference system is:

```text
ETRS89 / UTM zone 32N
EPSG:25832
```

---

## Directory Contents

```text
scripts/
├── README.md
├── train_and_predict_rooftop_solar.py
├── join_labels.py
├── make_calibration_and_shap.py
├── plot_calibration_scatter.py
├── make_lozo_residuals.py
├── plot_lozo_residuals_santo_stefano.py
├── plot_oof_residual_distribution.py
├── ablation_run.py
├── q4_threshold_sensitivity.py
├── q4_threshold_sensitivity_1pct.py
├── q4_threshold_by_zone_all.py
├── make_corr_heatmap.py
└── make_group_feature_heatmap.py
```

The repository contains selected scripts that can be traced to the original research workflow.

Not every GIS preprocessing operation was implemented as a standalone Python script. Several upstream stages were carried out interactively using GIS software and are documented through the repository data-provenance material.

---

## Main Modelling Script

### `train_and_predict_rooftop_solar.py`

This is the main machine-learning script for rooftop solar-irradiation prediction.

It:

- loads `train_dataset.csv`;
- loads `inference_features.csv`;
- prepares the numerical predictor matrix;
- excludes identifiers and grouping variables from predictors;
- creates grouped and stratified train/test partitions;
- trains a LightGBM regression model;
- evaluates model performance;
- exports feature importance;
- generates city-wide rooftop predictions;
- optionally saves the trained model.

The principal target variable is:

```text
label_mean
```

with units:

```text
kWh·m⁻²·yr⁻¹
```

The script retains a fixed random seed for reproducibility.

The original research version preserves local Windows paths such as:

```text
C:\GIS\work\
```

Users reproducing the workflow should adapt these paths to their own system.

---

## Label Joining

### `join_labels.py`

This script joins physics-based irradiation labels to the sampled rooftop geometries.

Inputs include:

```text
roof_step7_1525.gpkg
train_dataset.csv
```

The join key is:

```text
roof_id
```

The target field is:

```text
label_mean
```

The resulting labelled GeoPackage is used by subsequent calibration and interpretation scripts.

---

## Calibration and Explainability

### `make_calibration_and_shap.py`

This script produces model-calibration and SHAP explainability outputs.

It can:

- generate 10-fold out-of-fold predictions;
- fit a calibration relationship between predicted and observed irradiation;
- export a calibration report;
- create a calibration plot;
- fit a LightGBM model on the full labelled dataset;
- calculate SHAP values;
- generate a SHAP beeswarm plot;
- export the top features ranked by mean absolute SHAP value.

Typical outputs include:

```text
calibration_report.csv
calibration_plot.png
shap_beeswarm.png
shap_top10.csv
```

---

### `plot_calibration_scatter.py`

This script independently generates a predicted-versus-observed calibration scatter plot from out-of-fold predictions.

It reports diagnostic quantities including:

- R²;
- RMSE;
- MAPE;
- fitted calibration slope;
- fitted calibration intercept.

This script is retained as a diagnostic and visualisation component of the original research workflow.

---

## Spatial Validation

### `make_lozo_residuals.py`

This script performs a Leave-One-Zone-Out-style evaluation for a selected administrative district.

The included version uses:

```text
Santo Stefano
```

as the held-out district.

It:

- trains the model on rooftops outside the held-out district;
- predicts the held-out rooftops;
- calculates residuals as:

```text
observed - predicted
```

- exports roof-level residuals;
- reports R² and RMSE for the held-out district.

---

### `plot_lozo_residuals_santo_stefano.py`

This script maps the spatial distribution of LOZO residuals for the Santo Stefano case.

It combines:

- roof-level residuals;
- rooftop geometries;
- Bologna administrative boundaries.

The map distinguishes spatial patterns of under-prediction and over-prediction.

---

### `plot_oof_residual_distribution.py`

This script generates a distribution plot of out-of-fold model residuals.

Residuals are calculated as:

```text
observed - predicted
```

The resulting figure supports inspection of model error distribution and potential systematic bias.

---

## Ablation Analysis

### `ablation_run.py`

This script evaluates the contribution of different feature groups using grouped cross-validation.

The analysed configurations include:

```text
Baseline-Geom
Geom+Context
Geom+Context_noUA
```

The analysis compares model performance using combinations of:

- geometric and terrain descriptors;
- WorldCover context;
- Tree Cover Density context;
- Urban Atlas variables.

Reported metrics include:

- mean R²;
- R² standard deviation;
- MAE;
- RMSE.

The script also produces a ΔR² comparison relative to the geometry-only baseline.

---

## Threshold Sensitivity

### `q4_threshold_sensitivity.py`

This script evaluates sensitivity of the city-wide rooftop screening threshold to:

```text
-2%
+2%
```

relative to the city-wide third quartile (`Q3`) of predicted annual irradiation.

It compares the overlap of selected rooftop sets under the perturbed thresholds.

---

### `q4_threshold_sensitivity_1pct.py`

This script performs the same sensitivity analysis using:

```text
-1%
+1%
```

around the city-wide `Q3` threshold.

---

### `q4_threshold_by_zone_all.py`

This script performs threshold-sensitivity analysis separately for each administrative zone.

For each `z_admin`, it calculates:

- the local third-quartile threshold;
- the base selected rooftop set;
- ±1% threshold scenarios;
- ±2% threshold scenarios;
- overlap percentages.

The script requires a table containing predicted rooftop irradiation together with administrative-zone information.

---

## Feature Diagnostics

### `make_corr_heatmap.py`

This script calculates correlations among numerical rooftop and environmental descriptors.

It includes:

- missing-value diagnostics;
- removal of zero-variance or near-empty columns;
- correlation-matrix export;
- full heatmap generation;
- lower-triangle heatmap generation.

The default correlation method is Pearson correlation.

---

### `make_group_feature_heatmap.py`

This script summarises selected descriptor means across morphological groups.

The default grouping variable is:

```text
z_morph_k4
```

Selected feature means are standardised using column-wise z-scores and visualised as a heatmap.

---

## Main Data Inputs

The two principal tabular inputs used by the modelling workflow are:

```text
train_dataset.csv
inference_features.csv
```

### `train_dataset.csv`

Contains the labelled modelling sample of:

```text
1,525 rooftops
```

including the target:

```text
label_mean
```

and the corresponding rooftop predictor variables.

### `inference_features.csv`

Contains city-wide predictor variables for:

```text
48,688 rooftops after quality control
```

The deterministic:

```text
roof_id
```

is preserved to maintain traceability between GIS geometries, model inputs, predictions, and validation outputs.

---

## Variables Used for Grouping and Traceability

Several fields are retained for grouping, joining, validation, or interpretation rather than as ordinary model predictors.

Important examples include:

```text
roof_id
z_admin
z_admin_code
z_morph_k4
```

Variables beginning with:

```text
nrm_
```

were used in morphology clustering and are excluded from the final predictive feature matrix where appropriate.

---

## Software Dependencies

Python dependencies are documented in the repository-level:

```text
requirements.txt
```

The scripts use packages including:

- NumPy
- pandas
- scikit-learn
- LightGBM
- XGBoost
- matplotlib
- joblib
- SHAP
- GeoPandas
- Fiona
- Shapely

Some geospatial preprocessing stages were performed using QGIS and associated GIS tools rather than through the Python scripts in this directory.

---

## Reproducibility Notes

The research workflow incorporates:

- deterministic `roof_id` identifiers;
- fixed random seeds;
- documented model hyperparameters;
- version-controlled scripts;
- explicit CRS information;
- grouped and spatial validation;
- calibration diagnostics;
- SHAP explainability;
- ablation analysis;
- threshold-sensitivity analysis.

The scripts are retained as closely as possible to the versions used in the original research workflow.

Some scripts preserve original local filenames, figure names, comments, and Windows paths for provenance.

A future portable or refactored version, if added, should be clearly distinguished from the original executed research scripts.

---

## Data Availability

Large GIS files, raster datasets, externally licensed source data, and model binaries are not automatically distributed through this directory.

Information on source datasets and data provenance is provided in:

```text
../data/README.md
```

Users reproducing the workflow should obtain third-party source data from the corresponding official providers and adapt local paths as required.

---

## Citation

If you use or adapt scripts from this repository, please cite the corresponding versioned repository release.

Machine-readable citation metadata is provided in:

```text
../CITATION.cff
```

A version-specific DOI will be added when a formal repository release is archived through Zenodo.
