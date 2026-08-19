# Scripts

This directory contains the reproducible analysis and modelling components used in the **Bologna Rooftop Solar Potential Mapping with Machine Learning** research workflow.

The workflow converts open geospatial datasets into roof-level morphological and contextual descriptors, generates physics-based annual irradiation labels, trains and validates machine-learning models, and produces city-wide prediction and interpretation outputs.

## Workflow Overview

The computational workflow follows the main research sequence:

1. Data ingestion and harmonisation
2. Roof geometry and terrain descriptors
3. Sky openness, shading, and relief indicators
4. Neighbourhood land-cover context
5. Administrative zoning and morphology clustering
6. Stratified sampling
7. Physics-based irradiation labelling
8. Machine-learning modelling
9. Validation, calibration, and explainability
10. City-wide prediction and research outputs

The project coordinate reference system is:

**ETRS89 / UTM zone 32N — EPSG:25832**

---

## Suggested Script Organisation

```text
scripts/
├── README.md
│
├── data_preparation/
│   └── scripts and notebooks for data ingest, cleaning, harmonisation, and joins
│
├── feature_engineering/
│   └── scripts and notebooks for geometry, sky, shading, relief, and context variables
│
├── modelling/
│   └── step8_model.py
│
└── validation/
    └── scripts and notebooks for CV, LOZO, LOCO, calibration, residual analysis, and SHAP
```

Additional original scripts will be added using their actual filenames from the research archive. Filenames will not be reconstructed or invented where the original executed file is unavailable.

---

## Data Preparation

The data-preparation stage includes:

* acquisition and clipping of the Bologna study area;
* cleaning and validation of building geometries;
* generation of deterministic `roof_id` values;
* reprojection and harmonisation to EPSG:25832;
* raster alignment and masking;
* preparation of administrative boundaries;
* joins between roof polygons and derived attributes.

Major source datasets include OpenStreetMap, Copernicus DEM, ESA WorldCover, Urban Atlas, Tree Cover Density, and PVGIS.

Raw third-party datasets are documented separately in `data/README.md` and are not automatically redistributed with this repository.

---

## Feature Engineering

The feature-engineering stage derives interpretable predictors describing roof morphology, sky exposure, terrain context, and surrounding land cover.

Principal variables include:

* `area_m2`
* `slpmean`
* `asinmean`
* `acosmean`
* `asp_mean_circ`
* `svf_mean`
* `shadow_mean`
* `relief_mean`
* `rbwc50_pct`
* `rbtcd10_pct`
* Urban Atlas percentage variables
* PVGIS climate baseline variables

Aspect is represented using sine and cosine components to avoid the discontinuity between 0° and 360°.

Neighbourhood context is summarised primarily within approximately 50 m around roofs.

---

## Morphology Clustering

Normalised descriptors are used to derive morphology-based clusters for transferability analysis.

The normalised `nrm_*` variables are used for clustering only and are **not used as predictors in the final LightGBM regression model**.

The resulting morphology identifier is stored as:

`z_morph_k4`

Administrative and morphology-based zoning are retained separately so that the model can be evaluated across both policy-relevant districts and built-form typologies.

---

## Physics-Based Labelling

Annual roof-plane solar irradiation labels are generated for a stratified subset of rooftops.

The primary modelling target is:

`label_mean`

with units:

**kWh·m⁻²·yr⁻¹**

The labelled dataset contains approximately **1,525 rooftops**.

Physics-based annual irradiation calculations include shadowing and edge masking before roof-level zonal aggregation.

---

## Modelling

The main executed modelling script documented in the dissertation is:

`step8_model.py`

The principal model is a **LightGBM gradient-boosted decision-tree regressor**.

The modelling stage uses:

`train_dataset.csv`

containing approximately 1,525 labelled rooftops, and:

`inference_features.csv`

containing approximately 48,688 city-wide rooftop records for inference.

Identifiers such as:

* `roof_id`
* `z_admin`
* `z_morph_k4`

are retained for traceability and grouping but are excluded from the final predictive feature matrix.

Random seeds are fixed for reproducibility.

---

## Validation

Model evaluation includes:

* cross-validation;
* grouped validation;
* Leave-One-Zone-Out (LOZO);
* Leave-One-Cluster-Out (LOCO);
* RMSE;
* MAPE;
* R²;
* calibration slope and intercept;
* residual diagnostics;
* spatial residual inspection.

Group-aware validation is used to reduce leakage between related spatial and morphological observations.

---

## Explainability

SHAP is used to interpret model predictions and evaluate whether learned relationships remain physically plausible.

Important drivers include:

* roof orientation;
* Sky View Factor;
* shading;
* slope;
* local relief;
* neighbourhood land-cover context.

Explainability outputs are intended to support both scientific interpretation and planning-oriented communication.

---

## City-Wide Inference

The trained model is applied to approximately **48,688 rooftops** across Bologna.

City-wide outputs include:

* predicted annual roof-plane irradiation;
* quartile classifications;
* administrative-zone summaries;
* morphology-cluster summaries;
* screening shortlists;
* explainability products;
* quality and uncertainty indicators.

Predictions retain `roof_id` so that results can be joined back to GIS geometries.

---

## Reproducibility

Scripts included in this repository should, where applicable, document:

* required inputs;
* expected outputs;
* CRS;
* software dependencies;
* parameters;
* random seeds;
* relevant data versions;
* processing date or release version.

The Python environment used for the main modelling workflow is documented in the repository-level `requirements.txt`.

Where parts of the original workflow were executed interactively in GIS software rather than through a standalone script, the corresponding procedure will be documented rather than replaced by reconstructed code.

---

## Status

This directory is being populated from the original research workflow.

Only files that can be traced to the executed thesis workflow will be presented as original research scripts. Additional reconstruction or refactoring, if introduced later, will be clearly identified as such.

---

## Citation

If you use or adapt scripts from this repository, please cite the corresponding repository release.
The definitive citation information is provided in the repository-level `CITATION.cff` file. A version-specific DOI will be added through Zenodo when the first formal release is archived.
