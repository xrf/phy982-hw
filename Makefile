help:
	@echo "Targets:"
	@echo "  - all"
	@echo "  - hw1.pdf"
	@echo "  - hw2.pdf"
	@echo "  - clean"

all: hw1.pdf hw2.pdf

# ----------------------------------------------------------------------------

dist/cabal.ok: phy982.cabal Setup.hs
	mkdir -p dist
	touch $@

dist/hw1.dat.ok: hw1.hs Common.hs dist/cabal.ok
	cabal run
	mkdir -p dist
	touch $@

hw1-delta.dat hw1-u.dat: dist/hw1.dat.ok

dist/hw1.svg.ok: hw1.r common.r hw1-delta.dat hw1-u.dat
	./hw1.r
	mkdir -p dist
	touch $@

hw1-delta.svg hw1-u.svg: dist/hw1.svg.ok

hw1-delta.pdf: hw1-delta.svg
	tools/svg2pdf hw1-delta.svg

hw1-u.pdf: hw1-u.svg
	tools/svg2pdf hw1-u.svg

hw1.pdf: hw1.tex common.tex hw1-delta.pdf hw1-u.pdf
	tools/texc hw1 common.tex hw1-*.pdf

# ----------------------------------------------------------------------------

dist/hw2.in.ok: hw2.py common.py
	mkdir -p hw2
	./hw2.py generate_inputs
	mkdir -p dist
	touch $@

hw2-Ni60-p-elastic-high-16.out: dist/hw2.in.ok
	mkdir -p dist/tmp
	( rm -r dist/tmp && mkdir -p dist/tmp && \
          cd dist/tmp && ../../tools/fresco ) \
	  <hw2-Ni60-p-elastic-high.in
	cp dist/tmp/fort.16 $@

hw2-Ni60-p-elastic-low-16.out: dist/hw2.in.ok
	mkdir -p dist/tmp
	( rm -r dist/tmp && mkdir -p dist/tmp && \
          cd dist/tmp && ../../tools/fresco ) \
	  <hw2-Ni60-p-elastic-low.in
	cp dist/tmp/fort.16 $@

hw2-Ni60-n-elastic-high-16.out: dist/hw2.in.ok
	mkdir -p dist/tmp
	( rm -r dist/tmp && mkdir -p dist/tmp && \
          cd dist/tmp && ../../tools/fresco ) \
	  <hw2-Ni60-n-elastic-high.in
	cp dist/tmp/fort.16 $@

hw2-Ni60-n-elastic-low-16.out: dist/hw2.in.ok
	mkdir -p dist/tmp
	( rm -r dist/tmp && mkdir -p dist/tmp && \
          cd dist/tmp && ../../tools/fresco ) \
	  <hw2-Ni60-n-elastic-low.in
	cp dist/tmp/fort.16 $@

hw2-Ni60-p-elastic-low.dat:  hw2-Ni60-p-elastic-low-16.out
	./hw2.py extract_rdcr hw2-Ni60-p-elastic-low-16.out $@

hw2-Ni60-p-elastic-high.dat: hw2-Ni60-p-elastic-high-16.out
	./hw2.py extract_rdcr hw2-Ni60-p-elastic-high-16.out $@

hw2-Ni60-n-elastic-low.dat:  hw2-Ni60-n-elastic-low-16.out
	./hw2.py extract_rdcr hw2-Ni60-n-elastic-low-16.out $@

hw2-Ni60-n-elastic-high.dat: hw2-Ni60-n-elastic-high-16.out
	./hw2.py extract_rdcr hw2-Ni60-n-elastic-high-16.out $@

hw2-expt-data.dat: hw2-expt-data.py common.py hw2.py
	./hw2-expt-data.py

dist/hw2.svg.ok: \
    hw2.r \
    common.r \
    hw2-expt-data.dat \
    hw2-Ni60-p-elastic-low.dat \
    hw2-Ni60-p-elastic-high.dat \
    hw2-Ni60-n-elastic-low.dat \
    hw2-Ni60-n-elastic-high.dat
	./hw2.r
	mkdir -p dist
	touch $@

hw2-1.pdf: dist/hw2.svg.ok
	tools/svg2pdf hw2-1.svg

hw2.pdf: hw2.tex common.tex hw2-1.pdf
	tools/texc hw2 common.tex hw2-*.pdf

# ----------------------------------------------------------------------------

clean:
	rm -f hw?.aux hw?.bib hw?.blg hw?.log hw?.out hw?.pdf hw?.thm \
	      hw?.toc hw?Notes.bib Rplots.pdf
	cabal clean
