db_download_uniprot <- function (verbose = TRUE)
{
  require(taxizedb, quietly = TRUE, warn.conflicts = FALSE)
  db_url <- "ftp://ftp.ncbi.nih.gov/pub/taxonomy/accession2taxid/prot.accession2taxid.gz"
  db_path_dir <- file.path(tdb_cache$cache_path_get(), "uniprot_dump")
  prot_file <- file.path(db_path_dir, "prot.accession2taxid")
  final_file <- file.path(tdb_cache$cache_path_get(), "UniProt.sql")
  if (file.exists(final_file)) {
    if (verbose) message("Existing database found, returning existing database.")
    return(final_file)
  }
  tdb_cache$mkdir()
  zip_name <- basename(db_url)
  db_file <- file.path(db_path_dir, substr(zip_name, 1, (nchar(zip_name) - 3)))
  db_path_file <- file.path(tdb_cache$cache_path_get(), zip_name)
  if (verbose) message(paste("Downloading '", zip_name, "'...", sep = ""))
  curl::curl_download(url = db_url, destfile = db_path_file, quiet = TRUE)
  if (verbose) message(paste("Unzipping '", zip_name, "'...", sep = ""))
  R.utils::gunzip(filename = db_path_file, destname = db_file, skip = TRUE, remove = FALSE)
  if (verbose) message(paste("Loading '", prot_file, "'...", sep = ""))
  nucl_prot <- readr::read_tsv(file = prot_file)
  if (verbose) message("Building SQLite database...")
  db <- RSQLite::dbConnect(RSQLite::SQLite(), dbname = final_file)
  RSQLite::dbWriteTable(conn = db, name = "tbl_nucl_prot", value = as.data.frame(nucl_prot))
  RSQLite::dbExecute(conn = db, statement = "CREATE INDEX taxid_index_nucl_prot ON tbl_nucl_prot (taxid)")
  RSQLite::dbExecute(conn = db, statement = "CREATE INDEX accession_index_nucl_prot ON tbl_nucl_prot (accession)")
  RSQLite::dbDisconnect(db)
  if (verbose) message("Cleaning up...")
  unlink(db_path_file)
  unlink(db_path_dir, recursive = TRUE)
  return(final_file)
}

db_download_uniprot ()