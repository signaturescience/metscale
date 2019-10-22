process_braken <- function(data_dir = NULL, out_dir = NULL, verbose = TRUE, overwrite = TRUE,
                           file_type = c("kraken2", "krakenuniq", "bracken"), data_set_name)
{

  require("dplyr")
  require("taxize")
  require("stringr")

  data_dir  <- "P:/Mondavi/Option Year Tasks/Task 2 - Interpretation Guideline Integration/Benchmark Sets/Benchmark_Results/ZymoBIOMICS_DNA_in7321_1/4 - Taxonomic Classification/4.3 - Kraken2"
  #data_dir  <- "C:/Users/chulmelowe/Documents/Projects/Mondavi/Benchmark Results/ZymoBIOMICS Microbial in 7322.1/Bracken"
  out_dir   <- "P:/Mondavi/Option Year Tasks/Task 2 - Interpretation Guideline Integration/Benchmark Sets/Taxonomic Classification Results/ProcessedData/ZymoBIOMICS_DNA_in731_1/Kraken2"
  verbose   <- TRUE
  overwrite <- TRUE
  file_type <- "kraken2"
  data_set_name <- "ZymoBIOMICS_Microbial_in7321_1"

  Sys.setenv(ENTREZ_KEY = "1df332e342c8cc46709c3fc5985598445908")

  parse_kraken_rept <- function(file.path) {

    file_in <- readLines(con = file.path)
    file_in <- file_in[which(grepl("%", file_in)):length(file_in)]

    var_names <- file_in[1]
    var_names <- stringr::str_replace(string = var_names, pattern = "%", replacement = "percent")
    var_names <- unlist(strsplit(x = var_names, split = "\t"))

    data <- file_in[2:length(file_in)]
    data <- strsplit(data, split = "\t")
    data <- do.call(rbind, data)
    colnames(data) <- var_names
    data <- as.data.frame(data)

    data$percent  <- as.numeric(data$percent)
    data$reads    <- as.numeric(data$reads)
    data$taxReads <- as.numeric(data$taxReads)
    data$kmers    <- as.numeric(data$kmers)
    data$dup      <- as.numeric(data$dup)
    data$cov      <- as.numeric(data$cov)
    data$taxID    <- as.numeric(data$taxID)
    data$rank     <- as.character(data$rank)
    data$taxName  <- trimws(x = as.character(data$taxName), which = "both")

    return(data)
  }

  if (is.null(data_dir)) {
    data_dir <- choose.dir(caption = "Select output directory:")
  } else {
    if (!dir.exists(data_dir)) {
      warning("The specified data directory does not exist. Please check the directory path.")
    }
  }

  file_list <- list.files(path = data_dir, pattern = "*report*", full.names = T)

  if (is.null(out_dir)) {
    out_dir <- choose.dir(caption = "Select the directory for processed output:")
  } else {
    if (!dir.exists(out_dir)) {
      dir.create(path = out_dir, recursive = TRUE)
    }
  }

  for (i in 1:length(file_list)) {

    bn <- basename(file_list[i])

    # Check for existing output
    out_file <- paste(paste(out_dir, bn, sep = "/"), "csv", sep = ".")

    if (overwrite == FALSE & file.exists(out_file)) {
      if(verbose) cat(paste("Skipping", bn, "\n", sep = " "))
      next
    }

    if (verbose) cat(paste("Parsing ", bn, "...\n", sep = ""))

    if (file_type %in% c("kraken2", "bracken")) {
      dat <- read.table(file = file_list[i], sep = "\t", as.is = T, header = F)
      colnames(dat) <- c("percent", "fragments", "tax_fragments", "rank", "species_id", "species_name")
    }

    if(file_type == "krakenuniq") {
      dat <- parse_kraken_rept(file.path = file_list[i])
      colnames(dat)[colnames(dat) == "taxID"] <- "species_id"
      colnames(dat)[colnames(dat) == "taxName"] <- "species_name"
    }

    dat <- dat %>% filter(rank == "S" | rank == "species")

    dat$species_name <- trimws(x = dat$species_name, which = "both")

    dat <- subset(dat, select = -rank)

    if (verbose) {cat("Querying taxon IDs...\n")}
    all_lin <- taxize::classification(unique(dat$species_id), db = "ncbi")
    all_lin <- do.call(rbind, all_lin)
    all_lin$species_id <- trunc(as.numeric(row.names(all_lin)))
    row.names(all_lin) <- NULL

    king_id <- all_lin %>%
      filter(rank == "superkingdom") %>%
      select(kingdom_id = id, species_id)

    phylum_id <- all_lin %>%
      filter(rank == "phylum") %>%
      select(phylum_id = id, species_id)

    class_id <- all_lin %>%
      filter(rank == "class") %>%
      select(class_id = id, species_id)

    order_id <- all_lin %>%
      filter(rank == "order") %>%
      select(order_id = id, species_id)

    family_id <- all_lin %>%
      filter(rank == "family") %>%
      select(family_id = id, species_id)

    genus_id <- all_lin %>%
      filter(rank == "genus") %>%
      select(genus_id = id, species_id)

    dat <- merge(x = dat, y = genus_id,  by = "species_id", all.x = T)
    dat <- merge(x = dat, y = family_id, by = "species_id", all.x = T)
    dat <- merge(x = dat, y = order_id,  by = "species_id", all.x = T)
    dat <- merge(x = dat, y = class_id,  by = "species_id", all.x = T)
    dat <- merge(x = dat, y = phylum_id, by = "species_id", all.x = T)
    dat <- merge(x = dat, y = king_id,   by = "species_id", all.x = T)

    trim_value <- unlist(stringr::str_extract_all(pattern = "trim[0-9]?[0-9]", string = bn))
    trim_value <- unlist(stringr::str_extract_all(string = trim_value, pattern = "[0-9]?[0-9]"))
    trim_value <- paste("Trim", trim_value)
    dat$trim   <- rep(x = trim_value, times = nrow(dat))

    dat$use <- rep(x = TRUE, times = nrow(dat))

    dat$data_set <- rep(x = data_set_name, times = nrow(dat))

    dat$assembler <- NA

    k_value   <- unlist(stringr::str_extract_all(pattern = "k[0-9]?[0-9]", string = bn))
    if (length(k_value) == 0) k_value <- NA
    dat$k <- rep(x = k_value, times = nrow(dat))

    setwd(out_dir)
    write.csv(x = dat, file = out_file, row.names = F)
  }
}
