# Database Query Tool (DQT)

## Table of Contents
* [Workflow Overview](#Workflow-Overview)
* [Required Files](#Required-Files)
* [Workflow Execution](#Workflow-Execution)
* [Adding Custom Databases](#Adding-Custom-Databases)
* [Additional Information](#Additional-Information)

## Workflow Overview 
The Databse Query Tool is used to compare the contents of the reference databases used by various taxonomic classification tools. Specifically, since NCBI taxonomy is constantly being updated and different taxonomic classification tools use different databases, not all tools have the same reference organisms in their database. Thus, comparing outputs from one tool to another requires accounting for differences in the presence of organisms in their respective reference databases. If a taxonomic classification tool does not report an expected species in a metagenome, the DQT allows users to quickly query whether or not that species was present in the tool's reference database. The DQT allows the user to input one or more NCBI taxonomy IDs (taxids) and output a list of the databases that contain that taxid or its ancestor. While taxons from any level can be queried, this tool was specifically designed to work with species-level taxons. 

![](https://github.com/signaturescience/metagenomics-wiki/blob/master/documentation/figures/DQT%20v1.png)

## Required Files
If you have not already, you will need to clone the MetScale repository and activate your `metscale` environment (see [Install](https://github.com/signaturescience/metscale/wiki/02.-Install)) before proceeding:

```sh
[user@localhost ~]$ source activate metscale 

(metscale)[user@localhost ~]$ cd metscale/scripts

```

### Input Files

If you ran the MetScale installation correctly, the following files and directories should be present in the `metscale/scripts` directory.

| File Name | File Size | MD5 Checksum |
| ------------- | ------------- | ------------- |
| `query_tool.py` | `74 KB` | `48cf643151dc44de063d5639152a5c6c` |
| `testtax.txt` | `188 B` | `195cd9131bcbcfcc1bea2aa1793a5740` |
| `containment_dict_.json.gz` | `14 MB` | `5c19fd8ee009e23d40b4744c941c2ee2` |
| `doc/` | `4 KB` | `directory` |
| `example_input_files/` | `4 KB` | `directory` |
| `databases/` | `54 KB` | `directory` |

If you are missing any of these files, you should re-clone the MetScale repository, as per instructions in [Install](https://github.com/signaturescience/metscale/wiki/02.-Install). 

 
## Workflow Execution
![](https://github.com/signaturescience/metscale/blob/master/scripts/DQT%20(Hackathon%202022).png)

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
The command `--setup` first sets the value of `working_folder` in this file to be the path to the scripts folder containing the DQT (by default this is `metascale/scripts`). After this, it creates a folder for the NCBI taxonomy, then downloads and extracts the needed `nodes.dmp` to `path_to_ncbi_taxonomy_nodes`. Finally it decompresses the file `containment_dict.json.gz` to create the `containment_dict.json` which contains metadata about the taxa in all of the various databases in a single json file.

## Usage 

### Taxon ID Querying

The default usage of the tool is to give one or more taxids and output a text-based report showing which databases contain that taxid. The output goes to the console by default but can optionally be directed to a file. The default queried databases include several of the tools in the MetScale Taxonomic Classification Workflow, as well as versions of the NCBI RefSeq Database. The full list of databases is below.

|Tool|Database Name|Source|
|:---|:---|:---|
|RefSeq|`RefSeq_v98`|[NCBI RefSeq FTP](https://ftp.ncbi.nlm.nih.gov/refseq/release/release-catalog/archive/)|
|Kraken2|`minikraken2_v2_8GB_201904_UPDATE`|[Kraken2: minikraken2_v2 DB](https://genome-idx.s3.amazonaws.com/kraken/minikraken2_v2_8GB_201904.tgz) |
|KrakenUniq|`minikraken_20171019_8GB`|[Kraken1: minikraken_8GB `seqid2taxid.map`](https://ccb.jhu.edu/software/kraken/dl/seqid2taxid.map)|
|Kaiju|`kaiju_db_nr_euk`|(corresponds to [Kaiju NCBI *nr+euk* DB](http://kaiju.binf.ku.dk/database/kaiju_db_nr_euk_2019-06-25.tgz))|
|GenBank|`NCBI_nucl_gb`|[NCBI accn2taxid (nucl_gb)](https://ftp.ncbi.nlm.nih.gov/pub/taxonomy/accession2taxid/nucl_gb.accession2taxid.gz)|
|GenBank (WGS/TSA)|`NCBI_nucl_wgs`|[NCBI accn2taxid (nucl_wgs)](https://ftp.ncbi.nlm.nih.gov/pub/taxonomy/accession2taxid/nucl_wgs.accession2taxid.gz)|
|MetaPhlAn3|`metaphlan3`|[MetaPhlAn3 Google Drive](https://drive.google.com/drive/folders/1_HaY16mT7mZ_Z8JtesH8zCfG9ikWcLXG)|
|MTSv|`MTSV_Oct-28-2019`|[MTSv Complete Genome DB](https://rcdata.nau.edu/fofanov_lab/Compressed_MTSV_database_files/complete_genome.tar.gz)|

All RefSeq versions up to v98 can be included in the query by adding the flag `--all_refseq_versions`. 

#### Details & Example

The query functionality can be run using the following command (for example):

```
python3 query_tool.py -t <taxid_source>
```

Here, `<taxid_source>` can have one of three forms:

1. A file path to a text file with a list of line-separated taxids. Excluding the newline and leading or trailing whitespace, each line must readily convert to an integer or the procedure will raise an error.
2. The string `stdin` (i.e. `python3 query_tool.py -t stdin`). In this case a line-separated list (formatted as above) is expected from standard input. When an empty or all-whitespace line is encountered, input is terminated.
3. A single integer representing a taxid. The procedure will run for only this taxon. Additionally, the output report will have a slightly different format than for multiple IDs.

**Example**:

<details><summary>(show example)</summary>

```
(metscale) :~$ python3 query_tool.py -t testtax.txt

DB Column Names:
   1: minikraken_20171019_8GB
   2: minikraken2_v2_8GB_201904_UPDATE
   3: kaiju_db_nr_euk
   4: NCBI_nucl_wgs
   5: NCBI_nucl_gb
   6: MTSV_Oct-28-2019
   7: metaphlan3
   8: RefSeq_v98

    taxid      rank 1 2 3 4 5 6 7 8
  1251942   species - - - - 1 - - -
  1913708   species - - 1 - 1 - - -
   980453   species - - - - 1 - - -
   743653   species - - - - 1 - - -
  2196333   species - - - - 1 - - -
   146582   species - - - - 1 - - -
  1950923   species - - - 1 - - - -
  1420363   species - - - - 1 - - -
  1367599   species - - - - 1 - - -
    48959   species - - - - 1 - - -

   (...truncated...)
```

</details>


## Output
To understand how to interpret the output of the DQT we will use the example query from the previous section:

```
(metscale) :~$ python3 query_tool.py -t testtax.txt

DB Column Names:
   1: minikraken_20171019_8GB
   2: minikraken2_v2_8GB_201904_UPDATE
   3: kaiju_db_nr_euk
   4: NCBI_nucl_wgs
   5: NCBI_nucl_gb
   6: MTSV_Oct-28-2019
   7: metaphlan3
   8: RefSeq_v98

    taxid      rank 1 2 3 4 5 6 7 8
  1251942   species - - - - 1 - - -
  1913708   species - - 1 - 1 - - -
   980453   species - - - - 1 - - -
   743653   species - - - - 1 - - -
  2196333   species - - - - 1 - - -
   146582   species - - - - 1 - - -
  1950923   species - - - 1 - - - -
  1420363   species - - - - 1 - - -
  1367599   species - - - - 1 - - -
    48959   species - - - - 1 - - -

   (...truncated...)
```

For the numeric values present in the matrix there are 3 possible outcomes:
* 1: Taxid is present in that database
* 2: Taxid is not present but it's species-level ancestor is
* -: Neither is present

*Note:* For taxids above species level, only outcomes 1/0 are possible.

If only a single taxid is input, the DQT will output the rank of that taxon ID and a `Yes` or `--` (No) response for containment in each database.
```
(metscale) :~$ python3 query_tool.py -t 10
Taxon ID:         10 (rank: genus)
DB results:
          minikraken_20171019_8GB: --
 minikraken2_v2_8GB_201904_UPDATE: Yes
                  kaiju_db_nr_euk: Yes
                    NCBI_nucl_wgs: --
                     NCBI_nucl_gb: Yes
                 MTSV_Oct-28-2019: --
                       metaphlan3: --
                       RefSeq_v98: Yes
```

## Adding Custom Databases

If a database of interest is not currently present in the DQT you can easily add it to the pool! A mock database `example_db.txt` is included with MetScale and we will use this file to demonstrate how to add a database.

### Database Format
The database must be formatted as follows:
* 1: A `.txt` file
* 2: One NCBI taxid per line
* 3: New-line delimited

We can view this format by taking a look at `metscale/scripts/databases/example_db.txt`:
```
(metscale) :~$ cd metscale/scripts/databases 
(metscale) :~$ head example_db.txt
113
54362
220668
2497577
4321
332160
```

### Adding The Database

The DQT uses a configuration file `dbqt_config` to organize databate inclusion. If you ran the DQT `--setup` your config file should look like:
```
[paths]
working_folder = path/to/metscale/scripts
path_to_containment_file = ${working_folder}/containment_dict.json
path_to_ncbi_taxonomy_nodes = ${working_folder}/ncbi_taxonomy/nodes.dmp
db_folder = ~/metscale/scripts/databases

[import_locs]
path_to_db_import_manifest = ${paths:working_folder}/doc/db_import_manifest.txt
refseq_folder = ${paths:db_folder}/refseq/catalog_taxid

[formats]
accn2taxid = ('\t', 2, 1)
kraken2_inspect = ('\t', 4, 0)
first_col = ('\t', 0, 0)
refseq = ('\t', 0, 0)
seqid2taxid = ('\t', 1, 0)

[db_source_files]
example = ${paths:db_folder}/example_db.txt

[db_source_formats]
example = first_col 0
```
The default path for `db_folder` is the `~/metscale/scripts/databases/` directory, but feel free to choose any location you like. 

Under `[db_source_format]`, we point to the database file. This has already been entered for the example database, but for a real database you could either add a line below the example, or replace the example entirely. You may name your database anything you like. Inside the the parentheses, the first position indicates that the file is tab-delimited, the second position denotes the zero-indexed column in the file that contains the taxids, and the third position reports the number of lines in the header before the rows with the taxids begin. These fields of information must be updated to correspond to your database file when adding a new database.

Under `[db_source_formats]`, we specify the `first_col` format which corresponds to the format requirements we listed [above](#Database-Format). This will tell the DQT what format to expect your new database file to follow. Then we add a binary operator `0` or `1` to determine whether or not to add the database during the import step (our next step). Go ahead and change the `0` to a `1`, with `1` indicating that the database should be imported and `0` meaning that it should not. When you add your own database make sure the name here matches the name under `[db_source_files]`.

### Inspection and Import
Now that we have included all our information in the config file, we will check to verify the DQT recognizes our new database. We will run the inspection flag `-CMO` to do this.
```
(metscale) :~$ cd metscale/scripts
(metscale) :~$ python3 query_tool.py -CMO
 Database                         | In           | In      | Action
 Name                             | Config     | Contain | to be Taken
 -------------------------------- | ------------ | ------- | ----------
 RefSeq_v64                       | YES (refseq_ | YES     | (same md5, leave in)
 RefSeq_v3                        | YES (refseq_ | YES     | (same md5, leave in)
 RefSeq_v54                       | YES (refseq_ | YES     | (same md5, leave in)
 RefSeq_v42                       | YES (refseq_ | YES     | (same md5, leave in)
 RefSeq_v68                       | YES (refseq_ | YES     | (same md5, leave in)
 RefSeq_v31                       | YES (refseq_ | YES     | (same md5, leave in)
 RefSeq_v38                       | YES (refseq_ | YES     | (same md5, leave in)
 RefSeq_v36                       | YES (refseq_ | YES     | (same md5, leave in)
 MTSV_Oct-28-2019                 | no           | YES     | (leave in)
 RefSeq_v9                        | YES (refseq_ | YES     | (same md5, leave in)
 RefSeq_v49                       | YES (refseq_ | YES     | (same md5, leave in)
 RefSeq_v78                       | YES (refseq_ | YES     | (same md5, leave in)
 RefSeq_v22                       | YES (refseq_ | YES     | (same md5, leave in)
 RefSeq_v98                       | YES (refseq_ | YES     | (same md5, leave in)
 RefSeq_v6                        | YES (refseq_ | YES     | (same md5, leave in)
 RefSeq_v86                       | YES (refseq_ | YES     | (same md5, leave in)
 RefSeq_v52                       | YES (refseq_ | YES     | (same md5, leave in)
 RefSeq_v59                       | YES (refseq_ | YES     | (same md5, leave in)
 RefSeq_v16                       | YES (refseq_ | YES     | (same md5, leave in)
 RefSeq_v43                       | YES (refseq_ | YES     | (same md5, leave in)
 RefSeq_v7                        | YES (refseq_ | YES     | (same md5, leave in)
 RefSeq_v18                       | YES (refseq_ | YES     | (same md5, leave in)
 RefSeq_v80                       | YES (refseq_ | YES     | (same md5, leave in)
 RefSeq_v66                       | YES (refseq_ | YES     | (same md5, leave in)
 minikraken_20171019_8GB          | no           | YES     | (leave in)
 RefSeq_v96                       | YES (refseq_ | YES     | (same md5, leave in)
 RefSeq_v70                       | YES (refseq_ | YES     | (same md5, leave in)
 RefSeq_v93                       | YES (refseq_ | YES     | (same md5, leave in)
 RefSeq_v21                       | YES (refseq_ | YES     | (same md5, leave in)
 RefSeq_v92                       | YES (refseq_ | YES     | (same md5, leave in)
 RefSeq_v65                       | YES (refseq_ | YES     | (same md5, leave in)
 RefSeq_v84                       | YES (refseq_ | YES     | (same md5, leave in)
 RefSeq_v58                       | YES (refseq_ | YES     | (same md5, leave in)
 RefSeq_v73                       | YES (refseq_ | YES     | (same md5, leave in)
 RefSeq_v76                       | YES (refseq_ | YES     | (same md5, leave in)
 RefSeq_v30                       | YES (refseq_ | YES     | (same md5, leave in)
 RefSeq_v11                       | YES (refseq_ | YES     | (same md5, leave in)
 RefSeq_v5                        | YES (refseq_ | YES     | (same md5, leave in)
 RefSeq_v75                       | YES (refseq_ | YES     | (same md5, leave in)
 RefSeq_v57                       | YES (refseq_ | YES     | (same md5, leave in)
 NCBI_nucl_wgs                    | no           | YES     | (leave in)
 RefSeq_v41                       | YES (refseq_ | YES     | (same md5, leave in)
 RefSeq_v47                       | YES (refseq_ | YES     | (same md5, leave in)
 RefSeq_v82                       | YES (refseq_ | YES     | (same md5, leave in)
 RefSeq_v23                       | YES (refseq_ | YES     | (same md5, leave in)
 RefSeq_v95                       | YES (refseq_ | YES     | (same md5, leave in)
 RefSeq_v62                       | YES (refseq_ | YES     | (same md5, leave in)
 RefSeq_v25                       | YES (refseq_ | YES     | (same md5, leave in)
 RefSeq_v71                       | YES (refseq_ | YES     | (same md5, leave in)
 RefSeq_v27                       | YES (refseq_ | YES     | (same md5, leave in)
 RefSeq_v60                       | YES (refseq_ | YES     | (same md5, leave in)
 RefSeq_v83                       | YES (refseq_ | YES     | (same md5, leave in)
 RefSeq_v87                       | YES (refseq_ | YES     | (same md5, leave in)
 RefSeq_v17                       | YES (refseq_ | YES     | (same md5, leave in)
 RefSeq_v40                       | YES (refseq_ | YES     | (same md5, leave in)
 minikraken2_v2_8GB_201904_UPDATE | no           | YES     | (leave in)
 RefSeq_v28                       | YES (refseq_ | YES     | (same md5, leave in)
 RefSeq_v56                       | YES (refseq_ | YES     | (same md5, leave in)
 RefSeq_v37                       | YES (refseq_ | YES     | (same md5, leave in)
 RefSeq_v34                       | YES (refseq_ | YES     | (same md5, leave in)
 RefSeq_v97                       | YES (refseq_ | YES     | (same md5, leave in)
 RefSeq_v35                       | YES (refseq_ | YES     | (same md5, leave in)
 RefSeq_v19                       | YES (refseq_ | YES     | (same md5, leave in)
 RefSeq_v94                       | YES (refseq_ | YES     | (same md5, leave in)
 RefSeq_v45                       | YES (refseq_ | YES     | (same md5, leave in)
 RefSeq_v1                        | YES (refseq_ | YES     | (same md5, leave in)
 RefSeq_v77                       | YES (refseq_ | YES     | (same md5, leave in)
 RefSeq_v61                       | YES (refseq_ | YES     | (same md5, leave in)
 metaphlan3                       | no           | YES     | (leave in)
 example                          | YES (config) | no      | IMPORT
 RefSeq_v32                       | YES (refseq_ | YES     | (same md5, leave in)
 RefSeq_v67                       | YES (refseq_ | YES     | (same md5, leave in)
 RefSeq_v2                        | YES (refseq_ | YES     | (same md5, leave in)
 RefSeq_v72                       | YES (refseq_ | YES     | (same md5, leave in)
 RefSeq_v89                       | YES (refseq_ | YES     | (same md5, leave in)
 RefSeq_v44                       | YES (refseq_ | YES     | (same md5, leave in)
 RefSeq_v79                       | YES (refseq_ | YES     | (same md5, leave in)
 RefSeq_v13                       | YES (refseq_ | YES     | (same md5, leave in)
 NCBI_nucl_gb                     | no           | YES     | (leave in)
 kaiju_db_nr_euk                  | no           | YES     | (leave in)
 RefSeq_v55                       | YES (refseq_ | YES     | (same md5, leave in)
 RefSeq_v12                       | YES (refseq_ | YES     | (same md5, leave in)
 RefSeq_v14                       | YES (refseq_ | YES     | (same md5, leave in)
 RefSeq_v15                       | YES (refseq_ | YES     | (same md5, leave in)
 RefSeq_v46                       | YES (refseq_ | YES     | (same md5, leave in)
 RefSeq_v4                        | YES (refseq_ | YES     | (same md5, leave in)
 RefSeq_v88                       | YES (refseq_ | YES     | (same md5, leave in)
 RefSeq_v90                       | YES (refseq_ | YES     | (same md5, leave in)
 RefSeq_v85                       | YES (refseq_ | YES     | (same md5, leave in)
 RefSeq_v24                       | YES (refseq_ | YES     | (same md5, leave in)
 RefSeq_v39                       | YES (refseq_ | YES     | (same md5, leave in)
 RefSeq_v20                       | YES (refseq_ | YES     | (same md5, leave in)
 RefSeq_v33                       | YES (refseq_ | YES     | (same md5, leave in)
 RefSeq_v74                       | YES (refseq_ | YES     | (same md5, leave in)
 RefSeq_v29                       | YES (refseq_ | YES     | (same md5, leave in)
 RefSeq_v63                       | YES (refseq_ | YES     | (same md5, leave in)
 RefSeq_v26                       | YES (refseq_ | YES     | (same md5, leave in)
 RefSeq_v8                        | YES (refseq_ | YES     | (same md5, leave in)
 RefSeq_v81                       | YES (refseq_ | YES     | (same md5, leave in)
 RefSeq_v50                       | YES (refseq_ | YES     | (same md5, leave in)
 RefSeq_v51                       | YES (refseq_ | YES     | (same md5, leave in)
 RefSeq_v69                       | YES (refseq_ | YES     | (same md5, leave in)
 RefSeq_v10                       | YES (refseq_ | YES     | (same md5, leave in)
 RefSeq_v53                       | YES (refseq_ | YES     | (same md5, leave in)
 RefSeq_v48                       | YES (refseq_ | YES     | (same md5, leave in)
 RefSeq_v91                       | YES (refseq_ | YES     | (same md5, leave in)
```
Here we can see all the databases currently present in the DQT and all the databases ready to be imported (NOTE: the order of the databases in this output may vary). 

In the first column `In Config` we see whether or not a database has been entered into `dbqt_config`. The default MetScale databases do not need to be present in the config file. Due to the version structure of RefSeq databases they do need to be included in the config (NOTE: this has already been done for the user). You should see our `example` database showing `YES (config)` in this column. 

The second column `In Contain` represents if a database is already present in the DQT. This should be `YES` for every database other than our new `example` database.

The third column `Action to be Taken` tells us what the DQT will do during import. 
* 1: For any database in the config file that is already present, the DQT will check its `md5` and replace the database if the `md5` differs. If it does not differ, nothing will happen and we will see `(same md5, leave in)`. 
* 2: For databases not in the config file but already present the DQT will just leave them in `(leave in)`. 
* 3: For databases entered in the config file and new to the DQT we will see an output of `IMPORT`, which should be what you see for `example`. 

Now that we have verified the DQT recognizes our new database we can import it! We import our database using the `-BCD` flag. 
```
(metscale) :~$ python3 query_tool.py -BCD
Summary of sources to be imported: (count = 1)
   example      /path/to/metscale/scripts/databases/example_db.txt
[query_tool.py (1551)] INFO: Containment Dictionary Summary (all_refseq = False)
   ***
    # Databases: 106 (98 RefSeq, 8 other)
  Latest RefSeq: v98

Main Databases:
 Database Name                        # Taxa  Date Parsed
 ---------------------------------  --------  --------------------
 minikraken_20171019_8GB               10624  2020-02-24 15:56:01
 minikraken2_v2_8GB_201904_UPDATE      21112  2020-02-24 15:56:01
 kaiju_db_nr_euk                      224818  2020-02-24 15:56:01
 NCBI_nucl_wgs                         74902  2020-04-11 14:16:57
 NCBI_nucl_gb                        1893626  2020-04-11 14:20:05
 MTSV_Oct-28-2019                      24422  2020-05-19 02:28:52
 metaphlan3                            13519  2021-07-23 08:46:51
 example                                   7  2021-08-04 09:21:15
 RefSeq_v98                            98406  2020-02-24 15:56:00


[query_tool.py (1110)] INFO: Saving containment dictionary to /path/to/metscale/scripts/containment_dict.json
```
You should see the above output now displaying the new pool of databases in the DQT. Our `example` database is there! The process is now complete. You can replicate all these steps with as many custom databases as you would like. 

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
