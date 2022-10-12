#! usr/bin/python3
### load packages
import pickle, copy, datetime, shutil, argparse, configparser
import os, logging, sys
import glob
import json
import pandas as pd
import pytaxonkit
import itertools
#from _utils import util_filter_out_main_dbnames

### function grabbed from _utils.py
def util_filter_out_main_dbnames(db_iterable):
    '''
    takes an iterable of db names and returns a list containing a subset that includes only the
    latest version of refseq.
    '''
    out = []
    latest_refseq_ver = -1
    latest_refseq_name = ''

    for nm in db_iterable:
        if nm[:6].lower()=='refseq':
            v = int(nm[8:])
            if v > latest_refseq_ver:
                latest_refseq_ver = v
                latest_refseq_name = nm
        else:
            out.append(nm)
    out.append(latest_refseq_name)
    return out

### set directories and files. replace with variable
pathname = os.path.dirname( __file__ )  
script_path = os.path.abspath(pathname)  
up_path = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..'))
#dqt_dir = "/Users/tiszamj/Documents/mike_tisza/database_taxa_query/metscale/scripts"
db_taxids = "containment_dict.json" 

### add if is file
if os.path.isfile(up_path + "/" + db_taxids):
    f = open(up_path + "/" + db_taxids)
    taxid_dict = json.load(f)
else:
    print ("file not found: " + up_path + "/" + db_taxids)
    exit()

main_db_list = util_filter_out_main_dbnames(taxid_dict["taxid_lists"])
if main_db_list:
    print ("DBs for table construction: ")
    for i in main_db_list:
        print (i)
else:
    print ("list of main DBs not found.")
    exit()

### make empty df
large_tax_hi_df = pd.DataFrame(columns=['TaxID','kingdom','phylum','class','order','family','genus','species','DB'])
#for item in itertools.islice(mylist, n):
### Loops through lists of taxids from each of the main DBs 
print ("Looping through DBs to get hierarchy")
for i in main_db_list :
    print (i)
    i_IDs = taxid_dict["taxid_lists"][i]
    result = pytaxonkit.lineage(i_IDs, data_dir = "/Users/tiszamj/Documents/mike_tisza/database_taxa_query/taxdmp/", threads=16, formatstr = "{K};{p};{c};{o};{f};{g};{s}")
    result_df = pd.DataFrame(result[['TaxID','LineageTaxIDs']])
    result_df[['kingdom','phylum','class','order','family','genus','species']] = result_df['LineageTaxIDs'].str.split(';',expand=True)
    result_df = result_df.drop(['LineageTaxIDs'], axis=1)
    result_df['DB'] = i
    large_tax_hi_df = pd.concat([large_tax_hi_df, result_df])

if large_tax_hi_df.empty:
    print ("output table not found. ")
    exit()
else:
    print ("table rows = " + str(len(large_tax_hi_df)))
### write as tsv file
large_tax_hi_df.to_csv(script_path + "/main_DBs_con_dict_hierarchical_taxonomy.tsv", sep = "\t", index_label = False)


