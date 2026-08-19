# Bologna Rooftop Solar Potential Mapping with Machine Learning

Reproducible geospatial and machine-learning workflow for predicting and mapping **annual roof-plane solar irradiation** across rooftops in Bologna, Italy.

The predicted quantity is expressed in **kWh·m⁻²·yr⁻¹**.

This repository contains selected Python scripts, dependency information, and data-provenance documentation from the associated PhD research:

**Predicting Solar Potentials Using Machine Learning: A Data-Driven Approach to Map Solar Energy Potential in the Urban Fabric — The Case of Bologna**

---

## Repository Purpose

The repository provides the computational material needed to understand and reproduce the main machine-learning and evaluation stages of the research.

It is intended as a **research-code and reproducibility repository**, rather than a copy of the dissertation or associated journal article.

The workflow combines GIS-derived rooftop and urban-context features, physics-based irradiation labels, and gradient-boosted machine learning.

The labelled modelling sample contains approximately **1,525 rooftops**, and city-wide inference was performed for approximately **48,688 rooftops** after quality control.

---

## Repository Structure

```text
Bologna-rooftop-solar-ml/
│
├── data/
│   └── README.md
│
├── scripts/
│   ├── README.md
│   ├── train_and_predict_rooftop_solar.py
│   ├── join_labels.py
│   ├── make_calibration_and_shap.py
│   ├── plot_calibration_scatter.py
│   ├── make_lozo_residuals.py
│   ├── plot_lozo_residuals_santo_stefano.py
│   ├── plot_oof_residual_distribution.py
│   ├── ablation_run.py
│   ├── q4_threshold_sensitivity.py
│   ├── q4_threshold_sensitivity_1pct.py
│   ├── q4_threshold_by_zone_all.py
│   ├── make_corr_heatmap.py
│   └── make_group_feature_heatmap.py
│
├── requirements.txt
├── CITATION.cff
├── LICENSE
└── README.md
```

---

## Main Workflow

The research workflow consists of the following main stages:

1. Acquire and preprocess open geospatial datasets.
2. Prepare rooftop geometries and stable `roof_id` identifiers.
3. Derive roof, terrain, sky-view, shading, and contextual variables.
4. Generate physics-based annual irradiation labels for a stratified rooftop sample.
5. Construct the labelled training dataset.
6. Train a LightGBM regression model.
7. Apply the trained workflow to city-wide rooftop features.
8. Evaluate predictive performance and spatial transferability.
9. Assess model calibration and feature contributions.
10. Perform ablation and threshold-sensitivity analyses.

GIS preprocessing was carried out using QGIS and associated geospatial tools. The Python scripts in this repository cover the main modelling, validation, interpretation, and post-processing stages.

---

## Core Modelling Script

### `train_and_predict_rooftop_solar.py`

Main Python modelling script used to:

- load the labelled training dataset;
- select numerical predictor variables;
- define grouped and stratified train/test partitions;
- train the LightGBM regression model;
- calculate prediction metrics;
- generate feature-importance outputs;
- predict annual irradiation for city-wide rooftops;
- export city-wide predictions;
- optionally save the trained LightGBM model.

The principal target variable is:

```text
label_mean
```

representing annual roof-plane solar irradiation in:

```text
kWh·m⁻²·yr⁻¹
```

---

## Supporting Scripts

### Data preparation

`join_labels.py`

Joins physics-based irradiation labels to rooftop geometries using the deterministic `roof_id` identifier.

### Calibration and explainability

`make_calibration_and_shap.py`

Generates model-calibration outputs and SHAP-based model interpretation.

`plot_calibration_scatter.py`

Produces an out-of-fold predicted-versus-observed calibration plot and associated diagnostic metrics.

### Spatial validation

`make_lozo_residuals.py`

Generates Leave-One-Zone-Out residuals for a held-out administrative district.

`plot_lozo_residuals_santo_stefano.py`

Maps spatial residual patterns for the Santo Stefano LOZO case.

`plot_oof_residual_distribution.py`

Visualises the distribution of out-of-fold prediction residuals.

### Ablation and sensitivity analysis

`ablation_run.py`

Evaluates the contribution of geometric and contextual feature groups.

`q4_threshold_sensitivity.py`

Tests rooftop-selection sensitivity to ±2% changes around the city-wide third-quartile threshold.

`q4_threshold_sensitivity_1pct.py`

Tests sensitivity to ±1% changes around the same threshold.

`q4_threshold_by_zone_all.py`

Performs threshold-sensitivity analysis separately across administrative zones.

### Feature diagnostics

`make_corr_heatmap.py`

Generates correlation matrices and heatmaps for numerical rooftop and environmental descriptors.

`make_group_feature_heatmap.py`

Visualises standardised descriptor means across morphological groups.

---

## Required Inputs

The principal tabular inputs used by the modelling workflow are:

```text
train_dataset.csv
inference_features.csv
```

### `train_dataset.csv`

Contains the labelled rooftop sample, including:

- `roof_id`
- `label_mean`
- administrative and morphological grouping variables
- geometric descriptors
- sky-view and shading indicators
- terrain descriptors
- land-cover and urban-context variables
- climatic variables

### `inference_features.csv`

Contains the corresponding predictor variables for city-wide rooftop inference.

A deterministic `roof_id` is retained throughout the workflow so predictions and labels can be linked back to the original GIS geometries.

The principal working coordinate reference system is:

```text
EPSG:25832
```

---

## Data Availability and Provenance

Raw third-party geospatial datasets are not redistributed through this repository.

The workflow uses data from sources including:

- OpenStreetMap / Geofabrik
- Comune di Bologna Open Data
- Copernicus DEM GLO-30
- ESA WorldCover
- Copernicus Tree Cover Density
- Urban Atlas
- PVGIS / Joint Research Centre

External datasets remain subject to their original licences, terms of use, and attribution requirements.

Detailed information on data sources, processing, and provenance is provided in:

```text
data/README.md
```

The MIT License of this repository applies to the original repository code and does not relicense third-party datasets.

---

## Installation

The Python dependencies used by the repository are listed in:

```text
requirements.txt
```

Install them with:

```bash
pip install -r requirements.txt
```

The main modelling workflow was executed primarily in a Windows environment using Python 3.12.

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

---

## Running the Main Model

After preparing the required input files, the main modelling script can be executed with:

```bash
python scripts/train_and_predict_rooftop_solar.py
```

The original research scripts preserve local file paths used during execution, including paths such as:

```text
C:\GIS\work\
```

Users reproducing the workflow on another computer should update these paths to match their local directory structure.

The scripts are preserved as closely as possible to the versions used during the original research workflow.

---

## Reproducibility

The workflow incorporates several measures to support traceability and reproducibility:

- deterministic rooftop identifiers (`roof_id`);
- fixed random seeds;
- documented data provenance;
- explicit coordinate reference system;
- version-controlled Python scripts;
- documented model hyperparameters;
- grouped and spatial validation;
- calibration diagnostics;
- SHAP-based explainability;
- ablation analysis;
- threshold-sensitivity analysis.

Some preprocessing stages depend on GIS operations performed outside Python and therefore require the corresponding documented intermediate datasets.

---

## Citation

Machine-readable citation metadata is provided in:

```text
CITATION.cff
```

A formal versioned release of this repository is intended to be archived through Zenodo so that the research software can receive a persistent DOI.

When using the scientific results, interpretations, or methodology associated with this repository, please also cite the corresponding dissertation and/or associated journal publication.

---

## Related Publication

Tabatabaei, M., & Antonini, E. (2025).  
*Machine Learning for Optimizing Urban Photovoltaics: A Review of Static and Dynamic Factors.*  
**Sustainability, 17(18), 8308.**

DOI:

```text
https://doi.org/10.3390/su17188308
```

The citation for the research article directly associated with this repository will be added after publication.

---

## License

Original source code in this repository is released under the **MIT License**, unless otherwise stated.

Third-party datasets, imagery, maps, and other external materials retain their respective licences and terms of use.

---

## Author

**Mahdiyeh Tabatabaei**

ORCID:

```text
https://orcid.org/0009-0007-7219-3525
```

Google Scholar:

```text
https://scholar.google.com/citations?hl=en&user=WjHURE0AAAAJ
```
