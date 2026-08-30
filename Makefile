# ==========================================================================
#  《线性代数：抽象结构 —— 算子及其分解》构建脚本
#
#    make            转换 Markdown 并编译出 PDF
#    make tex        只做 Markdown -> LaTeX 转换
#    make pdf        只编译（假定 tex/ 已经是最新的）
#    make clean      删除编译中间文件
#    make distclean  额外删除自动生成的 tex/chapters 与 output/
# ==========================================================================

MD       := 线性代数-抽象结构-算子及其分解.md
TEXDIR   := tex
MAIN     := main
OUTDIR   := output
PDFNAME  := 线性代数-算子及其分解.pdf
CONVERT  := tools/md2tex.py
XELATEX  := xelatex -interaction=nonstopmode -halt-on-error

.PHONY: all tex pdf clean distclean stats

all: pdf

# ---- Markdown -> LaTeX ---------------------------------------------------
tex: $(TEXDIR)/body.tex

$(TEXDIR)/body.tex: $(MD) $(CONVERT)
	python3 $(CONVERT) $(MD) $(TEXDIR)

# ---- LaTeX -> PDF（三遍：目录、交叉引用、定理一览）----------------------
pdf: tex
	cd $(TEXDIR) && $(XELATEX) $(MAIN).tex >/dev/null
	cd $(TEXDIR) && $(XELATEX) $(MAIN).tex >/dev/null
	cd $(TEXDIR) && $(XELATEX) $(MAIN).tex | tail -n 3
	@mkdir -p $(OUTDIR)
	@cp $(TEXDIR)/$(MAIN).pdf "$(OUTDIR)/$(PDFNAME)"
	@printf '==> %s (%s 页)\n' "$(OUTDIR)/$(PDFNAME)" \
	  "$$(pdfinfo '$(TEXDIR)/$(MAIN).pdf' | awk '/Pages/{print $$2}')"

# ---- 检查排版警告 -------------------------------------------------------
stats:
	@echo "溢出行 (Overfull/Underfull):"
	@grep -cE 'Overfull|Underfull' $(TEXDIR)/$(MAIN).log || true
	@echo "未定义引用:"
	@grep -c 'undefined' $(TEXDIR)/$(MAIN).log || true

clean:
	cd $(TEXDIR) && rm -f ./*.aux ./*.log ./*.out ./*.toc ./*.fls ./*.fdb_latexmk \
	    ./*.synctex.gz ./*.jdeflist ./*.jthmlist ./*.jproplist ./*.lol
	rm -f $(TEXDIR)/$(MAIN).pdf

distclean: clean
	rm -rf $(TEXDIR)/chapters $(TEXDIR)/body.tex $(OUTDIR)
