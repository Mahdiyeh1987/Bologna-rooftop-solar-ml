import pandas as pd
from pathlib import Path

root = Path(r"C:\GIS\work")
pred = pd.read_csv(root/"predictions_city.csv")  # roof_id,y_hat_kWhm2yr

# اگر Q3 دقیق داری جایگزین کن؛ وگرنه از داده محاسبه می‌شود
# Q3 = 1782.02
Q3 = pred["y_hat_kWhm2yr"].quantile(0.75)

t_minus = 0.98 * Q3
t_plus  = 1.02 * Q3

base  = set(pred.loc[pred["y_hat_kWhm2yr"]>=Q3, "roof_id"])
minus = set(pred.loc[pred["y_hat_kWhm2yr"]>=t_minus, "roof_id"])
plus  = set(pred.loc[pred["y_hat_kWhm2yr"]>=t_plus,  "roof_id"])

def overlap(a,b):
    n = len(a); inter = len(a & b)
    return inter, n, round(inter/n*100,1) if n>0 else 0.0

m_inter, m_n, m_pct = overlap(base, minus)
p_inter, p_n, p_pct = overlap(base, plus)

out = pd.DataFrame([
    {"scenario":"−2% threshold","threshold":round(t_minus,2),
     "base_size":m_n,"intersection":m_inter,"overlap_%":m_pct},
    {"scenario":"+2% threshold","threshold":round(t_plus,2),
     "base_size":p_n,"intersection":p_inter,"overlap_%":p_pct}
])
out.to_csv(root/"q4_threshold_sensitivity.csv", index=False)
print(out)
