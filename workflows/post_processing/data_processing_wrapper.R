# Wrapper script for data processing functions

# Source the processing functions
# Note to Chris G: You will need to tell this script where the processing functions are being kept
source("Bracken_Kraken_Preprocessing_Local.R")
source("Kaiju_Preprocessing_Local.R")
source("Mash_Preprocessing_local.R")

# Each preprocessing script needs two inputs from the user:
# data_dir - The path to the directory containing the output from the tools
# out_dir - The path to the directory where the user would like the processed outputs to go
data_dir="/home/cgrahlmann/eclipse-workspace/mondavi/workflows/data"
out_dir="/home/cgrahlmann/eclipse-workspace/mondavi/workflows/data"
# Process Kaiju output
process_kaiju(data_dir, out_dir, verbose = TRUE)

# Process Sourmash output
process_mash(data_dir, out_dir, file_type = "sourmash", verbose = TRUE)

# Process MashScreen output
process_mash(data_dir, out_dir, file_type = "mashscreen", verbose = TRUE)

# Process Kraken2 output
process_bracken(data_dir, out_dir, file_type = "kraken2", verbose = TRUE)

# Process KrakenUniq output
process_bracken(data_dir, out_dir, file_type = "krakenuniq", verbose = TRUE)

# Process Bracken output
process_bracken(data_dir, out_dir, file_type = "bracken", verbose = TRUE)
