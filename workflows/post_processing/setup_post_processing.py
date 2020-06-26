import argparse
import subprocess

'''
sudo yum install mysql-devel
sudo yum install postgresql-devel

conda install -c r r-dplyr
conda install -c r r-tidyr
conda install -c conda-forge r-r.utils
conda install -c r r-rjson
'''




if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", help="input/data dir")
    parser.add_argument("--post", help="output/data dir")
    args = parser.parse_args()

    subprocess.call (["Rscript", "-e", 'library(devtools); install_github("ropensci/taxizedb")' ])
    subprocess.call (["Rscript", "-e", "taxizedb::db_download_ncbi()"])
    subprocess.call (["Rscript", "-e", "db_download_genbank.R"])
    subprocess.call (["Rscript", "-e", "db_download_uniprot.R"])
    subprocess.call (["Rscript", "-e", "add_assembly_lookup.R "])
    process_str = "process_output.R " + args.input + " " + args.output
    subprocess.call (["Rscript", "-e", process_str])
    #Rscript -e 'library(devtools); install_github("ropensci/taxizedb")'   #<- this install 0.1.9.93
    #Rscript -e "taxizedb::db_download_ncbi()"
    #Rscript db_download_genbank.R
    #Rscript db_download_uniprot.R
    #Rscript add_assembly_lookup.R 
    #Rscript process_output.R "/data/home/cgrahlmann/metag2/metagenomics/workflows/data" "/data/home/cgrahlmann/metag2/metagenomics/workflows/post_processing"