# 线性代数：抽象结构 —— 算子及其分解



> 一本讲「有限维向量空间上的**算子**如何被分解」的自编教材。
> Markdown 写内容，Python 脚本转成 LaTeX，XeLaTeX 排成 117 页的 PDF。

| | | |
| --- | --- | --- |
| 撰写（一作） | **夜航未西飞** · [github.com/Singularity-baakaka](https://github.com/Singularity-baakaka) | <img width="460" height="460" alt="图片" src="https://github.com/user-attachments/assets/50dd6367-40a6-4086-b8ce-ae4a5e34806f" /> |
| 校对、LaTeX 排版（二作） | **阿酒** · Basstt ElSevic · [github.com/BassttElSevic](https://github.com/BassttElSevic) | <img width="500" height="500" alt="图片" src="https://github.com/user-attachments/assets/c5a5ea84-8b31-4641-81b1-cea08a739ba7" /> |
| 成品 | [`output/线性代数-算子及其分解.pdf`](output/) · 117 页 · B5 开本 | |
| 许可 | [MIT](LICENSE)（正文与代码同时适用） | |

---

## 一、这本书是什么

这不是一本从行列式讲起的计算型线性代数书，而是专题讲义：

> 给定一个算子 $T:V\to V$，能不能找到一组好基，把它拆成互不干扰的简单部分？

全书围绕这个问题展开，路线是「先只用线性结构，再加上内积结构，最后放宽到一般线性映射」：

**绪论** 算子为什么值得单独研究：定义域与陪域相同 ⇒ 可以反复作用 ⇒ 描述的是一个系统的长期演化。
分解的共同基础是**不变子空间**与直和。

**第一部分（第 1–15 章）一般实 / 复向量空间上的算子分解**——只用线性结构，不用内积。

* 算子与不变子空间、限制算子与商算子
* 特征值、特征向量、特征空间；算子多项式
* 代数基本定理 ⇒ 复空间上算子必有特征值
* 特征多项式、Cayley–Hamilton 定理、最小多项式
* 上三角化（含 Schur 定理）、对角化
* 幂零算子与零空间链、Fitting 分解
* 广义特征空间与主分解 $V=\bigoplus_\lambda G_\lambda$
* Jordan 链的构造、Jordan 块与 Jordan 标准型
* 实向量空间的复化，以及复特征值如何回落成实二维不变块

**第二部分（第 16–24 章）内积空间上的算子分解**——多了长度、正交与伴随。

* 伴随算子（由 Riesz 表示定理给出）、伴随的零空间与值域、伴随的矩阵
* 自伴算子、正规算子
* 复谱定理与实谱定理（为什么实数情形必须要求自伴而不只是正规）
* 正算子与正平方根、等距同构 / 酉算子 / 正交算子

**第三部分（第 25–26 章）一般线性映射的分解**——不再要求定义域与陪域相同。

* 极分解 $T=U|T|$，$|T|=(T^*T)^{1/2}$
* 奇异值分解：从 $T^*T$ 与 $TT^*$ 两侧分别构造右 / 左奇异向量

书末附**定义、定理与命题三份一览表**（共 24 个定义、14 个定理、34 个命题），
以及 89 条嵌套 PDF 书签。

### 阅读时的颜色约定

知识块统一风格：**满宽饱和色标题条（白字粗体）+ 细同色边框 + 极淡底色 + 圆角**。

| 颜色 | 含义 |
| --- | --- |
| 藏青蓝 `#000080` | 定义 |
| 暗红 `#8B0000` | 定理 |
| 墨绿 `#006B3C` | 命题、性质、刻画 |
| 灰色竖线 `#3F4A5A` | 证明或证明思路，段末有小方块 |
| 靛紫 `#4B0082` | 「理解」——对刚才那段形式化内容的翻译 |
| 琥珀金 `#8A5A00` | 「要点」——一节浓缩成一句话 |
| 藏青蓝大框 | 每一「部分」开头的导读 |

定义、定理、命题在同一章内**共用一套编号**（`定义 12.1`、`定理 12.2`、`命题 12.3`……）。

---

## 二、编译环境

实测环境：Debian + TeX Live 2026 + Python 3.14。只要满足下面的依赖，其他发行版同样可以。

### 必需组件

| 组件 | 用途 | 说明 |
| --- | --- | --- |
| XeLaTeX | 编译引擎 | 必须是 XeLaTeX，pdfLaTeX 不行（中文 + OpenType 数学字体） |
| `ctex` | 中文排版 | 章节名「第一章」、中文标点、行末断行 |
| `tcolorbox` | 全部知识块 | 需要 `most` 选项 + `theorems`/`breakable`/`skins` 库 |
| `unicode-math` | 数学字体 | 配合 Libertinus Math；**不要再加载 `amssymb`**，会和它冲突 |
| `titlesec` / `titletoc` | 章节与目录样式 | |
| `fancyhdr`、`geometry`、`enumitem`、`microtype`、`pifont`、`tikz`、`hyperref`、`bookmark`、`emptypage`、`mathtools` | 版式零件 | |
| Libertinus 字体（OTF） | 西文 + 数学 | `LibertinusSerif/Sans/Mono` + `LibertinusMath-Regular.otf` |
| Noto CJK 字体 | 中文 | 正文 `Noto Serif CJK SC`，标题 `Noto Sans CJK SC` |
| Python ≥ 3.9 | 跑转换脚本 | 只用标准库，无需 pip 安装任何东西 |
| `make`（可选） | 一键构建 | 不装也行，见下面的「不用 make」 |

### 安装

#### Debian / Ubuntu

```bash
sudo apt install texlive-xetex texlive-lang-chinese texlive-latex-extra \
                 texlive-latex-recommended texlive-fonts-extra \
                 fonts-noto-cjk python3 make
```

#### Arch Linux

```bash
sudo pacman -S texlive-xetex texlive-langchinese texlive-latexextra \
               texlive-fontsextra noto-fonts-cjk python make
```

#### macOS

```bash
brew install --cask mactex        # 或 basictex + tlmgr install ctex tcolorbox ...
brew install --cask font-noto-serif-cjk-sc font-noto-sans-cjk-sc
```

#### 通用（TeX Live 网络安装）

`tlmgr install ctex tcolorbox unicode-math titlesec
fancyhdr enumitem microtype pifont pgf hyperref bookmark emptypage mathtools libertinus-fonts`

### 检查环境是否就绪

```bash
xelatex --version                              # 有输出即可
kpsewhich ctex.sty tcolorbox.sty unicode-math.sty
kpsewhich LibertinusSerif-Regular.otf LibertinusMath-Regular.otf
fc-list | grep -c "Noto Serif CJK SC"          # 结果 > 0
python3 --version
```

### 换字体

字体全部集中在 `tex/preamble.tex` 第 2 节。若系统没有 Noto CJK，可改成思源宋体：

```latex
\setCJKmainfont{Source Han Serif SC}
\setCJKsansfont{Source Han Sans SC}
```

---

## 三、怎么编译

### 方式 A：一键（推荐）

```bash
make            # 转换 Markdown → LaTeX，再跑三遍 xelatex，成品拷进 output/
```

其他目标：

```bash
make tex        # 只做 Markdown → LaTeX（只重写 tex/body.tex 与 tex/chapters/）
make pdf        # 只编译（假定 tex/ 已是最新）
make stats      # 数一下 Overfull/Underfull 行与未定义引用
make clean      # 删中间文件（.aux/.log/.toc/.jdeflist…）
make distclean  # 连自动生成的 tex/chapters、tex/body.tex、output/ 一起删
```

### 方式 B：直接用 Python 脚本（不用 make）

转换脚本的用法是 `md2tex.py <讲义.md> <输出目录>`：

```bash
# 第 1 步：Markdown → LaTeX
python3 tools/md2tex.py 线性代数-抽象结构-算子及其分解.md tex

# 它会打印统计并生成：
#   tex/body.tex            全书骨架（\part 与 \input）
#   tex/chapters/ch01..27   每章一个文件
#   tex/chapters/part1..3   三个「部分」的标题页与导读

# 第 2 步：编译三遍
#   第 1 遍生成 .aux/.toc，第 2 遍填目录页码，
#   第 3 遍填书末「定义/定理/命题一览」的页码
cd tex
xelatex -interaction=nonstopmode main.tex
xelatex -interaction=nonstopmode main.tex
xelatex -interaction=nonstopmode main.tex

# 第 3 步：取走成品
mkdir -p ../output && cp main.pdf "../output/线性代数-算子及其分解.pdf"
```

用 `latexmk` 也可以，但因为定理一览表写在自定义的 `.jdeflist` 等文件里，
latexmk 未必能察觉需要重跑，所以 Makefile 里是老老实实跑三遍。

### 编译成功的标志

* `tex/main.log` 里 `grep -cE 'Overfull|Underfull'` 结果为 **0**
* PDF 是 117 页，`pdfinfo` 里 `Author` 显示两位作者
* 书末三份一览表都有页码（不是 `??`）

---

## 四、目录结构

```text
线代教材/
├── 线性代数-抽象结构-算子及其分解.md   ← 唯一的手写正文，改这个文件
├── tools/md2tex.py                     ← Markdown → LaTeX 转换器（纯标准库）
├── tex/
│   ├── main.tex                        ← 手写：扉页、署名、体例说明、目录、书末一览
│   ├── preamble.tex                    ← 手写：页面、字体、配色、章节样式、各种知识块
│   ├── body.tex                        ← 自动生成：\part + \input
│   └── chapters/                       ← 自动生成：27 章 + 3 个部分标题页
├── output/线性代数-算子及其分解.pdf     ← 成品（提交进仓库）
├── Makefile
├── LICENSE                             ← MIT
└── README.md
```

## 五、改东西的正确姿势

`tex/chapters/*.tex` 和 `tex/body.tex` **是自动生成的，不要手改**——下次 `make` 会覆盖掉。

| 想改什么 | 改哪里 |
| --- | --- |
| 数学内容、章节增删 | `线性代数-抽象结构-算子及其分解.md` |
| 颜色、字体、圆角、页眉、目录样式 | `tex/preamble.tex` |
| 扉页（书名、署名、分工）、体例说明页、前后置页 | `tex/main.tex` |
| 「哪些标题算定义 / 定理 / 命题」 | `tools/md2tex.py` 里的 `CLASSIFY` 表 |
| 页面尺寸、页边距 | `tex/preamble.tex` 第 1 节的 `geometry` |

## 六、转换规则

| Markdown 写法 | 排版结果 |
| --- | --- |
| `#` 一级标题 | 一章。三个总览标题排成汉字编号的整页 `\part`；第一个总览排成不编号的「绪论」 |
| `##` 二级标题 | 一节。若标题登记在 `CLASSIFY` 里，整节正文变成**定义 / 定理 / 命题**知识块 |
| `###` 三级标题 | 小节。「证明思路」→ 灰色证明块，「理解」→ 靛紫旁注块；父节若已成知识块则自动提升为 `\section`，避免编号错乱 |
| `> 引用` | 琥珀金**要点**块 |
| `$$ … $$` | 行间公式（支持跨行、`pmatrix` 等） |
| `$ … $` | 行内公式，原样保留 |
| `-` / `1.` | 列表，支持缩进的续行公式 |
| `---` | 忽略（原稿里只是章节分隔） |

标题里带公式时（例如 `## 从 $T^*T$ 出发`），脚本会自动生成纯文本短标题给目录和 PDF 书签用。

## 七、许可

[MIT](LICENSE) © 2026 Singularity-baakaka（夜航未西飞）、Basstt ElSevic（阿酒）。

## Choose Life

<img width="1080" height="723" alt="ChooseLife" src="https://github.com/user-attachments/assets/00d99cb5-e325-4cf0-b4d6-534a428eb9d1" />

正文、LaTeX 模板、转换脚本与编译出的 PDF 都在此许可之下：可以自由使用、修改、
再分发，包括商业用途，只需保留版权声明与许可声明。
