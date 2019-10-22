require('stringr')
require('RColorBrewer')
require('tidyverse')
require('data.table')

setwd("P:/Mondavi/Option Year Tasks/Task 2 - Interpretation Guideline Integration/Benchmark Sets")
data_dir  <- "Taxonomic Classification Results/ProcessedData"

#-----assign.col <- function to assign color (ranging from blue [low] to red [hi])  based on a variable
#-----but with vals below threshold on a greyscale

assign.col.thresh <- function(varcol, thresh) {

  tmpcol <- rep(NA, length(varcol))
  rel.res <- rep(NA, length(varcol))

  if (length(varcol[varcol >= thresh & !is.na(varcol)]) > 0) {
    detrange <- c(thresh, max(varcol[varcol >= thresh], na.rm = T))
    ind <- round((max(detrange, na.rm = T) - varcol[varcol >= thresh & !is.na(varcol)]) / diff(detrange) * 500, 0) + 1
    tmpcol[varcol >= thresh & !is.na(varcol)] <- grDevices::rainbow(n = 501, start = 0, end = 4/6)[ind]
    rel.res[varcol >= thresh & !is.na(varcol)] <- 2 - ((max(detrange, na.rm = T) - varcol[varcol >= thresh & !is.na(varcol)]) / diff(detrange))
  }

  if (length(varcol[varcol < thresh & !is.na(varcol)]) > 0) {
    ndrange  <- c(min(varcol[varcol < thresh], na.rm = T), thresh)
    ind <- round((max(ndrange, na.rm = T) - varcol[varcol < thresh & !is.na(varcol)]) / diff(ndrange) * 179, 0) + 1
    tmpcol[varcol < thresh & !is.na(varcol)] <- grDevices::gray(1:180 / 200, alpha = 1)[ind]
    rel.res[varcol < thresh & !is.na(varcol)] <- 1 - ((max(ndrange, na.rm = T) - varcol[varcol < thresh & !is.na(varcol)]) / diff(ndrange))
  }

  data.frame(tmpcol, rel.res, stringsAsFactors = F)

}

# Create a dataframe that specifies the tools and metrics and thresholds for each (and subset of results for now)

tools <- data.frame(
  toolname = c("Kaiju", "Sourmash", "Kraken2", "Krakenuniq", "Braken"),
  lookup = c("(?!.*megahit)(?!.*metaspades).*trim30", "trim30_k51", "trim30", "trim30", "trim30"),
  resval = c("read_count", "f_match", "fragments", "kmers", "fragments"),
  threshold = c(10000,.8, 10000,10000,10000),
  stringsAsFactors = F
)

subdir <- "Shakya_SRR606249_subset10"  # just use Shakya sample for now

tax_res <- NULL
for(toolnum in c(1, 2, 4, 5)) {

  data.file <- grep(
    pattern = tools$lookup[toolnum],
    x = list.files(path = paste(data_dir, subdir, tools$toolname[toolnum], sep = "/")),
    perl = T,
    value = T
  )

  tmpres <- read.csv(file = paste(data_dir, subdir,tools$toolname[toolnum], data.file, sep = "/"),
                     header = T, as.is = T)
  tmpres[, c("tool","metric")] <- tools[toolnum, c("toolname", "resval")]
  tmpres <- subset(
    x = tmpres,
    select = c("species_id", "species_name", tools$resval[toolnum], "tool", "trim", "assembler", "k", "metric")
  )
  setnames(tmpres, tools$resval[toolnum], "resval")
  tmpres[, c("col", "relmag")] <- assign.col.thresh(tmpres$resval, tools$threshold[toolnum])

  tax_res <- rbind(tax_res, tmpres)

}

tmpsum <- tax_res %>%
  group_by(species_id) %>%
  summarise(rel.res = sum(relmag))   # played with max, avg, sum - landed on sum
tmpsum$plotord <- -99
tmpsum$plotord[order(-tmpsum$rel.res)] <- c(1:nrow(tmpsum))

tax_res <- merge(tax_res,tmpsum)
tax_res <- tax_res[tax_res$plotord <= 80, ]

par(mar = c(5, 8, 3, 1), oma = c(1, 0, 0, 0))
ymax <- max(tax_res$plotord)

#png(file="P:/Mondavi/Base Year Tasks/Task 3 - Tools and Workflows Delivery/For Molly/output/Matches v3 %03d.png",
#   height=8.5,width=11,units="in",res=500)

plot(x = c(1, 1 + length(unique(tax_res$tool))), y = c(1,ymax), pch = " ", yaxt = "n", ylab = " ",
     xaxt = "n", xlab = " ", frame = F)
for (i in c(1:length(unique(tax_res$tool)))) {
  tmpdat <- merge(tax_res[tax_res$tool == unique(tax_res$tool)[i], ], data.frame(plotord = c(1:ymax)), all.y = T)
  tmpdat$col[is.na(tmpdat$col)] <- "white"
  rect(xleft = i + 0.15, ybottom = c(ymax:1) - .75, xright = i + 0.85, ytop = c(ymax:1) - .25, col = tmpdat$col[tmpdat$plotord])
  mtext(side = 3, at = i + .5, text = unique(tax_res$tool)[i], line = 0, cex = .8)
  mtext(side = 1, at = i + .5, text = tools$resval[tools$toolname == unique(tax_res$tool)[i]], line = .15, cex = .8)
}
tmpnames <- tax_res %>%
  group_by(plotord) %>%
  summarise(plotname = unique(species_name)[1])
mtext(side = 2, adj = 1, line = -1, at = c(1:ymax), text = tmpnames$plotname[order(tmpnames$plotord)], cex = .55, las = 1)
mtext(side = 1, at = 1, adj = 1, text = "Threshold based on:", line = .15, cex = .8)
mtext(side = 1, outer = T, line = -1,text = "White: species not found; Greyscale: species found but below threshold; Colors: species found above threshold", cex = .75)

#dev.off()
