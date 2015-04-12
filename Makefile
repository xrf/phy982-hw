.POSIX:
.SUFFIXES:
.SUFFIXES: .pdf .svg

help:
	@echo "Targets:"
	@echo "  - all"
	@echo "  - hw1.pdf"
	@echo "  - hw2.pdf"
	@echo "  - clean"

all: hw1.pdf hw2.pdf

clean:
	rm -f hw?.aux hw?.bib hw?.blg hw?.log hw?.out hw?.pdf hw?.thm \
	      hw?.toc hw?Notes.bib Rplots.pdf
	cabal clean

.svg.pdf: tools/svg2pdf
	tools/svg2pdf $<

# ----------------------------------------------------------------------------

dist/hw1.dat.ok: hw1.hs Common.hs phy982.cabal Setup.hs
	cabal run
	mkdir -p dist
	touch $@

hw1-delta.dat hw1-u.dat: dist/hw1.dat.ok
	touch $@

dist/hw1.svg.ok: hw1.r common.r hw1-delta.dat hw1-u.dat
	./hw1.r
	mkdir -p dist
	touch $@

hw1-delta.svg hw1-u.svg: dist/hw1.svg.ok
	touch $@

hw1.pdf: hw1.tex common.tex hw1-delta.pdf hw1-u.pdf
	tools/texc $(@:.pdf=) common.tex $(@:.pdf=)-*.pdf

# ----------------------------------------------------------------------------

dist/hw2.ok: hw2.py common.py
	mkdir -p dist
	./hw2.py do_runs
	touch $@

hw2-1.dat \
hw2-1-large-radius.dat \
hw2-Ni60-p-elastic-low-both.svg \
hw2-Ni60-p-elastic-low-spinorb.svg \
hw2-Ni60-p-elastic-low-surf-im.svg \
hw2-Ni60-p-elastic-low-vol-re.svg: dist/hw2.ok
	touch $@

hw2-1.svg: hw2-1.dat hw2.r common.r
	./hw2.r $(@:.svg=)

hw2-1-large-radius.svg: hw2-1.dat hw2.r common.r
	./hw2.r $(@:.svg=)

hw2.pdf: \
    hw2.tex \
    common.tex \
    hw2-1.pdf \
    hw2-1-large-radius.pdf \
    hw2-Ni60-p-elastic-low-both.pdf \
    hw2-Ni60-p-elastic-low-spinorb.pdf \
    hw2-Ni60-p-elastic-low-surf-im.pdf \
    hw2-Ni60-p-elastic-low-vol-re.pdf \
    hw2-p60Ni-OMP108-Smat.pdf
	tools/texc $(@:.pdf=) common.tex $(@:.pdf=)-*.pdf

# ----------------------------------------------------------------------------

hw3.pdf: hw3.tex common.tex
	tools/texc $(@:.pdf=) common.tex $(@:.pdf=)-*.pdf
