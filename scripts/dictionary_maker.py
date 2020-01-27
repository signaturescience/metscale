#! usr/bin/python
# Author: Dreycey Albin
# Update(s):07/11/2019, 10/31/2019, 11/01/2019 

import pickle
import os
import glob
# from sets import Set
from dictionary_maker_parameters import *

print (" DICTIONARY MAKER v2 ")

# purpose of this script
"""
This script will be used to store the information of the databases, allowing
a quick assesment of what databases contain what organisms. Overall, this will
give insights into why a certain database may not be able to classify an organism
of interest. In addition, it should allow for reasoning the pitfalls of certain 
public databases.
"""

# opening the files
if create_genebank_dict:
    genebank_file_open = open(path + genebank_file)
##refseq_file_open = open(path + refseq_file)

if create_nucleo_dict:
    nucleo_file_open = open(path + nucleo_file)
    nucleo_file_read = nucleo_file_open.readlines()

#wgsmap_file_open = open(path + wgsmap_file)
##refseq_file_read = refseq_file_open.readlines()
#wgsmap_file_read = wgsmap_file_open.readlines()

# dictionaries to hold the information
genebank_dict = {}
refseq_dict = {}
kraken_dict = {}
nucleo_dict = {}
taxid_dict = {}
wgsmap_dict = {}

#handle genbank versions? only a few files are available
if create_genebank_dict:
    # parsing each of the files
    print ("\n"+"genbank output:")
    genebank_file_read = genebank_file_open.readlines()
    for genebank_line in genebank_file_read:
        # parsing by comma delimits
        genebank_line = genebank_line.split(",")
    
#opening/parsing the WGS databases
wgs_counter = 0;
if create_wgsmap_dict:
    print ("\n"+"wgs mapping output:")
    for wgsmap_line in wgsmap_file_read:
        # parsing by comma delimits
        wgsmap_line = wgsmap_line.split("\t")
    
        # Taking out indivdual columns
        wgsmap_tax_id = int(wgsmap_line[2])
        wgsmap_acc_id = wgsmap_line[0]
 
        if wgs_counter > 0:
            wgsmap_dict[wgsmap_tax_id] = wgsmap_acc_id;

        wgs_counter += 1;

#opening/parsing the kraken databases
if create_kraken_dict:
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

#opening/parsing the refseq databases
if create_refseq_dict:
    refseqfiles = []
    # r=root, d=directories, f = files
    for r, d, f in os.walk(refseq_dir):
        for refseqfile in f:
            refseqfiles.append(os.path.join(r, refseqfile))
        
    print ("\n"+"refseq output:")
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

    print ("All of the refseq version have been added!")

#opening/parsing the nt database
if create_nucleo_dict:
    # parsing nucleotide DB
    nucleo_counter = 0;
    print ("\n"+"nucleo:")
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

#opening/parsing the kaiju database
k_counter = 0;
if create_kaiju_dict:
    kaiju_dict = {}
    print ("The Kaiju DB is being opened")
    kaiju_file = open(path+kaiju_file).readlines()

    #line_count = len(kaiju_file)
    print ("The Kaiju DB is being inserted into a dictionary")
    for line in kaiju_file:
        taxid = int(line.split(">")[1].split("_")[-1])
        kaiju_dict[taxid]=1

        #print out status
        #perc = (float(k_counter) // float(line_count))*100
        if k_counter % 10000000 == 0: #in #line_count*[.1,.25,.50,.75,1]:
            print (str(k_counter) + " tax IDs have been added to the Kaiju dict")
        k_counter += 1;

# saving the dicitonaries as pickled files
if create_genebank_dict:
    pickle.dump(genebank_dict, open(path_for_storing_pickles + genebank_dict_pickle, "wb" ) )
if create_refseq_dict:
    for version in refect_dict.keys():
        pickle.dump(refseq_dict[version], open(path_for_storing_pickles + "v"+version+"."+refseq_dict_pickle, "wb" ) )
if create_kraken_dict:
    for version in kraken_dict.keys():
        pickle.dump(kraken_dict[version], open(path_for_storing_pickles + "kraken1_"+version+"."+kraken_dict_pickle, "wb" ) )
if create_nucleo_dict:
    pickle.dump(nucleo_dict, open(path_for_storing_pickles + nucleo_dict_pickle, "wb" ) )
if create_taxid_dict:
    pickle.dump(taxid_dict, open(path_for_storing_pickles + taxid_dict_pickle, "wb" ) )
if create_wgsmap_dict:
    pickle.dump(wgsmap_dict, open(path_for_storing_pickles + wgsmap_dict_pickle, "wb" ) )
if create_kaiju_dict:
    pickle.dump(kaiju_dict, open(path_for_storing_pickles+kaiju_dict_pickle, "wb" ))  #open(path_for_storing_pickles+kaiju_dict_pickle, "w" ) )
            

# Loading in the pickled dictionaries for rebuilding the final containment dictionary
## Refseq pickle import 
refseq_dict = {}
if import_refseq_dict:
    #reading from pickle, need versions
    vers = glob.glob(path_for_storing_pickles+"v*")
    versions = []
    for ver in vers:
        versions.append(ver.split(os.sep)[-1].split(".")[0])

    print ("Loading refseq pickle..")
    for version in versions:
        refseq_dict[version]  = pickle.load(open(path_for_storing_pickles +version+"."+refseq_dict_pickle, "rb" ))
        #print refseq_dict[version].keys()[-1]

## Genbank pickle import 
if import_nucleo_dict:
    print( "Loading genbank pickle..")
    nucleo_dict  = pickle.load(open(path_for_storing_pickles + nucleo_dict_pickle, "rb" ))

## Kraken pickle import
kraken_dict={}
if import_kraken_dict:
    vers = glob.glob(path_for_storing_pickles+"*"+kraken_dict_pickle)
    versions = []
    for ver in vers:
        versions.append(ver.split(os.sep)[-1].split(".")[0])
    print (versions)
    print ("Loading Kraken pickle..")
    for version in versions:
         kraken_dict[version]  = pickle.load(open(path_for_storing_pickles +version+"."+kraken_dict_pickle, "rb" ))

## Kaiju pickle import
if import_kaiju_dict:
    print ("importing the Kaiju pickle..")
    kaiju_dict = pickle.load(open(path_for_storing_pickles+kaiju_dict_pickle, "rb" ))    

#calculate jaccard similarity
if calculate_jaccard:
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

    print ("Creating jaccard file:")
    outfile = open("dbs.jaccard.tsv",'w')
    if 1:
        outfile.write("\t")
        for key in all_sets.keys()[:-1]:
            outfile.write("%s\t"%(key))
        outfile.write("%s\n"%(all_sets.keys()[-1]))
    for key2 in all_sets.keys():
        outfile.write("%s\t"%(key2))
        for key1 in all_sets.keys()[:-1]:
            jaccard = float(len(all_sets[key1].intersection(all_sets[key2])))/float(len(all_sets[key1].union(all_sets[key2])))
            outfile.write("%.9f\t"%(jaccard))
        key1 = all_sets.keys()[-1]
        jaccard = float(len(all_sets[key1].intersection(all_sets[key2])))/float(len(all_sets[key1].union(all_sets[key2])))
        outfile.write("%.9f\n"%(jaccard))
                      
    outfile.close()

#using the dictionaries to make the "containment dictionary"
if create_full_dict:
    containment_dict = {} # should have {taxid_1: [DB_1, DB_3], taxid_2: [DB_1], ...
     
    print ("\n")
    print ("Creating containment dict:")

    ## Adding an already made containment dictionary
    if use_old_containment:
        print ("Adding taxIDs from previous containment file")
        containment_dict = pickle.load(open(path_for_old_containment + containment_dictionary_pickle, "rb" ))
            

    ## Adding genbank taxonomy
    if import_nucleo_dict or create_nucleo_dict:
        print ("Adding genbank taxonomy")
        for wgs_key in nucleo_dict.keys():
            wgs_key = int(wgs_key)
            if wgs_key in containment_dict:
                containment_dict[wgs_key].append("GenBank_060219")
            if wgs_key not in containment_dict:
                containment_dict[wgs_key] = ["GenBank_060219"]
            else:
                None

    ## Adding refseq taxonomy
    if import_refseq_dict or create_refseq_dict:
        print ("Adding refseq taxonomy to containment")
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
    if import_kraken_dict or create_kraken_dict:
        print( "Adding kraken taxonomy containment")
        for version in kraken_dict.keys():
            for kraken_key in kraken_dict[version].keys():
                kraken_key = int(kraken_key)
                if kraken_key in containment_dict:
                    containment_dict[kraken_key].append("Kraken1_"+version)
                if kraken_key not in containment_dict:
                    containment_dict[kraken_key] = ["Kraken1_"+version]
                else:
                    None

    ## Adding Kaiju taxonomy
    if import_kaiju_dict or create_kaiju_dict:
        print ("Adding kaiju taxonomy to containment")
        for kaiju_key in kaiju_dict.keys():
            kaiju_key = int(kaiju_key)
            if kaiju_key in containment_dict:
                containment_dict[kaiju_key].append("Kaiju")
            if kaiju_key not in containment_dict:
                containment_dict[kaiju_key] = ["Kaiju"]
            else:
                None

    # saving the "containment dictionary" as a pickled file
    pickle.dump(containment_dict, open(path_for_storing_pickles + containment_dictionary_pickle, "wb" ));


