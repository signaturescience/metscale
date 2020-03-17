
# Database Query Tool (DQT)

This tool is used to compare the contents of the reference databases used by the various taxonomic classification tools. Specifically, since the NCBI taxonomy is constantly changing and being updated, not all tools may be using the same version. Thus, comparing outputs from one tool to another requires accounting for differences in the coverage of their respective reference databases.

In its most basic form, the tool allows the user to input one or more taxon IDs and output a list of the databases that contain that taxon ID. The metadata about the taxa in all of the various databases is contained in a single pickle file called (by default) `containment_dict.p`. The tool also contains several algorithms to construct, examine, add to, update or replace this file. It additionally has several functions that interface with the NCBI taxonomy to facilitate interpretation.

## Requirements

* Python 3
* NCBI Taxonomy (local copy of `nodes.dmp`, included here: [zip](ftp://ftp.ncbi.nlm.nih.gov/pub/taxonomy/taxdmp.zip) [tar.gz](ftp://ftp.ncbi.nlm.nih.gov/pub/taxonomy/taxdump.tar.gz))


## Usage 
*Note: a complete list of the commands and options is available using the `--help` flag at the command line:*

```python3 query_tool.py --help
```

### Taxon ID Querying

The default usage of the tool is to give one or more taxon IDs and output a text-based report showing which databases contain that taxon ID. The output goes to the console by default but can optionally be directed to a file. The included metadata file includes many databases of interest, including several of tools in the Taxon Classification workflows and all versions of RefSeq through v98, and is described in more detail below.

<details><summary>
##### Details & Example</summary>

The query tool can be run using the following command (for example):

```
python3 query_tool.py -t <taxid_source>
```

Here, `<taxid_source>` can have one of three forms:

1. A file path to a text file with a list of line-separated taxon IDs. Excluding the newline and leading or trailing whitespace, each line must readily convert to an integer or the procedure will raise an error.
2. The string `stdin` (i.e. `python3 query_tool.py -t stdin`). In this case a line-separated list (formatted as above) is expected from standard input. When an empty or all-whitespace line is encountered, input is terminated.
3. A single integer representing a taxon ID. The procedure will run for only this taxon. Additionally, the output report will have a slightly different format than for multiple IDs.

**Example**

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

### Inspecting and Editing Metadata

The tool additionally contains several processes to update or change the metadata in `containment_dict.p`.

<details><summary>
##### New Database Definitions</summary>

To import a new database, the set of taxon IDs included must be contained somehow in a delimited text file (duplicates OK), which covers many common default metadata formats. If it does not exist, it must be created. A new database, therefore, must be specified by 1) a name, 2) a path to a delimited text file, 3) a format name specified in the config file. (Format specifications are documented in `dbqt_config`, but are simply a python tuple object containing `(<delimiter>, <column>, <# header rows to skip>)`. See `dbqt_config` for examples and additional documentation.)

Before the metadata can be updated or appended, a roster of new databases must be specified. This can be done using either a config file or a tab-delimited text file in a specified form. (See comments in the default config file for how to use that. To see the specs for a roster as a tab-delimited text file, run `python3 query_tool.py --print_source_file_list_specs`.) In either case, an option is available to skip a particular database which can save time in parsing without heavy file editing.

**RefSeq**: The exception to the database definition is RefSeq. In that case, a folder should be given rather than a file name. The tool recognizes this database name and will gather all the files in the folder and try to parse the names for RefSeq version numbers.  **The tool assumes that all files are in the form `RefSeq-release##.catalog.taxid`**. It uses python string splitting (not regex matching) to parse the version number, so filenames that are not in this form could cause an error.
</details>

<details><summary>
##### Commands:</summary>

Four procedures dealing with the metadata are available at the command-line (corresponding command-line flag in parentheses):

* **Inspect Database Source Roster** (`-IFL`): Checks the source roster (however provided) for validity and prints the results to the console.
* **Inspect Existing Taxon-Containment Metadata File (containment_dict.p)** (`-ICD`): Reads the default Metadata file (e.g. `containment_dict.p`) and prints a report of its contents to the console.
* **Generate Metadata File Build Plan (i.e. Compare Source/Target)** (`-CMO`): Runs each of the two procedures above but does not print reports. Instead, compares the files in the source roster to the contents of the exsiting metadata file to identify which files from the roster should be imported (either to replace a database in the existing Metadata or as a new addition). Reports results to the console.
* **Build Taxon-Containment Metadata File** (`-BCD`): Runs the above procedure to generate the build plan and then executes it. 

</details>

### Config File

<details><summary>
##### Description</summary>

The tool relies on a config file for several key settings. Many of these settings can be overridden by command-line arguments (any conflicting command-line argument given will be prioritized), but values stored in the config will be used as defaults. The default config file is [`dbqt_config`](../blob/master/scripts/dbqt_config), though a different file can be given at the command line. 

which additionally contains comments documenting the requirements for the sections other than `[paths]`.

The file is read using the Python [`configparse`](https://docs.python.org/3.7/library/configparser.html) module, so the documentation of the file format can be found [here](https://docs.python.org/3.7/library/configparser.html#supported-ini-file-structure). 
</details>

<details><summary>
##### Contents</summary>

The `[paths]` section specifies a few important paths for the tool:

* **Working Folder** (`working_folder`): Not strictly used if all other files and folders required by the tool are given explicitly, but it is a useful relative path for storing the NCBI taxonomy, any database files that are added, output files, etc... Can be overridden via command-line using `-wd` flag. (Defaults to the folder containing `query_tool.py`.) 

* **Containment Metadata File** (`path_to_pickle_file`): The path to the desired pickle file with the taxon-containment metadata. Can be overridden via command-line using `-pf` flag. (Default: `scripts/pickle_dir`).

* **NCBI Taxonomy Nodes File** (`path_to_ncbi_taxonomy_nodes`): The path to the downloaded NCBI-taxonomy `nodes.dmp` file. (No Default.)

* **Database Source Roster (Text-File)** (`path_to_source_file_list`): (OPTIONAL) The path to a tab-delimited text file containing a roster of databases and associated taxon list files. This can be given in addition to or instead of the roster via the config file. Can be overridden via command-line using `-dbs` flag.

The remaining sections (`[formats]`, `[db_source_files]`, and `[db_source_formats]`) are used to define the specifications for any source files to be imported. This can be left empty if the only planned use is to query the included metadata. See [`dbqt_config`](../blob/master/scripts/dbqt_config) for documentation in comments about what each of these sections must contain.

</details>

### Additional Command-line Arguments

* __`--all_refseq_versions`__: RefSeq is treated differently than other databases in the tool. Since many versions are included by default, only the latest version is included in the output unless this option is given at the command-line.
* __Logging__: the tool does extensive logging of the steps involved. That log can be sunk to a file using the `--logfile` option. It can also be made more or less verbose using the `--debug` (more) or '-qt' (less) or `-vqt` flags.
* __`-o/--output`__: Specifies a file for the output of the procedure. If this is printing a report then it will print the report to the output file instead of the console. This applies to most of the procedures.

**Note:** Only one argument specifying a procedure can be specified at a time. These are the arguments whose short-hand is three capital letters (e.g. `-BCD`) or whose long-hand starts with `--cmd_` (e.g. `--cmd_inspect_filelist`).

## Packaged Taxon-Containment [Metadata File](../blob/master/scripts/pickle_dir/containment_dict.p)

### Databases Included
The [containment metadata file](../blob/master/scripts/pickle_dir/containment_dict.p) packaged with this repo includes a number of databases relevant to the taxon classification workflows in MetScale. Below is a table of the databases included:

|Database|Metadata Key|Source|
|:---|:---|:---|
|RefSeq|RefSeq_v##|[NCBI RefSeq FTP](ftp://ftp.ncbi.nlm.nih.gov/refseq/release/release-catalog/archive/)|
|Kraken2* |minikraken2_v2_8GB_201904_UPDATE |[Kraken2: minikraken2_v2 DB](ftp://ftp.ccb.jhu.edu/pub/data/kraken2_dbs/minikraken2_v2_8GB_201904_UPDATE.tgz) |
|Krakenuniq* |minikraken_20171019_8GB|[kraken1: minikraken_8GB `seqid2taxid.map`](https://ccb.jhu.edu/software/kraken/dl/seqid2taxid.map)|
|Kaiju* |kaiju_db_nr_euk|(corresponds to [Kaiju NCBI *nr+euk* DB](http://kaiju.binf.ku.dk/database/kaiju_db_nr_euk_2019-06-25.tgz))|
|GenBank|NCBI_nucl_gb|[NCBI accn2taxid (nucl_gb)](ftp://ftp.ncbi.nlm.nih.gov/pub/taxonomy/accession2taxid/nucl_gb.accession2taxid.gz)|
|GenBank (WGS/TSA)|NCBI_nucl_wgs|[NCBI accn2taxid (nucl_wgs)](ftp://ftp.ncbi.nlm.nih.gov/pub/taxonomy/accession2taxid/nucl_wgs.accession2taxid.gz)|

*Notes:*

* __\*Kraken2/Krakenuniq/Kaiju__:
	* Taxon ID files specifically match databases used by Taxon Classification workflows.
	* Each database required specific research to identify proper Taxon sets (see documentation).
* __RefSeq__:
	* Includes RefSeq versions 1 through 98.
* __GenBank/GenBank (WGS/TSA)__:
	* Pulled directly from the NCBI's broadest [accession-to-taxonID database](ftp://ftp.ncbi.nlm.nih.gov/pub/taxonomy/accession2taxid/).


### Data Sources 

The process for downloading all of the data included in the packaged metadata file is re-created (approximately) in the script `prepare_taxid_metadata.sh`. Below is a description of the process for each database:

<details><summary>
##### NCBI Sources:</summary>

* **RefSeq**
    * The RefSeq catalog contains all Accessions included in a release, with a column for NCBI taxon ID. Downloading the catalog file directly is sufficient for importing with `query_tool.py`.
* **GenBank & GenBank (WGS/TSA)**:
    * These are downloaded directly as tab-delimited text files. Due to file size, it is best to use bash commands to create a file with only the unique taxon IDs for query_tool to parse:
    ```cat $accn2taxid/nucl_wgs.accession2taxid | cut -f 3 | sort | uniq > $accn2taxid/nucl_wgs.taxid_list.txt
    ```
* **NCBI Taxonomy**
    * Taxonomy can be downloaded from [NCBI] directly. After extracting, `nodes.dmp` should be in the target folder. That file path should be given in the config file (see above).
</details> 
   
<details><summary>
##### Taxon Classification Tool-Specific Databases:</summary>

* **Krakenuniq**
    * Krakenuniq uses databases in the same form as Kraken1. When those DBs were packaged by the developers, they included a file called `seqid2taxid.map`. The provenenace of that particular file is not well-documented as far as I can tell, although it is ostensibly a mapping from database sequence to taxon ID, which is what we need. 
    * That file is tab-delimited, so it can be retreived from the Kraken1 website (link above) and imported directly by `query_tool.py`.
* **Kraken2**
    * Kraken2 usus a very different (non-human-readable) database format. For this format the command `kraken2-inspect` can produce the list of Taxon IDs:
    ```kraken2-inspect --db $kraken2_db_fold --report-zero-counts > $kraken2_work_fold/kraken2_inspect_taxonids.txt
    ```
* **Kaiju**
    * For Kaiju, pulling the list of taxa is possible when creating a Kaiju database, but it is not possible to reverse engineer without the same versions of the original source data.
    * There is a specific step ([here](https://github.com/bioinformatics-centre/kaiju/blob/a0cb55179043e0143b3637822a682483d086c94f/util/kaiju-makedb#L217)) in the process of constructing the database where the sequence-names contain the corresponding TaxonID. At that point, it is necessary to insert a step to copy a list of the sequence-names to a separate file, for analysis later.
    * For the developer provided databases, that data is not available, so we contacted the developers who kindly provided it for the latest *nr+euk* database for download (see link above).
</details> 
    




