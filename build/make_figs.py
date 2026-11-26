# -*- coding: utf-8 -*-
"""Generate all figures for the Riemann Hypothesis report."""
import json, math
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import hsv_to_rgb
from matplotlib.patches import Rectangle, FancyArrowPatch
import mpmath as mp

BASE = Path(__file__).resolve().parent
FIG = BASE / "figs"
FIG.mkdir(exist_ok=True)
CACHE = BASE / "zeros.json"

plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei"]
plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["savefig.dpi"] = 220
plt.rcParams["figure.dpi"] = 120

NAVY = "#16283f"
COPPER = "#9a6b2f"
WINE = "#7a1f2b"
GREY = "#5c6775"
CREAM = "#f6f2e9"

# ---------------------------------------------------------------- zeros
def get_zeros(n):
    if CACHE.exists():
        data = json.loads(CACHE.read_text(encoding="utf-8"))
        if len(data) >= n:
            return data[:n]
    mp.mp.dps = 30
    zs = [float(mp.zetazero(k).imag) for k in range(1, n + 1)]
    CACHE.write_text(json.dumps(zs), encoding="utf-8")
    return zs

print("computing zeros ...", flush=True)
Z = get_zeros(520)
print("zeros ready:", len(Z), flush=True)

# ---------------------------------------------------------------- zeta via Euler-Maclaurin
def zeta_em(s, N=80):
    """s: 1-D complex array. Euler-Maclaurin, accurate for |Im s| <~ 60."""
    n = np.arange(1, N, dtype=float)
    logn = np.log(n)
    terms = np.exp(-s[None, :] * logn[:, None])
    total = terms.sum(axis=0)
    total += N ** (1 - s) / (s - 1)
    total += 0.5 * N ** (-s)
    total += (1.0 / 12.0) * s * N ** (-s - 1)
    total -= (1.0 / 720.0) * s * (s + 1) * (s + 2) * N ** (-s - 3)
    total += (1.0 / 30240.0) * s * (s + 1) * (s + 2) * (s + 3) * (s + 4) * N ** (-s - 5)
    return total

# accuracy check
mp.mp.dps = 20
for t in (0.5, 5.0, 14.134725, 30.0):
    got = zeta_em(np.array([0.3 + 1j * t]))[0]
    ref = complex(mp.zeta(mp.mpc(0.3, t)))
    print(f"zeta check t={t}: err={abs(got-ref):.2e}", flush=True)

# ---------------------------------------------------------------- fig 1 domain colouring
print("fig1 domain colouring ...", flush=True)
W, H = 620, 1240
re = np.linspace(-1.6, 2.6, W)
im = np.linspace(-36, 36, H)
img = np.zeros((H, W, 3))
for j, t in enumerate(im):
    s = re + 1j * t
    z = zeta_em(s, N=70)
    r = np.abs(z)
    hue = (np.angle(z) + np.pi) / (2 * np.pi)
    val = 0.04 + 0.96 * (1 - 1 / (1 + r ** 0.38))
    hsv = np.stack([hue, np.full_like(hue, 0.82), np.clip(val, 0, 1)], axis=-1)
    img[j] = hsv_to_rgb(hsv)

fig, ax = plt.subplots(figsize=(6.6, 10.2))
ax.imshow(img, extent=[re[0], re[-1], im[0], im[-1]], origin="lower", aspect="auto", interpolation="lanczos")
ax.axvline(0.5, color="white", lw=1.1, ls=(0, (7, 5)), alpha=0.9)
ax.axvline(0.0, color="white", lw=0.6, alpha=0.35)
ax.axvline(1.0, color="white", lw=0.6, alpha=0.35)
ax.set_xlim(re[0], re[-1])
ax.set_ylim(im[0], im[-1])
ax.set_xlabel("Re(s)", color="white", fontsize=11)
ax.set_ylabel("Im(s)", color="white", fontsize=11)
ax.tick_params(colors="white", labelsize=8)
for spine in ax.spines.values():
    spine.set_color("white"); spine.set_alpha(0.4)
ax.text(0.53, 33.2, "临界线 Re(s) = 1/2", color="white", fontsize=10, va="top")
ax.text(1.03, 2.4, "极点 s = 1", color="white", fontsize=9, va="bottom")
ax.text(0.02, -33.5, "零点 = 暗点", color="white", fontsize=9, va="bottom")
fig.patch.set_facecolor(NAVY)
ax.set_facecolor(NAVY)
fig.tight_layout()
fig.savefig(FIG / "fig1_domain.png", facecolor=NAVY, bbox_inches="tight")
plt.close(fig)

# ---------------------------------------------------------------- fig 2 critical strip schematic
print("fig2 critical strip ...", flush=True)
fig, ax = plt.subplots(figsize=(7.2, 6.2))
ax.add_patch(Rectangle((0, -34), 1, 68, facecolor="#e8eef4", edgecolor="none", zorder=0))
ax.axhline(0, color="#8a8f98", lw=0.8, zorder=1)
ax.axvline(0, color="#8a8f98", lw=0.8, zorder=1)
ax.axvline(0.5, color=COPPER, lw=1.4, ls="--", zorder=2)
ax.axvline(1.0, color=WINE, lw=1.0, ls=":", zorder=2)
# trivial zeros
triv = [-2, -4, -6, -8]
ax.scatter(triv, [0] * len(triv), s=42, facecolor="white", edgecolor=NAVY, zorder=4)
ax.annotate("平凡零点\ns = −2, −4, −6, …", xy=(-6, 0), xytext=(-8.3, 9.5),
            fontsize=9, color=NAVY, arrowprops=dict(arrowstyle="-", color=GREY, lw=0.8))
ax.scatter([1], [0], marker="x", s=90, color=WINE, lw=2.0, zorder=5)
ax.annotate("极点 s = 1", xy=(1, 0), xytext=(1.25, -7.5), fontsize=9, color=WINE,
            arrowprops=dict(arrowstyle="-", color=WINE, lw=0.8))
# nontrivial zeros
ys = Z[:14]
ax.scatter([0.5] * len(ys), ys, s=26, color=COPPER, zorder=5)
ax.annotate("非平凡零点\n$\\rho = 1/2 + i\\gamma$", xy=(0.5, ys[3]), xytext=(1.25, 18),
            fontsize=9, color=COPPER, arrowprops=dict(arrowstyle="-", color=COPPER, lw=0.8))
ax.text(0.25, 32.4, "临界带 0 < Re(s) < 1", ha="center", fontsize=9.5, color=NAVY)
ax.text(0.5, -32.5, "临界线 Re(s) = 1/2", ha="center", fontsize=9.5, color=COPPER, fontweight="bold")
ax.set_xlim(-9.2, 2.3)
ax.set_ylim(-34, 34)
ax.set_xlabel("Re(s)")
ax.set_ylabel("Im(s)")
ax.set_title("复平面上的 ζ(s)：极点、平凡零点与非平凡零点", fontsize=11.5, color=NAVY, pad=10)
for s in ("top", "right"):
    ax.spines[s].set_visible(False)
fig.tight_layout()
fig.savefig(FIG / "fig2_strip.png", bbox_inches="tight", facecolor="white")
plt.close(fig)

# ---------------------------------------------------------------- fig 3 pi(x), li, R
print("fig3 primes ...", flush=True)
LIM = 1_000_000
sieve = np.ones(LIM + 1, dtype=bool)
sieve[:2] = False
for p in range(2, int(LIM ** 0.5) + 1):
    if sieve[p]:
        sieve[p * p::p] = False
primes = np.flatnonzero(sieve)
xs = primes.astype(float)
pi_vals = np.arange(1, len(primes) + 1, dtype=float)

def riemann_R(x):
    lx = math.log(x)
    total = 1.0
    term = 1.0
    for k in range(1, 80):
        term *= lx / k
        total += term / (k * float(mp.zeta(k + 1)))
    return total

grid = np.unique(np.round(np.logspace(np.log10(3), 6, 260)).astype(int))
li_vals, R_vals = [], []
for x in grid:
    li_vals.append(float(mp.li(x)))
    R_vals.append(riemann_R(x))

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(7.4, 6.6), gridspec_kw={"height_ratios": [1.55, 1]})
ax1.set_xscale("log")
ax1.plot(grid, li_vals, color=WINE, lw=1.5, label=r"$\mathrm{li}(x)$")
ax1.plot(grid, R_vals, color=COPPER, lw=1.5, label=r"$R(x)$（黎曼 R 函数）")
ax1.plot(xs, pi_vals, color=NAVY, lw=1.1, drawstyle="steps-post", label=r"$\pi(x)$（实际素数计数）")
ax1.set_xlim(3, 1e6)
ax1.set_xlabel("x（对数坐标）")
ax1.set_ylabel("计数")
ax1.legend(frameon=False, fontsize=8.5, loc="upper left")
ax1.set_title(r"素数计数 $\pi(x)$ 与两个经典近似", fontsize=11.5, color=NAVY, pad=8)
ax1.grid(alpha=0.18, lw=0.6)

# errors sampled at primes logarithmically
err_li, err_R, err_x = [], [], []
for target in np.logspace(np.log10(10), 6, 90):
    idx = min(np.searchsorted(xs, target), len(xs) - 1)
    x = xs[idx]
    err_li.append(pi_vals[idx] - float(mp.li(x)))
    err_R.append(pi_vals[idx] - riemann_R(x))
    err_x.append(x)
ax2.set_xscale("log")
ax2.axhline(0, color="#8a8f98", lw=0.8)
ax2.plot(err_x, err_li, color=WINE, lw=1.4, marker="o", ms=1.7, label=r"$\pi(x)-\mathrm{li}(x)$")
ax2.plot(err_x, err_R, color=COPPER, lw=1.4, marker="o", ms=1.7, label=r"$\pi(x)-R(x)$")
ax2.set_xlim(10, 1e6)
ax2.set_xlabel("x（对数坐标）")
ax2.set_ylabel("误差")
ax2.legend(frameon=False, fontsize=8.5)
ax2.grid(alpha=0.18, lw=0.6)
ax2.set_title("误差对比：R(x) 显著优于 li(x)", fontsize=10, color=GREY, pad=6)
fig.tight_layout()
fig.savefig(FIG / "fig3_primes.png", bbox_inches="tight", facecolor="white")
plt.close(fig)

# ---------------------------------------------------------------- fig 4 explicit formula
print("fig4 explicit formula ...", flush=True)
XLIM = 60
x_exact = np.arange(2, XLIM + 1, dtype=float)
psi = np.zeros_like(x_exact)
for p in primes[primes <= XLIM]:
    pk = p
    while pk <= XLIM:
        psi[x_exact >= pk] += math.log(p)
        pk *= p

x_dense = np.linspace(2, XLIM, 2400)
def approx(nzeros):
    val = x_dense.astype(complex)
    for g in Z[:nzeros]:
        rho = 0.5 + 1j * g
        val -= 2 * np.real(np.exp(rho * np.log(x_dense)) / rho)
    val -= math.log(2 * math.pi)
    val -= 0.5 * np.log(np.maximum(1 - x_dense ** -2, 1e-12))
    return np.real(val)

fig, ax = plt.subplots(figsize=(7.4, 4.9))
ax.step(x_exact, psi, where="post", color="#c9c2b3", lw=3.2, label=r"$\psi(x)$（精确阶梯函数）", zorder=1)
for n, c in [(0, "#b9b0a0"), (10, "#7f9bb3"), (50, COPPER), (200, WINE)]:
    ax.plot(x_dense, approx(n), lw=1.15 if n else 1.4, color=c,
            label=("仅主项 $x$" if n == 0 else f"用前 {n} 个零点"), zorder=3)
ax.set_xlim(2, XLIM)
ax.set_ylim(-2, 70)
ax.set_xlabel("x")
ax.set_ylabel(r"$\psi(x)$")
ax.set_title(r"显式公式：零点越多，阶梯函数被还原得越精确", fontsize=11.5, color=NAVY, pad=8)
ax.legend(frameon=False, fontsize=8.2, ncol=2, loc="upper left")
ax.grid(alpha=0.15, lw=0.6)
fig.tight_layout()
fig.savefig(FIG / "fig4_explicit.png", bbox_inches="tight", facecolor="white")
plt.close(fig)

# ---------------------------------------------------------------- fig 5 GUE spacing
print("fig5 GUE ...", flush=True)
N = 500
g = np.array(Z[:N])
spac = np.diff(g) * np.log(g[:-1] / (2 * math.pi)) / (2 * math.pi)
spac = spac[spac > 0]
fig, ax = plt.subplots(figsize=(7.0, 4.0))
ax.hist(spac, bins=34, density=True, color="#d9c9a8", edgecolor="white", lw=0.8,
        label="前 500 个零点的归一化间距")
s = np.linspace(0, 3.2, 300)
gue = (32 / math.pi ** 2) * s ** 2 * np.exp(-4 * s ** 2 / math.pi)
ax.plot(s, gue, color=WINE, lw=2.0, label="GUE Wigner  surmise")
ax.set_xlim(0, 3.2)
ax.set_xlabel("归一化间距 s")
ax.set_ylabel("概率密度")
ax.set_title("零点间距的“能级排斥”：随机矩阵理论的指纹", fontsize=11.5, color=NAVY, pad=8)
ax.legend(frameon=False, fontsize=8.5)
ax.grid(alpha=0.15, lw=0.6)
fig.tight_layout()
fig.savefig(FIG / "fig5_gue.png", bbox_inches="tight", facecolor="white")
plt.close(fig)

# ---------------------------------------------------------------- fig 6 long timeline
print("fig6 timeline ...", flush=True)
events = [
    ("1859", "黎曼发表 8 页论文，提出 ζ 函数与零点猜想"),
    ("1896", "Hadamard 与 de la Vallée Poussin 独立证明素数定理"),
    ("1900", "Hilbert 将黎曼猜想列入第 8 问题"),
    ("1914", "Hardy 证明临界线上有无穷多个零点"),
    ("1942", "Selberg 证明临界线上的零点占正比例"),
    ("1972", "Montgomery 提出零点对关联猜想，与 GUE 相遇"),
    ("1974", "Levinson 把临界线比例推进到 1/3"),
    ("1989", "Conrey 证明超过 40.88% 的零点在临界线上"),
    ("2000", "Clay 研究所设立 100 万美元千禧年奖"),
    ("2004", "Gourdon 验证前 10¹³ 个零点"),
    ("2020", "PRZZ 把比例提高到 41.72%"),
    ("2021", "Platt–Trudgian 严格验证到高度 3×10¹²"),
    ("2024", "Guth–Maynard 突破零点密度的 3/4 壁垒"),
    ("2025", "Connes–Consani–Moscovici 构造谱三元组"),
    ("2026", "Alpöge–Claude 形式化证明获 Lean 认证；Masullo 手稿公开"),
]
fig, ax = plt.subplots(figsize=(7.2, 8.6))
ax.set_xlim(0, 1)
ax.set_ylim(-0.6, len(events) - 0.2)
ax.axis("off")
ax.plot([0.115, 0.115], [-0.25, len(events) - 0.55], color="#d8d2c4", lw=2.2, zorder=1)
for i, (year, text) in enumerate(events):
    y = len(events) - 1 - i
    hot = year == "2026"
    ax.scatter([0.115], [y], s=52 if hot else 34, color=WINE if hot else COPPER,
               edgecolor="white", lw=1.2, zorder=3)
    ax.text(0.085, y, year, ha="right", va="center", fontsize=9.5,
            color=WINE if hot else NAVY, fontweight="bold")
    ax.text(0.145, y, text, ha="left", va="center", fontsize=8.8,
            color="#1c2430" if not hot else WINE, wrap=True)
fig.tight_layout()
fig.savefig(FIG / "fig6_timeline.png", bbox_inches="tight", facecolor="white")
plt.close(fig)

# ---------------------------------------------------------------- fig 7 2026 timeline
print("fig7 2026 timeline ...", flush=True)
events26 = [
    ("11-20", "Alpöge 发布 4 页说明与 175,187 个 Lean 文件（约 1700 万行）"),
    ("11-20", "Vakil 以“仓促公告”公开 Masullo 940 页手稿《素数的音乐》"),
    ("11-21", "Lean FRO 与 Mathlib 发表联合声明：形式证明通过四项检验"),
    ("11-21", "学界报告 Masullo 手稿存在关键计算错误与占位章节"),
    ("11-22", "Rubinstein 发布 265 页人类可读解读（第二版）"),
    ("11-23", "Clay 研究所：问题仍列 Active，奖项流程未启动"),
    ("11-25", "Sernau 等发布 7.6 万行压缩版 Lean 证明"),
    ("11-26", "压缩版通过全部六内核复核，Alpöge 原版仍为正式记录"),
]
fig, ax = plt.subplots(figsize=(7.4, 4.6))
ax.set_xlim(0, 1); ax.set_ylim(-0.6, len(events26) - 0.2); ax.axis("off")
ax.plot([0.105, 0.105], [-0.3, len(events26) - 0.55], color="#d8d2c4", lw=2.2)
for i, (d, text) in enumerate(events26):
    y = len(events26) - 1 - i
    hot = i == 2
    ax.scatter([0.105], [y], s=46 if hot else 30, color=WINE if hot else COPPER,
               edgecolor="white", lw=1.1, zorder=3)
    ax.text(0.075, y, d, ha="right", va="center", fontsize=9.0, color=COPPER, fontweight="bold")
    ax.text(0.135, y, text, ha="left", va="center", fontsize=8.6, color="#1c2430")
fig.tight_layout()
fig.savefig(FIG / "fig7_2026.png", bbox_inches="tight", facecolor="white")
plt.close(fig)

# ---------------------------------------------------------------- fig 8 proportion
print("fig8 proportion ...", flush=True)
labels = ["Levinson\n1974", "Conrey\n1989", "Bui–Conrey–Young\n2008", "PRZZ\n2020"]
vals = [33.3, 40.88, 41.05, 41.72]
fig, ax = plt.subplots(figsize=(7.2, 2.9))
bars = ax.barh(range(len(vals)), vals, color=["#c9b48c", "#b8945c", COPPER, WINE], height=0.55)
for i, v in enumerate(vals):
    ax.text(v + 0.7, i, f"{v:.2f}%", va="center", fontsize=9, color=NAVY)
ax.set_yticks(range(len(vals))); ax.set_yticklabels(labels, fontsize=8.6)
ax.set_xlim(0, 50)
ax.set_xlabel("已证明位于临界线上的零点比例（下界）")
ax.set_title("九十年的 incremental progress：比例路线离 100% 仍很遥远", fontsize=10.5, color=NAVY, pad=8)
ax.grid(axis="x", alpha=0.15, lw=0.6)
for s in ("top", "right"):
    ax.spines[s].set_visible(False)
fig.tight_layout()
fig.savefig(FIG / "fig8_proportion.png", bbox_inches="tight", facecolor="white")
plt.close(fig)

print("ALL FIGURES DONE", flush=True)
