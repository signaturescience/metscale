#! usr/bin/python
# Author: Dreycey Albin
# Update(s):10/31/2019, 11/01/2019

"""
NOTES:
1. If using create_full_dict, make sure to turn on a couple of the other
databases. Turn on any database you would like to integrate into the final
containment file. 

2. If using calculate_jaccard, make sure either the create or import 
is true for kraken and refseq. This will calculate the jaccard index
between both of these databases. 

3. If trying to rebuilding the the final containment pickle using databases,
then change the paths to the databases below. Thereafter, make sure to change
the create switches to True for the databases being added. 

4. If one would like to add a database to the current containment dictionary,
then turn the "use_old_containment" switch to True. In addition, follow the steps
in 3, adding the new database to the paths below and updating the "create" switch
for that particular database. Lastly, it is advised to move the previous containment
file to a new directory for backup, as the newly created one will overwrite the 
previous. This can be achived by changing the path titled "path_for_old_containment".
"""

## Major paths (change these as needed!)
path = 'PATH TO WORKING DIRECTORY';
path_for_storing_pickles = 'PATH TO THE PICKLED FILES DIRECTORY';
path_for_old_containment = 'PATH TO THE DIRECTORY FOR THE OLD containment_dict.py';

## To run a process below, change value to true (change these as needed!)
calculate_jaccard = False; # This will calculate the jaccard between DBs
create_full_dict = False; # This will create a new full dictionary
use_old_containment = False; # This will import the old containment
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

## input file/directory names for processing (recommended to not change these!)
genebank_file = "genebank_livelist/GbAccList.0602.2019" # genebank file path
nucleo_file = "accession2taxid_files/nucl_gb.accession2taxid" #nt DB file path
wgsmap_file = "accession2taxid_files/nucl_wgs.accession2taxid" #wgsmap file path
kaiju_file = "kaiju_files/kaiju_nr.taxids.txt" #kaiju file path
refseq_dir = "refseq_archives" #refseq directory path
kraken_dir = "kraken_versions" #kraken directory path


## pickled file names (recommended to not change these!)
containment_dictionary_pickle = "containment_dict.p" #Complete dictionary (use this)
genebank_dict_pickle = "genebank_dict.p" #genebank dictionary
refseq_dict_pickle = "refseq_dict.p" #refseq dictionary
kraken_dict_pickle = "kraken_dict.p" #kraken dictionary
nucleo_dict_pickle = "nucleo_dict.p" #nucleo dictionary
taxid_dict_pickle = "taxid_dict.p" #taxid dictionary
wgsmap_dict_pickle = "wgsmap_dict.p" #wgsim dictionary
kaiju_dict_pickle = "kaiju_dict.p" #kaiju dictionary



