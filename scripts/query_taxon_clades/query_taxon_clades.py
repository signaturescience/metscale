#! usr/bin/python3
### load packages
import pickle, copy, datetime, shutil, argparse, configparser
import os, logging, sys
import glob
import json
import pandas as pd
import pytaxonkit
import itertools
import subprocess


### str2bool not currently used, but could help with future options
def str2bool(v):
    if isinstance(v, bool):
       return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')
        
### set directories and files. replace with variable
pathname = os.path.dirname( __file__ )  
script_path = os.path.abspath(pathname)  
up_path = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..'))

parser = argparse.ArgumentParser(description='Query DBs for all records at or below taxonomical level for given taxid.' \
    'For example, if taxid for genus Bacteroides is given, # sequence records within Bacteroides are returned. ')

required_args = parser.add_argument_group(' REQUIRED ARGUMENTS for query hierarchical taxon')

help_taxid_list = 'The NCBI taxonomy ID(s) to query against the containment_dict metadatabase. Can be in one of ' \
                    'three forms: a) a single integer, which will be queried and the results output, b) a valid path ' \
                    'to a text file containing one taxon ID per line, all of which will be queried and the results ' \
                    'output as tab-delimited text, or c) \'stdin\' in which case a list of taxon_ids is pulled from ' \
                    'standard input and processed as with a file.'

required_args.add_argument('-t', '--taxids', dest='taxid_list', type=str, default=None, help=help_taxid_list)

help_db_table = 'Database hierarchical table. Can be generated from script make_hierarchy_table.py'
required_args.add_argument('-d', '--db_table', dest='db_table', type=str, default= script_path + "/main_DBs_con_dict_hierarchical_taxonomy.tsv", help=help_db_table)

help_output = 'output file name. TSV format.'
required_args.add_argument('-o', '--output', dest='output_file', type=str, default="output_hierarchical_taxonomy.tsv", help=help_output)

args = parser.parse_args()



taxids = []
if args.taxid_list is None:
    #options.parser_store.print_help()
    sys.exit(1)
elif args.taxid_list == 'stdin':
    # while True:
    #     foo = input()
    for foo in sys.stdin:
        if len(foo.strip())==0:
            break
        taxids.append(int(foo.strip()))
elif os.path.isfile(args.taxid_list):
    tf = open(args.taxid_list, 'r')
    tfl = tf.readlines()
    taxids = list(map(lambda x: int(x.strip()), tfl))
else:
    try:
        taxids.append(int(args.taxid_list))
    except:
        logging.error('The taxonID list argument \'-t\' must be either a single integer string, or \'stdin\', or'
                        'a valid file path')
        #options.parser_store.print_help()
        sys.exit(1)

#db_table
if os.path.isfile(args.db_table):
    large_tax_hi_df = pd.read_csv(args.db_table, sep = "\t", header=0)
elif os.path.isfile(args.db_table + ".gz"):
    subprocess.run(['gzip', '-d', args.db_table + ".gz"])
    if os.path.isfile(args.db_table):
        large_tax_hi_df = pd.read_csv(args.db_table, sep = "\t", header=0)
    else:
        print(str(args.db_table) + " not found")
        exit()
else:
    print(str(args.db_table) + " not found")
    exit()

### have to rename because "class" is a no-no column name
large_tax_hi_df = large_tax_hi_df.rename(columns={"class": "tax_class" })

### one column DF
DBs_df = pd.DataFrame({"DB": large_tax_hi_df.DB.unique()})

### actual querying
for taxid in taxids:
    tmp = large_tax_hi_df.query('(TaxID == @taxid) or (kingdom == @taxid) or (phylum == @taxid) or (order == @taxid) or (family == @taxid) or (genus == @taxid) or (species == @taxid)') \
    .groupby('DB').count().reset_index()[['DB', 'TaxID']].rename(columns={"TaxID": "ID_" + str(taxid)})
    DBs_df = pd.merge(DBs_df, tmp, on="DB", how='left')

### remove decimals
pd.options.display.float_format = '{:,.0f}'.format

### current output print to terminal
print(DBs_df.fillna(0))

DBs_df.fillna(0).to_csv(args.output_file, sep="\t", index=False)
'''
NOTES
On my macbook pro, it took 3 seconds to query 50 taxids and 42 seconds to query 1000 taxids

SUGGESTIONS/TO-DO
1. Change output file format and/or print the result in a more compact format ala the other tool
2. Query the taxdump file to get taxon level "species, genus, family, etc" for each query taxid, similar to other script and set the column names to, for example Genus_816 instead of ID_816 (line 96)
 -- Mike Tisza, 2022-10-12
'''