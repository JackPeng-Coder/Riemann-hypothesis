# -*- coding: utf-8 -*-
"""Build the Riemann Hypothesis report PDF: HTML -> Edge print -> merge/bookmarks."""
import io, re, sys, json
from pathlib import Path
from playwright.sync_api import sync_playwright
from pypdf import PdfReader, PdfWriter

BASE = Path(__file__).resolve().parent
ROOT = BASE.parent
SRC = BASE / "src"
OUT = ROOT / "黎曼猜想全景报告.pdf"
BODY_PDF = BASE / "body.pdf"
COVER_PDF = BASE / "cover.pdf"

sys.stdout.reconfigure(encoding="utf-8")

TOC = [
    dict(id="abs",  t="摘要：一页速览",                 en="Executive Summary",        match="这份报告试图回答三个问题", page="1"),
    dict(id="ch01", t="第 1 章　引子：素数之谜",         en="Prime Numbers",            match="素数是数学中最古老的原子"),
    dict(id="ch02", t="第 2 章　数学基础：ζ 函数与临界线", en="The Zeta Function",        match="要理解黎曼猜想，必须先理解"),
    dict(id="ch03", t="第 3 章　精确陈述与等价形式",       en="Equivalent Formulations",  match="黎曼猜想有许多张面孔"),
    dict(id="ch04", t="第 4 章　为什么重要",               en="Why It Matters",           match="一个关于复变函数零点的问题"),
    dict(id="ch05", t="第 5 章　167 年攻坚史",            en="A History of Attacks",     match="从 1859 年到 2023 年"),
    dict(id="ch06", t="第 6 章　谱解释与随机矩阵",         en="Spectra and Random Matrices", match="如果黎曼猜想有一个“物理证明”"),
    dict(id="ch07", t="第 7 章　函数域上的成功",           en="The Function Field Case",  match="在另一条战线上"),
    dict(id="ch08", t="第 8 章　数值验证",                en="Numerical Verification",   match="数学猜想不能靠“数了很多个例子”"),
    dict(id="ch09", t="第 9 章　2024–2025：前沿的两条线",  en="Recent Breakthroughs",     match="在 2026 年那场风暴到来之前"),
    dict(id="ch10", t="第 10 章　2026：一天之内的两份证明",  en="Two Proofs in One Day",    match="数学界从未在二十四小时内经历过如此密集的震动"),
    dict(id="ch11", t="第 11 章　如果黎曼猜想成立",        en="If It Is True",            match="假设黎曼猜想已经被完全证明"),
    dict(id="ch12", t="第 12 章　如果黎曼猜想不成立",      en="If It Is False",           match="反过来说，如果黎曼猜想是假的"),
    dict(id="ch13", t="第 13 章　常见误解与问答",          en="FAQ",                      match="围绕黎曼猜想流传着大量误解"),
    dict(id="appA", t="附录 A　前 50 个非平凡零点",        en="Zeros Table",              match="下表给出前 50 个非平凡零点", app=True),
    dict(id="appB", t="附录 B　关键公式与定理速查",        en="Formula Sheet",            match="本附录把全书出现的关键公式", app=True),
    dict(id="appC", t="附录 C　167 年时间线",             en="Timeline",                 match="1859 年，黎曼在柏林科学院", app=True),
    dict(id="appD", t="附录 D　参考文献与验证资源",        en="References",               match="以下文献按正文引用顺序", app=True),
]

TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<title>黎曼猜想全景报告</title>
<script>
window.MathJax = {
  tex: { inlineMath: [['\\\\(','\\\\)']], displayMath: [['\\\\[','\\\\]']], tags: 'none' },
  svg: { fontCache: 'local' },
  options: { enableMenu: false },
  startup: { typeset: true }
};
</script>
<script src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-svg.js" id="MathJax-script"></script>
<style>
__CSS__
</style>
</head>
<body>
__FRONT__
__TOC__
__CONTENT__
</body>
</html>
"""


def norm(s: str) -> str:
    return re.sub(r"\s+", "", s or "")


def read_fragments():
    files = [f for f in sorted(SRC.glob("*.html")) if f.name != "00_front.html"]
    return "\n".join(f.read_text(encoding="utf-8") for f in files)


def zeros_table():
    data = json.loads((BASE / "zeros.json").read_text(encoding="utf-8"))
    rows = []
    for i in range(25):
        a, b = i, i + 25
        ga = f"{data[a]:.9f}"
        gap_a = "—" if i == 0 else f"{data[a]-data[a-1]:.6f}"
        gb = f"{data[b]:.9f}"
        gap_b = f"{data[b]-data[b-1]:.6f}"
        rows.append(
            f'<tr><td class="c">{a+1}</td><td>{ga}</td><td>{gap_a}</td>'
            f'<td class="c">{b+1}</td><td>{gb}</td></tr>'
        )
    return "\n".join(rows)


def render_toc(pages):
    rows = []
    for e in TOC:
        p = pages.get(e["id"], e.get("page", "00"))
        cls = "app" if e.get("app") else ""
        rows.append(
            f'<li class="{cls}"><span class="t">{e["t"]}</span>'
            f'<span class="cn">{e["en"]}</span><span class="dots"></span>'
            f'<span class="p">{p}</span></li>'
        )
    return (
        '<section class="toc-page">'
        '<div class="toc-title">目　录</div>'
        '<div class="toc-sub">Contents</div>'
        '<ul class="toc">' + "\n".join(rows) + '</ul>'
        '<p class="toc-note">页码为正文页码。第 10 章涉及 2026 年 11 月仍在快速演进的验证与评审进程，'
        '本书信息截至 2026 年 11 月 26 日；引用与链接见附录 D。</p>'
        '</section>'
    )


def build_html(pages=None, out_name="body.html"):
    pages = pages or {}
    front = (SRC / "00_front.html").read_text(encoding="utf-8")
    content = read_fragments().replace("<!--ZEROS50-->", zeros_table())
    html = (TEMPLATE
            .replace("__CSS__", (BASE / "style.css").read_text(encoding="utf-8"))
            .replace("__FRONT__", front)
            .replace("__TOC__", render_toc(pages))
            .replace("__CONTENT__", content))
    p = BASE / out_name
    p.write_text(html, encoding="utf-8")
    return p


def render_body(html_path, pdf_path):
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="msedge", headless=True)
        page = browser.new_page(viewport={"width": 1240, "height": 1754})
        page.goto(html_path.as_uri(), wait_until="networkidle", timeout=180000)
        page.wait_for_function("window.MathJax && MathJax.startup && MathJax.startup.promise", timeout=180000)
        page.evaluate("MathJax.startup.promise")
        page.wait_for_timeout(1200)
        n = page.evaluate("document.querySelectorAll('mjx-container').length")
        print("  math nodes:", n, flush=True)
        page.pdf(
            path=str(pdf_path), format="A4", print_background=True,
            margin={"top": "21mm", "bottom": "19mm", "left": "19mm", "right": "19mm"},
            display_header_footer=True,
            header_template=(
                '<div style="width:100%;padding:0 19mm;font-family:Microsoft YaHei,Arial;'
                'font-size:7px;color:#8a8f98;letter-spacing:.08em;">'
                '<table style="width:100%;border-collapse:collapse;"><tr>'
                '<td style="text-align:left;border-bottom:0.5px solid #ddd6c8;padding-bottom:3px;">'
                '黎曼猜想全景报告</td>'
                '<td style="text-align:right;border-bottom:0.5px solid #ddd6c8;padding-bottom:3px;">'
                'THE RIEMANN HYPOTHESIS · 2026</td></tr></table></div>'
            ),
            footer_template=(
                '<div style="width:100%;text-align:center;font-family:Cambria,serif;'
                'font-size:8px;color:#9a6b2f;">— <span class="pageNumber"></span> —</div>'
            ),
        )
        browser.close()


def render_cover():
    html = BASE / "cover.html"
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="msedge", headless=True)
        page = browser.new_page(viewport={"width": 1240, "height": 1754})
        page.goto(html.as_uri(), wait_until="networkidle", timeout=120000)
        page.wait_for_timeout(800)
        page.pdf(path=str(COVER_PDF), width="210mm", height="297mm",
                 margin={"top": "0", "bottom": "0", "left": "0", "right": "0"},
                 print_background=True, prefer_css_page_size=True,
                 display_header_footer=False)
        browser.close()


def locate_pages():
    reader = PdfReader(str(BODY_PDF))
    texts = [norm(p.extract_text() or "") for p in reader.pages]
    pages, missing = {}, []
    for e in TOC:
        if e["id"] == "abs":
            pages[e["id"]] = "1"
            continue
        needle = norm(e["match"])
        found = None
        for i, txt in enumerate(texts):
            if needle in txt:
                found = i + 1
                break
        if found:
            pages[e["id"]] = str(found)
        else:
            missing.append((e["id"], needle))
            pages[e["id"]] = "??"
    return pages, missing, len(reader.pages)


def assemble(pages):
    writer = PdfWriter()
    writer.append(str(COVER_PDF))
    writer.append(str(BODY_PDF))
    # bookmarks: merged index == printed body page number (cover occupies index 0)
    for e in TOC:
        if e["id"] == "abs":
            continue
        try:
            idx = int(pages.get(e["id"], "0"))
        except ValueError:
            continue
        if idx > 0:
            writer.add_outline_item(e["t"].replace("　", " "), idx)
    writer.add_metadata({
        "/Title": "黎曼猜想全景报告：从 1859 年的八页论文到 2026 年的形式化证明",
        "/Author": "OpenCode 综合研究报告",
        "/Subject": "黎曼猜想的历史、数学表述、等价形式、数值验证、2024–2026 前沿进展与 AI 形式化证明事件",
        "/Keywords": "黎曼猜想, Riemann Hypothesis, 素数, ζ函数, Lean, Mathlib, Alpöge, Masullo, Guth-Maynard",
        "/Creator": "HTML/CSS + MathJax + Playwright",
    })
    with open(OUT, "wb") as f:
        writer.write(f)


def main():
    print("[1/5] build HTML (placeholder TOC)", flush=True)
    html = build_html({}, "body_pass1.html")
    print("[2/5] render pass 1", flush=True)
    render_body(html, BODY_PDF)
    pages, missing, npages = locate_pages()
    print("  body pages:", npages)
    print("  TOC pages:", {k: v for k, v in pages.items()})
    if missing:
        print("  !! missing anchors:", missing, flush=True)
    print("[3/5] render pass 2 with real page numbers", flush=True)
    html = build_html(pages, "body.html")
    render_body(html, BODY_PDF)
    print("[4/5] render cover", flush=True)
    render_cover()
    print("[5/5] merge + bookmarks", flush=True)
    assemble(pages)
    print("DONE ->", OUT, flush=True)


if __name__ == "__main__":
    main()
