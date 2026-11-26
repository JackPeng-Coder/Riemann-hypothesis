# -*- coding: utf-8 -*-
"""Regenerate two small figures after label edits."""
import json, math
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BASE = Path(__file__).resolve().parent
FIG = BASE / "figs"
Z = json.loads((BASE / "zeros.json").read_text(encoding="utf-8"))
plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei"]
plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["savefig.dpi"] = 220

NAVY, COPPER, WINE, GREY = "#16283f", "#9a6b2f", "#7a1f2b", "#5c6775"

# fig 5 spacing
g = np.array(Z[:500])
spac = np.diff(g) * np.log(g[:-1] / (2 * math.pi)) / (2 * math.pi)
spac = spac[spac > 0]
fig, ax = plt.subplots(figsize=(7.0, 4.0))
ax.hist(spac, bins=34, density=True, color="#d9c9a8", edgecolor="white", lw=0.8,
        label="前 500 个零点的归一化间距")
s = np.linspace(0, 3.2, 300)
gue = (32 / math.pi ** 2) * s ** 2 * np.exp(-4 * s ** 2 / math.pi)
ax.plot(s, gue, color=WINE, lw=2.0, label="GUE Wigner surmise")
ax.set_xlim(0, 3.2); ax.set_xlabel("归一化间距 s"); ax.set_ylabel("概率密度")
ax.set_title("零点间距的“能级排斥”：随机矩阵理论的指纹", fontsize=11.5, color=NAVY, pad=8)
ax.legend(frameon=False, fontsize=8.5); ax.grid(alpha=0.15, lw=0.6)
fig.tight_layout(); fig.savefig(FIG / "fig5_gue.png", bbox_inches="tight", facecolor="white"); plt.close(fig)

# fig 8 proportion
labels = ["Levinson\n1974", "Conrey\n1989", "Bui–Conrey–Young\n2011", "PRZZ\n2020"]
vals = [33.3, 40.88, 41.05, 41.72]
fig, ax = plt.subplots(figsize=(7.2, 2.9))
ax.barh(range(len(vals)), vals, color=["#c9b48c", "#b8945c", COPPER, WINE], height=0.55)
for i, v in enumerate(vals):
    ax.text(v + 0.7, i, f"{v:.2f}%", va="center", fontsize=9, color=NAVY)
ax.set_yticks(range(len(vals))); ax.set_yticklabels(labels, fontsize=8.6)
ax.set_xlim(0, 50); ax.set_xlabel("已证明位于临界线上的零点比例（下界）")
ax.set_title("九十年间的渐进：比例路线离 100% 仍很遥远", fontsize=10.5, color=NAVY, pad=8)
ax.grid(axis="x", alpha=0.15, lw=0.6)
for s in ("top", "right"): ax.spines[s].set_visible(False)
fig.tight_layout(); fig.savefig(FIG / "fig8_proportion.png", bbox_inches="tight", facecolor="white"); plt.close(fig)
print("ok")
