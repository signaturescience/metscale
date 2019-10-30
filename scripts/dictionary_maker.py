#! usr/bin/python
# Author: Dreycey Albin
# Update(s):07/11/2019 

import pickle
import os
import glob


# purpose of this script
"""
This script will be used to store the information of the databases, allowing
a quick assesment of what databases contain what organisms. Overall, this will
give insights into why a certain database may not be able to classify an organism
of interest. In addition, it should allow for reasoning the pitfalls of certain 
public databases.
"""

# parameters

## Paths
path_for_storing_pickles = "pickle_dir/"
#TODO: Move to an args sections
#TODO: delete all these if 0 sections
path="/data/home/cgrahlmann/mondavi/metagenomics/scripts/"
#path = "/data/project_data/dhs_db/database_comparisons/scripts_for_informative_files/"

## outputfile names
containment_dictionary_pickle = "containment_dict.p"
genebank_dict_pickle = "genebank_dict.p"
refseq_dict_pickle = "refseq_dict.p"
kraken_dict_pickle = "kraken_dict.p"
nucleo_dict_pickle = "nucleo_dict.p"
taxid_dict_pickle = "taxid_dict.p"
wgsmap_dict_pickle = "wgsmap_dict.p"

## input file names for processing
genebank_file = "GbAccList.0602.2019"
##refseq_file = "RefSeq-release1_catalog"

nucleo_file = "nucl_gb.accession2taxid"
wgsmap_file = "nucl_wgs.accession2taxid"

## path to refseq directory
refseq_dir = "refseq_archives"

## path to kraken directory
kraken_dir = "kraken_versions"

# opening the files
genebank_file_open = open(path + genebank_file)
##refseq_file_open = open(path + refseq_file)

nucleo_file_open = open(path + nucleo_file)
#wgsmap_file_open = open(path + wgsmap_file)

if 0:
    # reading in the files
    genebank_file_read = genebank_file_open.readlines()


##refseq_file_read = refseq_file_open.readlines()
nucleo_file_read = nucleo_file_open.readlines()
#wgsmap_file_read = wgsmap_file_open.readlines()

# dictionaries to hold the information
genebank_dict = {}
refseq_dict = {}
kraken_dict = {}
nucleo_dict = {}
taxid_dict = {}
wgsmap_dict = {}

#handle genbank versions? only a few files are available

if 0:
    # parsing each of the files
    print("\n"+"genbank output:")
    for genebank_line in genebank_file_read:
        # parsing by comma delimits
        genebank_line = genebank_line.split(",")
    
        # Taking out indivdual columns

wgs_counter = 0;

if 0:
    print("\n"+"wgs mapping output:")
    for wgsmap_line in wgsmap_file_read:
        # parsing by comma delimits
        wgsmap_line = wgsmap_line.split("\t")
    
        # Taking out indivdual columns
        wgsmap_tax_id = int(wgsmap_line[2])
        wgsmap_acc_id = wgsmap_line[0]
 
        if wgs_counter > 0:
            wgsmap_dict[wgsmap_tax_id] = wgsmap_acc_id;

        wgs_counter += 1;



krakenfiles = glob.glob(kraken_dir+"/*.map")
for kraken_file in krakenfiles:
    version = kraken_file.split(os.sep)[-1].split(".")[0]
    
    kraken_dict[version] = {}
    kraken_file_open = open(path + kraken_file)
    for kraken_line in kraken_file_open.readlines():
        # parsing based on tab delimited format
        kraken_tax_id = 0
        kraken_tax_name = "NA"
        if "kraken2" in kraken_file or "root" in kraken_line or ";" in kraken_line:
            items = kraken_line.split("\t")
            kraken_tax_id = int(items[0])
            kraken_dict[version][kraken_tax_id] = 1
        else:
            items = kraken_line.split("\t")
            # splitting the list on columns 
            kraken_tax_id = int(items[-1])
            kraken_tax_name = items[-1]
            #print kraken_tax_id,
            kraken_dict[version][kraken_tax_id] = 1


if 0:
    refseqfiles = []
    # r=root, d=directories, f = files
    for r, d, f in os.walk(refseq_dir):
        for refseqfile in f:
            refseqfiles.append(os.path.join(r, refseqfile))
        
    print("\n"+"refseq output:")
    for refseq_file in refseqfiles:
        version = refseq_file.split(".")[0].split("release")[-1]
        refseq_dict[version] = {}
        refseq_file_open = open(path + refseq_file)
        refseq_file_read = refseq_file_open.readlines()
        for refseq_line in refseq_file_read:
            # parsing based on tab delimited format
            refseq_line = refseq_line.split("\t")
    
            # splitting the list on columns 
            refseq_tax_id = int(refseq_line[0])
            refseq_tax_name = refseq_line[1]
            refseq_id = refseq_line[2]
    
            refseq_dict[version][refseq_tax_id] = refseq_id

    print("IT SURVIVED THE MONSTEROUS REFSEQ!")

if 0:
    # parsing nucleotide DB
    nucleo_counter = 0;
    print("\n"+"nucleo:")
    for nucleo_line in nucleo_file_read:
        # parsing based on tab delimited format
        nucleo_line = nucleo_line.split("\t")
    
        # splitting the list on columns
        ncbi_tax_nucleo = int(nucleo_line[2])
        accession_nucelo = nucleo_line[0] 
        accession_version_nucleo = nucleo_line[1]
    
        if nucleo_counter > 0:
            nucleo_dict[ncbi_tax_nucleo] = accession_nucelo

        nucleo_counter += 1;

        
# saving the dicitonaries as pickled files

if 0:
    pickle.dump(genebank_dict, open(path_for_storing_pickles + genebank_dict_pickle, "w" ) )

if 0:
    for version in refect_dict.keys():
        pickle.dump(refseq_dict[version], open(path_for_storing_pickles + "v"+version+"."+refseq_dict_pickle, "w" ) )

if 1:
    for version in kraken_dict.keys():
        pickle.dump(kraken_dict[version], open(path_for_storing_pickles + "kraken1_"+version+"."+kraken_dict_pickle, "wb" ) )
#TODO: Flipped to if 1. Looks like script wants nucleo_dict
if 1:
    pickle.dump(nucleo_dict, open(path_for_storing_pickles + nucleo_dict_pickle, "wb" ) )

pickle.dump(taxid_dict, open(path_for_storing_pickles + taxid_dict_pickle, "wb" ) )
pickle.dump(wgsmap_dict, open(path_for_storing_pickles + wgsmap_dict_pickle, "wb" ) )

refseq_dict = {}
if 1:

    #reading from pickle, need versions
    vers = glob.glob(path_for_storing_pickles+"v*")
    versions = []
    for ver in vers:
        versions.append(ver.split(os.sep)[-1].split(".")[0])

    print("Loading refseq pickle:")
    for version in versions:
        refseq_dict[version]  = pickle.load(open(path_for_storing_pickles +version+"."+refseq_dict_pickle, "rb" ))
        #print refseq_dict[version].keys()[-1]

if 1:

    print("Loading genbank pickle:")
    nucleo_dict  = pickle.load(open(path_for_storing_pickles + nucleo_dict_pickle, "rb" ))


#calculate jaccard similarity
all_sets = {}
all_keys = []

if 1:
    taxids = []
    for key in nucleo_dict.keys():
        taxids.append(int(key))
    all_sets["GenBank_060219"] = set(taxids)
for key in kraken_dict.keys():
    taxids = []
    for tid in kraken_dict[key].keys():
        taxids.append(int(tid))
    all_sets["Kraken1_"+key] = set(taxids)
for key in refseq_dict.keys():
    taxids = []
    for tid in refseq_dict[key].keys():
        taxids.append(int(tid))
    all_sets["Refseq_"+key] = set(taxids)


print("Creating jaccard file:")
outfile = open("dbs.jaccard.tsv",'w')
if 1:
    outfile.write("\t")
    #all_sets_list = list(all_sets.keys()[:-1])
    for key in all_sets.keys()[:-1]:
        outfile.write("%s\t"%(key))
    outfile.write("%s\n"%(all_sets.keys()[-1]))
for key2 in all_sets.keys():
    outfile.write("%s\t"%(key2))
    for key1 in all_sets.keys()[:-1]:
#ERROR: float divison by zero
        jaccard = float(len(all_sets[key1].intersection(all_sets[key2])))/float(len(all_sets[key1].union(all_sets[key2])))
        outfile.write("%.9f\t"%(jaccard))
    key1 = all_sets.keys()[-1]
    jaccard = float(len(all_sets[key1].intersection(all_sets[key2])))/float(len(all_sets[key1].union(all_sets[key2])))
    outfile.write("%.9f\n"%(jaccard))
                  
outfile.close()
#using the dictionaries to make the "containment dictionary"
containment_dict = {} # should have {taxid_1: [DB_1, DB_3], taxid_2: [DB_1], ...

print("Creating containment dict:")
## Adding genbank taxonomy
for wgs_key in nucleo_dict.keys():
    wgs_key = int(wgs_key)
    if wgs_key in containment_dict:
        containment_dict[wgs_key].append("GenBank_060219")
    if wgs_key not in containment_dict:
        containment_dict[wgs_key] = ["GenBank_060219"]
    else:
        None

## Adding refseq taxonomy
for version in refseq_dict.keys():
    for refseq_key in refseq_dict[version].keys():
        refseq_key = int(refseq_key)
        if refseq_key in containment_dict:
            containment_dict[refseq_key].append("RefSeq_"+version)
        if refseq_key not in containment_dict:
            containment_dict[refseq_key] = ["RefSeq_"+version]
        else:
            None

## Adding kraken taxonomy
for version in kraken_dict.keys():
    for kraken_key in kraken_dict[version].keys():
        kraken_key = int(kraken_key)
        if kraken_key in containment_dict:
            containment_dict[kraken_key].append("Kraken1_"+version)
        if kraken_key not in containment_dict:
            containment_dict[kraken_key] = ["Kraken1_"+version]
        else:
            None

# saving the "containment dictionary" as a pickled file
## Another script will open the "containment dictionary" and turn it into
## a query like service for an interested end user. 

pickle.dump(containment_dict, open(path_for_storing_pickles + containment_dictionary_pickle, "w" ) )
