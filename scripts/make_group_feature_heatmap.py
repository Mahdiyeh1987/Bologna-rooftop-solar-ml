import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib

CSV_PATH = r"C:\GIS\work\train_dataset.csv"   # یا inference_features.csv
OUT_DIR  = r"C:\GIS\work"
OUT_NAME = "chapter4_group_feature_heatmap.png"

GROUP_COL = "z_morph_k4"   # می‌توانی "z_admin" یا "z_admin_code" بگذاری
FEATURES = [
    "svf_mean","shadow_mean","relief_mean","slpmean","asinmean","acosmean",
    "rbwc50_pct","rbtcd10_pct"
]

matplotlib.rcParams["font.family"] = "Times New Roman"
DPI = 300
FIG_W, FIG_H = 4800/100, 2700/100  # inches

df = pd.read_csv(CSV_PATH)
df = df[[GROUP_COL] + FEATURES].copy()
for c in FEATURES:
    df[c] = pd.to_numeric(df[c], errors="coerce")

grp = df.groupby(GROUP_COL, dropna=False)[FEATURES].mean()

mu = grp.mean(axis=0)
sd = grp.std(axis=0).replace(0, np.nan)
Z = (grp - mu) / sd   # z-score ستونی

fig, ax = plt.subplots(figsize=(FIG_W, FIG_H), dpi=DPI)
M = Z.values
im = ax.imshow(M, cmap="coolwarm", vmin=-2, vmax=2)

ax.set_yticks(np.arange(Z.shape[0])); ax.set_yticklabels([str(i) for i in Z.index], fontsize=12)
ax.set_xticks(np.arange(Z.shape[1])); ax.set_xticklabels(Z.columns.tolist(), rotation=45, ha="right", fontsize=12)

ax.set_title("Standardised descriptor means by group", fontsize=16, pad=14)
cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
cbar.set_label("z-score (column-wise)", fontsize=12)

ax.set_xticks(np.arange(-.5, Z.shape[1], 1), minor=True)
ax.set_yticks(np.arange(-.5, Z.shape[0], 1), minor=True)
ax.grid(which="minor", color="white", linewidth=0.5)
ax.tick_params(which="minor", bottom=False, left=False)

plt.tight_layout()
out_path = os.path.join(OUT_DIR, OUT_NAME)
plt.savefig(out_path, dpi=DPI)
plt.close()
print("Saved:", out_path)
