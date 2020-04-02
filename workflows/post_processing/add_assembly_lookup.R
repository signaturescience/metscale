# Add the assembly accession ID to taxon ID look-up table to the genbank database
require(RSQLite)
require(taxizedb)
db_path_dir <- file.path(tdb_cache$cache_path_get(),"assemblyAccession")
tdb_cache$mkdir()
db_path_file <- "/data/home/chulmelowe/assemblyAccession_to_taxid.zip"
db_file <- "data/home/chulmelowe/assemblyAccession_to_taxid.txt"
unzip(zipfile = "/data/home/chulmelowe/assemblyAccession_to_taxid.zip")
foo <- read.table(file = "/data/home/chulmelowe/assemblyAccession_to_taxid.txt")
colnames(foo) <- c("ASSEMBLY_ACCESSION_ID", "ASSEMBLY_ACCESSION_VERSION", "TAXON_ID", "SPECIES_TAXON_ID", "HISTORICAL_INDICATOR")
head(foo)
final_file <- file.path(tdb_cache$cache_path_get(), "GenBank.sql")
db <- RSQLite::dbConnect(RSQLite::SQLite(), dbname = final_file)
RSQLite::dbWriteTable(conn = db, name = "tbl_assembly_accession",  value = as.data.frame(foo))
RSQLite::dbDisconnect(db)
