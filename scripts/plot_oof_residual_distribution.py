# -*- coding: utf-8 -*-
"""
make_residuals_fig.py
Generates Figure 4-3: Residual density/histogram (observed - predicted)
for 10-fold OOF predictions from LightGBM with grouped+stratified CV.

Inputs:
    C:\GIS\work\train_dataset.csv  (must include: label_mean, roof_id, z_admin, z_morph_k4, features)
Outputs:
    C:\GIS\work\figures\Figure_4_3_residuals.png
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import StratifiedGroupKFold
import lightgbm as lgb

# ---------- PATHS ----------
DATA_CSV   = r"C:\GIS\work\train_dataset.csv"
OUT_DIR    = r"C:\GIS\work\figures"
OUT_PNG    = os.path.join(OUT_DIR, "Figure_4_3_residuals.png")

# ---------- LOAD ----------
df = pd.read_csv(DATA_CSV)

# ---------- TARGET / GROUPS / STRATA ----------
y = df["label_mean"].to_numpy()
groups = df["z_admin"].astype(str) + "|" + df["z_morph_k4"].astype(str)
# 10-quantile strata for stratified CV (duplicates='drop' handles ties)
strata = pd.qcut(y, 10, labels=False, duplicates="drop")

# ---------- FEATURE MATRIX X ----------
# columns to drop (IDs, strata, and any normalised nrm_* created for K-means only)
drop_cols = ["label_mean", "roof_id", "z_admin", "z_morph_k4"]
drop_cols += [c for c in df.columns if c.startswith("nrm_")]

# Drop known columns; then keep only numeric dtypes (avoid object like admin_flag)
X = df.drop(columns=drop_cols, errors="ignore")
X = X.select_dtypes(include=["number"]).copy()

# Optional sanity: remove near-constant columns (variance ~ 0)
# (Keeps the script robust if any accidental dummy/flag is all zeros)
if X.shape[1] > 0:
    nunique = X.nunique(dropna=False)
    keep = nunique[nunique > 1].index
    X = X[keep]

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
        callbacks=[lgb.early_stopping(150, verbose=False)]
    )
    oof[va_idx] = model.predict(Xva)

# ---------- RESIDUALS ----------
residuals = y - oof  # observed - predicted
mu = float(np.nanmean(residuals))
sd = float(np.nanstd(residuals, ddof=1))

# ---------- PLOT ----------
os.makedirs(OUT_DIR, exist_ok=True)
plt.figure(figsize=(12, 6))
plt.hist(residuals, bins=40, density=True)
plt.axvline(0.0, linestyle="--")
plt.title("Residual density (OOF, 10-fold GBM)")
plt.xlabel("Residual (kWh·m⁻²·yr⁻¹)")
plt.ylabel("Density")
plt.text(
    0.02, 0.95,
    f"Mean = {mu:.2f}   SD = {sd:.2f}",
    transform=plt.gca().transAxes, ha="left", va="top"
)
plt.tight_layout()
plt.savefig(OUT_PNG, dpi=300)
plt.close()

print(f"Saved: {OUT_PNG}")
