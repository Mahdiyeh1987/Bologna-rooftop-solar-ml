# Data

This directory documents the datasets and principal data products used in the **Bologna Rooftop Solar Potential Mapping with Machine Learning** research workflow.

The project combines open geospatial, environmental, climatic, and physics-based solar-irradiation data to construct roof-level predictors for Bologna, Italy.

---

## Data Redistribution

The source datasets used in this research are provided by external organisations and remain subject to their **original licences, attribution requirements, and terms of use**.

The MIT License of this GitHub repository applies to the original source code developed for this project. It does **not** apply automatically to third-party datasets.

For this reason, raw third-party datasets are generally **not redistributed through this repository**. Instead, this directory documents their provenance and the information required to obtain the original data from the corresponding providers.

Where derived research datasets are released separately, their redistribution status and applicable licence will be documented with the released files.

---

## Data Sources

| Dataset / Layer | Provider | Version / Year | Role in the workflow | Redistribution / licence note |
|---|---|---|---|---|
| OpenStreetMap building footprints | OpenStreetMap contributors | 2025 | Building footprint geometries | Subject to ODbL 1.0 |
| Geofabrik Nord-Est extract | Geofabrik / OpenStreetMap contributors | 2025 | Regional OpenStreetMap extract used for building footprints | Subject to OSM / ODbL terms |
| Quartieri di Bologna | Comune di Bologna | 2020/2021 | Administrative district boundaries | Subject to Comune di Bologna open-data terms |
| Copernicus DEM GLO-30 | Copernicus | 2019–2020 | Terrain, slope, aspect, relief, skyline and irradiation-related processing | Subject to official provider terms |
| ESA WorldCover 2021 v200 | ESA WorldCover | 2021 | Land-cover context around rooftops | Subject to official provider terms |
| Urban Atlas 2018 | Copernicus Land Monitoring Service / EEA | 2018 | Urban land-use context | Subject to official provider terms |
| HRL Tree Cover Density | Copernicus Land Monitoring Service / EEA | 2018/2021 | Tree-cover context | Subject to official provider terms |
| PVGIS SARAH3 | European Commission Joint Research Centre | 2005–2023 | Solar irradiation and climatic baseline variables | Subject to JRC / PVGIS terms |
| Sentinel-2 L2A | ESA / Copernicus | 2017–2025 | Auxiliary spatial information | Subject to official provider terms |

Users should consult the official provider documentation for the current and complete licensing and attribution requirements before redistributing source or derived datasets.

---

## Main Derived Variables

The workflow derives roof-level and neighbourhood-level variables from the source datasets.

### Building geometry

- `roof_id` — deterministic rooftop identifier retained throughout the workflow
- `area_m2` — rooftop polygon area

### Roof and terrain morphology

- `slpmean` — mean slope
- `asinmean` — sine representation of aspect
- `acosmean` — cosine representation of aspect
- `asp_mean_circ` — circular mean aspect used for interpretation

### Skyline and shading

- `svf_mean` — Sky View Factor
- `shadow_mean` — multi-azimuth structural shading indicator
- `relief_mean` — local terrain-relief descriptor

### Neighbourhood context

- `rbwc50_pct` — WorldCover-derived context within approximately 50 m
- `rbtcd10_pct` — Tree Cover Density context
- `ua_*_pct` — Urban Atlas land-use class shares

### Climatic variables

- `clim_ghi_y` — annual Global Horizontal Irradiance
- `clim_dni_y` — annual Direct Normal Irradiance
- `clim_dhi_y` — annual Diffuse Horizontal Irradiance
- `clim_t2m_y` — annual mean air temperature

The PVGIS SARAH3 climatic baseline used in the modelling workflow covers the period **2005–2023**.

---

## Physics-Based Irradiation Labels

A stratified rooftop sample was used to generate physics-based annual irradiation labels.

The final labelled sample contains:

```text
1,525 rooftops
```

Annual potential incoming solar radiation was calculated for the sampled rooftops and aggregated to roof level.

The modelling target is:

```text
label_mean
```

and represents annual roof-plane solar irradiation in:

```text
kWh·m⁻²·yr⁻¹
```

The target represents **solar irradiation**, not direct photovoltaic electricity generation.

---

## Principal Research Data Products

The modelling workflow uses two main tabular datasets.

### `train_dataset.csv`

Labelled training dataset containing exactly:

```text
1,525 rooftops
```

It contains:

- `roof_id`
- `label_mean`
- rooftop geometric variables
- slope and aspect descriptors
- sky-view and shading indicators
- local relief
- land-cover and tree-cover context
- Urban Atlas context variables
- climatic baseline variables
- administrative and morphological grouping information used for validation

The deterministic `roof_id` allows each training record to be linked back to its corresponding GIS rooftop geometry.

---

### `inference_features.csv`

City-wide feature dataset containing:

```text
48,688 rooftops after quality control
```

It contains the predictor variables required for city-wide machine-learning inference but does not contain the physics-based training target.

The same deterministic `roof_id` system is retained so predictions can be joined back to rooftop geometries.

---

## Other Intermediate and Derived Files

The original workflow also produces intermediate GIS and modelling files, including GeoPackage layers, raster products, prediction tables, model files, validation outputs, and figures.

Examples include:

```text
predictions_city.csv
feature_importance.csv
calibration_report.csv
shap_top10.csv
q4_threshold_sensitivity.csv
q4_threshold_sensitivity_1pct.csv
q4_threshold_by_zone_all.csv
```

Large intermediate GIS files, raster products, and model binaries are not necessarily distributed through this GitHub repository.

Their role in the workflow is documented through the repository scripts and provenance information.

---

## Coordinate Reference System

The main geospatial processing workflow is harmonised in:

```text
ETRS89 / UTM zone 32N
EPSG:25832
```

Using a common projected coordinate reference system supports consistent:

- area calculations;
- raster alignment;
- spatial joins;
- neighbourhood operations;
- zonal statistics;
- rooftop-level aggregation.

---

## Data Processing and Quality Control

The workflow follows reproducibility and quality-control principles including:

- documenting source provenance;
- checking and repairing geometries where necessary;
- harmonising spatial layers to a common CRS;
- aligning raster and vector datasets before extraction;
- retaining deterministic `roof_id` identifiers;
- preserving identifiers for traceability between GIS and Python outputs;
- checking missing and invalid values;
- separating clustering-only variables from final predictive features;
- excluding identifiers and grouping variables from predictive features where appropriate;
- using fixed random seeds for reproducible sampling and modelling;
- keeping source and derived datasets conceptually separate.

---

## Rooftop Sampling

The labelled training sample was selected using stratification based on administrative and morphological groupings.

The workflow uses:

```text
z_admin
```

and:

```text
z_morph_k4
```

to represent administrative and morphological group structure.

A deterministic sampling key was used so that the selected rooftop sample could be reproduced.

The resulting physics-labelled sample contains **1,525 rooftops**.

---

## Suggested Local Directory Structure

A local reproduction of the workflow may use a structure such as:

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

The original research scripts retain the local paths used during execution, including paths under:

```text
C:\GIS\work\
```

Users reproducing the workflow should adapt these paths to their own directory structure.

Large raw datasets should normally remain outside Git version control.

---

## Attribution

Users reproducing or extending this research should retain all attribution requirements associated with the original data providers.

In particular:

- OpenStreetMap-derived material requires attribution to **OpenStreetMap contributors** and remains subject to the **ODbL 1.0**.
- Geofabrik extracts remain derived from OpenStreetMap data and are subject to the corresponding OSM terms.
- Copernicus and ESA products retain their respective provider terms and attribution requirements.
- Comune di Bologna datasets remain subject to the terms associated with the corresponding municipal open-data resources.
- PVGIS data and derived climatic variables should retain attribution to the **European Commission Joint Research Centre**.

Always consult the official provider documentation before redistributing source or derived data.

---

## Repository Data Policy

This repository is primarily intended to distribute:

- original analysis and modelling code;
- reproducibility documentation;
- data provenance;
- data-acquisition information;
- metadata;
- selected derived research outputs where redistribution is appropriate.

It is **not intended to reproduce or mirror the original third-party data repositories**.

Raw source datasets should normally be obtained directly from their official providers.

---

## Citation

If the data-processing workflow or derived research products are used in academic work, please cite the corresponding repository release together with the associated dissertation and/or research publication where appropriate.

Machine-readable citation information is provided in the repository-level:

```text
CITATION.cff
```

A persistent DOI will be added when a formal versioned repository release is archived through Zenodo.
