#!/usr/bin/env Rscript

source("common.r")

data <- read.table("hw1-u.dat", header=TRUE)
data <- dfactor(data, c("case", "E", "l"))

(ggplot(data, aes(x=R, y=u, color=case, linetype=case))
 + geom_line()
 + facet_grid(l ~ E, labeller=function(k, x)
     if (k == "E") paste0("E = ", x, "MeV")
     else          paste0("l = ", x))
 + scale_y_continuous(breaks=c(0), limits=c(-1.5, 1.5))
 + xlab("R /fm")
 + ylab("u")
 + mytheme
 + save("hw1-u.svg"))

data <- read.table("hw1-delta.dat", header=TRUE)
data <- dfactor(data, c("l"))
fit.data <- read.table("hw1-fit.dat", header=TRUE)

(ggplot(data, aes(x=E, y=delta, color=case, linetype=case))
 + geom_line()
 + facet_grid(l ~ ., labeller=function(k, x) paste0("l = ", x), scales="free")
 + xlab("E /MeV")
 + geom_vline(data=fit.data, aes(xintercept=E),
              linetype="dotted", color="grey")
 + ylab("delta /rad")
 + mytheme
 + save("hw1-delta.svg"))
