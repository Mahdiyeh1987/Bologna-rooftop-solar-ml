# q4_threshold_by_zone_all.py
import pandas as pd
from pathlib import Path

root = Path(r"C:\GIS\work")
df = pd.read_csv(root/"predictions_city_with_zone.csv")  # roof_id, y_hat_kWhm2yr, z_admin

rows = []
for zone, sub in df.groupby("z_admin", dropna=False):
    Q3 = sub["y_hat_kWhm2yr"].quantile(0.75)
    def stats(factor):
        t = factor * Q3
        base  = set(sub.loc[sub["y_hat_kWhm2yr"]>=Q3, "roof_id"])
        comp  = set(sub.loc[sub["y_hat_kWhm2yr"]>=t,  "roof_id"])
        n = len(base); inter = len(base & comp)
        pct = round(inter/n*100,1) if n>0 else 0.0
        return round(t,2), n, inter, pct
    # −1%, +1%, −2%, +2%
    t_m1, n0, i_m1, p_m1 = stats(0.99)
    t_p1, _,  i_p1, p_p1 = stats(1.01)
    t_m2, _,  i_m2, p_m2 = stats(0.98)
    t_p2, _,  i_p2, p_p2 = stats(1.02)

    rows.append({
        "z_admin": zone, "Q3": round(Q3,2), "base_size": n0,
        "t_-1%": t_m1, "overlap_-1%": p_m1,
        "t_+1%": t_p1, "overlap_+1%": p_p1,
        "t_-2%": t_m2, "overlap_-2%": p_m2,
        "t_+2%": t_p2, "overlap_+2%": p_p2
    })

pd.DataFrame(rows).to_csv(root/"q4_threshold_by_zone_all.csv", index=False)
print("Saved q4_threshold_by_zone_all.csv")
