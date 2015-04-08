Dependencies
------------

### Calculation

  - [Python](https://python.org)

      - numpy
      - pandas

  - [Glasgow Haskell Compiler (GHC)](https://haskell.org/ghc)
    (only required for HW1)

      - [Cabal](https://haskell.org/cabal).

      - Other dependencies can be installed by running this command in the
        project directory:

            cabal install --dependencies-only

### Plotting

  - [R](http://r-project.org) with the following packages:
      - [ggplot2](http://ggplot2.org)
      - [ggthemes](https://github.com/jrnold/ggthemes)
      - [extrafont](https://github.com/wch/extrafont)
        (note: some post-install configuration required)

  - [Roboto font](https://developer.android.com/design/style/typography.html)
    (optional: you can alter this in `common.r`)

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
      - tikz
      - xstring

      - color
      - listings
      - hyperref
      - url

      - plus an additional meta package via:

            ( cd "$HOME/texmf/tex/latex" && sh ) <tools/sigilz.shar
            texhash
