.libPaths( c( .libPaths(), "../resources/packages/"))
library("ggplot2")
library("stringr")


options(stringsAsFactors = FALSE)

# Select the file to load
file_name <- snakemake@input[[1]]
file_name

# Check that the data are in comma separated format (csv).
if (!grepl(".csv", file_name)) {
  stop("The data need to be in comma separated format.")
}

# Load the data
jac_ind <- read.csv(file_name, header=TRUE, as.is = TRUE)

# Check that the data are a square matrix
if (nrow(jac_ind) != ncol(jac_ind)) {
  stop("The data need to be contained in a square, symmetric matrix.")
}

# Determine the row & column names
n_col <- ncol(jac_ind)
for (nc in 1:n_col) {
  cn <- colnames(jac_ind)[nc]
  if (grepl("megahit", cn, ignore.case = T) & grepl("trim[0-9]?[0-9]", cn)) {
    trim_num <- unlist(str_extract_all(cn, "trim[0-9]?[0-9]"))
    colnames(jac_ind)[nc] <- paste("MEGAHIT", trim_num, sep = "_")
  } else if (grepl("metaspades", cn, ignore.case = T) & grepl("trim[0-9]?[0-9]", cn)) {
    trim_num <- unlist(str_extract_all(cn, "trim[0-9]?[0-9]"))
    colnames(jac_ind)[nc] <- paste("metaSPAdes", trim_num, sep = "_")
  } else if (grepl("fq", cn, ignore.case = T) & grepl("trim[0-9]?[0-9]", cn)) {
    trim_num <- unlist(str_extract_all(cn, "trim[0-9]?[0-9]"))
    colnames(jac_ind)[nc] <- paste("reads", trim_num, sep = "_")
  } else {
    colnames(jac_ind)[nc] <- substr(cn, 1, min(c(20, nchar(cn))))
  }
}
rownames(jac_ind) <- colnames(jac_ind)

# Reformat the data
plot_df <- data.frame(Sample.x = character(), Sample.y = character(),
                      Jaccard.Index = numeric())
for (i in 1:nrow(jac_ind)) {
  for (j in 1:ncol(jac_ind)) {
    tmp <- data.frame(
      Sample.x = rownames(jac_ind)[i], 
      Sample.y = colnames(jac_ind)[j], 
      Jaccard.Index = jac_ind[i,j]
    )
    plot_df <- rbind(plot_df, tmp)
    rm(tmp)
  }
}
plot_df$Sample.x <- factor(plot_df$Sample.x, 
                           levels = sort(unique(plot_df$Sample.x)))
plot_df$Sample.y <- factor(plot_df$Sample.y,
                           levels = sort(unique(plot_df$Sample.y), decreasing = TRUE))

# Name the output file and make the plot.
out_file <- paste(substr(file_name, 1, nchar(file_name) - 4), ".png",
                  sep = "")
png(file = out_file, height = 8.5, width = 8.5, units = "in", res = 250)
p <- ggplot(data = plot_df, 
            mapping = aes(x = Sample.x, y = Sample.y, fill = Jaccard.Index))
p <- p + geom_tile()
p <- p + geom_text(aes(x = Sample.x, y = Sample.y, label = round(Jaccard.Index, 2)),
                   color = "white", size = 8)
p <- p + theme_classic()
p <- p + theme(text = element_text(size = 20), aspect.ratio = 1)
p <- p + theme(axis.text.x = element_text(angle = 45, hjust = 1))
p <- p + scale_fill_gradient2(limits = c(0,1), name = "Jaccard Index",low = "blue", 
                              high = "red", midpoint = 0.5, mid = "lightgrey")
p <- p + xlab("")
p <- p + ylab("")
p <- p + ggtitle(label = substr(file_name, 1, (nchar(file_name) - 4)))
p <- p + theme(plot.title = element_text(size = 20, hjust = 0.5))
print(p)
dev.off()