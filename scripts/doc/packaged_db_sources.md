# Taxon Containment Metadata Repository: `containment_dict.json.gz`

## Background

This file is the centerpiece of the DQT. It contains the full set of metadata for each database to be queried for inclusion of a particular taxon, including specifically the list of taxa included in that database and some metadata about where and when it was captured. This file has been prepared and packaged to include as many databases used in MetScale as possible, though the user is free to augment it and the program offers several procedures accessible by command line for that purpose. 

This document is meant to describe what is in the packaged version of this file and, as well as possible, how it was gathered.

## Databases Included
The [containment file](../blob/master/scripts/containment_dict.json.gz) packaged with this repo includes a number of databases relevant to the taxon classification workflows in MetScale. Below is a table of the databases included:

|Database|Metadata Key|Source|
|:---|:---|:---|
|RefSeq|RefSeq_v##|[NCBI RefSeq FTP](ftp://ftp.ncbi.nlm.nih.gov/refseq/release/release-catalog/archive/)|
|Kraken2* |minikraken2_v2_8GB_201904_UPDATE |[Kraken2: minikraken2_v2 DB](ftp://ftp.ccb.jhu.edu/pub/data/kraken2_dbs/minikraken2_v2_8GB_201904_UPDATE.tgz) |
|Krakenuniq* |minikraken_20171019_8GB|[kraken1: minikraken_8GB `seqid2taxid.map`](https://ccb.jhu.edu/software/kraken/dl/seqid2taxid.map)|
|Kaiju* |kaiju_db_nr_euk|(corresponds to [Kaiju NCBI *nr+euk* DB](http://kaiju.binf.ku.dk/database/kaiju_db_nr_euk_2019-06-25.tgz))|
|GenBank|NCBI_nucl_gb|[NCBI accn2taxid (nucl_gb)](ftp://ftp.ncbi.nlm.nih.gov/pub/taxonomy/accession2taxid/nucl_gb.accession2taxid.gz)|
|GenBank (WGS/TSA)|NCBI_nucl_wgs|[NCBI accn2taxid (nucl_wgs)](ftp://ftp.ncbi.nlm.nih.gov/pub/taxonomy/accession2taxid/nucl_wgs.accession2taxid.gz)|
|MetaPhlAn2|metaphlan_mpa_v20_m200|MetaPhlAn2 Bitbucket (new link needed)|
|MTSV|MTSV_Oct-28-2019|[MTSV Complete Genome DB](https://rcdata.nau.edu/fofanov_lab/Compressed_MTSV_database_files/complete_genome.tar.gz)|

*Notes:*

* __\*Kraken2/Krakenuniq/Kaiju__:
	* Taxon ID files specifically match databases used by Taxon Classification workflows.
	* Each database required specific research to identify proper Taxon sets (see documentation).
* __RefSeq__:
	* Includes RefSeq versions 1 through 98.
* __GenBank/GenBank (WGS/TSA)__:
	* Pulled directly from the NCBI's broadest [accession-to-taxonID database](ftp://ftp.ncbi.nlm.nih.gov/pub/taxonomy/accession2taxid/).


## Data Sources 

Each data source has a particular way of identifying the set of Taxon IDs included. The sources provided by NCBI (such as RefSeq) tend to have a straightfoward table of metadata included, so queueing these up for import by the DQT is simple. For databases constructed by individual method developers, there is often considerable legwork involved in identifing the taxon set.

The process for each of the tools included with the packaged database is described below. For most of them, a set of commands that reproduces those steps is included in the script `prepare_taxid_metadata.sh`. 

### NCBI Sources

* **RefSeq**
    * The RefSeq catalog contains all Accessions included in a release, with a column for NCBI taxon ID. Downloading the catalog file directly is sufficient for importing with `query_tool.py`.
* **GenBank & GenBank (WGS/TSA)**:
    * These are downloaded directly as tab-delimited text files. Due to file size, it is best to use bash commands to create a file with only the unique taxon IDs for query_tool to parse:
    ```cat $accn2taxid/nucl_wgs.accession2taxid | cut -f 3 | sort | uniq > $accn2taxid/nucl_wgs.taxid_list.txt
    ```
* **NCBI Taxonomy**
    * Taxonomy can be downloaded from [NCBI] directly. After extracting, `nodes.dmp` should be in the target folder. That file path should be given in the config file (see above).

### Databases Specific to Individual Taxon Classification Programs

* **Krakenuniq**
    * Krakenuniq uses databases in the same form as Kraken1. When those DBs were packaged by the developers, they included a file called `seqid2taxid.map`. The provenenace of that particular file is not well-documented as far as I can tell, although it is ostensibly a mapping from database sequence to taxon ID, which is what we need. 
    * That file is tab-delimited, so it can be retreived from the Kraken1 website (link above) and imported directly by `query_tool.py`.

* **Kraken2**
    * Kraken2 usus a very different (non-human-readable) database format. For this format the command `kraken2-inspect` can produce the list of Taxon IDs:
    ```kraken2-inspect --db $kraken2_db_fold --report-zero-counts > $kraken2_work_fold/kraken2_inspect_taxonids.txt
    ```
    * The output is tab-delimited and the default config file has a format for it.

* **Kaiju**
    * For Kaiju, pulling the list of taxa is possible when creating a Kaiju database, but it is not possible to reverse engineer without the same versions of the original source data.
    * There is a specific step ([here](https://github.com/bioinformatics-centre/kaiju/blob/a0cb55179043e0143b3637822a682483d086c94f/util/kaiju-makedb#L217)) in the process of constructing the database where the sequence-names contain the corresponding TaxonID. At that point, it is necessary to insert a step to copy a list of the sequence-names to a separate file, for analysis later.
    * For the developer provided databases, that data is not available, so we contacted the developers who kindly provided it for the latest *nr+euk* database for download (see link above).
    
* **MetaPhlAn2**
    * Sequence names in the FASTA file at the heart of this DB contain either NCBI Accession ID or NCBI Gene ID within the name string.
    * Those IDs can be looked up using the NCBI accession2taxid database or the corresponding database for Gene IDS.
    
* **MTSV**
    * When `complete_genome.tar.gz` is extracted it creates a subfolder called `artifacts` with several files, one of which is called `complete_genome_ff.txt`. That file contains a line-separated list of the `.gbff` files from genbank, which are named according to an NCBI Assembly Accession ID. E.g.:
    ```/scratch/tes87/SuGR/Oct-28-2019/flat_files/GCF_000002515.2_ASM251v1_genomic.gbff
    ...```
    * The Accembly Accession IDs can be extracted into a list using sed:
    ```cat Oct-28-2019/artifacts/complete_genome_ff.txt | sed 's/.*flat_files\/\([^\.]\+\).*/\1/g' > 20191028_ff_assemblyAccns.txt
    ```
    * The resulting list can be used to look up Taxon ID using NCBI Reference Tables.
