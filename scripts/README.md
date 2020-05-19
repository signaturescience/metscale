# Database Query Tool (DQT)

This tool is used to compare the contents of the reference databases used by the various taxonomic classification tools. Specifically, since the NCBI taxonomy is constantly changing and being updated, not all tools may be using the same version. Thus, comparing outputs from one tool to another requires accounting for differences in the coverage of their respective reference databases.

In its most basic form, the tool allows the user to input one or more taxon IDs and output a list of the databases that contain that taxon ID. The metadata about the taxa in all of the various databases is contained in a single json file called (by default) `containment_dict.json`. The tool also contains several algorithms to construct, examine, add to, update or replace this file. It additionally has several functions that interface with the NCBI taxonomy to facilitate interpretation.

## Table of Contents
* [Getting Started](#Getting-Started)
* [Usage](#Usage)
     * [Taxon ID Querying](#Taxon-ID-Querying)
     * [Inspecting and Editing Metadata](#Inspecting-and-Editing-Metadata)
     * [Config File](#Config-File)
     * [Additional Command-line Arguments](#Additional-Command-line-Arguments)
* [Packaged Taxon-Containment Metadata File](#Packaged-Taxon-Containment-Metadata-File)
     * [Databases Included](#Databases-Included)   
     * [Data Sources](#Data-Sources)

## Initial Configuration and Setup

### Quick Start:
After cloning the Metscale reposotory, some configuration is necessary before use. It can be done automatically using default settings by runing the command:
```
python3 query_tool.py --setup
```
That will populate the setting `working_folder` in the default config file with the home folder of the DQT. Following that, the tool should be ready for use.

### Detailed Settings
The command above will automatically set the three important paths the DQT needs to run. Two of them are files: 1) the repository of taxon coverage information for the various MetScale tools, and 2) the full reference taxonomy maintained by NCBI. The third is a working folder for any outputs that are provided. Those are the first three settings listed in the config file:
```
[paths]
working_folder = 
path_to_containment_file = ${working_folder}/containment_dict.json
path_to_ncbi_taxonomy_nodes = ${working_folder}/ncbi_taxonomy/nodes.dmp
```
The command above first sets the value of the working_folder in this file to be the path to the scripts folder containing the DQT. After this, it creates a folder for the NCBI taxonomy, then downloads and extracts the file needed to the path in the third setting above. Finally it decompresses the file `containment_dict.json.gz` to create the file in the middle entry abvoe.

These paths can be changed if needed, but by design they can be left alone except for periodic updates.

## Usage 
*Note: a complete list of the commands and options is available using the `--help` flag at the command line:*

```
python3 query_tool.py --help
```

### Taxon ID Querying

The default usage of the tool is to give one or more taxon IDs and output a text-based report showing which databases contain that taxon ID. The output goes to the console by default but can optionally be directed to a file. The included metadata file includes many databases of interest, including several of tools in the Taxon Classification workflows and all versions of RefSeq through v98, and is described in more detail below.


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

### Inspecting and Editing Metadata

The tool additionally contains several processes to update or change the metadata in `containment_dict.p`.

#### New Database Definitions

To import a new database, the set of taxon IDs included must be contained somehow in a delimited text file (duplicates OK), which covers many common default metadata formats. If it does not exist, it must be created. A new database, therefore, must be specified by 1) a name, 2) a path to a delimited text file, 3) a format name specified in the config file. (Format specifications are documented in `dbqt_config`, but are simply a python tuple object containing `(<delimiter>, <column>, <# header rows to skip>)`. See `dbqt_config` for examples and additional documentation.)

Before the metadata can be updated or appended, a roster of new databases must be specified. This can be done using either a config file or a tab-delimited text file in a specified form. (See comments in the default config file for how to use that. To see the specs for a roster as a tab-delimited text file, run `python3 query_tool.py --print_db_import_manifest_specs`.) In either case, an option is available to skip a particular database which can save time in parsing without heavy file editing.

**RefSeq**: The exception to the database definition is RefSeq. In that case, a folder should be given rather than a file name. The tool recognizes this database name and will gather all the files in the folder and try to parse the names for RefSeq version numbers.  **The tool assumes that all files are in the form `RefSeq-release##.catalog.taxid`**. It uses python string splitting (not regex matching) to parse the version number, so filenames that are not in this form could cause an error.

#### Commands

Four procedures dealing with the metadata are available at the command-line (corresponding command-line flag in parentheses):

* **Inspect Database Source Roster** (`-IFL`): Checks the source roster (however provided) for validity and prints the results to the console.
* **Inspect Existing Taxon-Containment Metadata File (containment_dict.json)** (`-ICD`): Reads the default Metadata file (e.g. `containment_dict.p`) and prints a report of its contents to the console.
* **Generate Metadata File Build Plan (i.e. Compare Source/Target)** (`-CMO`): Runs each of the two procedures above but does not print reports. Instead, compares the files in the source roster to the contents of the exsiting metadata file to identify which files from the roster should be imported (either to replace a database in the existing Metadata or as a new addition). Reports results to the console.
* **Build Taxon-Containment Metadata File** (`-BCD`): Runs the above procedure to generate the build plan and then executes it. 

### Config File


The tool relies on a config file for several key settings. Many of these settings can be overridden by command-line arguments (any conflicting command-line argument given will be prioritized), but values stored in the config will be used as defaults. The default config file is [`dbqt_config`](../blob/master/scripts/dbqt_config), though a different file can be given at the command line. 

The file is read using the Python [`configparse`](https://docs.python.org/3.7/library/configparser.html) module, so the documentation of the file format can be found [here](https://docs.python.org/3.7/library/configparser.html#supported-ini-file-structure). 

#### Contents

The `[paths]` section specifies a few important paths for the tool:

* **Working Folder** (`working_folder`): Not strictly used if all other files and folders required by the tool are given explicitly, but it is a useful relative path for storing the NCBI taxonomy, any database files that are added, output files, etc... Can be overridden via command-line using `-wd` flag. (Defaults to the folder containing `query_tool.py`.) 

* **Containment Metadata File** (`path_to_containment_file`): The path to the desired pickle file with the taxon-containment metadata. Can be overridden via command-line using `-pf` flag. (Default: `scripts/pickle_dir`).

* **NCBI Taxonomy Nodes File** (`path_to_ncbi_taxonomy_nodes`): The path to the downloaded NCBI-taxonomy `nodes.dmp` file. (No Default.)

The `[import_locs]` section specifies a two more paths useful for importing new databases, particular those which might be regularly updated and re-imported:

* **Database Source Roster (Text-File)** (`path_to_db_import_manifest`): (OPTIONAL) The path to a tab-delimited text file containing a roster of databases and associated taxon list files. This can be given in addition to or instead of the roster via the config file. Can be overridden via command-line using `-dbs` flag.

* **RefSeq Folder** (`refseq_folder`): (OPTIONAL) The path to a folder containing text files for many refseq databases. This should ideally not be needed unless re-importing many old versions of RefSeq (though they are contained in the packaged containment_dict.json.gz). In that event, however, the entire set can be imported by specifying this single folder in the manifest or in the config file.

The remaining sections (`[formats]`, `[db_source_files]`, and `[db_source_formats]`) are used to define the specifications for any source files to be imported. This can be left empty if the only planned use is to query the included metadata. See [`dbqt_config`](../blob/master/scripts/dbqt_config) for documentation in comments about what each of these sections must contain.

### Additional Command-line Arguments

* __`--all_refseq_versions`__: RefSeq is treated differently than other databases in the tool. Since many versions are included by default, only the latest version is included in the output unless this option is given at the command-line.
* __Logging__: the tool does extensive logging of the steps involved. That log can be sunk to a file using the `--logfile` option. It can also be made more or less verbose using the `--debug` (more) or '-qt' (less) or `-vqt` flags.
* __`-o/--output`__: Specifies a file for the output of the procedure. If this is printing a report then it will print the report to the output file instead of the console. This applies to most of the procedures.

**Note:** Only one argument specifying a procedure can be specified at a time. These are the arguments whose short-hand is three capital letters (e.g. `-BCD`) or whose long-hand starts with `--cmd_` (e.g. `--cmd_inspect_filelist`).

## Packaged Taxon-Containment [Metadata File](../blob/master/scripts/containment_dict.json.gz)

(See [doc folder](../blob/master/scripts/doc) for details about this file.

