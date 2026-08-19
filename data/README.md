# Data

This directory documents the datasets used in the **Bologna Rooftop Solar Potential Mapping with Machine Learning** research workflow.

The project combines open geospatial, environmental, and climatic datasets to construct roof-level predictors and physics-based solar irradiation labels for Bologna, Italy.

## Important Note on Data Redistribution

The source datasets used in this research are provided by external organisations and remain subject to their **original licences, attribution requirements, and terms of use**.

The MIT License of this GitHub repository applies to the original source code developed for this project. It does **not** automatically apply to third-party datasets.

For this reason, raw third-party datasets are generally **not redistributed directly through this repository**. Instead, this directory documents their provenance and provides information needed to obtain the original data from the official providers.

Where derived research data are later released, their redistribution status and applicable licence will be documented separately.

---

## Data Sources

| Dataset / Layer                   | Provider                                  | Version / Year | Role in the workflow                                           | Licence / status            |
| --------------------------------- | ----------------------------------------- | -------------- | -------------------------------------------------------------- | --------------------------- |
| OpenStreetMap building footprints | OpenStreetMap contributors                | 2025           | Building footprint geometries                                  | ODbL 1.0                    |
| Geofabrik Nord-Est extract        | Geofabrik                                 | 2025           | Regional OpenStreetMap extract                                 | ODbL 1.0                    |
| Quartieri di Bologna              | Comune di Bologna                         | 2020/2021      | Administrative district boundaries                             | Comune di Bologna open data |
| Copernicus DEM GLO-30             | Copernicus / OpenTopography               | 2019–2020      | Terrain, slope, aspect, relief and skyline-related descriptors | EU open data                |
| ESA WorldCover 2021 v200          | ESA WorldCover                            | 2021           | Land-cover context around buildings                            | ESA open data               |
| Urban Atlas 2018                  | Copernicus Land Monitoring Service / EEA  | 2018           | Urban land-use context                                         | EU open data                |
| HRL Tree Cover Density            | Copernicus Land Monitoring Service / EEA  | 2018/2021      | Tree-cover context                                             | EU open data                |
| PVGIS SARAH3 / TMY                | European Commission Joint Research Centre | 2005–2023      | Solar irradiation and climate baseline variables               | JRC open data               |
| Sentinel-2 L2A                    | ESA / Copernicus                          | 2017–2025      | Auxiliary spatial information                                  | EU open data                |

---

## Core Variables Derived from the Source Data

The workflow derives several roof-level and neighbourhood-level variables from the original datasets.

### Building geometry

* `roof_id` — deterministic identifier used for traceability
* `area_m2` — roof polygon area

### Roof and terrain morphology

* `slpmean` — mean slope
* `asinmean` — sine representation of roof aspect
* `acosmean` — cosine representation of roof aspect
* `asp_mean_circ` — circular mean aspect for interpretation

### Skyline and shading indicators

* `svf_mean` — Sky View Factor
* `shadow_mean` — structural shading indicator
* `relief_mean` — local terrain relief

### Neighbourhood context

* `rbwc50_pct` — WorldCover-derived land-cover context within approximately 50 m
* `rbtcd10_pct` — Tree Cover Density context
* `ua_code_pct` — Urban Atlas land-use class shares

### Climate variables

* `clim_ghi_y` — annual Global Horizontal Irradiance
* `clim_dni_y` — annual Direct Normal Irradiance
* `clim_dhi_y` — annual Diffuse Horizontal Irradiance
* `clim_t2m_y` — annual mean air temperature

---

## Research Data Products

The modelling workflow uses two principal tabular datasets:

### `train_dataset.csv`

Labelled training dataset containing approximately **1,525 rooftops**.

It contains roof-level predictor variables together with the physics-based target:

`label_mean`

representing annual roof-plane solar irradiation.

### `inference_features.csv`

City-wide feature dataset containing approximately **48,688 rooftops** used for model inference.

This dataset contains predictor variables but does not contain the physics-based training label.

The deterministic `roof_id` allows predictions and intermediate results to be joined back to the corresponding GIS roof geometries.

---

## Coordinate Reference System

The geospatial processing workflow is harmonised in:

**ETRS89 / UTM zone 32N — EPSG:25832**

A common projected CRS is used to ensure consistent area calculations, raster alignment, spatial joins, and neighbourhood operations.

---

## Data Processing Principles

The workflow follows several reproducibility and quality-control principles:

* source provenance is documented;
* geometries are checked and repaired where necessary;
* spatial layers are harmonised to a common CRS;
* raster and vector inputs are aligned before extraction;
* deterministic `roof_id` values are preserved across processing steps;
* range and consistency checks are applied to derived variables;
* model identifiers and administrative labels are excluded from predictive features where appropriate;
* source and derived data are kept conceptually separate.

---

## Suggested Local Directory Structure

When reproducing the workflow locally, the following structure is recommended:

```text
data/
├── raw/
│   ├── osm/
│   ├── copernicus_dem/
│   ├── worldcover/
│   ├── urban_atlas/
│   ├── tree_cover_density/
│   ├── pvgis/
│   └── sentinel2/
│
├── interim/
│
├── processed/
│   ├── train_dataset.csv
│   └── inference_features.csv
│
└── README.md
```

Large raw datasets should normally remain outside Git version control.

---

## Attribution

Users reproducing or extending this research must retain the attribution requirements of the original data providers.

In particular:

* OpenStreetMap-derived data require attribution to **OpenStreetMap contributors** and remain subject to the **ODbL 1.0**.
* Copernicus and ESA products retain their respective attribution and reuse requirements.
* Data obtained from the Comune di Bologna remain subject to the terms associated with the corresponding municipal open-data resource.
* PVGIS data should retain attribution to the **European Commission Joint Research Centre**.

Users should consult the official provider pages for the current and complete licence terms before redistributing source or derived datasets.

---

## Repository Policy

This GitHub repository is intended primarily to distribute:

* original analysis and modelling code;
* reproducibility documentation;
* data-acquisition instructions;
* metadata and provenance information;
* selected derived outputs where redistribution is appropriate.

The repository is **not intended to serve as a mirror of the original third-party data providers**.

---

## Citation

If these data-processing procedures or derived research products are used in academic work, please cite the associated repository release and the corresponding dissertation and/or publication.

A persistent DOI will be added when the repository is formally archived through Zenodo.
