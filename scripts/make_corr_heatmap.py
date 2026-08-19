# -*- coding: utf-8 -*-
"""
make_corr_heatmap.py
ساخت هیت‌مپ همبستگیِ ویژگی‌ها برای تز (Matplotlib-only، چاپ‌پسند)

خروجی‌ها (پیش‌فرض در C:\GIS\work):
- chapter4_corr_<method>.csv                  # ماتریس همبستگی
- chapter4_corr_<method>_full.png             # کل ماتریس
- chapter4_corr_<method>_lowertri.png         # نیم‌ساز پایین (چاپ‌پسند)
- chapter4_corr_dropped_cols.csv              # گزارش ستون‌های حذف‌شده
- chapter4_corr_missing_ratio.csv             # درصد خلأ هر ستون قبل از پر کردن
"""

import os
import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt

# ========= تنظیمات کاربر =========
CSV_PATH       = r"C:\GIS\work\train_dataset.csv"   # مسیر دیتاست
OUT_DIR        = r"C:\GIS\work"                     # پوشه خروجی
OUT_BASENAME   = "chapter4_corr"                    # پیشوند نام خروجی‌ها

# اگر می‌خواهی فقط ستون‌های خاصی را روی شکل داشته باشی؛ اگر خالی بماند، همهٔ عددی‌ها استفاده می‌شود
keep_cols = [
    # "area_m2","slpmean","asinmean","acosmean","svf_mean","shadow_mean","relief_mean",
    # "rbwc50_pct","rbtcd10_pct","UA11210_pct","UA11220_pct","UA11230_pct",
    # "UA12100_pct","UA13400_pct","UA14100_pct","clim_ghi_y","clim_dni_y",
    # "clim_dhi_y","clim_t2m_y"
]

# روش همبستگی: "pearson" یا "spearman"
CORR_METHOD    = "pearson"

# برای دیتاست‌های خیلی بزرگ می‌توانی داونسَمپل کنی (مثلاً 5000). None یعنی بدون محدودیت
MAX_ROWS       = None

# آستانه‌ها برای پاکسازی
MISSING_DROP_THRESHOLD = 0.98   # ستون‌هایی با >98% خلأ حذف می‌شوند
ANNOTATION_MAX         = 12     # اگر تعداد متغیرها بیش از این باشد، اعداد روی سلول‌ها نوشته نمی‌شوند

# تنظیمات شکل/فونت
matplotlib.rcParams["font.family"] = "Times New Roman"
DPI        = 300
FIG_W_IN   = 4800 / 100.0   # inches (4800px @ 100 px/in ⇒ 300 dpi نهایی در savefig)
FIG_H_IN   = 2700 / 100.0
COLORMAP   = "coolwarm"     # برای چاپ سیاه‌وسفید: "Greys"
TITLE_FULL = "Correlation Heatmap of Geometric & Environmental Descriptors"
TITLE_LOW  = "Correlation Heatmap (Lower Triangle)"
# =================================

def main():
    os.makedirs(OUT_DIR, exist_ok=True)

    # --- خواندن CSV با تشخیص NA سفارشی ---
    na_vals = ["", " ", "NA", "NaN", "nan", "-", "--", "null", "NULL"]
    df = pd.read_csv(CSV_PATH, na_values=na_vals)

    # تبدیل ستون‌های متنی به عدد در صورت امکان
    for c in df.columns:
        if df[c].dtype == object:
            df[c] = pd.to_numeric(df[c], errors="coerce")

    # فقط عددی‌ها
    num_df = df.select_dtypes(include=[np.number]).copy()

    # اگر لیست دلخواه تعیین شده
    if keep_cols:
        missing = [c for c in keep_cols if c not in num_df.columns]
        if missing:
            raise ValueError(f"ستون‌های یافت نشد: {missing}")
        num_df = num_df[keep_cols]

    # داونسَمپل اختیاری
    if MAX_ROWS is not None and len(num_df) > MAX_ROWS:
        num_df = num_df.sample(n=MAX_ROWS, random_state=42)

    # گزارش نسبت خلأ اولیه
    missing_ratio = num_df.isna().mean().sort_values(ascending=False)
    missing_ratio.to_csv(os.path.join(OUT_DIR, f"{OUT_BASENAME}_missing_ratio.csv"),
                         header=["missing_ratio"])

    # تشخیص ستون‌های واریانس صفر/تک‌مقداری یا بسیار خالی
    zero_var = num_df.nunique(dropna=True).le(1)  # ≤1 مقدار یکتا
    drop_too_missing = missing_ratio[missing_ratio > MISSING_DROP_THRESHOLD].index.tolist()
    drop_zero_var    = num_df.columns[zero_var].tolist()

    to_drop = sorted(set(drop_too_missing + drop_zero_var))
    if to_drop:
        pd.DataFrame({"col": to_drop,
                      "reason": ["too_missing_or_zero_variance"]*len(to_drop)}
                     ).to_csv(os.path.join(OUT_DIR, f"{OUT_BASENAME}_dropped_cols.csv"), index=False)
        num_df = num_df.drop(columns=to_drop)

    # اگر چیز کافی نماند، خطا بده
    if num_df.shape[1] < 2:
        raise RuntimeError("ستون عددی کافی پس از پاکسازی باقی نمانده است.")

    # پر کردن خلأ با میانگین هر ستون
    num_df = num_df.fillna(num_df.mean(numeric_only=True))

    # محاسبه همبستگی
    corr = num_df.corr(method=CORR_METHOD)
    corr_csv_path = os.path.join(OUT_DIR, f"{OUT_BASENAME}_{CORR_METHOD}.csv")
    corr.to_csv(corr_csv_path, index=True)

    # لیبل‌ها و ابعاد
    labels = corr.columns.tolist()
    n = len(labels)
    C = corr.values

    # ===== رسم نسخه کامل =====
    fig, ax = plt.subplots(figsize=(FIG_W_IN, FIG_H_IN), dpi=DPI)
    im = ax.imshow(C, vmin=-1, vmax=1, cmap=COLORMAP)

    ax.set_xticks(np.arange(n)); ax.set_yticks(np.arange(n))
    ax.set_xticklabels(labels, fontsize=10, rotation=45, ha="right")
    ax.set_yticklabels(labels, fontsize=10)

    # خطوط شبکه ظریف
    ax.set_xticks(np.arange(-.5, n, 1), minor=True)
    ax.set_yticks(np.arange(-.5, n, 1), minor=True)
    ax.grid(which="minor", color="white", linestyle="-", linewidth=0.5)
    ax.tick_params(which="minor", bottom=False, left=False)

    ax.set_title(TITLE_FULL, fontsize=14, pad=16)
    cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.set_label("Correlation (ρ)", fontsize=12)

    # نوشتن اعداد در صورت کم‌بودن ابعاد
    if n <= ANNOTATION_MAX:
        for i in range(n):
            for j in range(n):
                val = C[i, j]
                txt = f"{val:.2f}"
                color = "black" if abs(val) < 0.6 else "white"
                ax.text(j, i, txt, ha="center", va="center", fontsize=9, color=color)

    plt.tight_layout()
    png_full = os.path.join(OUT_DIR, f"{OUT_BASENAME}_{CORR_METHOD}_full.png")
    plt.savefig(png_full, dpi=DPI)
    plt.close(fig)

    # ===== نسخه نیم‌ساز پایین (lower triangle) =====
    mask = np.triu(np.ones_like(C, dtype=bool), k=1)  # بالایی را ماسک کن
    C_masked = np.ma.array(C, mask=mask)

    fig2, ax2 = plt.subplots(figsize=(FIG_W_IN, FIG_H_IN), dpi=DPI)
    im2 = ax2.imshow(C_masked, vmin=-1, vmax=1, cmap=COLORMAP)

    ax2.set_xticks(np.arange(n)); ax2.set_yticks(np.arange(n))
    ax2.set_xticklabels(labels, fontsize=10, rotation=45, ha="right")
    ax2.set_yticklabels(labels, fontsize=10)

    ax2.set_xticks(np.arange(-.5, n, 1), minor=True)
    ax2.set_yticks(np.arange(-.5, n, 1), minor=True)
    ax2.grid(which="minor", color="white", linestyle="-", linewidth=0.5)
    ax2.tick_params(which="minor", bottom=False, left=False)

    ax2.set_title(TITLE_LOW, fontsize=14, pad=16)
    cbar2 = fig2.colorbar(im2, ax=ax2, fraction=0.046, pad=0.04)
    cbar2.set_label("Correlation (ρ)", fontsize=12)

    if n <= ANNOTATION_MAX:
        # فقط روی نیم‌ساز پایین بنویس
        for i in range(n):
            for j in range(n):
                if j <= i:  # پایین یا روی قطر
                    val = C[i, j]
                    txt = f"{val:.2f}"
                    color = "black" if abs(val) < 0.6 else "white"
                    ax2.text(j, i, txt, ha="center", va="center", fontsize=9, color=color)

    plt.tight_layout()
    png_low = os.path.join(OUT_DIR, f"{OUT_BASENAME}_{CORR_METHOD}_lowertri.png")
    plt.savefig(png_low, dpi=DPI)
    plt.close(fig2)

    print("Saved:")
    print(" -", corr_csv_path)
    print(" -", png_full)
    print(" -", png_low)
    print("Reports:")
    print(" -", os.path.join(OUT_DIR, f"{OUT_BASENAME}_missing_ratio.csv"))
    print(" -", os.path.join(OUT_DIR, f"{OUT_BASENAME}_dropped_cols.csv"))

if __name__ == "__main__":
    main()
