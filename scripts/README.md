
# Database Query Tool (DQT)

This is a database query tool that can be used to query the contents of reference databases that are commonly used with taxonomic classification tools. This tool integrates the contents of many databases used in the taxonomic workflows, and it allows an end-user to query tax ids to find databases that contain information on those individual IDs. 

![](https://github.com/signaturescience/metagenomics/blob/master/scripts/DB_querytool.png)


## How to use the DQT

### query_tool.py (Using the tool)
To query for specific tax ids, a line delimited file is used as input. For example, a test file, query_file.txt, could look like the following:

```
29760
160
3223
22
9606
```

When using query_tool.py on the input file, query_file.txt, there needs to be a precomputed query database. This query database is a pickled python dictionary containing information for all of the input databases. The dictionary_maker.py and dictionary_maker_parameters.py together create a containment_dict.p file that aggregates all of the information for the databases used in the taxonomic classification tools. The first argument for the tool is the path to the containment_dict.p pickle file, and the second argument is the path to the file containing the tax id's being queried. For example:

```
python query_tool.py <PATH TO PICKLE FILE> <QUERY FILE>
```

In the specific example given here, this would be:

 ```
 python query_tool.py pickle_dir/containment_dict.p query_file.txt
 ```

### dictionary_maker.py (Building query database for the tool)
To use the dictionary_maker.py (v2), the end user only needs to modify the dictionary_maker_parameters.py file. This allows for a friendly interface, where a user only needs to change the paths and the boolean statements for what they would like to build. This therefore supports an easy-to-use method for adding databases as they are released, in addition to completely rebuilding indexes used by the tool from scratch if desired. 

Below are a couple examples of how to use the dictionary_maker.py tool. 

#### Scenario #1 - Creating a new query database from scratch
To create a new query database, the end user miust supply the paths to the downloaded databases for the different tools used by the taxonomic classification tools. All that needs to be done for this is editing paths and boolean switch-like statements
in dictionary_maker_parameters.py. To accomplish this, the use must turn on the create_full_dict switch, as well as the create switches for the databases they would like incorporate. 

For example, the dictionary_maker_parameters.py could look like:
```
## To run a process below, change value to true (change these as needed!)
calculate_jaccard = False; # This will calculate the jaccard between DBs
create_full_dict = True; # This will create a new full dictionary
use_old_containment = False; # This will import the old containment
import_refseq_dict = False; # This will import the pickled refseq
import_nucleo_dict = False; # This will import the picked genebank
import_kraken_dict = False; # This will import the picked kraken DBs
import_kaiju_dict = False; # This will import the picked kraken DBs

## The below rebuilds the dictionaries.(change these as needed!)
create_genebank_dict = True; # This will create a genebank dictionary
create_refseq_dict = True; # This will create a refseq dictionary
create_kraken_dict = True; # This will create a kraken dictionary
create_nucleo_dict = True; # This will create a nucleo dictionary
create_taxid_dict = True; # This will create a NCBI taxid dictionary
create_wgsmap_dict = True; # This will create a wgsmap dictionary
create_kaiju_dict = True; # This will import the picked kraken DBs
```

#### Scenario #2 - Adding a new DB
If the user would just like to add a database to the existing query database, then the only switch that needs to be changed is the "use_old_containment" switch. For example, if the only DB being updated is a kraken database, then the end user could supply a new path to the kraken DB in the dictionary_maker_parameters.py file:

```
## input file/directory names for processing (recommended to not change these!)
genebank_file = "genebank_livelist/GbAccList.0602.2019" # genebank file path
nucleo_file = "accession2taxid_files/nucl_gb.accession2taxid" #nt DB file path
wgsmap_file = "accession2taxid_files/nucl_wgs.accession2taxid" #wgsmap file path
kaiju_file = "kaiju_files/kaiju_nr.taxids.txt" #kaiju file path
refseq_dir = "refseq_archives" #refseq directory path
kraken_dir = "kraken_versions" #kraken directory path <------- CHANGE THIS ONE FOR KRAKEN
```

Thereafter, the following switch statements could be used:

```
## To run a process below, change value to true (change these as needed!)
calculate_jaccard = False; # This will calculate the jaccard between DBs
create_full_dict = True; # This will create a new full dictionary
use_old_containment = True; # This will import the old containment
import_refseq_dict = False; # This will import the pickled refseq
import_nucleo_dict = False; # This will import the picked genebank
import_kraken_dict = False; # This will import the picked kraken DBs
import_kaiju_dict = False; # This will import the picked kraken DBs

## The below rebuilds the dictionaries.(change these as needed!)
create_genebank_dict = False; # This will create a genebank dictionary
create_refseq_dict = False; # This will create a refseq dictionary
create_kraken_dict = False; # This will create a kraken dictionary
create_nucleo_dict = False; # This will create a nucleo dictionary
create_taxid_dict = False; # This will create a NCBI taxid dictionary
create_wgsmap_dict = False; # This will create a wgsmap dictionary
create_kaiju_dict = False; # This will import the picked kraken DBs
```

#### Scenario #3 - Rebuilding the query database from pickle files
To rebuild the query database from pickled python dictionaries, the paths to the pickled files must be changed (within dictionary_maker_parameters.py): 

 ```
 ## pickled file names (recommended to not change these!)
containment_dictionary_pickle = "containment_dict.p" #Complete dictionary (use this)
genebank_dict_pickle = "genebank_dict.p" #genebank dictionary
refseq_dict_pickle = "refseq_dict.p" #refseq dictionary
kraken_dict_pickle = "kraken_dict.p" #kraken dictionary
nucleo_dict_pickle = "nucleo_dict.p" #nucleo dictionary
taxid_dict_pickle = "taxid_dict.p" #taxid dictionary
wgsmap_dict_pickle = "wgsmap_dict.p" #wgsim dictionary
kaiju_dict_pickle = "kaiju_dict.p" #kaiju dictionary
 ```
 Note, is recommended to keep these file names the same. In addition, make sure to change the path in the 'path_for_storing_pickles' variable within dictionary_maker_parameters.py. 
 
