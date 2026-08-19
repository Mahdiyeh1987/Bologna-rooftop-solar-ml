# -*- coding: utf-8 -*-
"""
make_calibration_scatter.py
Generates Figure 4-5: Predicted vs Observed scatter with 1:1 and fitted line,
and summary metrics (R2, RMSE, MAPE) using 10-fold OOF predictions (LightGBM).

Inputs:
    C:\GIS\work\train_dataset.csv  (must include: label_mean, roof_id, z_admin, z_morph_k4, features)
Outputs:
    C:\GIS\work\figures\Figure_4_5_calibration_scatter.png
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.metrics import r2_score, mean_squared_error
import lightgbm as lgb

# ---------- PATHS ----------
DATA_CSV = r"C:\GIS\work\train_dataset.csv"
OUT_DIR  = r"C:\GIS\work\figures"
OUT_PNG  = os.path.join(OUT_DIR, "Figure_4_5_calibration_scatter.png")

# ---------- LOAD ----------
df = pd.read_csv(DATA_CSV)

# ---------- TARGET / GROUPS / STRATA ----------
y = df["label_mean"].to_numpy()
groups = df["z_admin"].astype(str) + "|" + df["z_morph_k4"].astype(str)
# 10-quantile strata for stratified CV (duplicates='drop' handles ties)
strata = pd.qcut(y, 10, labels=False, duplicates="drop")

# ---------- FEATURE MATRIX X ----------
# Drop IDs / strata / normalised fields (nrm_*) used only for clustering
drop_cols = ["label_mean", "roof_id", "z_admin", "z_morph_k4"]
drop_cols += [c for c in df.columns if c.startswith("nrm_")]

# Keep only numeric columns after dropping known non-features
X = df.drop(columns=drop_cols, errors="ignore").select_dtypes(include=["number"]).copy()

# Remove near-constant columns (variance ~ 0) to prevent degenerate splits
if X.shape[1] > 0:
    nunique = X.nunique(dropna=False)
    X = X[nunique[nunique > 1].index]

# ---------- MODEL ----------
params = dict(
    learning_rate=0.02,
    n_estimators=2000,
    num_leaves=127,
    subsample=0.90,
    colsample_bytree=0.90,
    reg_lambda=0.5,
    min_child_samples=10,
    max_bin=511,
    random_state=42,
    n_jobs=-1
)
model = lgb.LGBMRegressor(**params)

cv = StratifiedGroupKFold(n_splits=10, shuffle=True, random_state=42)
oof = np.full(len(df), np.nan, dtype=float)

for tr_idx, va_idx in cv.split(X, strata, groups):
    Xtr, Xva = X.iloc[tr_idx], X.iloc[va_idx]
    ytr, yva = y[tr_idx], y[va_idx]
    model.fit(
        Xtr, ytr,
        eval_set=[(Xva, yva)],
        eval_metric="l2",
        # quiet logs + early stopping
        callbacks=[lgb.early_stopping(150, verbose=False), lgb.log_evaluation(0)]
    )
    oof[va_idx] = model.predict(Xva)

# ---------- METRICS (mask finite to avoid env/version issues) ----------
mask = np.isfinite(y) & np.isfinite(oof)
y_m, oof_m = y[mask], oof[mask]

r2   = r2_score(y_m, oof_m)
mse  = mean_squared_error(y_m, oof_m)          # no 'squared' kwarg (compat with older sklearn)
rmse = float(np.sqrt(mse))
mape = float((np.abs((y_m - oof_m) / y_m).mean()) * 100)

# Linear fit: obs ≈ a * pred + b (on masked vectors)
a, b = np.polyfit(oof_m, y_m, 1)
mn = float(min(oof_m.min(), y_m.min()))
mx = float(max(oof_m.max(), y_m.max()))

# ---------- PLOT ----------
os.makedirs(OUT_DIR, exist_ok=True)
plt.figure(figsize=(12, 8))
plt.scatter(oof_m, y_m, s=8, alpha=0.5)
# 1:1 line
plt.plot([mn, mx], [mn, mx], linestyle="--")
# fitted line
plt.plot([mn, mx], [a * mn + b, a * mx + b])
plt.xlabel("Predicted (kWh·m⁻²·yr⁻¹)")
plt.ylabel("Observed (kWh·m⁻²·yr⁻¹)")
plt.title("Predicted vs Observed Annual Irradiation (OOF, 10-fold GBM)")
txt = (
    f"R² = {r2:.3f}   RMSE ≈ {rmse:.1f}   MAPE ≈ {mape:.2f}%\n"
    f"Fit: obs ≈ {a:.4f}·pred + {b:.2f}"
)
plt.text(0.02, 0.98, txt, transform=plt.gca().transAxes, ha="left", va="top")
plt.tight_layout()
plt.savefig(OUT_PNG, dpi=300)
plt.close()

print(f"Saved: {OUT_PNG}")
print(f"Fit slope={a:.4f}, intercept={b:.2f}, R2={r2:.3f}, RMSE={rmse:.1f}, MAPE={mape:.2f}%")
