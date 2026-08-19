# Bologna Rooftop Solar Potential Mapping with Machine Learning

A reproducible open-data and machine-learning workflow for predicting and mapping rooftop solar potential in Bologna, Italy.

This repository accompanies the PhD research:

**Predicting Solar Potentials Using Machine Learning: A Data-Driven Approach to Map Solar Energy Potential in the Urban Fabric — The Case of Bologna**

**Google Scholar:** https://scholar.google.com/citations?hl=en&user=WjHURE0AAAAJ

---

## Overview

This research develops a reproducible, open-data and explainable machine-learning workflow for estimating **technical rooftop solar potential** in dense and historically sensitive urban environments.

The case study focuses on **Bologna, Italy**, where complex urban morphology, shading, roof orientation, heritage conditions, and heterogeneous building patterns make city-scale solar assessment challenging.

The workflow combines open geospatial data, physics-based solar irradiation labels, urban morphology indicators, and gradient-boosted machine-learning models to predict annual roof-plane solar irradiation at city scale.

The primary predicted quantity is expressed as:

**kWh·m⁻²·yr⁻¹**

The resulting maps are intended as a **pre-regulatory screening layer** for identifying areas and rooftops with comparatively favorable physical conditions for solar-energy deployment. They are not intended to replace structural, heritage, permitting, visibility, or detailed PV-design assessments.

---

## Research Objectives

The research addresses two main questions:

1. How do roof morphology and urban spatial characteristics influence technical rooftop solar potential in dense urban environments?
2. Can machine-learning models trained on spatial, morphological, and climatic features predict rooftop solar potential with planning-grade accuracy and transferability across different urban typologies?

The workflow is designed to be transparent, reproducible, scalable, and transferable to other European cities where detailed city-wide 3D data may not be consistently available.

---

## Methodology

The workflow combines:

* OpenStreetMap building footprints
* terrain-derived roof and skyline descriptors
* slope and circular aspect representations
* Sky View Factor (SVF)
* multi-azimuth shadow indicators
* local terrain relief
* neighborhood land-cover indicators
* tree-cover information
* Urban Atlas land-use context
* PVGIS climate baselines
* physics-based irradiation labels
* gradient-boosted decision trees
* grouped cross-validation
* Leave-One-Zone-Out (LOZO) validation
* Leave-One-Cluster-Out (LOCO) validation
* SHAP-based model explainability

A stratified subset of approximately **1,525 rooftops** was used to generate physics-based training labels.

The trained model was then applied city-wide to approximately **48,688 rooftops**.

---

## Machine-Learning Model

The primary model is based on gradient-boosted decision trees using **LightGBM**.

Linear models are used as baseline benchmarks, while the final tree-based model captures nonlinear relationships between solar irradiation and urban-form characteristics.

Important predictors include:

* roof slope
* sine/cosine encoding of roof aspect
* Sky View Factor (`svf_mean`)
* structural shading (`shadow_mean`)
* local relief (`relief_mean`)
* roof area
* WorldCover context
* Tree Cover Density
* Urban Atlas land-use shares
* climate baseline variables

SHAP values are used to interpret the contribution of individual features and assess whether model behavior remains physically plausible.

---

## Main Results

The modelling workflow achieved approximately:

* **Cross-validated R²:** 0.63 ± 0.11
* **RMSE:** ~25 kWh·m⁻²·yr⁻¹
* **MAPE:** ~0.9%
* **LOZO R²:** ~0.47
* **LOCO R²:** ~0.42

City-wide inference produced predicted annual irradiation values for approximately **48,688 rooftops**.

The city-wide 75th percentile was approximately:

**Q3 ≈ 1,782 kWh·m⁻²·yr⁻¹**

A screening threshold of:

**≥ 1,800 kWh·m⁻²·yr⁻¹**

is used for Tier-1 candidate shortlisting, with a ±1% decision band for borderline cases.

SHAP analysis indicates that roof orientation and sky openness are among the strongest drivers of predicted solar potential, while shading, slope, and terrain context further moderate the predictions.

---

## Data Sources

The workflow uses several open geospatial and climatic datasets, including:

| Dataset                           | Main use                          |
| --------------------------------- | --------------------------------- |
| OpenStreetMap                     | Building footprints               |
| Geofabrik                         | OSM regional extracts             |
| Comune di Bologna Open Data       | Administrative districts          |
| Copernicus DEM GLO-30             | Terrain, slope, aspect and relief |
| ESA WorldCover 2021               | Land-cover context                |
| Copernicus HRL Tree Cover Density | Tree-cover context                |
| Urban Atlas 2018                  | Urban land-use context            |
| PVGIS / JRC                       | Solar and climatic baselines      |
| Sentinel-2 L2A                    | Auxiliary spatial information     |

Third-party datasets retain their **original licences and attribution requirements** and are not relicensed under the repository's MIT License.

Where redistribution is inappropriate or unnecessary, this repository will provide download instructions, provenance information, and processing scripts instead of redistributing the original source data.

---

## Software Environment

The research workflow uses a combination of GIS and Python tools.

### GIS

* QGIS
* GDAL
* PROJ
* SAGA GIS
* GRASS GIS

### Python

* Python
* NumPy
* pandas
* scikit-learn
* LightGBM
* XGBoost
* matplotlib
* joblib
* SHAP

Exact dependencies and environment information will be provided in the reproducibility files of this repository.

---

## Planned Repository Structure

```text
bologna-rooftop-solar-ml/
│
├── README.md
├── LICENSE
├── CITATION.cff
├── requirements.txt
│
├── scripts/
│   ├── data_preparation/
│   ├── feature_engineering/
│   ├── modelling/
│   └── validation/
│
├── data/
│   └── README.md
│
├── outputs/
│   ├── tables/
│   └── summaries/
│
├── figures/
│
└── docs/
    ├── methodology.md
    ├── data_sources.md
    └── reproducibility.md
```

The repository is currently being prepared for the first documented research release.

---

## Reproducibility

The reproducibility workflow is designed around:

* deterministic rooftop identifiers (`roof_id`)
* documented data provenance
* fixed random seeds
* version-controlled analysis scripts
* explicit coordinate reference systems
* grouped and spatially aware validation
* documented model hyperparameters
* traceable intermediate and final outputs

The original modelling workflow uses:

* `train_dataset.csv` — labelled rooftop training sample
* `inference_features.csv` — city-wide inference features
* versioned Python modelling scripts
* stable `roof_id` identifiers for joining predictions back to GIS layers

Not all source datasets will necessarily be redistributed through GitHub. Instructions for acquiring and reconstructing the required inputs will be documented separately.

---

## Citation

A machine-readable `CITATION.cff` file and a persistent research-software citation will be added with the first formal release of this repository.

The repository is intended to be archived through **Zenodo**, allowing a DOI to be assigned to a specific research release.

When using results, methods, or scientific arguments derived from the dissertation, please cite the corresponding thesis and/or associated publication in addition to the archived software release.

---

## Related Research

**Tabatabaei, M., & Antonini, E. (2025).**
*Machine Learning for Optimizing Urban Photovoltaics: A Review of Static and Dynamic Factors.*
Sustainability, 17(18), 8308.
https://doi.org/10.3390/su17188308

---

## License

The original source code in this repository is released under the **MIT License** unless otherwise stated.

External datasets, maps, imagery, and other third-party materials remain subject to their respective licences, terms of use, and attribution requirements.

---

## Author

**Mahdiyeh Tabatabaei**

PhD Researcher in Architecture

Research interests: urban solar potential, machine learning, geospatial analysis, sustainable urban energy, and data-driven planning.

ORCID: https://orcid.org/0009-0007-7219-3525
