#!/usr/bin/env Rscript

source("common.r")

scale.dcs <- function(data, factor) {
    data[, "dcs"]     <- factor * data[, "dcs"]
    data[, "dcs_err"] <- factor * data[, "dcs_err"]
    data
}

normalize.dcs <- function(data, factor=1)
    scale.dcs(data, factor / mean(data[, "dcs"]))

add.expt.data <- function(str, factor=1, dcs.err.percent=FALSE) {
    data <- read.table(textConnection(str), header=TRUE)
    data2 <- data[, c("angle", "energy", "dcs", "dcs_err")]
    if (dcs.err.percent)
        data2[, "dcs_err"] <- data[, "dcs"] * data[, "dcs_err"] / 100
    data2[, "case"] <- "expt"
    normalize.dcs(data2, factor)
}

data <- rbind(
    with.case(
        "case", "theory",
        rbind(
            read.table("hw2-Ni60-p-elastic-high.dat", header=TRUE),
            read.table("hw2-Ni60-p-elastic-low.dat",  header=TRUE),
            read.table("hw2-Ni60-n-elastic-high.dat", header=TRUE),
            read.table("hw2-Ni60-n-elastic-low.dat",  header=TRUE)
        )
    ),
    with.case("case", "expt",
        read.table("hw2-expt-data.dat", header=TRUE)
    )
)

data[, "rdcs_min"] <- data$rdcs - data$rdcs_err
data[, "rdcs_max"] <- data$rdcs + data$rdcs_err
data[, "angle_min"] <- data$angle - data$angle_err
data[, "angle_max"] <- data$angle + data$angle_err

data <- dfactor(data, c("energy"))

(ggplot(subset(data, case == "expt"), aes(x=angle, y=rdcs, color=case))
 + geom_point(size=1)
 + geom_line(aes(x=angle, y=rdcs), subset(data, case == "theory"))
 + geom_errorbar(aes(x=angle, ymin=rdcs_min, ymax=rdcs_max))
 + geom_errorbarh(aes(y=rdcs, xmin=angle_min, xmax=angle_max))
 + facet_wrap(~ energy + projectile, scales="free")
 + xlab("angle /deg")
 + ylab(paste0("differential cross section /[",
               "proton: Rutherford, neutron: mb/sr]"))
 + mytheme
 + save("hw2-1.svg"))
