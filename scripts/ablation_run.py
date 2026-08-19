# ablation_run.py
import pandas as pd, numpy as np
from pathlib import Path
from sklearn.model_selection import GroupKFold
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
from lightgbm import LGBMRegressor
import matplotlib.pyplot as plt

root = Path(r"C:\GIS\work")
df = pd.read_csv(root/"train_dataset.csv")

# برچسب و گروه‌ها
y = df["label_mean"].values
groups = (df["z_admin"].astype(str) + "_" + df["z_morph_k4"].astype(str)).values

# خانواده‌های فیچر با نام ستون‌های دقیقت
geom = ["slpmean","asinmean","acosmean","svf_mean","shadow_mean","relief_mean"]
ctx  = ["rbwc50_pct","rbtcd10_pct"]
ua   = ["ua_rbua50_2018_11210_pct","ua_rbua50_2018_11220_pct",
        "ua_rbua50_2018_11230_pct","ua_rbua50_2018_12100_pct",
        "ua_rbua50_2018_13400_pct","ua_rbua50_2018_14100_pct"]

configs = {
    "Baseline-Geom": geom,
    "Geom+Context": geom + ctx + ua,
    "Geom+Context_noUA": geom + ctx
}

def groupcv_scores(X, y, groups, n_splits=5):
    # اطمینان از عددی بودن و پرکردن خلاها
    X = X.apply(pd.to_numeric, errors="coerce").fillna(0.0)

    gkf = GroupKFold(n_splits=n_splits)
    r2s, maes, rmses = [], [], []
    for tr, te in gkf.split(X, y, groups=groups):
        Xtr, Xte = X.iloc[tr], X.iloc[te]
        ytr, yte = y[tr], y[te]

        # مدل کمی محافظه‌کارتر برای داده‌های با تنوع کم
        mdl = LGBMRegressor(
            n_estimators=1600, learning_rate=0.03, num_leaves=63,
            subsample=0.9, colsample_bytree=0.9, reg_lambda=0.6,
            min_child_samples=20, min_data_in_bin=10,
            feature_pre_filter=False, random_state=42, n_jobs=-1, verbosity=-1
        )
        mdl.fit(Xtr, ytr)

        yhat = mdl.predict(Xte)
        r2s.append(r2_score(yte, yhat))
        maes.append(mean_absolute_error(yte, yhat))
        # برخی نسخه‌های sklearn پارامتر squared را ندارند؛ خودمان RMSE را می‌گیریم
        mse = mean_squared_error(yte, yhat)  # پیش‌فرض: MSE
        rmses.append(mse ** 0.5)

    return np.mean(r2s), np.std(r2s), np.mean(maes), np.mean(rmses)

rows = []
for name, cols in configs.items():
    X = df[cols]
    r2m, r2sd, mae, rmse = groupcv_scores(X, y, groups)
    rows.append({
        "config": name, "features": len(cols),
        "R2_mean": round(r2m, 3), "R2_sd": round(r2sd, 3),
        "MAE": round(mae, 2), "RMSE": round(rmse, 2)
    })

res = pd.DataFrame(rows).sort_values("R2_mean", ascending=False)
res.to_csv(root/"ablation_results.csv", index=False)
print(res)

# نمودار ΔR² نسبت به Baseline-Geom
base = res.loc[res["config"]=="Baseline-Geom","R2_mean"].values[0]
res["delta_R2"] = res["R2_mean"] - base
plt.figure()
plt.bar(res["config"], res["delta_R2"])
plt.axhline(0, ls="--")
plt.ylabel("ΔR² vs Baseline-Geom")
plt.title("Ablation: Impact of Context & UA")
plt.xticks(rotation=15, ha="right")
plt.tight_layout()
plt.savefig(root/"fig_ablation_deltaR2.png", dpi=300)
