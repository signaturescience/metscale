db_download_genbank <- function (verbose = TRUE)
{
 
  require("taxizedb")
  # urls of the files on NCBI's FTP site
  db_url <- c("ftp://ftp.ncbi.nih.gov/pub/taxonomy/accession2taxid/dead_nucl.accession2taxid.gz",
              "ftp://ftp.ncbi.nih.gov/pub/taxonomy/accession2taxid/dead_wgs.accession2taxid.gz",
              "ftp://ftp.ncbi.nih.gov/pub/taxonomy/accession2taxid/nucl_gb.accession2taxid.gz",
              "ftp://ftp.ncbi.nih.gov/pub/taxonomy/accession2taxid/nucl_wgs.accession2taxid.gz")

  # folder to keep the downloaded files in
  db_path_dir <- file.path(tdb_cache$cache_path_get(), "gbdump")

  # file names for the tables we need to download
  dead_nucl_file <- file.path(db_path_dir, "dead_nucl.accession2taxid")
  nucl_gb_file   <- file.path(db_path_dir, "nucl_gb.accession2taxid")
  dead_wgs_file  <- file.path(db_path_dir, "dead_wgs.accession2taxid")
  nucl_wgs_file  <- file.path(db_path_dir, "nucl_wgs.accession2taxid")

  # create the file name for the final database
  final_file <- file.path(tdb_cache$cache_path_get(), "GenBank.sql")

  # if the database already exists, return it and print a message
  if (file.exists(final_file)) {
    #(verbose, "Database already exists, returning old file")
    return(final_file)
  }

  # make the cache directory if it doesn't already exist
  tdb_cache$mkdir()

  # download the tables from NCBI
  for (url_ in db_url) {

    # extract the name of the database from the database url
    db_zip_name <- basename(url_)
    db_file <- file.path(db_path_dir, substr(db_zip_name, 1, (nchar(db_zip_name) - 3)))

    # download the tables from NCBI
    #mssg(verbose, paste("downloading '", db_zip_name, "'...", sep = ""))
    cat(paste("downloading '", db_zip_name, "'...\n", sep = ""))
    db_path_file <- file.path(tdb_cache$cache_path_get(), db_zip_name)
    curl::curl_download(url = url_, destfile = db_path_file, quiet = TRUE)

    # unzip the downloaded file into the dump directory
    #mssg(verbose, paste("unzipping '", db_zip_name, "'..."))
    cat(paste("unzipping '", db_zip_name, "'...\n"))
    R.utils::gunzip(filename = db_path_file, destname = db_file, skip = TRUE, remove = FALSE)

  }

  # load the dead nucleotides table
  #mssg(verbose, "loading 'dead_nucl.accession2taxid'...")
  dead_nucl <- readr::read_tsv(file = dead_nucl_file)

  # load the genbank nucleotides table
  #mssg(verbose, "loading 'nucl_gb.accession2taxid'...")
  nucl_gb <- readr::read_tsv(file = nucl_gb_file)

  # load the dead whole genome sequencing table
  #mssg(verbose, "loading 'dead_wgs.accession2taxid'...")
  dead_wgs <- readr::read_tsv(file = dead_wgs_file)

  # load the nucleotide whole genome sequencing table
  #mssg(verbose, "loading 'nucl_wgs.accession2taxid'...")
  nucl_wgs <- readr::read_tsv(file = nucl_wgs_file)

  #mssg(verbose, "building SQLite database...")
  db <- RSQLite::dbConnect(RSQLite::SQLite(), dbname = final_file)
  RSQLite::dbWriteTable(conn = db, name = "tbl_nucl_gb",  value = as.data.frame(nucl_gb))
  RSQLite::dbWriteTable(conn = db, name = "tbl_nucl_wgs", value = as.data.frame(nucl_wgs))
  RSQLite::dbWriteTable(conn = db, name = "tbl_dead_gb",  value = as.data.frame(dead_nucl))
  RSQLite::dbWriteTable(conn = db, name = "tbl_dead_wgs", value = as.data.frame(dead_wgs))

  RSQLite::dbExecute(db, "CREATE INDEX tax_id_index_nucl_gb ON tbl_nucl_gb (taxid)")
  RSQLite::dbExecute(db, "CREATE INDEX accession_index_nucl_gb ON tbl_nucl_gb (accession)")

  RSQLite::dbExecute(db, "CREATE INDEX tax_id_index_nucl_wgs ON tbl_nucl_wgs (taxid)")
  RSQLite::dbExecute(db, "CREATE INDEX accession_index_nucl_wgs ON tbl_nucl_wgs (accession)")

  RSQLite::dbExecute(db, "CREATE INDEX tax_id_index_dead_gb ON tbl_dead_gb (taxid)")
  RSQLite::dbExecute(db, "CREATE INDEX accession_index_dead_gb ON tbl_dead_gb (accession)")

  RSQLite::dbExecute(db, "CREATE INDEX tax_id_index_dead_wgs ON tbl_dead_wgs (taxid)")
  RSQLite::dbExecute(db, "CREATE INDEX accession_index_dead_wgs ON tbl_dead_wgs (accession)")

  RSQLite::dbDisconnect(db)

  #mssg(verbose, "cleaning up...")
  unlink(db_path_file)
  unlink(db_path_dir, recursive = TRUE)

  return(final_file)
}
db_download_genbank ()