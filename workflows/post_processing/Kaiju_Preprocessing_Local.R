process_kaiju <- function(data_dir = NULL, out_dir, verbose = TRUE, overwrite = TRUE) {

  require("dplyr")
  require("taxizedb")
  require("stringr")

  options(stringsAsFactors = F)
  src_ncbi <- src_ncbi()

  # Function to parse the raw Kaiju output
  parse_kaiju <- function(path) {

    # Read in the Kaiju .out file
    data <- read.table(path, sep = ";", header = F, stringsAsFactors = F)

    # Parse the unclassified reads
    u_data <- data[substr(data[, 1], 1, 1) == "U", 1]
    u_data <- matrix(unlist(strsplit(u_data, "\t")), ncol = 3, byrow = T)
    u_data <- data.frame(classified = u_data[, 1], name = u_data[, 2], tax_id = u_data[, 3],
                         length = NA, match_ids = NA, accession_num = NA, match_frag = NA)

    # Parse the classified reads
    c_data <- data[substr(data[, 1], 1, 1) == "C", 1]
    c_data <- matrix(unlist(strsplit(c_data, "\t")), ncol = 7, byrow = T)
    c_data <- data.frame(classified = c_data[, 1], name = c_data[, 2], tax_id = c_data[, 3],
                         length = c_data[, 4], match_ids = c_data[, 5], accession_num = c_data[, 6],
                         match_frag = c_data[, 7])

    # Return the parsed data set
    return(rbind(u_data, c_data))

  }

  # Choose the directory containing the Kaiju output
  if (is.null(data_dir)) {
    data_dir <- choose.dir()
  }

  # List the .out files
  f_list <- list.files(path = data_dir, pattern = "[.]out", full.names = T)
  f_list <- f_list[!grepl("[.]csv", f_list)]

  # Parse each file and save it as a .csv for future analysis
  for (i in 1:length(f_list)) {

    # Get the file base name
    bn  <- basename(f_list[i])

    # Check for existing output
    out_name <- paste(substr(bn, 1, (nchar(bn) - 4)), "read_counts.csv", sep = ".")
    if (overwrite == FALSE & file.exists(paste(out_dir, out_name, sep = "/"))) {
      if(verbose) cat(paste("Skipping", bn, "\n", sep = " "))
      next
    }

    # Parse the file into a dataframe
    if(verbose) cat(paste("Parsing ", bn, "...\n", sep = ""))
    tmp <- parse_kaiju(f_list[i])

    # Query the species taxon IDs from NCBI and add them to the dataframe
    if(verbose) cat("Querying species IDs...\n")
    tax_id  <- unique(tmp$tax_id[tmp$classified == "C"])
    all_lin <- taxizedb::classification(x = tax_id[1:8000], db = "ncbi", verbose = TRUE)
    tmp_lin <- taxizedb::classification(x = tax_id[8001:length(tax_id)], db = "ncbi", verbose = TRUE)
    all_lin <- c(all_lin, tmp_lin)
    all_lin <- do.call(rbind, all_lin)
    all_lin$rept_id <- trunc(as.numeric(row.names(all_lin)))
    row.names(all_lin) <- NULL
    all_lin <- all_lin[all_lin$rank == "species", ]
    colnames(all_lin)[3] <- "species_id"
    colnames(all_lin)[1] <- "species_name"
    all_lin <- subset(all_lin, select = c("species_id", "species_name", "rept_id"))
    memory.limit(size = 10024000)
    tmp <- merge(x = tmp, y = all_lin, by.x = "tax_id", by.y = "rept_id", all.x = T)

    # Count the number of times each species appears in the dataframe
    if(verbose) cat("\nCounting reads by species...\n")
    r_counts <- tmp %>%
      filter(classified == "C", !is.na(species_id)) %>%
      group_by(species_id, species_name) %>%
      summarise(read_count = length(unique(name)))

    # Query the higher-order taxon IDs associated with each species and add them to the counts
    if(verbose) cat("Attaching higher-order taxon IDs...\n")
    all_lin <- taxizedb::classification(unique(r_counts$species_id), db = "ncbi")
    all_lin <- do.call(rbind, all_lin)
    all_lin$species_id <- matrix(unlist(strsplit(row.names(all_lin), "[.]")), ncol = 2, byrow = T)[ ,1]
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

    r_counts <- merge(x = r_counts, y = king_id, by = "species_id", all.x = T)
    r_counts <- merge(x = r_counts, y = phylum_id, by = "species_id", all.x = T)
    r_counts <- merge(x = r_counts, y = class_id, by = "species_id", all.x = T)
    r_counts <- merge(x = r_counts, y = order_id, by = "species_id", all.x = T)
    r_counts <- merge(x = r_counts, y = family_id, by = "species_id", all.x = T)
    r_counts <- merge(x = r_counts, y = genus_id, by = "species_id", all.x = T)

    # Add the trim number to the counts (parsed from the file name)
    if(verbose) cat("Adding trim number...\n")
    trim_value <- unlist(stringr::str_extract_all(pattern = "trim[0-9]?[0-9]", string = bn))
    trim_value <- unlist(stringr::str_extract_all(string = trim_value, pattern = "[0-9]?[0-9]"))
    trim_value <- paste("Trim", trim_value)
    r_counts$trim <- rep(x = trim_value, times = nrow(r_counts))

    # Add the data set name to the counts (parsed from the path)
    if(verbose) cat("Adding data set name...\n")
    ds_name <- "spiked100x" #unlist(strsplit(f_list[i], "\\\\"))[7]
    r_counts$data_set <- rep(x = ds_name, times = nrow(r_counts))

    # Add the use variable for consistency with other tool output (is always TRUE for Kaiju)
    if(verbose) cat("Adding use indicator...\n")
    r_counts$use <- TRUE

    # Add the assembler name (parsed from the file name) if one was used
    if(verbose) cat("Adding assembler name...\n")
    r_counts$assembler <- NA

    if (grepl("megahit", bn)) {
      r_counts$assembler <- rep("megahit", nrow(r_counts))
    }

    if (grepl("metaspades", bn)) {
      r_counts$assembler <- rep("metaspades", nrow(r_counts))
    }

    # Add the kmer length (not used by Kaiju, here for consistency)
    if(verbose) cat("Adding kmer...\n")
    r_counts$k <- NA

    # Write out the read counts table as a .csv to the output directory.
    if(verbose) cat("Saving read counts...")
    write.csv(x = r_counts, file = paste(out_dir, out_name, sep = "/"), row.names = F)
    if(verbose) cat("Complete\n")

  }

}
