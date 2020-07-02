# Add the assembly accession ID to taxon ID look-up table to the genbank database
add_assembly_lookup <- function (zip_path, txt_path)
{
  require(RSQLite)
  require(taxizedb)
  db_path_dir <- file.path(tdb_cache$cache_path_get(),"assemblyAccession")
  tdb_cache$mkdir()
  db_path_file = zip_path
  db_file = txt_path
  unzip(zipfile = zip_path)
  foo <- read.table(file = txt_path)
  colnames(foo) <- c("ASSEMBLY_ACCESSION_ID", "ASSEMBLY_ACCESSION_VERSION", "TAXON_ID", "SPECIES_TAXON_ID", "HISTORICAL_INDICATOR")
  head(foo)
  final_file <- file.path(tdb_cache$cache_path_get(), "GenBank.sql")
  db <- RSQLite::dbConnect(RSQLite::SQLite(), dbname = final_file)
  RSQLite::dbWriteTable(conn = db, name = "tbl_assembly_accession",  value = as.data.frame(foo))
  RSQLite::dbDisconnect(db)
}

args = commandArgs(trailingOnly=TRUE)
zip_path = args[1]
txt_path = args[2]
add_assembly_lookup (zip_path, txt_path)
