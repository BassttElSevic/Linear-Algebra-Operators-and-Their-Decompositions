#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
md2tex.py —— 把 Markdown 讲义转换成 LaTeX 教材源码。

用法:
    python3 tools/md2tex.py <讲义.md> <输出目录 tex/>

生成:
    tex/body.tex              —— 只包含 \\part 与 \\input
    tex/chapters/chNN.tex     —— 每章一个文件
    tex/chapters/partN.tex    —— 每一"部分"的标题页与导读

转换约定
---------
* ``#``   顶层标题 = 一章（三个"部分"标题除外，见 PART_TITLES）
* ``##``  = 一节；若标题在 CLASSIFY 中登记，则整节正文被包进
           定义 / 定理 / 命题 彩色盒子
* ``###`` = 一小节；"证明思路""理解"之类改为专用盒子；
           若其父节已经变成盒子，则提升为 \\section 以免编号混乱
* ``> …``  = 要点盒子（jinsight）
* ``$$…$$``= 行间公式 \\[ … \\]
"""

from __future__ import annotations

import os
import re
import sys

# --------------------------------------------------------------------------
# 结构：哪些一级标题是"部分"（\part），哪些是绪论
# --------------------------------------------------------------------------

INTRO_TITLE = "算子与它的分解"

PART_TITLES = [
    "一般实向量空间与复向量空间上的算子分解",
    "内积空间上的算子及其分解",
    "对于更一般的线性映射的分解",
]

# --------------------------------------------------------------------------
# 语义分类：标题 -> 盒子种类
#   defn 定义 / thm 定理 / prop 命题
# --------------------------------------------------------------------------

CLASSIFY: dict[str, str] = {
    # ---------------- 定义 ----------------
    "算子": "defn",
    "不变子空间": "defn",
    "限制算子": "defn",
    "商算子": "defn",
    "特征值与特征向量": "defn",
    "特征空间": "defn",
    "算子多项式的定义": "defn",
    "特征多项式": "defn",
    "代数重数与几何重数": "defn",
    "最小多项式": "defn",
    "对角化的定义": "defn",
    "幂零算子": "defn",
    "广义特征向量": "defn",
    "广义特征空间": "defn",
    "Jordan 链": "defn",
    "Jordan 块": "defn",
    "复化空间": "defn",
    "伴随算子的定义": "defn",
    "自伴算子的定义": "defn",
    "正规算子的定义": "defn",
    "正算子的定义": "defn",
    "等距映射": "defn",
    "等距同构": "defn",
    "绝对值算子": "defn",
    # ---------------- 定理 ----------------
    "代数基本定理": "thm",
    "复向量空间上的算子一定存在特征值": "thm",
    "Cayley-Hamilton 定理": "thm",
    "上三角化定理": "thm",
    "舒尔定理": "thm",
    "Fitting 分解定理": "thm",
    "不同特征值的广义特征空间直和": "thm",
    "Jordan 链基存在定理": "thm",
    "Jordan 标准型定理": "thm",
    "复谱定理": "thm",
    "实谱定理": "thm",
    "正平方根": "thm",
    "极分解定理": "thm",
    "奇异值分解定理": "thm",
    # ---------------- 命题 ----------------
    "不同特征值对应的特征向量线性无关": "prop",
    "算子多项式的乘法": "prop",
    "多项式算子的核和值域是不变子空间": "prop",
    "特征值与特征多项式": "prop",
    "最小多项式的性质": "prop",
    "上三角矩阵的可逆性": "prop",
    "上三角矩阵的特征值": "prop",
    "零空间链递增": "prop",
    "零空间链稳定": "prop",
    "有限维空间中的稳定性": "prop",
    "幂零算子的幂": "prop",
    "单条 Jordan 链中的向量线性无关": "prop",
    "Jordan 标准型与对角化": "prop",
    "共轭特征值": "prop",
    "伴随算子的存在与唯一性": "prop",
    "伴随的代数性质": "prop",
    "伴随的零空间": "prop",
    "伴随的值域": "prop",
    "规范正交基下的共轭转置": "prop",
    "自伴算子的基本性质": "prop",
    "自伴算子的特征值是实数": "prop",
    "复内积空间中自伴的刻画": "prop",
    "复内积空间中的零二次型结论": "prop",
    "正规算子的范数刻画": "prop",
    "正规算子的特征向量也是伴随的特征向量": "prop",
    "不同特征值对应的特征向量正交": "prop",
    "一个二次算子可逆": "prop",
    "实自伴算子一定有实特征值": "prop",
    "自伴算子与不变子空间": "prop",
    "限制算子仍然自伴": "prop",
    "正算子的谱刻画": "prop",
    "等距同构与伴随": "prop",
    "非零奇异值对应的输出方向": "prop",
    "零奇异值与零空间": "prop",
}

ENV_OF_KIND = {"defn": "jdefn", "thm": "jthm", "prop": "jprop"}

# 这些标题变成"证明思路"盒子
PROOF_PAT = re.compile(r"证明思路|^证明$")
# 这些标题变成"理解"盒子
IDEA_TITLES = {"理解", "直观理解", "构造的目标"}

TEX_SPECIAL = {
    "\\": r"\textbackslash{}",
    "{": r"\{",
    "}": r"\}",
    "%": r"\%",
    "&": r"\&",
    "#": r"\#",
    "_": r"\_",
    "~": r"\textasciitilde{}",
    "^": r"\textasciicircum{}",
}


# --------------------------------------------------------------------------
# 小工具
# --------------------------------------------------------------------------

def is_cjk(ch: str) -> bool:
    """是否是中日韩文字或全角标点。"""
    o = ord(ch)
    return (
        0x2E80 <= o <= 0x9FFF
        or 0xF900 <= o <= 0xFAFF
        or 0xFF00 <= o <= 0xFFEF
        or ch in "“”‘’—…·"
    )


def esc(text: str) -> str:
    """转义正文中的 TeX 特殊字符，行内公式 $…$ 原样保留。"""
    parts = re.split(r"(\$[^$]*\$)", text)
    for i, part in enumerate(parts):
        if i % 2 == 1:  # 数学
            continue
        parts[i] = "".join(TEX_SPECIAL.get(c, c) for c in part)
    return "".join(parts)


def join_lines(lines: list[str]) -> str:
    """把硬换行的一段中文拼回一行：中文之间不加空格，涉及西文时加空格。"""
    out = ""
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if not out:
            out = line
            continue
        if is_cjk(out[-1]) and is_cjk(line[0]):
            out += line
        else:
            out += " " + line
    return out


def read_text(path: str) -> str:
    """读取 UTF-8 文本文件；失败时给出清晰的错误信息。"""
    try:
        with open(path, encoding="utf-8") as fh:
            return fh.read()
    except OSError as err:
        raise SystemExit("无法读取 %s：%s" % (path, err)) from err
    except UnicodeDecodeError as err:
        raise SystemExit("%s 不是 UTF-8 文本：%s" % (path, err)) from err


def write_text(path: str, content: str) -> None:
    """写出 UTF-8 文本文件；失败时给出清晰的错误信息。"""
    try:
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(content)
    except OSError as err:
        raise SystemExit("无法写入 %s：%s" % (path, err)) from err


def plain(title: str) -> str:
    """给目录 / PDF 书签用的纯文本标题（去掉数学符号）。"""
    t = re.sub(r"\$([^$]*)\$", r"\1", title)
    t = t.replace("\\", "").replace("{", "").replace("}", "")
    t = t.replace("^", "").replace("_", "")
    return re.sub(r"\s+", " ", t).strip()


def heading_args(title: str) -> str:
    """若标题含公式，输出 [纯文本]{原标题}，否则只输出 {标题}。"""
    if "$" in title:
        return "[%s]{%s}" % (plain(title), esc(title))
    return "{%s}" % esc(title)


# --------------------------------------------------------------------------
# 正文块渲染
# --------------------------------------------------------------------------

LIST_RE = re.compile(r"^(\s*)([-*]|\d+[.)])\s+(.*)$")
HRULE_RE = re.compile(r"^\s*(---+|\*\*\*+)\s*$")


def read_display_math(lines: list[str], i: int) -> tuple[list[str], int]:
    """读取 $$ … $$ 行间公式，返回 (tex 行, 新下标)。"""
    first = lines[i].strip()
    if first != "$$" and first.endswith("$$") and len(first) > 4:
        body = [first[2:-2].strip()]
        i += 1
    else:
        body = []
        i += 1  # 跳过开头的 $$
        while i < len(lines) and lines[i].strip() != "$$":
            if lines[i].strip():
                body.append(lines[i].rstrip())
            i += 1
        i += 1  # 跳过结尾的 $$
    return [r"\[", *body, r"\]", ""], i


def parse_list(lines: list[str], i: int) -> tuple[list[list[str]], bool, int]:
    """读取一个列表块，返回 (每项的原始行, 是否有序, 新下标)。"""
    ordered = bool(re.match(r"^\s*\d+[.)]\s", lines[i]))
    items: list[list[str]] = []
    while i < len(lines):
        m = LIST_RE.match(lines[i])
        if m:
            items.append([m.group(3).rstrip()])
            i += 1
            continue
        if not items:
            break
        stripped = lines[i].strip()
        if stripped == "":
            # 空行：往后看下一个非空行，它要么是同级列表项，要么是缩进的续行
            j = i + 1
            while j < len(lines) and not lines[j].strip():
                j += 1
            if j < len(lines) and (
                LIST_RE.match(lines[j]) or re.match(r"^\s{2,}\S", lines[j])
            ):
                items[-1].append("")
                i += 1
                continue
            break
        if re.match(r"^\s{2,}\S", lines[i]):
            items[-1].append(stripped)
            i += 1
            continue
        break
    return items, ordered, i


def render(lines: list[str]) -> list[str]:
    """把一段 Markdown 正文（不含标题）渲染为 LaTeX 行。"""
    out: list[str] = []
    i, n = 0, len(lines)
    while i < n:
        line = lines[i]
        if not line.strip():
            i += 1
            continue
        if HRULE_RE.match(line):
            i += 1
            continue
        if line.strip().startswith("$$"):
            block, i = read_display_math(lines, i)
            out.extend(block)
            continue
        if line.lstrip().startswith(">"):
            quote: list[str] = []
            while i < n and (
                lines[i].lstrip().startswith(">") or
                (not lines[i].strip() and i + 1 < n and lines[i + 1].lstrip().startswith(">"))
            ):
                if lines[i].strip():
                    quote.append(lines[i].lstrip()[1:].strip())
                i += 1
            out.append(r"\begin{jinsight}")
            out.extend(render(quote))
            out.append(r"\end{jinsight}")
            out.append("")
            continue
        if LIST_RE.match(line):
            items, ordered, i = parse_list(lines, i)
            env = "jenum" if ordered else "jitem"
            out.append(r"\begin{%s}" % env)
            for item in items:
                out.append(r"\item %")
                out.extend(render(item))
            out.append(r"\end{%s}" % env)
            out.append("")
            continue
        para: list[str] = []
        while i < n:
            cur = lines[i]
            if (
                not cur.strip()
                or cur.strip().startswith("$$")
                or cur.lstrip().startswith(">")
                or LIST_RE.match(cur)
                or HRULE_RE.match(cur)
            ):
                break
            para.append(cur)
            i += 1
        out.append(esc(join_lines(para)))
        out.append("")
    # 去掉尾部多余空行
    while out and out[-1] == "":
        out.pop()
    return out


# --------------------------------------------------------------------------
# Markdown -> 节点树
# --------------------------------------------------------------------------

class Node:
    def __init__(self, level: int, title: str):
        self.level = level
        self.title = title
        self.body: list[str] = []

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Node h{self.level} {self.title!r} {len(self.body)} lines>"


def parse_markdown(text: str) -> list[Node]:
    # 去掉 GRAPH_PARAMS / LINKS 头部元数据
    text = re.sub(r"<!--\s*GRAPH_PARAMS\s*-->.*?<!--\s*END_GRAPH_PARAMS\s*-->", "", text, flags=re.S)
    text = re.sub(r"<!--\s*LINKS\s*-->.*?<!--\s*END_LINKS\s*-->", "", text, flags=re.S)
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)

    nodes: list[Node] = []
    for raw in text.split("\n"):
        m = re.match(r"^(#{1,6})\s+(.*?)\s*$", raw)
        if m:
            nodes.append(Node(len(m.group(1)), m.group(2)))
        elif nodes:
            nodes[0 if False else -1].body.append(raw)
    return nodes


# --------------------------------------------------------------------------
# 生成器
# --------------------------------------------------------------------------

class Builder:
    def __init__(self, outdir: str):
        self.outdir = outdir
        self.chapdir = os.path.join(outdir, "chapters")
        try:
            os.makedirs(self.chapdir, exist_ok=True)
        except OSError as err:
            raise SystemExit("无法创建输出目录 %s：%s" % (self.chapdir, err)) from err
        self.body: list[str] = []          # body.tex
        self.cur: list[str] | None = None   # 当前章缓冲
        self.chap_index = 0
        self.part_index = 0
        self.box_count = 0
        self.parent_boxed = False
        self.unnumbered = False      # 绘论章：节不编号
        self.files: list[str] = []
        self.stats = {"chapter": 0, "part": 0, "defn": 0, "thm": 0, "prop": 0,
                      "proof": 0, "idea": 0, "section": 0, "subsection": 0}

    # -------------------------------------------------- 文件
    def flush(self) -> None:
        if self.cur is None:
            return
        name = self.files[-1]
        write_text(os.path.join(self.chapdir, name), "\n".join(self.cur).rstrip() + "\n")
        self.cur = None

    def open_file(self, name: str, header: str) -> None:
        self.flush()
        self.files.append(name)
        self.cur = ["%% " + header, "%% 本文件由 tools/md2tex.py 自动生成，请勿直接编辑。", ""]
        self.body.append(r"\input{chapters/%s}" % name[:-4])

    def w(self, *lines: str) -> None:
        if self.cur is None:
            raise SystemExit("内部错误：还没有打开章节文件就写入内容")
        self.cur.extend(lines)

    # -------------------------------------------------- 结构
    def add_part(self, node: Node) -> None:
        self.part_index += 1
        self.open_file("part%d.tex" % self.part_index, "第 %d 部分：%s" % (self.part_index, node.title))
        self.w(r"\part%s" % heading_args(node.title), "")
        self.stats["part"] += 1

    def add_part_intro(self, node: Node) -> None:
        self.w(r"\thispagestyle{plain}")
        self.w(r"\begin{partintro}{%s}" % esc(node.title))
        self.w(*render(node.body))
        self.w(r"\end{partintro}", "")

    def add_intro_chapter(self, node: Node) -> None:
        self.chap_index += 1
        self.open_file("ch%02d.tex" % self.chap_index, "绪论：" + node.title)
        self.w(r"\chapter*{绪论\quad %s}" % esc(node.title))
        self.w(r"\addcontentsline{toc}{chapter}{绪论\quad %s}" % plain(node.title))
        self.w(r"\markboth{绪论}{绪论}", "")
        self.w(*render(node.body))
        self.w("")
        self.stats["chapter"] += 1
        self.unnumbered = True

    def add_chapter(self, node: Node) -> None:
        self.chap_index += 1
        self.open_file("ch%02d.tex" % self.chap_index, "第 %d 章：%s" % (self.chap_index - 1, node.title))
        self.w(r"\chapter%s" % heading_args(node.title), "")
        if node.body:
            self.w(*render(node.body))
            self.w("")
        self.stats["chapter"] += 1

    def add_box(self, kind: str, node: Node) -> bool:
        """把一节正文装进彩色盒子；返回是否真的生成了盒子。"""
        rendered = render(node.body)
        if not rendered:
            # 正文为空（结论就写在标题里）：不做盒子，避免空框
            self.add_section(node, "section")
            return False
        self.box_count += 1
        env = ENV_OF_KIND[kind]
        label = "r:%d:%d" % (self.chap_index, self.box_count)
        self.w(r"\begin{%s}{%s}{%s}" % (env, esc(node.title), label))
        self.w(*rendered)
        self.w(r"\end{%s}" % env, "")
        self.stats[kind] += 1
        return True

    def add_proof(self, node: Node) -> None:
        title = node.title if node.title != "证明思路" else "证明思路"
        self.w(r"\begin{jproof}{%s}" % esc(title))
        self.w(*render(node.body))
        self.w(r"\end{jproof}", "")
        self.stats["proof"] += 1

    def add_idea(self, node: Node) -> None:
        self.w(r"\begin{jidea}{%s}" % esc(node.title))
        self.w(*render(node.body))
        self.w(r"\end{jidea}", "")
        self.stats["idea"] += 1

    def add_section(self, node: Node, level: str) -> None:
        if self.unnumbered:
            # 绘论里的节不带编号（否则会变成 0.1、0.2 ……）
            self.w(r"\%s*%s" % (level, "{%s}" % esc(node.title)))
            self.w(r"\addcontentsline{toc}{%s}{%s}" % (level, plain(node.title)), "")
        else:
            self.w(r"\%s%s" % (level, heading_args(node.title)), "")
        self.w(*render(node.body))
        self.w("")
        self.stats[level] += 1

    # -------------------------------------------------- 主循环
    def run(self, nodes: list[Node]) -> None:
        in_part = False
        for node in nodes:
            if node.level == 1:
                self.box_count = 0
                self.parent_boxed = False
                if node.title == INTRO_TITLE:
                    self.add_intro_chapter(node)
                    in_part = False
                elif node.title in PART_TITLES:
                    self.unnumbered = False
                    self.add_part(node)
                    in_part = True
                else:
                    self.unnumbered = False
                    self.add_chapter(node)
                    in_part = False
                continue

            if node.level == 2:
                if in_part:            # \part 之后的唯一一节 = 导读
                    self.add_part_intro(node)
                    continue
                kind = CLASSIFY.get(node.title)
                if PROOF_PAT.search(node.title):
                    self.add_proof(node)
                    self.parent_boxed = True
                elif kind:
                    self.parent_boxed = self.add_box(kind, node)
                else:
                    self.add_section(node, "section")
                    self.parent_boxed = False
                continue

            if node.level >= 3:
                in_part = False
                if PROOF_PAT.search(node.title):
                    self.add_proof(node)
                elif node.title in IDEA_TITLES:
                    self.add_idea(node)
                elif self.parent_boxed:
                    # 父节已成盒子，提升一级，避免编号错乱
                    self.add_section(node, "section")
                    self.parent_boxed = False
                else:
                    self.add_section(node, "subsection")
        self.flush()

    def write_body(self) -> None:
        head = [
            "%% body.tex —— 全书骨架（由 tools/md2tex.py 自动生成）",
            "",
        ]
        write_text(os.path.join(self.outdir, "body.tex"), "\n".join(head + self.body) + "\n")


def main() -> int:
    if len(sys.argv) != 3:
        print(__doc__)
        return 2
    src, outdir = sys.argv[1], sys.argv[2]
    nodes = parse_markdown(read_text(src))
    builder = Builder(outdir)
    builder.run(nodes)
    builder.write_body()
    print("已转换 %s" % src)
    for key, val in builder.stats.items():
        print("  %-12s %d" % (key, val))
    print("  输出          %s" % os.path.join(outdir, "chapters"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
