process_mash <- function(data_dir = NULL, out_dir = NULL, verbose = TRUE,
                             type = c("sourmash", "mash screen"))
{

  # data_dir = dd
  # out_dir = f_name
  # verbose = TRUE
  # type = "mash screen"

  require("dplyr")
  require("taxize")
  require("stringr")

  parse_mash_screen <- function(path) {
    data <- readLines(con = path)
    data <- strsplit(x = data, split = "\t")
    data <- do.call(rbind, data)
    colnames(data) <- c("identity", "shared_hashes", "median_multiplicity", "p_value", "query_id",
                        "name")
    data <- as.data.frame(data)
    data$identity <- as.numeric(data$identity)
    data$median_multiplicity <- as.numeric(data$median_multiplicity)
    data$p_value <- as.numeric(data$p_value)
    data$name <- trimws(stringr::str_remove(string = data$name, pattern = "\\[[0-9]?[0-9] seqs\\]"))
    return(data)
  }

  getID <- function(tmp_dat, path, type) {

    # Extract the genbank IDs from the name string.
    tmp_dat$genbank_id <- unlist(lapply(strsplit(tmp_dat$name, " "), '[[', 1))

    # Check that all of the genbank IDs were extracted. This is a problem with Mash Screen files in
    # particular because Mash Screen will put a sequence count at the beginning of the name string.
    if (any(!grepl("[A-Z][A-Z]", tmp_dat$genbank_id))) {
      tmp_1 <- tmp_dat[!grepl("[A-Z][A-Z]", tmp_dat$genbank_id), ]
      tmp_2 <- tmp_dat[grepl("[A-Z][A-Z]", tmp_dat$genbank_id), ]
      tmp_1$genbank_id <- unlist(lapply(strsplit(tmp_1$name, " "), '[[', 3))
      tmp_dat <- rbind(tmp_1, tmp_2)
      rm(tmp_1, tmp_2)
    }

    # Query for the NCBI IDs
    # gbid <- unique(tmp_dat$genbank_id)
    gbpb <- txtProgressBar(min = 0, max = nrow(tmp_dat), initial = NA, style = 3)
    tmp_dat$ncbi_id <- numeric(nrow(tmp_dat))
    for (j in 33887:nrow(tmp_dat)) {
      setTxtProgressBar(pb = gbpb, value = j)
      tmp_dat$ncbi_id[j] <- as.numeric(genbank2uid(id = tmp_dat$genbank_id[j])[[1]])
      Sys.sleep(0.05)
    }
    # ncbi <- genbank2uid(id = gbid)
    # ncbi <- do.call(rbind, ncbi)
    # ncbi <- data.frame(genbank_id = gbid, ncbi_id = ncbi); rm(gbid)
    # tmp_dat <- merge(x = tmp_dat, y = ncbi, by = "genbank_id", all.x = T)

    unique_ids <- na.exclude(unique(tmp_dat$ncbi_id))
    all_lin <- NULL
    prog_bar <- txtProgressBar(min = 0, max = length(unique_ids), initial = NA, style = 3)
    for (i in 31420:length(unique_ids)) {
      setTxtProgressBar(pb = prog_bar, value = i)
      tmp <- taxize::classification(unique_ids[i], db = "ncbi")
      tmp <- tmp[[1]]
      tmp$ncbi_id <- unique_ids[i]
      all_lin <- rbind(all_lin, tmp)
      rm(tmp)
    }
    # all_lin <- classification(unique(tmp_dat$ncbi_id), db = "ncbi")
    # all_lin <- do.call(rbind, all_lin)
    # all_lin$ncbi_id <- trunc(as.numeric(row.names(all_lin)))
    # row.names(all_lin) <- NULL

    king_id <- all_lin %>%
      filter(rank == "superkingdom") %>%
      select(kingdom_id = id, ncbi_id)

    phylum_id <- all_lin %>%
      filter(rank == "phylum") %>%
      select(phylum_id = id, ncbi_id)

    class_id <- all_lin %>%
      filter(rank == "class") %>%
      select(class_id = id, ncbi_id)

    order_id <- all_lin %>%
      filter(rank == "order") %>%
      select(order_id = id, ncbi_id)

    family_id <- all_lin %>%
      filter(rank == "family") %>%
      select(family_id = id, ncbi_id)

    genus_id <- all_lin %>%
      filter(rank == "genus") %>%
      select(genus_id = id, ncbi_id)

    species_id <- all_lin %>%
      filter(rank == "species") %>%
      select(species_id = id, ncbi_id)

    species_name <- all_lin %>%
      filter(rank == "species") %>%
      select(species_name = name, ncbi_id)

    tmp_dat <- merge(x = tmp_dat, y = species_id, by = "ncbi_id", all.x = T)
    tmp_dat <- merge(x = tmp_dat, y = species_name, by = "ncbi_id", all.x = T)
    tmp_dat <- merge(x = tmp_dat, y = genus_id, by = "ncbi_id", all.x = T)
    tmp_dat <- merge(x = tmp_dat, y = family_id, by = "ncbi_id", all.x = T)
    tmp_dat <- merge(x = tmp_dat, y = order_id, by = "ncbi_id", all.x = T)
    tmp_dat <- merge(x = tmp_dat, y = class_id, by = "ncbi_id", all.x = T)
    tmp_dat <- merge(x = tmp_dat, y = phylum_id, by = "ncbi_id", all.x = T)
    tmp_dat <- merge(x = tmp_dat, y = king_id, by = "ncbi_id", all.x = T)

    tmp_dat <- subset(x = tmp_dat, select = -c(ncbi_id))

    tmp_dat$use <- rep(TRUE, nrow(tmp_dat))
    if (any(duplicated(tmp_dat$species_id))) {

      dup_id <- na.exclude(unique(tmp_dat$species_id[duplicated(tmp_dat$species_id)]))

      for (j in dup_id){

        if(type == "sourmash") {
          max_f <- max(tmp_dat$f_match[tmp_dat$species_id == j &
                                         !is.na(tmp_dat$species_id)])
          tmp_dat$use[tmp_dat$species_id == j & tmp_dat$f_match < max_f &
                        !is.na(tmp_dat$species_id)] <- FALSE
        }

        if(type == "mash screen") {

          # Get the unique p-values and identity values
          up <- unique(tmp_dat$p_value[tmp_dat$species_id == j & !is.na(tmp_dat$species_id)])
          ui <- unique(tmp_dat$identity[tmp_dat$species_id == j & !is.na(tmp_dat$species_id)])

          # If there is only one unique p-value and one unique identity value (i.e., all rows are the same)
          if (length(up) == 1 & length(ui) == 1) {

            # Get all the row numbers, drop the first appearance, and  set the others to use = FALSE
            rn <- which(tmp_dat$species_id == j & !is.na(tmp_dat$species_id))
            rn <- rn[2:length(rn)]
            tmp_dat$use[rn] <- FALSE

          # If there are multiple p- and identity values (i.e., there are differences)
          } else {

            # Find the smallest p-value
            up <- min(up, na.rm = T)

            # Set all of the rows with higher p-values to use = FALSE
            tmp_dat$use[tmp_dat$p_value > up & tmp_dat$species_id == j &
                          !is.na(tmp_dat$species_id)] <- F

            # Check how many rows still have use = TRUE
            dc <- sum(tmp_dat$species_id == j & !is.na(tmp_dat$species_id) & tmp_dat$use == T)

            # If more than one row has use = TRUE, keep the first appearance only
            if (dc > 1) {
              rn <- which(tmp_dat$species_id == j & !is.na(tmp_dat$species_id) & tmp_dat$use == T)
              rn <- rn[2:length(rn)]
              tmp_dat$use[rn] <- FALSE
            }
          }
        }
      }
    }

    bn <- basename(path)

    # Add the trim number to the counts (parsed from the file name)
    trim_value <- unlist(stringr::str_extract_all(pattern = "trim[0-9]?[0-9]", string = bn))
    trim_value <- unlist(stringr::str_extract_all(string = trim_value, pattern = "[0-9]?[0-9]"))
    trim_value <- paste("Trim", trim_value)
    tmp_dat$trim <- rep(x = trim_value, times = nrow(tmp_dat))

    ds_name <- unlist(strsplit(path, "\\\\"))[7]
    tmp_dat$data_set <- rep(x = ds_name, times = nrow(tmp_dat))

    tmp_dat$assembler <- NA

    k_value   <- unlist(stringr::str_extract_all(pattern = "k[0-9]?[0-9]", string = bn))
    tmp_dat$k <- rep(x = k_value, times = nrow(tmp_dat))

    return(tmp_dat)
  }

  if (is.null(data_dir)) {
    data_dir <- choose.dir(caption = "Select folder containing Sourmash output:")
  }

  file_list <- list.files(path = data_dir, full.names = T)

  if (is.null(out_dir)) {
    out_dir <- choose.dir(caption = "Select the directory for processed output:")
  }

  for (i in 1:length(file_list)) {

    if (type == "sourmash") {
      tmp_dat <- read.csv(file = file_list[i], header = T, as.is = T)
    }

    if (type == "mash screen") {
      tmp_dat <- parse_mash_screen(path = file_list[i])
    }

    if(verbose) cat(paste("Formatting ", basename(file_list[i]), "...\n", sep = ""))

    tmp_dat  <- getID(tmp_dat, file_list[i])
    out_file <- paste(out_dir, basename(file_list[i]), sep = "/")
    write.csv(x = tmp_dat, file = out_file, row.names = F)

  }

}
