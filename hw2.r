#!/usr/bin/env Rscript

source("common.r")

name <- commandArgs(trailingOnly=TRUE)[1]
data <- read.table(paste0(name, ".dat"), header=TRUE)

data[, "rdcs_min"]  <- data$rdcs  - data$rdcs_err
data[, "rdcs_max"]  <- data$rdcs  + data$rdcs_err
data[, "angle_min"] <- data$angle - data$angle_err
data[, "angle_max"] <- data$angle + data$angle_err

data <- dfactor(data, c("energy"))

(ggplot(subset(data, origin == "expt"), aes(x=angle, y=rdcs, color=origin))
 + geom_point(size=1)
 + geom_line(aes(x=angle, y=rdcs), subset(data, origin == "theory"))
 + geom_errorbar(aes(x=angle, ymin=rdcs_min, ymax=rdcs_max))
 + geom_errorbarh(aes(y=rdcs, xmin=angle_min, xmax=angle_max))
 + facet_wrap(~ energy + projectile, scales="free")
 + scale_y_log10()
 + annotation_logticks(sides="l")
 + xlab("angle /deg")
 + ylab(paste0("differential cross section ",
               "/[proton: Rutherford, neutron: mb/sr]"))
 + mytheme
 + save(paste0(name, ".svg")))
