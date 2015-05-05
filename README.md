PHY982 homework
===============

Group homework for [PHY982][1] by Adam Jones and Fei Yuan.

Building
--------

First off, make sure you have all the dependencies listed in the next section.

Then, to build every homework, just run:

    make all

If you only want to build one of them, say HW2, run:

    make hw2.pdf

Dependencies
------------

### Calculations

  - [Glasgow Haskell Compiler (GHC)](https://haskell.org/ghc)
    (required for HW1)

      - [Cabal](https://haskell.org/cabal).

      - Other dependencies can be installed by running this command in the
        project directory:

            cabal install --dependencies-only

  - [Fresco](http://fresco.org.uk)
    (required for HW2)

  - [Python](https://python.org) 3.4+ or 2.7+
    (required for HW2)

      - [numpy](http://numpy.org)
      - [pandas](http://pandas.pydata.org)

### Plotting

  - [R](http://r-project.org)
    (required for HW1 and HW2)

    The following packages are needed:

      - [ggplot2](http://ggplot2.org)
      - [ggthemes](https://github.com/jrnold/ggthemes)
      - [extrafont](https://github.com/wch/extrafont)
        (note: some [post-install configuration][2] required)

  - [Roboto font](https://developer.android.com/design/style/typography.html)
    (used for HW1 and HW2, optional: you can alter this in `common.r`)

### Report

  - [LaTeX](http://latex-project.org)
    with the following packages:

      - amsmath
      - amssymb
      - bm
      - booktabs
      - cancel
      - empheq
      - fancybox
      - fancyhdr
      - fontenc
      - isomath
      - kpfonts
      - mdframed
      - microtype
      - ntheorem
      - parskip
      - scalerel
      - siunitx
      - slashed
      - subcaption
      - subdepth
      - tikz
      - xstring
      - color
      - listings
      - hyperref
      - url
      - plus an additional meta package via:

            ( cd "`kpsewhich -var-value TEXMFHOME`/tex/latex" && sh ) <tools/sigilz.shar
            texhash

[1]: https://people.nscl.msu.edu/~nunes/phy982/phy982web2015.htm
[2]: https://github.com/wch/extrafont/blob/master/README.md#using-extrafont
