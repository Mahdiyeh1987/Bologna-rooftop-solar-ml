import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm
import matplotlib.patches as mpatches
import matplotlib.lines as mlines

import fiona
from shapely.geometry import shape

# -----------------------------
# INPUTS
# -----------------------------
RES_CSV   = r"C:\GIS\work\lozo_residuals_SantoStefano.csv"
ROOF_GPKG = r"C:\GIS\work\roof_step7_1525.gpkg"
QUAR_GPKG = r"C:\GIS\work\quartieri_epsg25832.gpkg"

OUT_PNG = r"C:\GIS\work\Fig15A_LOZO_residual_SantoStefano.png"
OUT_PDF = r"C:\GIS\work\Fig15A_LOZO_residual_SantoStefano.pdf"

# -----------------------------
# LOAD residuals
# -----------------------------
res = pd.read_csv(RES_CSV)
held_out = res["z_admin"].iloc[0] if "z_admin" in res.columns else "Santo Stefano"
idset = set(res["roof_id"].astype(str).tolist())

# -----------------------------
# Read Quartieri polygons (all) + held-out highlight polygon
# -----------------------------
quarts = []
held_poly = None
with fiona.open(QUAR_GPKG, layer="quartieri") as src:
    for ft in src:
        g = shape(ft["geometry"])
        p = dict(ft["properties"])
        name = p.get("quartiere", "")
        quarts.append((name, g))
        if name == held_out:
            held_poly = g

# -----------------------------
# Read roofs and extract representative points only for those in residual CSV
# -----------------------------
pts = []
with fiona.open(ROOF_GPKG, layer="roof_step7_1525") as src:
    for ft in src:
        p = dict(ft["properties"])
        rid = str(p.get("roof_id", ""))
        if rid not in idset:
            continue
        g = shape(ft["geometry"])
        rp = g.representative_point()
        pts.append((rid, rp.x, rp.y))

pts_df = pd.DataFrame(pts, columns=["roof_id","x","y"])
m = pts_df.merge(res[["roof_id","residual"]], on="roof_id", how="inner")

# -----------------------------
# Color scaling (symmetric around 0)
# -----------------------------
maxabs = np.nanpercentile(np.abs(m["residual"].values), 98)
if not np.isfinite(maxabs) or maxabs == 0:
    maxabs = float(np.nanmax(np.abs(m["residual"].values))) if len(m) else 1.0

norm = TwoSlopeNorm(vmin=-maxabs, vcenter=0.0, vmax= maxabs)

# -----------------------------
# Plot
# -----------------------------
plt.rcParams["font.family"] = "DejaVu Serif"  # اگر Times New Roman روی سیستم نصب داری، می‌تونی عوضش کنی
plt.rcParams["font.size"] = 11

fig, ax = plt.subplots(figsize=(16,9), dpi=300)

# quartieri outlines (light)
for name, g in quarts:
    x, y = g.exterior.xy
    ax.plot(x, y, linewidth=0.8, color="black", alpha=0.35, zorder=1)

# held-out outline (thick)
if held_poly is not None:
    x, y = held_poly.exterior.xy
    ax.plot(x, y, linewidth=2.2, color="black", alpha=0.9, zorder=2)

# residual points
sc = ax.scatter(
    m["x"], m["y"],
    c=m["residual"],
    cmap="coolwarm",
    norm=norm,
    s=26,
    edgecolor="black",
    linewidths=0.25,
    alpha=0.95,
    zorder=3
)

# extent
minx, miny, maxx, maxy = m["x"].min(), m["y"].min(), m["x"].max(), m["y"].max()
dx, dy = (maxx-minx), (maxy-miny)
ax.set_xlim(minx - 0.10*dx, maxx + 0.10*dx)
ax.set_ylim(miny - 0.10*dy, maxy + 0.10*dy)

ax.set_aspect("equal", adjustable="box")
ax.axis("off")

# colorbar
cbar = fig.colorbar(sc, ax=ax, fraction=0.03, pad=0.01)
cbar.set_label("Residual (observed − predicted)  [kWh·m$^{-2}$·yr$^{-1}$]")

# title / note
ax.text(
    0.01, 0.99,
    f"LOZO residuals — held-out Quartiere: {held_out}  |  n = {len(m)}",
    transform=ax.transAxes, ha="left", va="top", fontsize=11
)

# -----------------------------
# Annotations (auto: extreme + / -)
# -----------------------------
if len(m) >= 10:
    pos = m.sort_values("residual", ascending=False).head(min(25, len(m)))
    neg = m.sort_values("residual", ascending=True ).head(min(25, len(m)))

    px, py = pos["x"].mean(), pos["y"].mean()
    nx, ny = neg["x"].mean(), neg["y"].mean()

    ax.annotate(
        "Under-prediction\n(obs > pred)",
        xy=(px, py), xycoords="data",
        xytext=(px + 0.15*dx, py + 0.10*dy),
        textcoords="data",
        arrowprops=dict(arrowstyle="->", lw=1.0),
        bbox=dict(boxstyle="round,pad=0.25", fc="white", ec="black", alpha=0.95),
        zorder=4
    )
    ax.annotate(
        "Over-prediction\n(obs < pred)",
        xy=(nx, ny), xycoords="data",
        xytext=(nx - 0.22*dx, ny - 0.12*dy),
        textcoords="data",
        arrowprops=dict(arrowstyle="->", lw=1.0),
        bbox=dict(boxstyle="round,pad=0.25", fc="white", ec="black", alpha=0.95),
        zorder=4
    )

fig.tight_layout()
fig.savefig(OUT_PNG, dpi=300, bbox_inches="tight", facecolor="white")
fig.savefig(OUT_PDF, dpi=300, bbox_inches="tight", facecolor="white")
plt.close(fig)

print("Saved:", OUT_PNG)
print("Saved:", OUT_PDF)
