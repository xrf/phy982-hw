Dependencies
------------

### Calculations

  - [Glasgow Haskell Compiler (GHC)](https://haskell.org/ghc)
    (required for HW1)

      - [Cabal](https://haskell.org/cabal).

      - Other dependencies can be installed by running this command in the
        project directory:

            cabal install --dependencies-only

  - [Python](https://python.org) 3.4+ or 2.7+
    (required for HW2)

      - numpy
      - pandas

  - [OpenSSH](http://openssh.com)
    (required for HW2)

    You must be able to log into `fishtank` passwordlessly.  The easiest way
    to do this is via a shared connection (note: you can also use public key
    authentication, but it's more involved).  To configure this, append this
    to the bottom of `~/.ssh/config`:

        Host fishtank
        User ???
        ControlMaster auto
        ControlPath ~/.ssh/control:%h:%p:%r

    (Replace `???` with your actual username.)  Then, open a new terminal, log
    into `fishtank`, and make sure it stays open.  Now, any future connections
    to `fishtank` will reuse this connection without asking for the password.

    If this is not set up properly, you will see a `Permission denied (…).`
    error when running the code.

### Plotting

  - [R](http://r-project.org)
    (required for HW1 and HW2)

    The following packages are needed:

      - [ggplot2](http://ggplot2.org)
      - [ggthemes](https://github.com/jrnold/ggthemes)
      - [extrafont](https://github.com/wch/extrafont)
        (note: some post-install configuration required)

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
      - tikz
      - xstring

      - color
      - listings
      - hyperref
      - url

      - plus an additional meta package via:

            ( cd "$HOME/texmf/tex/latex" && sh ) <tools/sigilz.shar
            texhash
