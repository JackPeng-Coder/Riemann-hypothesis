# 黎曼猜想全景报告

> 从 1859 年的八页论文，到 2026 年的形式化证明。

**[📄 下载 PDF：黎曼猜想全景报告](./黎曼猜想全景报告.pdf)**

---

## 关于本报告

这是一份中文综合研究报告，试图回答三个问题：

1. 黎曼猜想究竟说了什么？
2. 一百六十七年来，人类走到了哪一步？
3. 2026 年 11 月那两份“证明”到底意味着什么？

报告共 **49 页**，含 **8 幅自制图表**、**50 条参考文献**，覆盖从 ζ 函数的基本定义、六种等价形式、167 年攻坚史，到 Guth–Maynard 零点密度、Connes–Consani–Moscovici 谱三元组，以及 2026 年 11 月 Alpöge–Claude 形式化证明事件的完整记录。

## 目录

| 章节 | 内容 |
|---|---|
| 摘要 | 一页速览、关键事实表 |
| 第 1 章 | 引子：素数之谜与黎曼的八页论文 |
| 第 2 章 | 数学基础：ζ 函数、函数方程、临界线、显式公式 |
| 第 3 章 | 精确陈述与六种等价形式（Mertens、Li、Weil、Nyman–Beurling、Lagarias 等） |
| 第 4 章 | 为什么重要：素数定理误差、素数间隙、算术级数、算法与密码学 |
| 第 5 章 | 167 年攻坚史：从 Hadamard 到 Conrey，再到 Guth–Maynard |
| 第 6 章 | 谱解释与随机矩阵：Hilbert–Pólya、Montgomery–Dyson、Berry–Keating、Connes |
| 第 7 章 | 函数域上的成功：Weil、Deligne，以及 \(\mathbb{F}_1\) 几何 |
| 第 8 章 | 数值验证：从手算到 \(3\times10^{12}\) 高度 |
| 第 9 章 | 2024–2025 前沿：Guth–Maynard 与 CCM 谱三元组 |
| 第 10 章 | **2026：一天之内的两份证明**（Alpöge–Claude、Lean 认证、Masullo 手稿） |
| 第 11–13 章 | 如果成立、如果不成立、十个常见误解 |
| 附录 A–D | 前 50 个零点、公式速查、167 年时间线、参考文献与验证资源 |

## 2026 年 11 月：报告的核心更新

- **2026-11-20**：Anthropic 的 Levent Alpöge 发布 4 页说明与 14 个压缩包，内含 **175,187 个 Lean 文件、约 1700 万行代码**，声称证明黎曼猜想及 Dirichlet L 函数上的广义黎曼猜想。
- **2026-11-21**：**Lean FRO 与 Mathlib Initiative 联合认证**，确认陈述正确、代码可编译、证明的正是标准陈述，并通过 Lean 官方内核、nanoda、con-leche、con-ron 等多个独立内核。
- **2026-11-25/26**：Luke Sernau 等发布约 **7.6 万行压缩版**，794 个模块通过六个内核复核。
- **同日**：Ravi Vakil 公开 Alessandro Masullo 耗时约十二年、**940 页**的纯人工手稿《素数的音乐》；约八小时后即有数学家报告关键计算错误、无效推论与占位章节。
- **Clay 状态**：截至 2026-11-26 仍列为 **Active**；奖项要求正式发表、至少两年审查与广泛接受，流程尚未启动。

> **重要区分**：形式证明通过机器检验 ≠ 人类已经理解并接受 ≠ Clay 千禧年奖已经颁发。本报告对三者做了明确区分，详见第 10 章。

## 技术栈与复现

报告由 HTML/CSS 排版，MathJax 渲染公式，Playwright 调用系统 Edge 打印为 PDF，matplotlib 生成图表，pypdf 合并封面并写入书签。

```
build/
├── src/             # 16 个 HTML 章节片段
├── figs/            # 8 幅图表（PNG）
├── style.css        # 版式
├── cover.html       # 封面
├── build.py         # 两遍排版、目录页码、合并、书签
├── make_figs.py     # 全部图表
├── fix_figs.py      # 局部图表重绘
└── zeros.json       # 前 520 个零点缓存
```

环境：Python 3.12、Windows、Microsoft Edge。

```bash
python -m pip install matplotlib numpy mpmath playwright pypdf pypdfium2
python build/make_figs.py
python build/build.py
```

生成的 PDF 位于仓库根目录。MathJax 通过 CDN 加载，构建时需要网络。

## 主要参考来源

- Riemann, B. (1859). *Über die Anzahl der Primzahlen unter einer gegebenen Größe*.
- Edwards, Titchmarsh–Heath-Brown, Iwaniec–Kowalski, Montgomery–Vaughan 等标准教材.
- Guth, L. & Maynard, J. (2024). *New large value estimates for Dirichlet polynomials*. arXiv:2405.20552.
- Connes, A., Consani, C. & Moscovici, H. (2025). *Zeta Spectral Triples*. arXiv:2511.22755.
- Lean FRO & Mathlib Initiative (2026). *Lean verification of the Riemann Hypothesis*.
- Rubinstein, M. (2026). *The Alpöge–Claude proof of the Riemann hypothesis explained for the Riemann zeta function* (v2).
- Sutherland, A. (2026). *RH Lean proof, verification files*.
- Vakil, R. (2026). *Hurried announcement: Alessandro Masullo, GRH*.
- Nielsen, J. L. (2026). *Invalidity of Masullo's Proof of the Riemann Hypothesis*.
- Castelvecchi, D. (2026). *Nature*; Howlett, J. (2026). *Scientific American*.

完整 50 条参考文献与可复现资源链接见报告附录 D。

## 免责声明

本报告是独立综合整理，不是同行评审论文。2026 年 11 月的事件仍在快速演进；关于 Alpöge–Claude 证明的人类可读化、Masullo 手稿的修订、Clay 奖的最终状态，均可能变化。请以报告附录 D 列出的原始资源为准。

---

**版本**：2026-11-26 · 第一版  
**作者**：OpenCode 综合研究报告
