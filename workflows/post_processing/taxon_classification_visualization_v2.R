# Visualize taxonomic performance of different tools

# Load R packages
require('stringr', quietly = TRUE, warn.conflicts = FALSE)
require('RColorBrewer', quietly = TRUE, warn.conflicts = FALSE)
require('tidyverse', quietly = TRUE, warn.conflicts = FALSE)
require('data.table', quietly = TRUE, warn.conflicts = FALSE)

# Tools data frame - Is this something we want to give the user the ability to modify?
tools <- data.frame(
  toolname = c("Kaiju", "Sourmash", "Kraken2", "Krakenuniq", "Braken"),
  lookup = c("[[:print:]]{1,}_trim[[:digit:]]{1,}[.]kaiju[.]read_counts[.]csv",
             "[[:print:]]{1,}_trim[[:digit:]]{1,}_k[[:digit:]]{1,}[.]gather_output[.]csv",
             "[[:print:]]{1,}_trim[[:digit:]]{1,}kraken2[[:print:]]{1,}_confidence[[:digit:]]{1,}[.]report[.]csv",
             "[[:print:]]{1,}_trim[[:digit:]]{1,}krakenuniq[[:print:]]{1,}_hll[[:digit:]]{1,}_report[.]csv",
             "_bracken_db[[:print:]]{1,}_r-[[:digit:]]{1,}_l-[[:digit:]]{1,}_t-[[:digit:]]{t,}"),
  resval = c("read_count", "f_match", "fragments", "kmers", "fragments"),
  threshold = c(10000, .8, 10000 ,10000, 10000),
  stringsAsFactors = FALSE
)

# Function to assign colors based the threshold values
assign.col.thresh <- function(varcol, thresh) {

    tmpcol <- rep(x = NA, times = length(varcol))
    rel.res <- rep(x = NA, times = length(varcol))

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

    return(data.frame(tmpcol, rel.res, stringsAsFactors = F))

  }

# Determine the number of plots (pages) needed to plot all of the output in the data directory
n_files <- numeric(nrow(tools))
f_list <- list.files(path = data_dir, full.names = TRUE)
for (i in 1:nrow(tools)) {
  n_files[i] <- sum(grepl(tools$lookup[i], f_list))
}
file_count <- sum(n_files)
if(file_count > 8){
  n_pages <- ifelse(file_count %% 8 == 0, (file_count / 8), (trunc(file_count / 8) + 1))
} else {
  n_pages <- 1
}

# Read in each data set and add columns for the tool, result value, and color
tax_res <- NULL
for (f in 1:length(f_list)) {

  base <- basename(f_list[f])

  ft <- logical(nrow(tools))
  for (i in 1:nrow(tools)) {
    ft[i] <- grepl(tools$lookup[i], base)
  }
  tv <- tools$threshold[ft == TRUE]
  rv <- tools$resval[ft == TRUE]
  ft <- tools$toolname[ft == TRUE]

  tmpres <- read.csv(file = f_list[f], header = T, as.is = T)
  tmpres$tool <- rep(x = ft, times = nrow(tmpres))
  tmpres$metric <- rep(x = rv, times = nrow(tmpres))
  tmpres <- subset(
    x = tmpres,
    select = c("species_id", "species_name", rv, "tool", "trim", "assembler", "k", "metric")
  )
  setnames(tmpres, rv, "resval")
  tmpres[, c("col", "relmag")] <- assign.col.thresh(tmpres$resval, tv)

  tax_res <- rbind(tax_res, tmpres)
}

tmpsum <- tax_res %>%
  group_by(species_id) %>%
  summarise(rel.res = sum(relmag))
tmpsum$plotord <- -99
tmpsum$plotord[order(-tmpsum$rel.res)] <- c(1:nrow(tmpsum))

tax_res <- merge(x = tax_res, y = tmpsum)
tax_res <- tax_res[tax_res$plotord <= 80, ]

ymax <- max(tax_res$plotord, na.rm = TRUE)

for (p in 1:n_pages) {

  par(mar = c(5, 8, 3, 1), oma = c(1, 0, 0, 0))
  file_name <- paste(out_dir, "Comparison Plot Page ", p, ".png", sep = "")
  if(!is.null(dev.list())){
    dev.off()
  }
  png(file = file_name, height = 8.5, width = 11, units = "in", res = 500)

  plot(
    x = c(1, (1 + length(unique(tax_res$tool)))),
    y = c(1, ymax),
    type = "n",
    yaxt = "n",
    ylab = NA,
    xaxt = "n",
    xlab = NA,
    frame = F
  )

  for (i in c(1:length(unique(tax_res$tool)))) {
    tmpdat <- merge(
      x = tax_res[tax_res$tool == unique(tax_res$tool)[i], ],
      y = data.frame(plotord = c(1:ymax)),
      all.y = T
    )
    tmpdat$col[is.na(tmpdat$col)] <- "white"
    rect(
      xleft = i + 0.15,
      ybottom = c(ymax:1) - .75,
      xright = i + 0.85,
      ytop = c(ymax:1) - .25,
      col = tmpdat$col[tmpdat$plotord]
    )
    mtext(side = 3, at = i + .5, text = unique(tax_res$tool)[i], line = 0, cex = .8)
    mtext(side = 1, at = i + .5, text = tools$resval[tools$toolname == unique(tax_res$tool)[i]],
          line = .15, cex = .8)
  }
  tmpnames <- tax_res %>%
    group_by(plotord) %>%
    summarise(plotname = unique(species_name)[1])
  mtext(side = 2, adj = 1, line = -1, at = c(1:ymax),
        text = tmpnames$plotname[order(tmpnames$plotord)], cex = .55, las = 1)
  mtext(side = 1, at = 1, adj = 1, text = "Threshold based on:", line = .15, cex = .8)
  mtext(
    side = 1,
    outer = T,
    line = -1,
    text = "White: species not found; Greyscale: species found but below threshold; Colors: species found above threshold",
    cex = .75
  )
  dev.off()
}
