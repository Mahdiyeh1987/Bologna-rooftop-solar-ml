# -*- coding: utf-8 -*-
# LOZO residuals for one district (Quartiere)

import pandas as pd
import numpy as np
import lightgbm as lgb
from sklearn.metrics import r2_score, mean_squared_error

CSV  = r"C:\GIS\work\train_dataset.csv"
DIST = "Santo Stefano"  # نام ناحیه را دقیقا مثل فیلد z_admin بگذار

# Load
df = pd.read_csv(CSV)

# Split train / hold-out
if "z_admin" not in df.columns:
    raise SystemExit("Column 'z_admin' not found. Available: " + ", ".join(df.columns))

mask_hold = df["z_admin"].astype(str).str.casefold() == DIST.casefold()
hold  = df[mask_hold].copy()
train = df[~mask_hold].copy()
if hold.empty:
    raise SystemExit(f"No rows matched DIST='{DIST}'. Check exact values in 'z_admin'.")

# Features
drop = ["label_mean","roof_id","z_admin","z_admin_code","z_morph_k4"]
drop += [c for c in df.columns if str(c).startswith("nrm_")]
Xtr = train.drop(columns=drop, errors="ignore").select_dtypes(include=["number"])
ytr = train["label_mean"].to_numpy()
Xhd = hold.drop(columns=drop, errors="ignore").select_dtypes(include=["number"])
yhd = hold["label_mean"].to_numpy()

# Model (same params as Ch.4)
m = lgb.LGBMRegressor(
    learning_rate=0.02, n_estimators=2000, num_leaves=127,
    subsample=0.90, colsample_bytree=0.90, reg_lambda=0.5,
    min_child_samples=10, max_bin=511, random_state=42, n_jobs=-1
)
m.fit(Xtr, ytr)

# Predict + residuals
yhat = m.predict(Xhd)
out = hold[["roof_id"]].copy()
out["y_true"]   = yhd
out["y_pred"]   = yhat
out["residual"] = out["y_true"] - out["y_pred"]

# --- Save + metrics (بدون squared=False) ---
out_path = rf"C:\GIS\work\residuals_lozo_{DIST.replace(' ','_')}.csv"
out.to_csv(out_path, index=False)

# اگر احیاناً NaN پیش آمد، ماسک کن
import numpy as np
mask = np.isfinite(yhd) & np.isfinite(yhat)
mse  = mean_squared_error(yhd[mask], yhat[mask])  # بدون squared
rmse = float(np.sqrt(mse))
r2   = r2_score(yhd[mask], yhat[mask])

print(f"Saved: {out_path}")
print(f"R2={r2:.3f}  RMSE={rmse:.2f}")
