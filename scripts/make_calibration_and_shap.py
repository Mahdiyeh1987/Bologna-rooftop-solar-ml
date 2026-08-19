# make_calibration_and_shap.py
import os
import geopandas as gpd
import pandas as pd
import numpy as np
import shap
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import KFold
from lightgbm import LGBMRegressor

# ----- paths & fields -----
GPKG  = r"C:\GIS\work\roof_step7_1525_with_labels.gpkg"
LAYER = "roof_step7_1525_labeled"
OUTDIR = r"C:\GIS\work\eval"
TARGET = "label_mean"
PREDCOL = "y_hat_kWhm2yr"   # اگر در لایه 1525 نداری، کد خودش OOF می‌سازد

os.makedirs(OUTDIR, exist_ok=True)

# ----- load -----
gdf = gpd.read_file(GPKG, layer=LAYER)
df = pd.DataFrame(gdf.drop(columns=gdf.geometry.name, errors="ignore"))

# feature set: همه ستون‌های عددی به جز تارگت
drop_cols = {TARGET}
num_cols = [c for c in df.columns if c not in drop_cols and pd.api.types.is_numeric_dtype(df[c])]
X = df[num_cols].copy()
y = df[TARGET].values

# اگر ستون پیش‌بینی موجود نیست، out-of-fold بساز
if PREDCOL in df.columns:
    yhat = df[PREDCOL].values
else:
    kf = KFold(n_splits=10, shuffle=True, random_state=42)
    yhat = np.zeros_like(y, dtype=float)
    model_params = dict(
        n_estimators=800, learning_rate=0.03, num_leaves=63,
        subsample=0.8, colsample_bytree=0.8, random_state=42
    )
    for tr, te in kf.split(X):
        m = LGBMRegressor(**model_params)
        m.fit(X.iloc[tr], y[tr])
        yhat[te] = m.predict(X.iloc[te])

# کالیبراسیون: y ~ yhat
X_lin = yhat.reshape(-1, 1)
reg = LinearRegression().fit(X_lin, y)
slope = float(reg.coef_[0])
intercept = float(reg.intercept_)
r2 = float(reg.score(X_lin, y))

calib = pd.DataFrame([dict(slope=slope, intercept=intercept, R2=r2)])
calib.to_csv(os.path.join(OUTDIR, "calibration_report.csv"), index=False)

# نمودار کالیبراسیون
plt.figure()
plt.scatter(yhat, y, s=10, alpha=0.6)
xline = np.linspace(float(np.min(yhat)), float(np.max(yhat)), 100)
plt.plot(xline, intercept + slope * xline, linewidth=2)
plt.plot(xline, xline, linestyle="--")  # خط ایده‌آل
plt.xlabel("Predicted (kWh·m^-2·yr^-1)")
plt.ylabel("Observed (kWh·m^-2·yr^-1)")
plt.title("Calibration: observed vs predicted")
plt.tight_layout()
plt.savefig(os.path.join(OUTDIR, "calibration_plot.png"), dpi=300)

# SHAP Top-10 (روی یک مدل فیت‌شده روی کل داده)
m = LGBMRegressor(
    n_estimators=800, learning_rate=0.03, num_leaves=63,
    subsample=0.8, colsample_bytree=0.8, random_state=42
)
m.fit(X, y)
explainer = shap.TreeExplainer(m)
shap_values = explainer(X)

# beeswarm
plt.figure()
shap.plots.beeswarm(shap_values, show=False, max_display=20)
plt.tight_layout()
plt.savefig(os.path.join(OUTDIR, "shap_beeswarm.png"), dpi=300)

# mean |SHAP| top-10
mean_abs = np.abs(shap_values.values).mean(axis=0)
top_idx = np.argsort(-mean_abs)[:10]
top = pd.DataFrame({
    "feature": np.array(X.columns)[top_idx],
    "mean_|SHAP|": mean_abs[top_idx]
})
top.to_csv(os.path.join(OUTDIR, "shap_top10.csv"), index=False)

print("Saved calibration & SHAP outputs to", OUTDIR)
