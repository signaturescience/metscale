# Database Query Tool (DQT)

## Table of Contents
* [Workflow Overview](#Workflow-Overview)
* [Required Files](#Required-Files)
* [Workflow Execution](#Workflow-Execution)
* [Additional Information](#Additional-Information)

## Workflow Overview 
The Databse Query Tool is used to compare the contents of the reference databases used by the various taxonomic classification tools. Specifically, since the NCBI taxonomy is constantly changing and being updated, not all tools may be using the same version. Thus, comparing outputs from one tool to another requires accounting for differences in the coverage of their respective reference databases.In its most basic form, the DQT allows the user to input one or more taxon IDs and output a list of the databases that contain that taxon ID, or that contain a species-level ancestor.

![](https://github.com/signaturescience/metagenomics-wiki/blob/master/documentation/figures/DQT%20v1.png)

## Required Files
If you have not already, you will need to clone the MetScale repository and activate your metag environment [Install](https://github.com/signaturescience/metagenomics/wiki/02.-Install) before proceeding:

```sh
[user@localhost ~]$ source activate metag 

(metag)[user@localhost ~]$ cd metagenomics/scripts

```

### Input Files

If you ran the MetScale installation correctly, the following files should be present in the `metagenomics/scripts` directory.

| File Name | File Size | MD5 Checksum |
| ------------- | ------------- | ------------- |
| `databases.png` | `177 KB` | `a37ee46c79ddbf59421f961fa7e440fb` |
| `DB_querytool.png` | `112 KB` | `f56f449cecc4851d85adac8e25f5eb0d` |
| `dictionary_maker_parameters.py` | `3.5 KB` | `27db92f1cecec971f18dfaf693142a2a` |
| `dictionary_maker.py` | `12 KB` | `175100ab02be48b65a2a21bd0c9c555b` |
| `query_tool.py` | `1.9 KB` | `6e3829b603ddf6d492b35aff5fe871d0` | 

If you are missing any of these files, you should re-clone the MetScale repository, as per instructions in [Install](https://github.com/signaturescience/metagenomics/wiki/02.-Install). 

 
## Workflow Execution
### Quick Start:
After cloning the MetScale repository, some configuration is necessary before use. It can be done automatically using default settings by running the command:
```
python3 query_tool.py --setup
```
That will populate the setting `working_folder` in the default config file with the home folder of the DQT. Following that, the tool should be ready for use.

### Detailed Settings
The `--setup` command will automatically set the three important paths the DQT needs to run:
* 1) The repository of taxon coverage information for the various MetScale tools
* 2) The full reference taxonomy maintained by NCBI. 
* 3) The working folder for any outputs that are provided. 
These are the first three settings listed in the config file:
```
[paths]
working_folder = 
path_to_containment_file = ${working_folder}/containment_dict.json
path_to_ncbi_taxonomy_nodes = ${working_folder}/ncbi_taxonomy/nodes.dmp
```
The command `--setup` first sets the value of `working_folder` in this file to be the path to the scripts folder containing the DQT (by default this is `metagenomics/scripts`). After this, it creates a folder for the NCBI taxonomy, then downloads and extracts the needed `nodes.dmp` to `path_to_ncbi_taxonomy_nodes`. Finally it decompresses the file `containment_dict.json.gz` to create the `containment_dict.json` which contains metadata about the taxa in all of the various databases in a single json file.

## Usage 

### Taxon ID Querying

The default usage of the tool is to give one or more taxon IDs and output a text-based report showing which databases contain that taxon ID. The output goes to the console by default but can optionally be directed to a file. The default queried databases include several of the tools in the Taxon Classification workflows and RefSeq_v98. The full list of databases is below.

|Tool|Database Name|Source|
|:---|:---|:---|
|RefSeq|`RefSeq_v98`|[NCBI RefSeq FTP](https://ftp.ncbi.nlm.nih.gov/refseq/release/release-catalog/archive/)|
|Kraken2|`minikraken2_v2_8GB_201904_UPDATE`|[Kraken2: minikraken2_v2 DB](https://ftp.ccb.jhu.edu/pub/data/kraken2_dbs/minikraken2_v2_8GB_201904_UPDATE.tgz) |
|Krakenuniq|`minikraken_20171019_8GB`|[kraken1: minikraken_8GB `seqid2taxid.map`](https://ccb.jhu.edu/software/kraken/dl/seqid2taxid.map)|
|Kaiju|`kaiju_db_nr_euk`|(corresponds to [Kaiju NCBI *nr+euk* DB](http://kaiju.binf.ku.dk/database/kaiju_db_nr_euk_2019-06-25.tgz))|
|GenBank|`NCBI_nucl_gb`|[NCBI accn2taxid (nucl_gb)](https://ftp.ncbi.nlm.nih.gov/pub/taxonomy/accession2taxid/nucl_gb.accession2taxid.gz)|
|GenBank (WGS/TSA)|`NCBI_nucl_wgs`|[NCBI accn2taxid (nucl_wgs)](https://ftp.ncbi.nlm.nih.gov/pub/taxonomy/accession2taxid/nucl_wgs.accession2taxid.gz)|
|MetaPhlAn2|`metaphlan_mpa_v20_m200`|[MetaPhlAn2 Google Drive](https://drive.google.com/drive/folders/1_HaY16mT7mZ_Z8JtesH8zCfG9ikWcLXG)|
|MTSV|`MTSV_Oct-28-2019`|[MTSV Complete Genome DB](https://rcdata.nau.edu/fofanov_lab/Compressed_MTSV_database_files/complete_genome.tar.gz)|

All RefSeq versions up to v98 can be included in the query by adding the flag `--all_refseq_versions`. Currently the DQT does not support user-end removal or addition of databases. These features are planned to be part of future releases. 

#### Details & Example

The query tool can be run using the following command (for example):

```
python3 query_tool.py -t <taxid_source>
```

Here, `<taxid_source>` can have one of three forms:

1. A file path to a text file with a list of line-separated taxon IDs. Excluding the newline and leading or trailing whitespace, each line must readily convert to an integer or the procedure will raise an error.
2. The string `stdin` (i.e. `python3 query_tool.py -t stdin`). In this case a line-separated list (formatted as above) is expected from standard input. When an empty or all-whitespace line is encountered, input is terminated.
3. A single integer representing a taxon ID. The procedure will run for only this taxon. Additionally, the output report will have a slightly different format than for multiple IDs.

**Example**:

<details><summary>(show example)</summary>

```
(metag) :~$ python3 query_tool.py -t testtax.txt

DB Column Names:
   1: minikraken_20171019_8GB
   2: minikraken2_v2_8GB_201904_UPDATE
   3: kaiju_db_nr_euk
   4: NCBI_nucl_gb
   5: NCBI_nucl_wgs
   6: RefSeq_v98

    taxid      rank 0 1 2 3 4 5
  1913708   species - - 1 1 - -
   980453   species - - - 1 - -
   146582   species - - - 1 - -
  1950923   species - - - - 1 -
  1420363   species - - - 1 - -
  1367599   species - - - 1 - -
    48959   species - - - 1 - -
  1594871   species - - - 1 - -
    69507     genus - - - - - -
   241522 subspecies - - - 1 - -
  1068967   species - - - 1 - -
  1007150   species - - - 1 - -
   498356   no rank - 2 1 1 - -
   
   (...truncated...)
```

</details>


## Output
To understand how to interpret the output of the DQT we will use the example query from the previous section:

```
(metag) :~$ python3 query_tool.py -t testtax.txt

DB Column Names:
   1: minikraken_20171019_8GB
   2: minikraken2_v2_8GB_201904_UPDATE
   3: kaiju_db_nr_euk
   4: NCBI_nucl_gb
   5: NCBI_nucl_wgs
   6: RefSeq_v98

    taxid      rank 0 1 2 3 4 5
  1913708   species - - 1 1 - -
   980453   species - - - 1 - -
   146582   species - - - 1 - -
  1950923   species - - - - 1 -
  1420363   species - - - 1 - -
  1367599   species - - - 1 - -
    48959   species - - - 1 - -
  1594871   species - - - 1 - -
    69507     genus - - - - - -
   241522 subspecies - - - 1 - -
  1068967   species - - - 1 - -
  1007150   species - - - 1 - -
   498356   no rank - 2 1 1 - -
   
   (...truncated...)
```

For the numeric values present in the matrix there are 3 possible outcomes:
* 1: Taxon ID is present in that database
* 2: Taxon ID is not present but it's species-level ancestor is
* -: Neither is present

*Note:* For taxon IDs above species level, only outcomes 1/0 are possible.

If only a single taxon ID is input, the DQT will output the rank of that taxon ID and a `Yes` or `--` (No) response for containment in each database.
```
(metag) :~$ python3 query_tool.py -t 10
Taxon ID:         10 (rank: genus)
DB results:
                minikraken_20171019_8GB: --
       minikraken2_v2_8GB_201904_UPDATE: Yes
                        kaiju_db_nr_euk: Yes
                       MTSV_May-22-2019: --
 MasonLab_Covid_Kraken_microDB_20200313: --
                          NCBI_nucl_wgs: --
                 metaphlan_mpa_v20_m200: --
                           NCBI_nucl_gb: Yes
                       MTSV_Oct-28-2019: --
                             RefSeq_v98: Yes
```

## Additional Information

A complete list of the commands and options is available using the `--help` flag at the command line:

```
python3 query_tool.py --help
```

### Logging Options:
Options related to how much information the program prints while running:

  `-qt`, `--quiet`      If given, disables logging to the console except for
                        warnings or errors (overrides `--debug`)
                        
  -`vqt`, `--veryquiet` If given, disables logging to the console (overrides
                        `--quiet` and `--debug`)
                        
  `--debug`             If given, enables more detailed logging useful in
                        debugging.
