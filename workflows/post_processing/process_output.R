process_output <- function(data_dir, out_dir) {
  
  # Load the required R packages
  require(package = dplyr,    quietly = TRUE, warn.conflicts = FALSE)
  require(package = tidyr,    quietly = TRUE, warn.conflicts = FALSE)
  require(package = taxizedb, quietly = TRUE, warn.conflicts = FALSE)
  require(package = stringr,  quietly = TRUE, warn.conflicts = FALSE)
  require(package = rjson,    quietly = TRUE, warn.conflicts = FALSE)
  
  # Connect to the local NCBI database
  src_ncbi <- src_ncbi()
  
  # RegEx patterns
  regex_pattern <- c(
    "Kaiju" = "[[:print:]]{1,}(_S[[:digit:]]{1, }_L[[:digit:]]{1, }_R[[:digit:]]{1, }_[[:digit:]]{1, })?_trim[[:digit:]]{1,}(_[[:print:]]{1, })?[.]kaiju[.]out",
    "Kraken2" = "[[:print:]]{1,}(_S[[:digit:]]{1, }_L[[:digit:]]{1, }_R[[:digit:]]{1, }_[[:digit:]]{1, })?_trim[[:digit:]]{1,}_kraken2_[[:print:]]{1,}_confidence[[:digit:]]{1,}[.]report",
    "KrakenUniq" = "[[:print:]]{1,}(_S[[:digit:]]{1, }_L[[:digit:]]{1, }_R[[:digit:]]{1, }_[[:digit:]]{1, })?_trim[[:digit:]]{1,}_krakenuniq[[:print:]]{0,}_report",
    "Bracken" = "._bracken_db-[[:print:]]{1,}_r-[[:digit:]]{1,}_l-[[:print:]]{1,}_t-[[:print:]]{1,}",
    "Sourmash" = "[[:print:]]{1,}(_S[[:digit:]]{1, }_L[[:digit:]]{1, }_R[[:digit:]]{1, }_[[:digit:]]{1, })?_trim[[:digit:]]{1,}_k[[:digit:]]{1,}[.]gather_output[.]csv",
    "Mash Screen" = "[[:print:]]{1,}(_S[[:digit:]]{1, }_L[[:digit:]]{1, }_R[[:digit:]]{1, }_[[:digit:]]{1, })?_trim[[:digit:]]{1,}_[[:print:]]{1,}_mash_screen[.]sorted[.]tab",
    "MTSV" = "[[:print:]]{1,}_[[:digit:]]{1,}_MTSV/Summary/summary.csv"
  )
  
  ##################################################################################################
  ####################################### Function Definitions #####################################
  ##################################################################################################
  
  # Parse Kaiju .out files
  parse_kaiju <- function(path) {
    
    # Read in the Kaiju .out file
    data <- read.table(path, sep = ";", header = F, stringsAsFactors = F)
    
    # Parse the unclassified reads
    u_data <- data[substr(data[, 1], 1, 1) == "U", 1]
    u_data <- matrix(unlist(strsplit(u_data, "\t")), ncol = 3, byrow = T)
    u_data <- data.frame(classified = u_data[, 1], name = u_data[, 2], tax_id = u_data[, 3],
                         length = NA, match_ids = NA, accession_num = NA, match_frag = NA,
                         stringsAsFactors = F)
    
    # Parse the classified reads
    c_data <- data[substr(data[, 1], 1, 1) == "C", 1]
    c_data <- matrix(unlist(strsplit(c_data, "\t")), ncol = 7, byrow = T)
    c_data <- data.frame(classified = c_data[, 1], name = c_data[, 2], tax_id = c_data[, 3],
                         length = c_data[, 4], match_ids = c_data[, 5], accession_num = c_data[, 6],
                         match_frag = c_data[, 7], stringsAsFactors = F)
    
    # Return the parsed data set
    return(rbind(u_data, c_data))
    
  }
  
  # Parse Kraken report files
  parse_kraken_rept <- function(path) {
    
    file_in <- readLines(con = path)
    file_in <- file_in[which(grepl("^%", file_in)):length(file_in)]
    
    var_names <- file_in[1]
    var_names <- stringr::str_replace(string = var_names, pattern = "%", replacement = "percent")
    var_names <- unlist(strsplit(x = var_names, split = "\t"))
    
    data <- file_in[2:length(file_in)]
    data <- strsplit(data, split = "\t")
    data <- do.call(rbind, data)
    colnames(data) <- var_names
    data <- data.frame(data, stringsAsFactors = F)
    
    data$percent  <- as.numeric(data$percent)
    data$reads    <- as.numeric(data$reads)
    data$taxReads <- as.numeric(data$taxReads)
    data$kmers    <- as.numeric(data$kmers)
    data$dup      <- as.numeric(data$dup)
    data$cov      <- as.numeric(data$cov)
    data$taxID    <- as.numeric(data$taxID)
    data$rank     <- as.character(data$rank)
    data$taxName  <- trimws(x = as.character(data$taxName), which = "both")
    
    colnames(data)[colnames(data) == "taxID"]   <- "species_id"
    colnames(data)[colnames(data) == "taxName"] <- "species_name"
    
    return(data)
    
  }
  
  # Parse Bracken text files
  parse_bracken <- function(path) {
    
    dat <- readLines(path)
    dat <- strsplit(dat, "\t")
    dat <- do.call(rbind, dat)
    
    colnames(dat) <- dat[1, ]
    
    dat <- dat[2:nrow(dat), ]
    dat <- data.frame(dat, stringsAsFactors = F)
    
    dat$name                  <- as.character(dat$name)
    dat$taxonomy_id           <- as.numeric(dat$taxonomy_id)
    dat$taxonomy_lvl          <- as.character(dat$taxonomy_lvl)
    dat$kraken_assigned_reads <- as.numeric(dat$kraken_assigned_reads)
    dat$added_reads           <- as.numeric(dat$added_reads)
    dat$new_est_reads         <- as.numeric(dat$new_est_reads)
    dat$fraction_total_reads  <- as.numeric(dat$fraction_total_reads)
    
    colnames(dat)[colnames(dat) == "taxonomy_id"]  <- "species_id"
    colnames(dat)[colnames(dat) == "taxonomy_lvl"] <- "rank"
    colnames(dat)[colnames(dat) == "name"]         <- "species_name"
    
    return(dat)
    
  }
  
  # Parse Mash Screen text files
  parse_mash_screen <- function(path) {
    data <- readLines(con = path)
    data <- strsplit(x = data, split = ",")
    data <- do.call(rbind, data)
    data <- strsplit(x = data, split = "\t")
    data <- do.call(rbind, data)
    colnames(data) <- c("identity", "shared_hashes", "median_multiplicity", "p_value", "query_id")
    data <- as.data.frame(data, stringsAsFactors = FALSE)
    data$identity <- as.numeric(data$identity)
    data$median_multiplicity <- as.numeric(data$median_multiplicity)
    data$p_value <- as.numeric(data$p_value)
    if (any(stringr::str_detect(data$query_id, "\\[[[:digit:]]{1,} seqs\\]"))) {
      data$query_id <- trimws(stringr::str_remove(string = data$query_id, pattern = "\\[[0-9]?[0-9] seqs\\]"))
    }
    data$accession = stringr::str_extract(data$query_id, "[[:alpha:]]{3}_[[:digit:]]{1,10}")
    return(data)
  }
  
  # Convert GenBank IDs to NCBI Taxon IDs
  genbank2uid <- function(id) {
    require(package = taxizedb, quietly = TRUE, warn.conflicts = FALSE)
    f <- file.path(tdb_cache$cache_path_get(), "GenBank.sql")
    if(!file.exists(f)) {stop("GenBank database not found.")}
    con <- RSQLite::dbConnect(RSQLite::SQLite(), dbname = f)
    id <- unlist(lapply(strsplit(id, '[.]'), '[[', 1))
    id_txt <- paste(id, collapse = "','")
    q1 <- paste("SELECT ACCESSION, TAXID FROM TBL_NUCL_GB WHERE ACCESSION IN ('", id_txt, "')", sep = "")
    q2 <- paste("SELECT ACCESSION, TAXID FROM TBL_DEAD_GB WHERE ACCESSION IN ('", id_txt, "')", sep = "")
    q3 <- paste("SELECT ACCESSION, TAXID FROM TBL_NUCL_WGS WHERE ACCESSION IN ('", id_txt, "')", sep = "")
    q4 <- paste("SELECT ACCESSION, TAXID FROM TBL_DEAD_WGS WHERE ACCESSION IN ('", id_txt, "')", sep = "")
    o1 <- RSQLite::dbGetQuery(con, q1)
    o2 <- RSQLite::dbGetQuery(con, q2)
    o3 <- RSQLite::dbGetQuery(con, q3)
    o4 <- RSQLite::dbGetQuery(con, q4)
    RSQLite::dbDisconnect(con)
    o <- rbind(o1, o2)
    o <- rbind(o, o3)
    o <- rbind(o, o4)
    return(o)
  }
  
  # Convert assembly IDs to NCBI Taxon IDs
  assembly2uid <- function(id) {
    require(taxizedb, quietly = TRUE, warn.conflicts = FALSE)
    f <- file.path(tdb_cache$cache_path_get(), "GenBank.sql")
    if (!file.exists(f)) {
      stop("GenBank database not found.")
    }
    con <- RSQLite::dbConnect(RSQLite::SQLite(), dbname = f)
    id  <- paste(id, collapse = "','")
    qa  <- paste("SELECT ASSEMBLY_ACCESSION_ID, TAXON_ID FROM TBL_ASSEMBLY_ACCESSION WHERE ASSEMBLY_ACCESSION_ID IN ('", id, "');", sep = "")
    out <- RSQLite::dbGetQuery(con, qa)
    RSQLite::dbDisconnect(con)
    colnames(out) <- c("accession", "species_id")
    return(out)
  }
  
  # Convert UniProt IDs to NCBI Taxon IDs
  uniprot2uid <- function(id) {
    require(taxizedb, quietly = TRUE, warn.conflicts = FALSE)
    f <- file.path(tdb_cache$cache_path_get(), "UniProt.sql")
    if (!file.exists(f)) {
      stop("UniProt database not found. Please run db_download_uniprot.R")
    }
    con <- RSQLite::dbConnect(RSQLite::SQLite(), dbname = f)
    id  <- paste(id, collapse = "','")
    qa  <- paste("SELECT ACCESSION, TAXID FROM TBL_NUCL_PROT WHERE ACCESSION IN ('", id, "');", sep = "")
    out <- RSQLite::dbGetQuery(con, qa)
    RSQLite::dbDisconnect(con)
    colnames(out) <- c("accession", "species_id")
    return(out)
  }
  
  ##################################################################################################
  ########################################### Read Ouput ###########################################
  ##################################################################################################
  
  # Get the file paths, file names, and tool names for each file in the directory
  file_list <- list.files(path = data_dir, full.names = TRUE)
  tool_name <- character(length = length(file_list))
  for (i in 1:length(regex_pattern)) {
    tool_name[grepl(pattern = regex_pattern[i], x = file_list)] <- names(regex_pattern)[i]
  }
  
  file_list <- data.frame(path = file_list, file = basename(file_list), tool = tool_name, 
                          stringsAsFactors = FALSE)
  #file_list <- cbind(file_list, basename(file_list), tool_name)
  colnames(file_list) <- c("path", "file", "tool")
  file_list <- data.frame(file_list, stringsAsFactors = FALSE)
  file_list <- file_list[file_list$tool != "", ]
  
  # Add the trim value for each output file
  trim <- stringr::str_extract_all(pattern = "trim[0-9]?[0-9]", string = file_list$file, simplify = TRUE)
  trim <- stringr::str_extract_all(pattern = "[0-9]?[0-9]", string = trim, simplify = TRUE)
  if (nrow(trim) > 0) {
    trim[trim == ""] <- NA
  } else {
    trim <- rep(NA, nrow(file_list))
  }
  file_list$trim <- trim
  rm(trim)
  
  # Add the k-value for each output file (not all tools allow the setting of a k-value)
  kmer <- stringr::str_extract_all(pattern = "k[0-9]?[0-9]", string = file_list$file, simplify = TRUE)
  kmer <- stringr::str_extract_all(pattern = "[0-9]?[0-9]", string = kmer, simplify = TRUE)
  if (nrow(kmer) > 0) {
    kmer[kmer == ""] <- NA
  } else {
    kmer <- rep(NA, nrow(file_list))
  }
  file_list$kmer <- kmer
  rm(kmer)
  
  # Add the assembler name (used exclusively by Kaiju as far as I know)
  file_list$assembler <- NA
  file_list$assembler[grepl(pattern = "megahit", x = file_list$file)]    <- "Megahit"
  file_list$assembler[grepl(pattern = "metaspades", x = file_list$file)] <- "Metaspades"
  
  file_list <- tibble::rownames_to_column(file_list, var = "out_id")
  
  ##################################################################################################
  ########################################## Load Variables ########################################
  ##################################################################################################
  
  # Create the table to store the thresholding variable values
  variables <- data.frame(var_id = numeric(), out_id = numeric(), species_id = numeric(), 
                          var_name = character(), var_value = numeric(), stringsAsFactors = FALSE)
  
  if (any(file_list$tool == "Kaiju")) {
    
    tmp_files <- file_list[file_list$tool == "Kaiju", ]
    
    for (i in 1:nrow(tmp_files)) {
      
      # Read in the .out file
      tmp_output <- parse_kaiju(path = tmp_files$path[i])
      
      # Extract the NCBI taxon IDs
      taxon_id <- unique(tmp_output$tax_id[tmp_output$classified == "C"])
      ncbi_lin <- taxizedb::classification(x = taxon_id, db = "ncbi", verbose = FALSE)
      ncbi_lin <- do.call(rbind, ncbi_lin)
      ncbi_lin$reported_id <- trunc(as.numeric(row.names(ncbi_lin)))
      row.names(ncbi_lin) <- NULL
      ncbi_lin <- ncbi_lin[ncbi_lin$rank == "species", ]
      colnames(ncbi_lin)[colnames(ncbi_lin) == "id"] <- "species_id"
      colnames(ncbi_lin)[colnames(ncbi_lin) == "name"] <- "species_name"
      ncbi_lin <- subset(x = ncbi_lin, select = c("species_id", "reported_id"))
      tmp_output <- merge(x = tmp_output, y = ncbi_lin, by.x = "tax_id", by.y = "reported_id", 
                          all.x = TRUE)
      
      # Count the number of reads for each taxon ID
      tmp_output %>%
        filter(classified == "C" & !is.na(species_id)) %>%
        group_by(species_id) %>%
        summarise(var_value = n()) %>%
        mutate(var_name = "read_count") -> read_counts
      
      # Add the output file ID to the variables table
      read_counts$out_id <- tmp_files$out_id[i]
      
      # Construct the variable ID
      read_counts$var_id <- paste(read_counts$out_id, read_counts$species_id, sep = "_")
      
      # Append the read counts to the variables
      variables <- rbind(variables, read_counts)
      
      # Remove objects
      if(exists('tmp_output'))  rm(tmp_output)
      if(exists('ncbi_lin'))    rm(ncbi_lin)
      if(exists('read_counts')) rm(read_counts)
      
    }
    
    rm(tmp_files)
    
  }
  
  if (any(file_list$tool == "Bracken")) {
    
    tmp_files <- file_list[file_list$tool == "Bracken", ]
    
    for (i in 1:nrow(tmp_files)) {
      
      # Read in the Bracken output
      tmp_output <- parse_bracken(path = tmp_files$path[i])
      
      # Convert to a long (rather than wide) format
      tmp_output %>% 
        select(species_id, kraken_assigned_reads, added_reads, new_est_reads, fraction_total_reads) %>%
        gather(kraken_assigned_reads, added_reads, new_est_reads, fraction_total_reads, 
               key = "var_name", value = "var_value") -> tmp_output
      
      # Add the output ID
      tmp_output$out_id <- tmp_files$out_id[i]
      
      # Construct the variable ID
      tmp_output$var_id <- paste(tmp_output$out_id, tmp_output$species_id, sep = "_")
      
      # Append the read counts to the variables
      variables <- rbind(variables, tmp_output)
      
      # Remove the tmp_output object
      if (exists('tmp_output')) rm(tmp_output)
    }
    
  }
  
  if (any(file_list$tool == "Kraken2")) {
    tmp_files <- file_list[file_list$tool == "Kraken2", ]
    for (i in 1:nrow(tmp_files)) {
      tmp_output <- read.table(file = tmp_files$path[i], sep = "\t", as.is = TRUE, header = FALSE, quote = '"')
      colnames(tmp_output) <- c("percent","fragments","tax_fragments","rank","species_id","species_name")
      tmp_output %>% 
        filter(rank == "S") %>%
        select(species_id, percent, fragments, tax_fragments) %>% 
        gather(percent, fragments, tax_fragments, key = "var_name", value = "var_value") -> tmp_output
      tmp_output$out_id <- tmp_files$out_id[i]
      tmp_output$var_id <- paste(tmp_output$out_id, tmp_output$species_id, sep = "_")
      variables <- rbind(variables, tmp_output)
      if (exists("tmp_output")) {
        rm(tmp_output)
      }
    }
    if (exists("tmp_files")) {
      rm(tmp_files)
    }
  }
  
  if (any(file_list$tool == "KrakenUniq")) {
    tmp_files <- file_list[file_list$tool == "KrakenUniq", ]
    for (i in 1:nrow(tmp_files)) {
      tmp_output <- parse_kraken_rept(path = tmp_files$path[i])
      colnames(tmp_output)[colnames(tmp_output) == "taxID"]   <- "species_id"
      colnames(tmp_output)[colnames(tmp_output) == "taxName"] <- "species_name"
      tmp_output %>%
        filter(rank == "species") %>%
        select(species_id, percent, reads, tax_reads = taxReads, kmers, dup, cov) %>%
        gather(percent, reads, tax_reads, kmers, dup, cov, key = "var_name", value = "var_value") -> tmp_output
      tmp_output$out_id <- tmp_files$out_id[i]
      tmp_output$var_id <- paste(tmp_output$out_id, tmp_output$species_id, sep = "_")
      variables <- rbind(variables, tmp_output)
      if (exists('tmp_output')) {
        rm(tmp_output)
      }
    }
    if (exists('tmp_files')) {
      rm(tmp_files)
    }
  }
  
  if (any(file_list$tool == "Sourmash")) {
    tmp_files <- file_list[file_list$tool == "Sourmash", ]
    for (i in 1:nrow(tmp_files)) {
      tmp_output <- read.csv(file = tmp_files$path[i], header = TRUE, as.is = TRUE)
      tmp_output$genbank_id <- unlist(lapply(strsplit(tmp_output$name, " "), '[[', 1))
      tmp_output$accession  <- unlist(lapply(strsplit(tmp_output$genbank_id, '[.]'), '[[', 1))
      tmp_ncbi <- genbank2uid(tmp_output$accession)
      if(nrow(tmp_ncbi)>0){
        tmp_output <- merge(tmp_output, tmp_ncbi, by = "accession", all.x = TRUE)
      } else {
        tmp_output$taxid <- NA
      }
      tmp_output %>%
        select(species_id = taxid, intersect_bp, f_orig_query, f_match, f_unique_to_query, average_abund,median_abund,std_abund) %>%
        gather(intersect_bp, f_orig_query, f_match, f_unique_to_query, average_abund,median_abund,std_abund, key = "var_name", value = "var_value") -> tmp_output
      tmp_output$out_id <- tmp_files$out_id[i]
      tmp_output$var_id <- paste(tmp_output$out_id,tmp_output$species_id,sep = "_")
      variables <- rbind(variables,tmp_output)
      if(exists("tmp_output")){rm(tmp_output)}
    }
    if (exists('tmp_files')) {
      rm(tmp_files)
    }
  }
  
  if (any(file_list$tool == "Mash Screen")) {
    tmp_files <- file_list[file_list$tool=="Mash Screen",]
    for(i in 1:nrow(tmp_files)){
      tmp_output <- parse_mash_screen(path=tmp_files$path[i])
      tmp_ncbi <- assembly2uid(id = tmp_output$accession)
      tmp_output <- merge(tmp_output, tmp_ncbi, by = "accession", all.x = TRUE)
      tmp_output$total_hashes <- unlist(lapply(strsplit(tmp_output$shared_hashes, "/"), '[[', 2))
      tmp_output$total_hashes <- as.numeric(tmp_output$total_hashes)
      tmp_output$shared_hashes <- unlist(lapply(strsplit(tmp_output$shared_hashes, "/"), '[[', 1))
      tmp_output$shared_hashes <- as.numeric(tmp_output$shared_hashes)
      tmp_output %>%
        select(species_id, identity, shared_hashes, total_hashes, median_multiplicity, p_value) %>%
        gather(identity, shared_hashes, total_hashes, median_multiplicity, p_value, key = "var_name", value = "var_value") -> tmp_output
      tmp_output$out_id <- tmp_files$out_id[i]
      tmp_output$var_id <- paste(tmp_output$out_id, tmp_output$species_id, sep = "_")
      variables <- rbind(variables, tmp_output)
    }
  }
  
  if (any(file_list$tool == "MTSV")) {
    tmp_files <- file_list[file_list$tool == "MTSV",]
    for (i in 1:nrow(tmp_files)){
      tmp_output <- read.csv(file = tmp_files$path[i], header = FALSE, as.is = TRUE, skip = 2)
      colnames(tmp_output) <- c("species_id", "division", "name", "total_hits", "unique_hits", "signature_hits", "unique_signature_hits")
      tmp_output %>%
        select(species_id, total_hits, unique_hits, signature_hits, unique_signature_hits) %>%
        gather(total_hits, unique_hits, signature_hits, unique_signature_hits, key = "var_name", value = "var_value")
      variables <- rbind(variables, tmp_output)
      if (exists("tmp_output")) {
        rm(tmp_output)
      }
    }
    if (exists("tmp_files")) {
      rm(tmp_files)
    }
  }
  
  ##################################################################################################
  ########################################## Query Taxon Lineage ###################################
  ##################################################################################################
  
  tax_ids <- unique(variables$species_id)
  all_lin <- classification(tax_ids, db = "ncbi")
  all_lin <- do.call(rbind, all_lin)
  all_lin$species_id <- trunc(as.numeric(row.names(all_lin)))
  row.names(all_lin) <- NULL
  
  ##################################################################################################
  ####################################### JSON Formatting ##########################################
  ##################################################################################################
  
  out <- list(files = file_list, variables = variables, taxa = all_lin)
  out <- rjson::toJSON(x = out)
  setwd(dir = out_dir)
  write(out, file = "combined_output.json")
  
}
args = commandArgs(trailingOnly=TRUE)
data_dir = args[1]
out_dir = args[2]
print(paste0("data dir: ",data_dir))
print(paste0("out dir: ",out_dir))

process_output (data_dir, out_dir)
