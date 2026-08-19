# join_labels.py
import geopandas as gpd
import pandas as pd

# مسیرها
GPKG_IN   = r"C:\GIS\work\roof_step7_1525.gpkg"
LAYER_IN  = "roof_step7_1525"
CSV_LABEL = r"C:\GIS\work\train_dataset.csv"   # اگر نام/مسیر فرق دارد، عوض کن

# ستون‌های کلیدی
KEY       = "roof_id"
TARGET    = "label_mean"

print("Reading GPKG layer...")
gdf = gpd.read_file(GPKG_IN, layer=LAYER_IN)

print("Reading labels CSV...")
dfc = pd.read_csv(CSV_LABEL)

# چک وجود ستون‌ها
assert KEY in gdf.columns, f"{KEY} not in GPKG layer"
assert KEY in dfc.columns, f"{KEY} not in CSV"
assert TARGET in dfc.columns, f"{TARGET} not in CSV"

print("Merging by roof_id ...")
merged = gdf.merge(dfc[[KEY, TARGET]], on=KEY, how="left")

missing = merged[TARGET].isna().sum()
print(f"Missing labels: {missing} / {len(merged)}")

OUT_GPKG  = r"C:\GIS\work\roof_step7_1525_with_labels.gpkg"
OUT_LAYER = "roof_step7_1525_labeled"
print("Saving:", OUT_GPKG, "| layer =", OUT_LAYER)
merged.to_file(OUT_GPKG, layer=OUT_LAYER, driver="GPKG")
print("DONE.")
