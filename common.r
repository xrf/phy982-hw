# how to import fonts via the 'extrafont' package:
#
#  1. run R with root privileges
#  2. execute `library("extrafont"); font_import(); loadfonts()`
#  3. if it complains "More than one version of regular/bold/italic ...", go
#     into `/usr/lib/R/library/extrafontdb/fontmap/fonttable.csv` and delete
#     any entry that isn't "Regular, Bold, Italic, or BoldItalic".
#

library("ggplot2")
library("ggthemes")
library("extrafont")

font <- "Roboto"

palette  <- ggthemes_data$few$medium
palettel <- ggthemes_data$few$light
paletted <- ggthemes_data$few$dark

# converts column type into factor
dfactor <- function(df, cols) {
    for (col in cols)
        df[, col] <- factor(df[, col])
    df
}

save <- function(fn) {
    write(paste("saving to:", fn), stdout())
    ggsave(fn, width=8, height=6)
}

with.case <- function(name, value, data) {
    data[, name] <- value
    data
}

mytheme <- theme_few(base_family=font)
