process_bracken <- function(data_dir = NULL, out_dir = NULL, verbose = FALSE, overwrite = TRUE,
                           file_type = c("kraken2", "krakenuniq", "bracken"))
{

  require("dplyr")
  require("taxizedb")
  require("stringr")

  options(stringsAsFactors=FALSE)
  src_ncbi <- src_ncbi()

  parse_kraken_rept <- function(file.path) {

    file_in <- readLines(con=file.path)
    file_in <- file_in[which(grepl("^%",file_in)):length(file_in)]

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

  if(file_type=="kraken2"){
    file_pattern <- "[[:print:]]{1,}(_S[[:digit:]]{1, }_L[[:digit:]]{1, }_R[[:digit:]]{1, }_[[:digit:]]{1, })?_trim[[:digit:]]{1,}_kraken2_[[:print:]]{1,}_confidence[[:digit:]]{1,}[.]report"
  }

  if(file_type=="krakenuniq"){
    file_pattern <- "[[:print:]]{1,}(_S[[:digit:]]{1, }_L[[:digit:]]{1, }_R[[:digit:]]{1, }_[[:digit:]]{1, })?_trim[[:digit:]]{1,}_krakenuniq[[:print:]]{0,}_report"
  }

  if(file_type=="bracken"){
    file_pattern <- "._bracken_db-[[:print:]]{1,}_r-[[:digit:]]{1,}_l-[[:print:]]{1,}_t-[[:print:]]{1,}"
  }

  file_list <- list.files(path = data_dir, pattern = file_pattern, full.names = T)

  for (i in 1:length(file_list)) {

    bn <- basename(file_list[i])
    if(file_type %in% c("kraken2","krakenuniq")){
      data_set_name <- unlist(strsplit(x=bn,split="_"))[1]
    } else{
      data_set_name <- bn
    }

    # Check for existing output
    out_file <- paste(paste(out_dir, bn, sep = "/"), "csv", sep = ".")

    if (overwrite == FALSE & file.exists(out_file)) {
      if(verbose) cat(paste("Skipping", bn, "\n", sep = " "))
      next
    }

    if (verbose) cat(paste("Parsing ", bn, "...\n", sep = ""))

    if (file_type == "kraken2") {
      dat <- read.table(file = file_list[i], sep = "\t", as.is = T, header = F, quote = '"')
      colnames(dat) <- c("percent","fragments","tax_fragments","rank","species_id","species_name")
    }

    if (file_type == "bracken") {
      dat <- readLines(file_list[i])
      dat <- strsplit(dat, "\t")
      dat <- do.call(rbind, dat)
      colnames(dat) <- dat[1, ]
      dat <- dat[2:nrow(dat), ]
      dat <- data.frame(dat)
      dat$name <- as.character(dat$name)
      dat$taxonomy_id <- as.numeric(dat$taxonomy_id)
      dat$taxonomy_lvl <- as.character(dat$taxonomy_lvl)
      dat$kraken_assigned_reads <- as.numeric(dat$kraken_assigned_reads)
      dat$added_reads <- as.numeric(dat$added_reads)
      dat$new_est_reads <- as.numeric(dat$new_est_reads)
      dat$fraction_total_reads <- as.numeric(dat$fraction_total_reads)
      colnames(dat)[colnames(dat) == "taxonomy_id"] <- "species_id"
      colnames(dat)[colnames(dat) == "taxonomy_lvl"] <- "rank"
      colnames(dat)[colnames(dat) == "name"] <- "species_name"
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
    all_lin <- taxizedb::classification(unique(dat$species_id),db="ncbi")
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
